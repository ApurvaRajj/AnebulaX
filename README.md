# AnebulaX — AI Voice + OS Assistant

A cross-platform (Windows/macOS/Linux) voice-controlled desktop assistant with offline command recognition, modular architecture, and optional online AI (Gemini REST API or Antigravity/gemini CLI) integration.

## What It Does

AnebulaX listens for voice commands (or accepts typed commands), matches them against a collection of intent patterns, and executes the corresponding action — opening apps, controlling the browser, managing files, running dev tools, answering questions, and more.

Two modes:
- **AnebulaX** (offline) — wake word "anebulax", processes commands locally via the word-set intent matcher
- **Nova** (online) — wake word "nova", routes questions to Gemini (API key preferred, Antigravity/Gemini CLI fallback)

## Architecture

```
User Input (voice/text)
        │
        ▼
┌──────────────────┐
│  Typo Corrector  │  ← fixes "volune" → "volume", "defien" → "define", "toggel" → "toggle"
└────────┬─────────┘
         ▼
┌──────────────────┐
│  Alias Applier   │  ← user-defined: "not bad" → "notepad" (~/.anebulax_aliases.json)
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Multi-step Split │  ← "go to youtube and reduce volume" → 2 commands
└────────┬─────────┘
         ▼
┌──────────────────┐
│    Matcher       │  ← word-set intersection scoring: weight × (1 + specificity×0.5) × (1 + n×0.1)
│ (1000+ patterns) │     scans _CMD_TABLE for best trigger-set match
└────────┬─────────┘
         ▼
┌──────────────────┐
│ Entity Extractor │  ← extracts {query}, {name}, {duration}, {level}, etc.
└────────┬─────────┘
         ▼
┌──────────────────┐
│    Executor      │  ← 743 functions: _fs_mkdir, _sys_vol_up, _p_time, etc.
└────────┬─────────┘
         ▼
┌──────────────────┐
│  TTS (speak)     │  ← only for informational responses (time, jokes, results)
│  + Output        │     action confirmations (chrome opened, volume up) are silent
└──────────────────┘
```

### Key Components & Modular Structure

The codebase is partitioned into distinct modular components:
- **`matcher.py`** — Word-set intersection scoring. Each command is a `frozenset` of trigger words; if all words in a trigger set appear in the input, it matches. Score = `weight × (1 + specificity×0.5) × (1 + n×0.1)` where `n` is the number of trigger words.
- **`intents_db.py`** — Central trigger table (`_CMD_TABLE`), speech routing filters (`_SPEAK_EXECUTORS`, `_SILENT_EXECUTORS`), facts, quotes, and affirmations data.
- **`licensing.py`** — Offline asymmetric Ed25519 licensing system (`~/.anebulax_license.key`).
- **`tts.py`** — Thread-safe queue with per-role muting. Engines: gTTS (online, natural) → pyttsx3 (offline) → espeak-ng → festival → flite → say (macOS). A `_SPEAK_EXECUTORS` set controls which commands speak vs stay silent.
- **`stt.py`** — Configurable: Google (online, default) or Vosk (offline) with `pause_threshold = 0.50s` and `non_speaking_duration = 0.40s`. Switch with `set stt google` / `set stt vosk`. Microphone device selection via `list mics` / `set mic N`.
- **`executors/`** — 100% of all 743 executors natively partitioned into domain modules (`system.py`, `web.py`, `media.py`, `productivity.py`, `developer.py`, `math_solver.py`, `config_exec.py`, `common.py`) with zero monolithic fallback dependency.
- **`main.py` / `anebulax.py`** — Application entrypoint, CLI REPL, Nova AI async worker, and voice loop with active confirmation handling and low-level C stderr audio suppression.

## Installation

```bash
pip install -r requirements.txt
```

**Linux system deps:**
```bash
sudo apt install portaudio19-dev espeak-ng ffplay xdotool wmctrl
```

**macOS:**
```bash
brew install portaudio ffmpeg
```

