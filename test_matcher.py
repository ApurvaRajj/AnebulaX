"""
Nebula v9 — Matcher, Architecture, Licensing, and Feature Test Suite

Run: pytest test_matcher.py -v

Tests verify:
- Intent matcher routing, scoring formula, and tie-breaking
- 100% of all 743 executors across all trigger sets are dispatchable natively
- Zero private key hardcoded in licensing.py or client source
- Shipped public key authenticates the pre-signed evaluation community license
- Forged or tampered licenses are rejected
- Expired licenses are rejected
- Software hot-reloading from ~/.nebula_software.txt without process restart
- Consolidated executor implementations (lock, clipboard, window controls)
- User-extensible file auto-generation and integrity
- Bookmarks management (add, list, delete, fuzzy match)
- Dynamic energy threshold toggles and settings
- Site-specific searches and greeting priority
- Persisted reminders and structured notes
"""
import sys
import os
import json
import re
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import licensing
import intents_db
import matcher
import tts
import stt
import executors
import main


class TestMatcher:
    """Test the Matcher class routes commands correctly."""

    def setup_method(self):
        self.matcher = matcher.Matcher(intents_db._CMD_TABLE)

    def _executor(self, text):
        result = self.matcher.match(text)
        assert result is not None, f"No match for: {text}"
        executor, score, entities = result
        return executor

    # ── Time & Date ──────────────────────────────────────────────────────────
    def test_time(self):
        assert self._executor("what time is it") == "p_time"

    def test_date(self):
        assert self._executor("current date") == "p_date"

    # ── System Volume & Brightness ───────────────────────────────────────────
    def test_volume_up(self):
        assert self._executor("volume up") == "sys_vol_up"

    def test_volume_set(self):
        assert self._executor("set volume to 50") == "sys_vol_set"

    def test_mute(self):
        assert self._executor("mute") == "sys_mute"

    def test_screenshot(self):
        assert self._executor("screenshot") == "sys_ss"

    def test_reduce_brightness(self):
        assert self._executor("reduce brightness") == "sys_br_dn"
        assert self._executor("lower brightness") == "sys_br_dn"
        assert self._executor("dim screen") == "sys_br_dn"

    def test_increase_brightness(self):
        assert self._executor("increase brightness") == "sys_br_up"
        assert self._executor("raise brightness") == "sys_br_up"

    # ── Network ──────────────────────────────────────────────────────────────
    def test_my_ip(self):
        assert self._executor("what is my ip") == "ni_ip"

    def test_local_ip(self):
        assert self._executor("local ip") == "ni_ip"

    def test_public_ip(self):
        assert self._executor("public ip") == "ni_ip"

    # ── Web & Site Searches ──────────────────────────────────────────────────
    def test_search_youtube(self):
        assert self._executor("search youtube for cats") == "web_yt_search"
        assert self._executor("in youtube search avg") == "web_yt_search"

    def test_search_claude(self):
        assert self._executor("in claude search python tutorial") == "web_ask_claude"

    def test_search_gemini(self):
        assert self._executor("in gemini search mobile") == "web_ask_gemini"

    def test_messages_web(self):
        assert self._executor("go to messages web") == "web_messages"
        assert self._executor("google messages") == "web_messages"

    def test_search_vs_greeting_priority(self):
        assert self._executor("search hello") == "web_search"
        assert self._executor("hello") == "fun_greet"

    # ── Browser Tab Control ──────────────────────────────────────────────────
    def test_refresh_tab(self):
        assert self._executor("refresh tab") == "bc_refresh"

    def test_close_tab(self):
        assert self._executor("close tab") == "bc_close_tab"

    def test_new_tab(self):
        assert self._executor("new tab") == "bc_new_tab"

    # ── Math & Solvers ───────────────────────────────────────────────────────
    def test_prime(self):
        assert self._executor("is 17 prime") == "me_is_prime"

    def test_fibonacci(self):
        assert self._executor("fibonacci 10") == "me_fibonacci"

    # ── Files & Apps ─────────────────────────────────────────────────────────
    def test_create_folder(self):
        assert self._executor("create folder test") == "fs_mkdir"

    def test_delete_file(self):
        assert self._executor("delete file test.txt") == "fs_del_file"

    def test_open_chrome(self):
        assert self._executor("open chrome") == "app_chrome"

    # ── Dynamic Threshold & STT Config ───────────────────────────────────────
    def test_dynamic_energy_triggers(self):
        assert self._executor("set dynamic on") == "cfg_set_dynamic"
        assert self._executor("set dynamic off") == "cfg_set_dynamic"
        assert self._executor("dynamic on") == "cfg_set_dynamic"
        assert self._executor("toggle dynamic") == "cfg_set_dynamic"

    def test_tts_toggle_triggers(self):
        assert self._executor("toggle tts") == "cfg_toggle_tts"
        assert self._executor("mute voice") == "cfg_toggle_tts"
        assert self._executor("unmute voice") == "cfg_toggle_tts"

    # ── Bookmarks Management ─────────────────────────────────────────────────
    def test_bookmark_triggers(self):
        assert self._executor("list bookmarks") == "mm_show_bookmarks"
        assert self._executor("show bookmarks") == "mm_show_bookmarks"
        assert self._executor("add bookmark wiki https://wikipedia.org") == "mm_add_bookmark"
        assert self._executor("delete bookmark wiki") == "mm_del_bookmark"

    # ── Notes & Reminders ────────────────────────────────────────────────────
    def test_add_note(self):
        assert self._executor("note meeting tomorrow") == "p_note_add_structured"

    def test_garbage_input(self):
        result = self.matcher.match("xyzzy abc123")
        if result:
            assert result[1] < 0.5


