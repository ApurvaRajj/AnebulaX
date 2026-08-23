"""
Nebula v9 — Text-To-Speech (TTS) Engine & Speech Queue
"""
import os
import re
import sys
import queue
import threading
import subprocess
from typing import Optional

from config import IS_WIN, IS_MAC, IS_LINUX, NCFG, Log
from intents_db import _SPEAK_EXECUTORS, _SILENT_EXECUTORS

_spk_ref = [None]


def _tts_clean(text: str) -> str:
    """Strip markdown formatting, URLs, code fences, and ANSI codes before speaking."""
    if not text:
        return ""
    # Strip markdown code blocks
    text = re.sub(r'```[\s\S]*?```', 'code block omitted', text)
    # Strip inline code
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Strip URLs
    text = re.sub(r'https?://\S+', 'URL', text)
    # Strip ANSI color codes
    text = re.sub(r'\x1b\[[0-9;]*m', '', text)
    # Strip markdown headers, bold, italics, bullets
    text = re.sub(r'[#*_~>]+', '', text)
    # Collapse multiple whitespace
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
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._init_engine()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
        _spk_ref[0] = self

    def _init_engine(self):
        # 1. Try pyttsx3
        try:
            import pyttsx3
            self._pyttsx = pyttsx3.init()
            self._pyttsx.setProperty("rate", 175)
            self._mode = "pyttsx"
            Log.info("TTS initialized with pyttsx3")
            return
        except Exception as e:
            Log.debug(f"pyttsx3 init failed: {e}")

        # 2. Try macOS say
        if IS_MAC:
            self._mode = "say"
            return

        # 3. Try Linux native tools
        if IS_LINUX:
            for tool in ["espeak-ng", "espeak", "festival", "flite"]:
                try:
                    p = subprocess.run([tool, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    if p.returncode == 0 or tool == "festival":
                        self._mode = tool
                        Log.info(f"TTS initialized with {tool}")
                        return
                except Exception:
                    pass

        # 4. Fallback gTTS
        try:
            import gtts
            self._mode = "gtts"
            Log.info("TTS initialized with gTTS (fallback)")
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
                if self._mode == "pyttsx" and self._pyttsx:
                    self._pyttsx.say(text)
                    self._pyttsx.runAndWait()
                elif self._mode in ("espeak-ng", "espeak"):
                    subprocess.run([self._mode, "-s", "170", text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif self._mode == "say":
                    subprocess.run(["say", "-r", "185", text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif self._mode == "flite":
                    subprocess.run(["flite", "-t", text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif self._mode == "gtts":
                    import tempfile
                    from gtts import gTTS
                    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf:
                        tmp_name = tf.name
                    tts = gTTS(text=text, lang="en")
                    tts.save(tmp_name)
                    if IS_WIN:
                        subprocess.run(["ffplay", "-nodisp", "-autoexit", tmp_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    elif IS_MAC:
                        subprocess.run(["afplay", tmp_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        subprocess.run(["ffplay", "-nodisp", "-autoexit", tmp_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    try:
                        os.remove(tmp_name)
                    except Exception:
                        pass
            except Exception as e:
                Log.error(f"TTS play error: {e}")

    def stop(self):
        self._stop_event.set()
        self._q.put(None)
