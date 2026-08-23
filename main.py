"""
Nebula v9 — Main Application Entrypoint, CLI REPL, Voice Mode, and AI Queue
"""
import os
import sys
import time
import queue
import threading
import platform
from pathlib import Path
from typing import Optional, Tuple

from config import (
    VERSION, NCFG, _save_cfg, _theme, Log, RICH, _RICH, rprint, Panel,
    _CMD_HISTORY_FILE
)
from licensing import verify_license, ensure_default_license
from intents_db import _CMD_TABLE
from matcher import Matcher, _typo_correct, apply_aliases
from tts import TTS, _should_speak, _tts_clean
from stt import STT, _ensure_vosk_model
from executors import (
    _e, find_bookmark, find_software, _open_software_by_path,
    smart_url_parse, _me_solve, _open_url
)
from executors.common import _VOICE_MODE_ACTIVE, _STT_REF


def _add_cmd_history(raw: str, ok: bool, msg: str):
    try:
        import json
        history = []
        if _CMD_HISTORY_FILE.exists():
            try:
                history = json.loads(_CMD_HISTORY_FILE.read_text(encoding="utf-8"))
            except Exception:
                history = []
        history.append({
            "command": raw,
            "success": ok,
            "output": msg[:200],
            "timestamp": time.time()
        })
        history = history[-100:]  # Keep last 100
        _CMD_HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")
    except Exception:
        pass


class GeminiProvider:
    """Gemini AI client wrapper for Nova mode."""

    def __init__(self):
        self.ok = False
        self._model = None
        self._init()

    def _init(self):
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self._model = genai.GenerativeModel("gemini-1.5-flash")
                self.ok = True
            except Exception as e:
                Log.debug(f"Gemini SDK init: {e}")

    def ask(self, prompt: str) -> str:
        prompt_clean = prompt
        for prefix in ("nova ", "ask nova ", "hey nova "):
            if prompt_clean.lower().startswith(prefix):
                prompt_clean = prompt_clean[len(prefix):].strip()
                break

        if self._model:
            try:
                resp = self._model.generate_content(prompt_clean)
                return resp.text.strip()
            except Exception as e:
                Log.error(f"Gemini API error: {e}")

        # Fallback Antigravity / Gemini CLI
        import subprocess
        for cli in ("agy", "gemini"):
            try:
                p = subprocess.run([cli, "ask", prompt_clean], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=12)
                if p.returncode == 0 and p.stdout.strip():
                    return p.stdout.strip()
            except Exception:
                pass

        return "__NOVA_SETUP__ Nova AI requires GEMINI_API_KEY or 'agy auth login'."