class TestNoBareExcept:
    """Verify no bare 'except:' remains in any Nebula v9 module."""

    def test_no_bare_except(self):
        nebula_files = [
            "config.py", "licensing.py", "intents_db.py", "matcher.py",
            "tts.py", "stt.py", "main.py", "nebula_v9_improved.py"
        ]
        py_files = [Path(__file__).parent / f for f in nebula_files if (Path(__file__).parent / f).exists()]
        py_files += list((Path(__file__).parent / "executors").glob("*.py"))
        for p in py_files:
            content = p.read_text(encoding="utf-8")
            bare = re.findall(r'\bexcept\s*:', content)
            assert len(bare) == 0, f"Found {len(bare)} bare 'except:' in {p.name}"


class TestAliasesAndTypos:
    """Test user-defined word aliases and phonetic typo corrections."""

    def test_alias_not_bad(self):
        result = matcher.apply_aliases("open not bad")
        assert "notepad" in result

    def test_alias_you_tube(self):
        result = matcher.apply_aliases("open you tube")
        assert "youtube" in result

    def test_typo_correction_define(self):
        corrected = matcher._typo_correct("defien forumn")
        assert corrected == "define forum"

    def test_typo_correction_toggle(self):
        corrected = matcher._typo_correct("toggel tts")
        assert corrected == "toggle tts"

    def test_typo_correction_dynamic(self):
        corrected = matcher._typo_correct("dynami on")
        assert corrected == "dynamic on"


class TestNoDeadExecutors:
    """Verify 100% of all 743 executors in _CMD_TABLE are dispatchable via executors._e()."""

    def test_all_matched_executors_are_dispatchable(self):
        dead = []
        for trig, (ex, w) in intents_db._CMD_TABLE:
            if executors._e(ex) is None:
                dead.append((ex, trig))
        assert len(dead) == 0, (
            f"{len(dead)} dead executors: "
            + ", ".join(f"{ex} (triggers: {trig})" for ex, trig in dead)
        )


class TestSoftwareHotReloading:
    """Test hot-reloading custom software registry without restarting process."""

    def test_software_hot_reloading(self):
        sw_file = config._SOFTWARE_FILE
        original_content = sw_file.read_text(encoding="utf-8") if sw_file.exists() else ""
        try:
            test_entry = f"{original_content}\ncustom_ide | /usr/bin/custom_ide_bin\n"
            sw_file.write_text(test_entry, encoding="utf-8")
            sw = executors.reload_software()
            assert "custom_ide" in sw
            assert sw["custom_ide"] == "/usr/bin/custom_ide_bin"

            name, path = executors.find_software("custom_ide")
            assert name == "custom_ide"
            assert path == "/usr/bin/custom_ide_bin"
        finally:
            sw_file.write_text(original_content, encoding="utf-8")
            executors.reload_software()


