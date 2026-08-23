"""
AnebulaX — Text-To-Speech (TTS) Engine & Multi-Engine Speech Queue
"""
import os
import re
import sys
import queue
import shutil
import tempfile
import threading
import subprocess
from typing import Optional

from config import IS_WIN, IS_MAC, IS_LINUX, NCFG, Log, no_c_stderr
from intents_db import _SPEAK_EXECUTORS, _SILENT_EXECUTORS

_spk_ref = [None]


def _find_audio_player() -> Optional[list]:
    """Find installed CLI audio player on the system."""
    if IS_WIN:
        if shutil.which("ffplay"):
            return ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"]
        return None
    elif IS_MAC:
        if shutil.which("afplay"):
            return ["afplay"]
        if shutil.which("ffplay"):
            return ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"]
        return None
    else:  # Linux
        if shutil.which("ffplay"):
            return ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"]
        if shutil.which("paplay"):
            return ["paplay"]
        if shutil.which("mpg123"):
            return ["mpg123", "-q"]
        if shutil.which("mpv"):
            return ["mpv", "--no-video", "--really-quiet"]
        if shutil.which("aplay"):
            return ["aplay", "-q"]
        return None


def _tts_clean(text: str) -> str:
    """Strip markdown formatting, URLs, code fences, and ANSI codes before speaking."""
    if not text:
        return ""
    text = re.sub(r'```[\s\S]*?```', 'code block omitted', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'https?://\S+', 'URL', text)
    text = re.sub(r'\x1b\[[0-9;]*m', '', text)
    text = re.sub(r'[#*_~>]+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _should_speak(executor: str) -> bool:
    """Return True if executor output should be spoken aloud."""
    if not NCFG.get("tts_on", True):
        return False
    if executor in _SILENT_EXECUTORS:
        return False
    if executor in _SPEAK_EXECUTORS:
        return True
    return False


class TTS:
    """Thread-safe multi-engine TTS queue with per-role muting."""

    def __init__(self):
        self._q = queue.Queue()
        self._mode = "none"
        self._pyttsx = None
        self._player_cmd = _find_audio_player()
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._init_engine()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
        _spk_ref[0] = self

    def _init_engine(self):
        # 1. High-quality gTTS if audio player is present
        try:
            import gtts
            if self._player_cmd:
                self._mode = "gtts"
                Log.info(f"TTS initialized with gTTS (player={' '.join(self._player_cmd)})")
                return
        except ImportError:
            pass

        # 2. Try pyttsx3 if native driver works
        try:
            import pyttsx3
            # On Linux, only use pyttsx3 if aplay or espeak binary is present
            if not IS_LINUX or shutil.which("aplay") or shutil.which("espeak-ng") or shutil.which("espeak"):
                with no_c_stderr():
                    self._pyttsx = pyttsx3.init()
                    self._pyttsx.setProperty("rate", 175)
                self._mode = "pyttsx"
                Log.info("TTS initialized with pyttsx3")
                return
        except Exception as e:
            Log.debug(f"pyttsx3 init failed: {e}")

        # 3. Try macOS say
        if IS_MAC and shutil.which("say"):
            self._mode = "say"
            return

        # 4. Try Linux native tools
        if IS_LINUX:
            for tool in ["espeak-ng", "espeak", "festival", "flite"]:
                if shutil.which(tool):
                    self._mode = tool
                    Log.info(f"TTS initialized with {tool}")
                    return

        # 5. Fallback gTTS with whatever player
        try:
            import gtts
            self._mode = "gtts"
            Log.info("TTS initialized with gTTS")
        except ImportError:
            self._mode = "none"
            Log.warn("No TTS engine available. Speech output disabled.")

    def speak(self, text: str, role: str = "nebula"):
        """Queue text to speak. role can be 'nebula' or 'nova'."""
        if not text or not NCFG.get("tts_on", True):
            return
        if role == "nebula" and not NCFG.get("tts_nebula", True):
            return
        if role == "nova" and not NCFG.get("tts_nova", True):
            return
        cleaned = _tts_clean(text)
        if cleaned:
            self._q.put((cleaned, role))

    def _worker(self):
        while not self._stop_event.is_set():
            try:
                item = self._q.get(timeout=0.5)
            except queue.Empty:
                continue
            if item is None:
                break
            text, role = item
            self._play(text)
            self._q.task_done()

    def _play(self, text: str):
        with self._lock:
            try:
                if self._mode == "gtts":
                    from gtts import gTTS
                    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf:
                        tmp_name = tf.name
                    tts = gTTS(text=text, lang="en")
                    tts.save(tmp_name)
                    player = self._player_cmd or (["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"] if shutil.which("ffplay") else None)
                    if player:
                        cmd = player + [tmp_name]
                        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    try:
                        os.remove(tmp_name)
                    except Exception:
                        pass
                elif self._mode == "pyttsx" and self._pyttsx:
                    with no_c_stderr():
                        self._pyttsx.say(text)
                        self._pyttsx.runAndWait()
                elif self._mode in ("espeak-ng", "espeak"):
                    subprocess.run([self._mode, "-s", "170", text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif self._mode == "say":
                    subprocess.run(["say", "-r", "185", text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif self._mode == "flite":
                    subprocess.run(["flite", "-t", text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                Log.error(f"TTS play error: {e}")

    def stop(self):
        self._stop_event.set()
        self._q.put(None)
