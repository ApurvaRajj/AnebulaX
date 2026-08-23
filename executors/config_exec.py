"""
Nebula v9 — System Configuration, Microphone Diagnostics, and STT/TTS Executors
"""
import re
import platform
from pathlib import Path
from typing import Tuple

from config import NCFG, _save_cfg, _VOSK_MODEL_DIR, Log, no_c_stderr
from stt import _ensure_vosk_model


def _cfg_show(e) -> Tuple[bool, str]:
    lines = [f"  {k:<22} = {v}" for k, v in NCFG.items()]
    return True, "⚙ Current Configuration:\n" + "\n".join(lines)


def _cfg_toggle_tts(e) -> Tuple[bool, str]:
    raw = str(e.get("raw", "") or "").lower()
    if "mute" in raw and "unmute" not in raw:
        NCFG["tts_on"] = False
        _save_cfg(NCFG)
        return True, "All voice output disabled"
    elif "unmute" in raw:
        NCFG["tts_on"] = True
        _save_cfg(NCFG)
        return True, "All voice output enabled"
    current = NCFG.get("tts_on", True)
    NCFG["tts_on"] = not current
    _save_cfg(NCFG)
    state = "enabled" if NCFG["tts_on"] else "disabled"
    return True, f"Voice output {state}"


def _cfg_set_stt(e) -> Tuple[bool, str]:
    q = (e.get("query", "") or e.get("raw", "")).lower()
    if "vosk" in q or "offline" in q:
        NCFG["stt_engine"] = "vosk"
        _save_cfg(NCFG)
        _ensure_vosk_model()
        return True, "STT set to Vosk (offline). Restart voice mode to apply."
    elif "google" in q or "online" in q or "auto" in q:
        NCFG["stt_engine"] = "google"
        _save_cfg(NCFG)
        return True, "STT set to Google (online + offline fallback). Restart voice mode to apply."
    return False, "Usage: 'set stt google' or 'set stt vosk'"


def _cfg_toggle_stt(e) -> Tuple[bool, str]:
    current = NCFG.get("stt_engine", "google").lower()
    new_eng = "vosk" if current in ("google", "online") else "google"
    NCFG["stt_engine"] = new_eng
    _save_cfg(NCFG)
    if new_eng == "vosk":
        _ensure_vosk_model()
    label = "Vosk (offline)" if new_eng == "vosk" else "Google (online + offline fallback)"
    return True, f"STT engine switched to: {label}. Restart voice mode to apply."


def _cfg_show_stt(e) -> Tuple[bool, str]:
    eng = NCFG.get("stt_engine", "google")
    mic = NCFG.get("mic_device_index", "system default")
    model_ok = _VOSK_MODEL_DIR.exists() and any(_VOSK_MODEL_DIR.iterdir())
    return True, f"STT Engine: {eng} | Mic Index: {mic} | Vosk Model: {'Ready' if model_ok else 'Not installed'}"


def _cfg_list_mics(e) -> Tuple[bool, str]:
    try:
        import speech_recognition as sr
        with no_c_stderr():
            names = sr.Microphone.list_microphone_names()
        if not names:
            return False, "No microphone devices found by PyAudio."
        pref = NCFG.get("mic_device_index")
        lines = []
        for i, name in enumerate(names):
            mark = " ◄ (selected)" if pref == i else ""
            lines.append(f"  [{i}] {name}{mark}")
        return True, f"Microphone devices ({len(names)}):\n" + "\n".join(lines)
    except Exception as ex:
        return False, f"Could not list microphones: {ex}"


def _cfg_set_mic(e) -> Tuple[bool, str]:
    q = (e.get("query", "") or e.get("raw", "")).strip().lower()
    for word in ("set", "microphone", "mic", "to"):
        q = q.replace(word, "").strip()
    if q in ("default", "system", "auto", "none", "-1", ""):
        NCFG["mic_device_index"] = None
        _save_cfg(NCFG)
        return True, "Microphone set to system default. Restart voice mode to apply."
    try:
        idx = int(q)
        NCFG["mic_device_index"] = idx
        _save_cfg(NCFG)
        return True, f"Microphone device set to [{idx}]. Restart voice mode to apply."
    except ValueError:
        return False, "Usage: 'set mic <number>' or 'set mic default'"


def _cfg_set_energy(e) -> Tuple[bool, str]:
    q = str(e.get("query", "") or e.get("setting_value", "") or e.get("raw", "")).strip()
    nums = re.findall(r"\d+", q)
    if not nums:
        current = NCFG.get("voice_energy", 300)
        return False, f"Current energy threshold: {current}. Usage: 'set energy 150' (more sensitive) or 'set energy 300' (default)"
    val = max(50, min(3000, int(nums[0])))
    NCFG["voice_energy"] = val
    _save_cfg(NCFG)
    return True, f"Energy threshold set to {val}. Restart voice mode to apply."


def _cfg_set_dynamic(e) -> Tuple[bool, str]:
    raw = str(e.get("raw", "") or "").lower()
    q = str(e.get("query", "") or e.get("setting_value", "") or "").strip().lower()
    text = f"{raw} {q}".lower()
    words = text.split()
    on_words = {"on", "true", "1", "yes", "enable", "auto"}
    off_words = {"off", "false", "0", "no", "disable", "fixed", "manual"}
    if any(w in on_words for w in words):
        NCFG["dynamic_energy"] = True
        _save_cfg(NCFG)
        return True, "Dynamic energy threshold: ON (auto-adjusts to room noise). Restart voice mode to apply."
    elif any(w in off_words for w in words):
        NCFG["dynamic_energy"] = False
        _save_cfg(NCFG)
        return True, f"Dynamic energy threshold: OFF (uses fixed threshold: {NCFG.get('voice_energy', 300)}). Restart voice mode to apply."
    elif "toggle" in raw or "switch" in raw:
        current = NCFG.get("dynamic_energy", True)
        new_val = not current
        NCFG["dynamic_energy"] = new_val
        _save_cfg(NCFG)
        state_str = "ON (auto-adjusts to room noise)" if new_val else "OFF (uses fixed threshold)"
        return True, f"Dynamic energy threshold: {state_str}. Restart voice mode to apply."
    else:
        current = NCFG.get("dynamic_energy", True)
        return False, f"Dynamic energy threshold: {'ON' if current else 'OFF'}\nUsage: 'set dynamic on', 'set dynamic off', or 'toggle dynamic'"


def _cfg_test_mic(e) -> Tuple[bool, str]:
    """Full 6-step microphone diagnostic."""
    lines = ["🎙 Microphone Diagnostic:"]
    try:
        import speech_recognition as sr
        lines.append("  [1/5] SpeechRecognition: OK")
    except ImportError:
        return False, "SpeechRecognition package is not installed."

    try:
        import pyaudio
        lines.append("  [2/5] PyAudio: OK")
    except ImportError:
        lines.append("  [2/5] PyAudio: NOT INSTALLED (Required on Linux/Windows)")

    try:
        names = sr.Microphone.list_microphone_names()
        lines.append(f"  [3/5] Devices detected: {len(names)}")
    except Exception as ex:
        lines.append(f"  [3/5] Device listing failed: {ex}")

    lines.append(f"  [4/5] Energy threshold: {NCFG.get('voice_energy', 300)} (Dynamic: {NCFG.get('dynamic_energy', True)})")
    lines.append(f"  [5/5] Active STT engine: {NCFG.get('stt_engine', 'google')}")
    return True, "\n".join(lines)