**Windows:** PyAudio wheels are prebuilt for Python 3.7–3.13 — `pip install pyaudio` should just work. If not: `pip install pipwin && pipwin install pyaudio`.

## Usage

```bash
python anebulax.py
# or: python main.py
```

Type commands or say `voice` to start voice mode. Type `help` for the full command reference.

### Voice Mode Troubleshooting

If voice mode prints "Voice mode ON" but doesn't detect speech:

1. **Run `test mic`** — checks if `speech_recognition` and `pyaudio` are installed, lists available mic devices, shows the energy threshold, and checks the active STT engine.
2. **Run `list mics`** — lists all microphone devices by index.
3. **Pick the right device** — `set mic 0` (or whichever index `list mics` shows for your headset/mic). Restart voice mode.
4. **Lower the energy threshold** — run `set dynamic off` then `set energy 150` (more sensitive). Restart voice mode.
5. **Windows mic permissions** — Settings → Privacy → Microphone → "Allow desktop apps to access the microphone" must be ON.
6. **Check `stt status`** — shows the active engine, mic index, and Vosk model state.

**Voice commands reference:**

| Command | What it does |
|---------|-------------|
| `voice` | Start/stop voice mode |
| `test mic` | Microphone diagnostic (deps, devices, levels, STT engine) |
| `list mics` | List all microphone devices |
| `set mic N` | Pick mic device by index (from `list mics`) |
| `set mic default` | Reset to system default mic |
| `set energy 300` | Set energy threshold (lower = more sensitive; 50–3000) |
| `set dynamic on` / `off` / `toggle dynamic` | Toggle auto-adjusting energy threshold |
| `set stt google` / `vosk` | Switch speech recognition engine |
| `stt status` | Show current STT/mic configuration |
| `toggle tts` / `mute voice` / `unmute voice` | Toggle spoken audio output |

### User-Configurable Files

All in `~/.anebulax_*`:

| File | Purpose | Format |
|------|---------|--------|
| `.anebulax_aliases.json` | Word substitutions | `{"not bad": "notepad"}` |
| `.anebulax_bookmarks.json` | Custom site shortcuts | `{"canva": "https://www.canva.com"}` |
| `.anebulax_software.txt` | Custom app paths (hot-reloaded) | `spotify \| /opt/spotify/spotify` |
| `.anebulax_license.key` | Offline signed license file (Ed25519) | Signed JSON payload |
| `.anebulax_notes_db.json` | Structured notes | Auto-managed |
| `.anebulax_cmd_history.json` | Command history (for `repeat`) | Auto-managed |
| `.anebulax_reminders.json` | Persisted reminders | Auto-managed |
| `.anebulax_config.json` | Settings (STT engine, theme, mic index, etc.) | Auto-managed |

## Known Limitations

1. **Modular Architecture** — All 743 executors are implemented directly in `executors/` with zero dependency on any legacy monolithic script. `anebulax.py` and `main.py` serve as the clean primary modular entrypoints.
2. **Licensing system & Key Management** — AnebulaX implements Option B (Offline signed license file using asymmetric Ed25519 public-key verification). The client embeds only `EMBEDDED_PUBLIC_KEY_HEX`, verifying genuine vendor signatures without a server. Vendor private keys are not stored in the repository; they are intended to be generated offline and kept strictly in vendor secret environments (`NEBULA_VENDOR_PRIVATE_KEY`). A pre-signed evaluation license is shipped with the client for out-of-the-box community testing.
3. **Voice confirmation for dangerous commands** — Shutdown, restart, sleep, and logout commands require explicit confirmation. In voice mode, the engine speaks the confirmation prompt and actively executes a targeted listening pass for verbal confirmation ("yes", "confirm", "proceed") before proceeding.
4. **Trigger-set redundancy** — 341 executors have more than one unique trigger-set registered in `_CMD_TABLE`, totaling 875 unique trigger-sets among them. This is intentional (natural-language robustness — "set volume to 50", "change volume 50", "volume 50" all route to the same executor) but inflates the pattern count.
5. **Functional duplication between `mm_*` and `clip_*`/`sys_*` batches** — Real duplicates identified in earlier versions (`mm_lock`/`sys_lock`, `mm_copy`/`clip_copy_sel`, `mm_cut`/`clip_cut`, `mm_paste`/`clip_paste`, `mm_maximize_app`/`win_max`, `mm_minimize_app`/`win_min_all`) have been consolidated to unified implementations.
6. **Dead references in the SILENT list** — 59 executor names appear in `_SILENT_EXECUTORS` but have no corresponding entry in the dispatch dict `_e()`. None of these 59 appear in `_CMD_TABLE` either, so they are unreachable by any user command. Breakdown by prefix: 30 `web_open_*` names, 8 other `web_*` names, 7 `sys_*` names, 5 `mm_*` media names, 3 `win_*` names, 2 `fs_*` names, and 4 others.
7. **Browser tab control** — `refresh`, `close tab`, etc. require a browser to be the focused window. Uses `xdotool` on Linux, `SendKeys` on Windows, `osascript` on macOS.