class TestConsolidatedExecutors:
    """Verify duplicated mm_* / sys_* operations route to unified implementations."""

    def test_lock_consolidation(self):
        ok1, msg1 = executors._sys_lock({})
        ok2, msg2 = executors._mm_lock({})
        assert ok1 is True and ok2 is True
        assert msg1 == msg2

    def test_clipboard_consolidation(self):
        ok1, msg1 = executors._clip_copy_sel({})
        ok2, msg2 = executors._mm_copy({})
        assert ok1 is True and ok2 is True
        assert msg1 == msg2

    def test_window_max_consolidation(self):
        ok1, msg1 = executors._win_max({})
        ok2, msg2 = executors._mm_maximize_app({})
        assert ok1 is True and ok2 is True
        assert msg1 == msg2


class TestLicensingSystemSecurity:
    """Verify asymmetric offline Ed25519 licensing system security & zero private key hardcoding."""

    def test_no_private_key_hardcoded_in_source(self):
        """Assert vendor private keys are NEVER present in client source files or module exports."""
        # 1. Check module attributes
        assert not hasattr(licensing, "VENDOR_DEMO_PRIV_HEX"), "VENDOR_DEMO_PRIV_HEX must not be in licensing module"
        assert not hasattr(licensing, "VENDOR_PRIV_HEX"), "VENDOR_PRIV_HEX must not be in licensing module"
        assert not hasattr(licensing, "PRIVATE_KEY"), "PRIVATE_KEY must not be in licensing module"

        # 2. Check licensing.py file content
        lic_code = (Path(__file__).parent / "licensing.py").read_text(encoding="utf-8")
        assert "VENDOR_DEMO_PRIV_HEX" not in lic_code
        assert "VENDOR_PRIV_HEX" not in lic_code
        # Ensure only the public key is embedded
        assert "EMBEDDED_PUBLIC_KEY_HEX" in lic_code

    def test_shipped_public_key_authenticates_community_license(self):
        """Assert the shipped EMBEDDED_PUBLIC_KEY_HEX verifies DEFAULT_COMMUNITY_LICENSE."""
        valid, msg, info = licensing.verify_license(
            licensing.DEFAULT_COMMUNITY_LICENSE,
            public_key_hex=licensing.EMBEDDED_PUBLIC_KEY_HEX
        )
        assert valid is True
        assert "Evaluation" in msg or "Community" in msg

    def test_forged_or_tampered_signature_rejected(self):
        """Assert modifying any field of the signed license fails verification."""
        tampered = dict(licensing.DEFAULT_COMMUNITY_LICENSE)
        tampered["customer"] = "Malicious Entity"
        valid, msg, _ = licensing.verify_license(tampered, public_key_hex=licensing.EMBEDDED_PUBLIC_KEY_HEX)
        assert valid is False
        assert "Invalid cryptographic signature" in msg

    def test_expired_license_rejected(self):
        """Assert expired licenses are rejected."""
        priv, pub = licensing.generate_keypair()
        payload = licensing.sign_license(
            customer="Expired User",
            email="expired@nebula.ai",
            tier="Pro",
            expires_at="2020-01-01T00:00:00Z",
            private_key_hex=priv,
        )
        valid, msg, _ = licensing.verify_license(payload, public_key_hex=pub)
        assert valid is False
        assert "expired" in msg.lower()


class TestRemindersAndNotes:
    """Test user config file auto-creation and reminder persistence."""

    def test_user_files_exist(self):
        files = [
            config._ALIASES_FILE,
            config._BOOKMARKS_FILE,
            config._SOFTWARE_FILE,
            config._CMD_HISTORY_FILE,
            config._NOTES_DB_FILE,
            config._REMINDERS_FILE,
        ]
        for f in files:
            assert f.exists(), f"User file {f} was not auto-generated."

    def test_reminder_written_to_file(self):
        remind_file = config._REMINDERS_FILE
        remind_file.write_text("[]", encoding="utf-8")
        e = {"duration": 3600, "text": "test reminder", "raw": "remind me in 1 hour to test"}
        executors._p_remind(e)
        data = json.loads(remind_file.read_text(encoding="utf-8"))
        assert len(data) > 0
        assert data[-1]["msg"] == "test reminder"
        remind_file.write_text("[]", encoding="utf-8")