class Nebula:
    """Nebula & Nova Desktop Voice Assistant."""

    def __init__(self):
        ensure_default_license()
        self.matcher = Matcher(_CMD_TABLE)
        self.spk = TTS()
        self.stt = STT()
        self.gemini = GeminiProvider()
        self.voice_mode = False
        self._nova_queue = queue.Queue()
        self._nova_thread = threading.Thread(target=self._nova_worker, daemon=True)
        self._nova_thread.start()

    def _nova_worker(self):
        while True:
            raw = self._nova_queue.get()
            if raw is None:
                break
            try:
                resp = self.gemini.ask(raw)
                if resp:
                    no_speak = resp.startswith("__NOVA_SETUP__")
                    resp_display = resp.replace("__NOVA_SETUP__", "")
                    self._output(True, resp_display, nova=True)
                    if no_speak:
                        self.spk.speak("Nova setup instructions are displayed on your screen.", role="nova")
                    else:
                        self.spk.speak(resp_display[:200], role="nova")
            except Exception as ex:
                self._output(False, f"Nova error: {ex}")
            finally:
                self._nova_queue.task_done()

    def banner(self):
        c = _theme()
        tts_state = "on" if NCFG.get("tts_on", True) else "off"
        stt_engine = NCFG.get("stt_engine", "google")
        lic_ok, lic_msg, _ = verify_license()
        lic_badge = f"[green]{lic_msg}[/green]" if lic_ok else f"[red]{lic_msg}[/red]"
        if RICH:
            rprint(Panel(
                f"[bold {c}]NEBULA / NOVA v{VERSION}[/bold {c}]\n"
                f"[dim]Type a command or say 'help'. Prefix with [bold]nova[/bold] to use AI.[/dim]\n"
                f"[dim]Voice: {tts_state} | STT: {stt_engine} | License: {lic_badge}[/dim]",
                title=f"[{c}]NEBULA v{VERSION}[/{c}]", border_style=c))
        else:
            print(f"\n{'='*60}\n  NEBULA / NOVA v{VERSION}\n  Voice:{tts_state} | STT:{stt_engine}\n{'='*60}\n")

    def _output(self, ok: bool, msg: str, nova: bool = False):
        c = _theme()
        icon = "✓" if ok else "✗"
        if not msg:
            return
        if RICH:
            if nova:
                rprint(Panel(msg.strip(), title=f"[bold {c}]Nova[/bold {c}]", border_style=c, padding=(0, 2)))
            elif "\n" in msg:
                color = "green" if ok else "red"
                rprint(Panel(msg.strip(), border_style=color, padding=(0, 1)))
            else:
                color = "green" if ok else "red"
                rprint(f"  [{color}]{icon}[/{color}] {msg}")
        else:
            prefix = "[OK]" if ok else "[!!]"
            print(f"  {prefix} {msg}")

    def run_cmd(self, raw: str) -> Tuple[bool, str]:
        raw = (raw or "").strip()
        if not raw:
            return False, ""

        # Check Nova AI routing
        low = raw.lower()
        if low.startswith("nova ") or low.startswith("ask nova ") or low.startswith("hey nova "):
            self._nova_queue.put(raw)
            if RICH:
                rprint("  [dim]◈ Nova is thinking...[/dim]")
            else:
                print("  ◈ Nova is thinking...")
            return True, "Queued to Nova"

        # Check multi-command chaining (" and ", " then ")
        if " and " in low or " then " in low:
            delim = " and " if " and " in low else " then "
            sub_cmds = [s.strip() for s in raw.split(delim) if s.strip()]
            if len(sub_cmds) > 1:
                results = []
                all_ok = True
                for sc in sub_cmds:
                    ok, msg = self.run_cmd(sc)
                    results.append(msg)
                    if not ok:
                        all_ok = False
                return all_ok, "\n".join(results)

        # Match intent
        match = self.matcher.match(raw)
        if match:
            intent, score, entities = match
            fn = _e(intent)
            if fn:
                try:
                    res = fn(entities)
                    if res and len(res) == 2:
                        ok, msg = res
                    else:
                        ok, msg = False, "Unexpected executor result"
                    if msg:
                        self._output(ok, msg)
                        if ok and self.spk and _should_speak(intent):
                            self.spk.speak(_tts_clean(msg[:200]), role="nebula")
                    _add_cmd_history(raw, ok, msg)
                    return ok, msg
                except Exception as ex:
                    self._output(False, f"Command error: {ex}")
                    return False, str(ex)

        # Smart fallback: Bookmarks, Software, Smart URLs, Math
        clean_raw = apply_aliases(raw, {"open", "goto"})
        bm_key, bm_url = find_bookmark(clean_raw)
        if bm_url:
            _open_url(bm_url)
            msg = f"Opening bookmark: {bm_key}"
            self._output(True, msg)
            if self.spk and _should_speak("web_url"):
                self.spk.speak(msg, role="nebula")
            _add_cmd_history(raw, True, msg)
            return True, msg

        sw_key, sw_path = find_software(clean_raw)
        if sw_path and _open_software_by_path(sw_path):
            msg = f"Opening {sw_key}"
            self._output(True, msg)
            if self.spk and _should_speak("app_open"):
                self.spk.speak(msg, role="nebula")
            _add_cmd_history(raw, True, msg)
            return True, msg

        parsed_url = smart_url_parse(clean_raw)
        if parsed_url:
            _open_url(parsed_url)
            msg = f"Opening: {parsed_url}"
            self._output(True, msg)
            if self.spk and _should_speak("web_url"):
                self.spk.speak(msg, role="nebula")
            _add_cmd_history(raw, True, msg)
            return True, msg

        import re
        if re.match(r'^[\d\s\+\-\*\/\^\(\)\.\%]+$', raw) and any(op in raw for op in "+-*/^"):
            try:
                ok, msg = _me_solve({"query": raw, "raw": raw})
                if ok:
                    self._output(True, msg)
                    if self.spk:
                        self.spk.speak(msg, role="nebula")
                    _add_cmd_history(raw, True, msg)
                    return True, msg
            except Exception:
                pass

        self._output(False, f"I didn't understand '{raw[:50]}'. Type 'help' for commands.")
        _add_cmd_history(raw, False, "unrecognized")
        return False, "unrecognized"

    def voice_mode_run(self):
        """Voice listening loop with dynamic confirmations and noise calibration."""
        if not self.stt.ok:
            if RICH:
                rprint("  [red]STT engine is unavailable. Please install SpeechRecognition & PyAudio.[/red]")
            else:
                print("  STT engine is unavailable.")
            return

        self.voice_mode = True
        _VOICE_MODE_ACTIVE[0] = True
        _STT_REF[0] = self.stt

        engine = NCFG.get("stt_engine", "google").lower()
        if engine in ("vosk", "offline"):
            _ensure_vosk_model()

        if RICH:
            rprint("  [bold green]🎙 Voice Mode ACTIVE[/bold green] [dim](Say 'stop listening' to exit)[/dim]")
        else:
            print("  🎙 Voice Mode ACTIVE (Say 'stop listening' to exit)")

        import speech_recognition as sr
        mic_idx = NCFG.get("mic_device_index")

        try:
            with sr.Microphone(device_index=mic_idx) as source:
                r = self.stt._rec
                if NCFG.get("dynamic_energy", True):
                    r.adjust_for_ambient_noise(source, duration=0.8)

                while self.voice_mode:
                    try:
                        audio = r.listen(source, timeout=5.0, phrase_time_limit=8.0)
                        text = self.stt.recognize(audio)
                        if text:
                            text_clean = text.strip()
                            if RICH:
                                rprint(f"  [cyan]🗣 Heard:[/cyan] {text_clean}")
                            else:
                                print(f"  🗣 Heard: {text_clean}")

                            if text_clean.lower() in ("stop listening", "exit voice", "stop voice", "quit voice"):
                                self.voice_mode = False
                                break

                            self.run_cmd(text_clean)
                    except sr.WaitTimeoutError:
                        continue
                    except Exception as e:
                        Log.debug(f"Voice loop cycle: {e}")
                        time.sleep(0.1)
        except Exception as ex:
            if RICH:
                rprint(f"  [red]Microphone error: {ex}[/red]")
            else:
                print(f"  Microphone error: {ex}")
        finally:
            self.voice_mode = False
            _VOICE_MODE_ACTIVE[0] = False
            if RICH:
                rprint("  [dim]🎙 Voice Mode stopped.[/dim]")
            else:
                print("  🎙 Voice Mode stopped.")


def main():
    neb = Nebula()
    neb.banner()

    while True:
        try:
            if RICH and _C:
                cmd = _C.input("[bold blue]nebula>[/bold blue] ").strip()
            else:
                cmd = input("nebula> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting Nebula. Goodbye!")
            break

        if not cmd:
            continue
        if cmd.lower() in ("exit", "quit", "q"):
            print("Goodbye!")
            break
        elif cmd.lower() in ("voice", "listen", "start voice"):
            neb.voice_mode_run()
        else:
            neb.run_cmd(cmd)


if __name__ == "__main__":
    main()