### History: dead executors & security rotation (fixed)

- **Dead Executors (Fixed)**: An earlier version of this codebase had 121 dead executors — commands referenced in `_CMD_TABLE` but not implemented in `_e()`. These caused silent failures on real commands. This was resolved by implementing missing handlers and creating regression test `TestNoDeadExecutors::test_all_matched_executors_are_dispatchable`.
- **Key Exposure & Rotation (Fixed)**: During adversarial security review, an initial draft implementation of `licensing.py` included a hardcoded demo vendor private key (`VENDOR_DEMO_PRIV_HEX`). The key was immediately revoked and rotated with a fresh offline Ed25519 keypair. The client source code was purged of all private key variables, the evaluation license re-signed offline under the fresh master key, and a pre-commit secret-scanning hook (`scripts/pre_commit_secret_scan.py`) plus unit test assertions (`TestLicensingSystemSecurity::test_no_private_key_hardcoded_in_source`) installed to permanently prevent unapproved secret inclusion.

## Testing

```bash
python -m pytest test_matcher.py -v
```

46 tests covering:
- Matcher routing, word-set scoring, and specificity tie-breaking
- Zero dead executors across all 743 triggers (`test_all_matched_executors_are_dispatchable`)
- No bare `except:` statements across all modules (`test_no_bare_except`)
- User-defined aliases and typo corrections (`test_alias_not_bad`, `test_typo_correction_define`)
- Software hot-reloading without restart (`test_software_hot_reloading`)
- Consolidated executor routing (`test_lock_consolidation`, `test_clipboard_consolidation`, `test_window_max_consolidation`)
- Offline asymmetric Ed25519 licensing security and zero private key hardcoding (`test_no_private_key_hardcoded_in_source`, `test_shipped_public_key_authenticates_community_license`, `test_forged_or_tampered_signature_rejected`, `test_expired_license_rejected`)
- User configuration file auto-generation and reminder persistence (`test_user_files_exist`, `test_reminder_written_to_file`)

## AI Assistance Disclosure

This codebase was developed with AI assistance (Claude/GLM). The architecture, bug fixes, and feature ports were guided by human review and rigorous adversarial security verification. Adversarial testing identified a critical private key exposure vulnerability during early licensing drafting, prompting an immediate master key rotation, offline pre-signing architecture, automated secret scanning in pre-commit hooks, and a comprehensive regression test suite (`test_matcher.py`). All code has been independently audited and verified to compile and run.

## License

This repository's source code is licensed under the [MIT License](file:///home/apurva/Desktop/Neb/16%20%28copy%201%29/nebula_v9/LICENSE).

For standalone/compiled distribution, AnebulaX includes an offline product activation mechanism (Option B: Offline signed license file with asymmetric Ed25519 public-key signature verification). The client ships strictly with the verification public key (`EMBEDDED_PUBLIC_KEY_HEX`); vendor signing keys are generated offline and stored in vendor secret environments (`NEBULA_VENDOR_PRIVATE_KEY`).
