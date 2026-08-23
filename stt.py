"""
Nebula v9 — Speech-To-Text (STT) Engine & Microphone Management
"""
import os
import sys
import json
import time
from pathlib import Path
from typing import Optional, Tuple

from config import NCFG, _save_cfg, _VOSK_MODEL_DIR, Log, RICH, rprint, no_c_stderr

# Silence Vosk C-level logging
try:
    from vosk import SetLogLevel
    SetLogLevel(-1)
except Exception:
    pass


def _ensure_vosk_model() -> bool:
    """Download and extract Vosk model if missing."""
    if _VOSK_MODEL_DIR.exists() and any(_VOSK_MODEL_DIR.iterdir()):
        return True
    import urllib.request
    import zipfile
    import tempfile

    url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    if RICH:
        rprint("  [dim yellow]Downloading offline Vosk model (~40MB)...[/dim yellow]")
    else:
        print("  Downloading offline Vosk model (~40MB)...")
    try:
        _VOSK_MODEL_DIR.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tf:
            tmp_zip = tf.name
        urllib.request.urlretrieve(url, tmp_zip)
        with zipfile.ZipFile(tmp_zip, "r") as zf:
            zf.extractall(_VOSK_MODEL_DIR.parent)
        os.remove(tmp_zip)
        if RICH:
            rprint("  [green]✓ Vosk model ready[/green]")
        return True
    except Exception as e:
        Log.error(f"Vosk download failed: {e}")
        return False


class STT:
    """Speech Recognition manager with Google (online) and Vosk (offline) engines."""

    def __init__(self):
        self.ok = False
        self._sr = None
        self._rec = None
        self.vosk_model = None
        self.vosk_rec = None
        self.vosk_ok = False
        self._init()

    def _init(self):
        try:
            import speech_recognition as sr
            self._sr = sr
            r = sr.Recognizer()
            r.energy_threshold = NCFG.get("voice_energy", 300)
            r.dynamic_energy_threshold = NCFG.get("dynamic_energy", True)
            r.dynamic_energy_adjustment_damping = 0.20
            r.pause_threshold = 0.50
            r.non_speaking_duration = 0.40
            r.phrase_threshold = 0.20
            self._rec = r
            self.ok = True
        except ImportError:
            Log.warn("Install: pip install SpeechRecognition pyaudio")
        except Exception as e:
            Log.error(f"STT init error: {e}")

        self._init_vosk()

    def _init_vosk(self):
        try:
            from vosk import Model, KaldiRecognizer, SetLogLevel
            SetLogLevel(-1)
            model_path = NCFG.get("vosk_model_path", "") or str(_VOSK_MODEL_DIR)
            if Path(model_path).exists() and any(Path(model_path).iterdir()):
                self.vosk_model = Model(model_path)
                self.vosk_rec = KaldiRecognizer(self.vosk_model, 16000)
                self.vosk_rec.SetWords(False)
                self.vosk_ok = True
        except Exception as e:
            Log.debug(f"Vosk init: {e}")

    def recognize_google(self, audio) -> Optional[str]:
        if not self.ok:
            return None
        try:
            return self._rec.recognize_google(audio).strip()
        except self._sr.UnknownValueError:
            return None
        except Exception:
            return None

    def recognize_vosk(self, audio) -> Optional[str]:
        if not self.vosk_ok:
            return None
        try:
            raw_data = audio.get_raw_data(convert_rate=16000, convert_width=2)
            if self.vosk_rec.AcceptWaveform(raw_data):
                res = json.loads(self.vosk_rec.Result())
            else:
                res = json.loads(self.vosk_rec.FinalResult())
            text = res.get("text", "").strip()
            return text if text else None
        except Exception:
            return None

    def recognize(self, audio) -> Optional[str]:
        """Recognize audio using configured engine with automatic offline fallback."""
        engine = NCFG.get("stt_engine", "google").lower()
        if engine in ("vosk", "offline"):
            return self.recognize_vosk(audio) or self.recognize_google(audio)
        # Default Google online with Vosk fallback
        text = self.recognize_google(audio)
        if text is None and self.vosk_ok:
            text = self.recognize_vosk(audio)
        return text

    def listen_phrase(self, timeout: float = 4.0, phrase_time_limit: float = 3.0) -> Optional[str]:
        """One-shot targeted listening pass for voice confirmations."""
        if not self.ok:
            return None
        try:
            mic_idx = NCFG.get("mic_device_index")
            with no_c_stderr():
                mic_ctx = self._sr.Microphone(device_index=mic_idx)
            with mic_ctx as source:
                audio = self._rec.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                return self.recognize(audio)
        except Exception:
            return None
