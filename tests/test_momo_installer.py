"""Offline tests. Run: python3 -m unittest discover -s tests -v."""

import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("momo_installer", ROOT / "tools/momo_installer.py")
momo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(momo)


class MockHTTP(io.BytesIO):
    def __init__(self, data, url, media):
        super().__init__(data)
        self._url = url
        self.headers = {"Content-Type": media}

    def geturl(self):
        return self._url


class CatalogTests(unittest.TestCase):
    def test_catalog_is_valid_and_has_known_start_wallpaper(self):
        items = momo.load_catalog()
        self.assertEqual(len(items), 79)
        self.assertIn("n6y9zl", {item["id"] for item in items})
        self.assertEqual(len({x["sha256"] for x in items}), 79)

    def test_catalog_rejects_injected_filename(self):
        content = {"version": 1, "wallpapers": [{"id": "abc123", "filename": "../evil.jpg",
                    "sha256": "0" * 64, "bytes": 10, "width": 1, "height": 1,
                    "source": "https://wallhaven.cc/w/abc123"}]}
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.json"
            path.write_text(json.dumps(content))
            with self.assertRaises(momo.InstallerError):
                momo.load_catalog(path)

    def test_cdn_host_whitelist(self):
        good = "https://w.wallhaven.cc/full/ab/wallhaven-abc123.jpg"
        self.assertTrue(momo.allowed_image_url(good, "abc123", "wallhaven-abc123.jpg"))
        for bad in ("https://evil.example/full/ab/wallhaven-abc123.jpg",
                    "http://w.wallhaven.cc/full/ab/wallhaven-abc123.jpg",
                    "https://w.wallhaven.cc/full/ab/wallhaven-xxx999.jpg",
                    "https://w.wallhaven.cc/full/ab/wallhaven-abc123.jpg?x=1",
                    "https://w.wallhaven.cc.evil.example/full/ab/wallhaven-abc123.jpg"):
            self.assertFalse(momo.allowed_image_url(bad, "abc123", "wallhaven-abc123.jpg"))


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.project = self.base / "repo"
        self.home = self.base / "home"
        self.home.mkdir()
        (self.project / "home/.config/hypr").mkdir(parents=True)
        (self.project / "home/.config/hypr/hyprland.lua").write_text("new\n")
        (self.project / "home/.config/waybar").mkdir(parents=True)
        (self.project / "home/.config/waybar/config.jsonc").write_text("new bar\n")
        (self.home / ".config/hypr").mkdir(parents=True)
        (self.home / ".config/hypr/hyprland.lua").write_text("old\n")
        self.state = self.base / "custom-state"
        self.env_patch = mock.patch.dict(os.environ, {"XDG_STATE_HOME": str(self.state)})
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)

    def test_replaces_only_selected_component_and_preserves_backup(self):
        backup = momo.install_components(["hyprland"], self.home, self.project)
        self.assertEqual((self.home / ".config/hypr/hyprland.lua").read_text(), "new\n")
        self.assertEqual((backup / ".config/hypr/hyprland.lua").read_text(), "old\n")
        self.assertFalse((self.home / ".config/waybar").exists())
        record = json.loads((backup / "install-record.json").read_text())
        self.assertEqual(record["files"], [{"destination": ".config/hypr", "previous_version": True}])

    def test_rejects_symlinked_parent_and_rolls_back(self):
        (self.project / "home/.local/share/icons/Notwaita-Black").mkdir(parents=True)
        (self.project / "home/.local/share/icons/default").mkdir(parents=True)
        (self.home / ".local").symlink_to(self.base / "outside")
        with self.assertRaises(momo.InstallerError):
            momo.install_components(["hyprland", "cursor"], self.home, self.project)
        self.assertEqual((self.home / ".config/hypr/hyprland.lua").read_text(), "old\n")

    def test_source_symlink_outside_component_is_rejected(self):
        (self.project / "home/.config/hypr/malicious").symlink_to("/etc/hosts")
        with self.assertRaisesRegex(momo.InstallerError, "escaping symlink"):
            momo.install_components(["hyprland"], self.home, self.project)
        self.assertEqual((self.home / ".config/hypr/hyprland.lua").read_text(), "old\n")

    def test_internal_relative_source_symlink_is_preserved(self):
        (self.project / "home/.config/hypr/alias").symlink_to("hyprland.lua")
        momo.install_components(["hyprland"], self.home, self.project)
        self.assertEqual((self.home / ".config/hypr/alias").readlink(), Path("hyprland.lua"))

    def test_state_directory_symlink_is_rejected_without_chmod(self):
        self.state.mkdir(parents=True)
        (self.state / "momo").symlink_to(self.base / "outside")
        with self.assertRaisesRegex(momo.InstallerError, "symlinked"):
            momo.install_components(["hyprland"], self.home, self.project)
        self.assertEqual((self.home / ".config/hypr/hyprland.lua").read_text(), "old\n")

    def test_rollback_after_first_component_when_second_parent_is_symlink(self):
        (self.project / "home/.local/share/icons/Notwaita-Black").mkdir(parents=True)
        (self.project / "home/.local/share/icons/default").mkdir(parents=True)
        (self.home / ".local").symlink_to(self.base / "outside")
        with self.assertRaises(momo.InstallerError):
            momo.install_components(["hyprland", "cursor"], self.home, self.project)
        self.assertEqual((self.home / ".config/hypr/hyprland.lua").read_text(), "old\n")

    def test_unknown_component_rejected(self):
        with self.assertRaises(momo.InstallerError):
            momo.install_components(["sudo-system"], self.home, self.project)


class DownloadTests(unittest.TestCase):
    def make_item(self, b):
        return {"id": "abc123", "filename": "wallhaven-abc123.jpg", "source": "https://wallhaven.cc/w/abc123",
                "sha256": hashlib.sha256(b).hexdigest(), "bytes": len(b), "width": 1, "height": 1}

    def test_download_and_idempotent_skip(self):
        content = b"mock-test-image"
        item = self.make_item(content)
        api_url = "https://wallhaven.cc/api/v1/w/abc123"
        image_url = "https://w.wallhaven.cc/full/ab/wallhaven-abc123.jpg"
        api_body = json.dumps({"data": {"id": "abc123", "purity": "sfw", "path": image_url}}).encode()
        def fake_open(request, timeout=25):
            url = request.full_url
            if url == api_url:
                return MockHTTP(api_body, api_url, "application/json")
            if url == image_url:
                return MockHTTP(content, image_url, "image/jpeg")
            raise AssertionError(f"Unexpected request: {url}")
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(momo, "safe_urlopen", fake_open):
            dst = Path(temp)
            self.assertIn("Downloaded:", momo.download_one(item, dst))
            self.assertEqual((dst / item["filename"]).read_bytes(), content)
            self.assertIn("Already downloaded:", momo.download_one(item, dst))

    def test_hash_mismatch_does_not_install_partial_file(self):
        item = self.make_item(b"expected")
        api_url = "https://wallhaven.cc/api/v1/w/abc123"
        image_url = "https://w.wallhaven.cc/full/ab/wallhaven-abc123.jpg"
        api_body = json.dumps({"data": {"id": "abc123", "purity": "sfw", "path": image_url}}).encode()
        def fake_open(request, timeout=25):
            if request.full_url == api_url:
                return MockHTTP(api_body, api_url, "application/json")
            return MockHTTP(b"wrong!!!", image_url, "image/jpeg")
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(momo, "safe_urlopen", fake_open):
            dst = Path(temp)
            with self.assertRaises(momo.InstallerError):
                momo.download_one(item, dst)
            self.assertEqual(list(dst.iterdir()), [])

    def test_never_overwrite_existing_different_file(self):
        item = self.make_item(b"expected")
        with tempfile.TemporaryDirectory() as temp:
            dst = Path(temp) / item["filename"]
            dst.write_bytes(b"original")
            with self.assertRaises(momo.InstallerError):
                momo.download_one(item, Path(temp))
            self.assertEqual(dst.read_bytes(), b"original")


class GumTests(unittest.TestCase):
    def test_choose_uses_label_delimiter_and_scoped_colors(self):
        class Result:
            returncode = 0
            stdout = "hyprland\nkitty\n"
        with mock.patch.object(momo.subprocess, "run", return_value=Result()) as call:
            selected = momo.gum_choose("Components", [("hyprland", "Hyprland"), ("kitty", "Kitty")], multiple=True)
        self.assertEqual(selected, ["hyprland", "kitty"])
        args, kwargs = call.call_args
        self.assertEqual(args[0][:2], ["gum", "choose"])
        self.assertIn("--no-limit", args[0])
        self.assertIn("--label-delimiter", args[0])
        self.assertIn("Hyprland::hyprland", args[0])
        self.assertIn("GUM_CHOOSE_CURSOR_FOREGROUND", kwargs["env"])
        self.assertNotIn("GUM_CHOOSE_CURSOR_FOREGROUND", os.environ)

    def test_unknown_menu_choice_is_rejected(self):
        with mock.patch.object(momo, "run_gum", return_value=mock.Mock(returncode=0, stdout="evil\n")):
            with self.assertRaisesRegex(momo.InstallerError, "Unexpected selection"):
                momo.gum_choose("Items", [("hyprland", "Hyprland")])

    def test_gum_cancel_not_an_error(self):
        with mock.patch.object(momo, "run_gum", return_value=mock.Mock(returncode=1, stdout="")):
            self.assertIsNone(momo.gum_choose("Items", [("a", "A")]))
            self.assertFalse(momo.gum_confirm("Go?"))

    def test_confirm_defaults_to_no(self):
        with mock.patch.object(momo, "run_gum", return_value=mock.Mock(returncode=0)) as call:
            self.assertTrue(momo.gum_confirm("Go?"))
            self.assertIn("--default=false", call.call_args.args)

    def test_custom_profile_and_wallpaper_choice(self):
        catalog = momo.load_catalog()
        answers = iter([["custom"], ["kitty", "fish"], ["choose"], [catalog[0]["id"]]])
        with mock.patch.object(momo, "show_heading"), mock.patch.object(momo, "gum_choose", side_effect=lambda *a, **k: next(answers)):
            keys, walls = momo.select_options(catalog)
        self.assertEqual(keys, ["kitty", "fish"])
        self.assertEqual(walls, [catalog[0]])

    def test_complete_profile_selects_all_groups(self):
        catalog = momo.load_catalog()
        answers = iter([["complete"], ["skip"]])
        with mock.patch.object(momo, "show_heading"), mock.patch.object(momo, "gum_choose", side_effect=lambda *a, **k: next(answers)):
            keys, walls = momo.select_options(catalog)
        self.assertEqual(keys, list(momo.COMPONENTS))
        self.assertFalse(walls)


class PlanAndRestoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.home = self.base / "home"
        self.repo = self.base / "repo"
        self.home.mkdir()
        (self.repo / "home/.config/hypr").mkdir(parents=True)
        (self.repo / "home/.config/hypr/hyprland.lua").write_text("new\n")
        (self.repo / "home/.config/kitty").mkdir(parents=True)
        (self.repo / "home/.config/kitty/kitty.conf").write_text("new kitty\n")
        (self.home / ".config/hypr").mkdir(parents=True)
        (self.home / ".config/hypr/hyprland.lua").write_text("old\n")
        self.state = self.base / "state"
        self.patch_env = mock.patch.dict(os.environ, {"XDG_STATE_HOME": str(self.state)})
        self.patch_env.start()
        self.addCleanup(self.patch_env.stop)

    def test_plan_add_replace_unchanged(self):
        plan = momo.build_plan(["hyprland", "kitty"], self.home, self.repo)
        self.assertEqual(plan, [(".config/hypr", "REPLACE"), (".config/kitty", "ADD")])
        backup = momo.install_components(["hyprland", "kitty"], self.home, self.repo)
        self.assertTrue(backup.is_dir())
        self.assertEqual(momo.build_plan(["hyprland", "kitty"], self.home, self.repo),
                         [(".config/hypr", "UNCHANGED"), (".config/kitty", "UNCHANGED")])

    def test_repeat_install_noop_preserves_only_backup(self):
        first = momo.install_components(["hyprland"], self.home, self.repo)
        self.assertIsNone(momo.install_components(["hyprland"], self.home, self.repo))
        self.assertEqual(momo.list_sessions(self.home), [first])

    def test_restore_retains_original_backup_and_pre_restore_current(self):
        saved = momo.install_components(["hyprland", "kitty"], self.home, self.repo)
        restore = momo.restore_session(saved, self.home)
        self.assertEqual((self.home / ".config/hypr/hyprland.lua").read_text(), "old\n")
        self.assertFalse((self.home / ".config/kitty").exists())
        self.assertEqual((saved / ".config/hypr/hyprland.lua").read_text(), "old\n")
        self.assertEqual((restore / ".config/hypr/hyprland.lua").read_text(), "new\n")
        self.assertEqual((restore / ".config/kitty/kitty.conf").read_text(), "new kitty\n")

    def test_malicious_record_cannot_escape_home(self):
        bad = self.state / "momo/backups/session-malicious"
        bad.mkdir(parents=True)
        (bad / "install-record.json").write_text(json.dumps({"version": 1, "files": [
            {"destination": "../../.ssh", "previous_version": False}]}))
        with self.assertRaisesRegex(momo.InstallerError, "Invalid backup"):
            momo.read_session(bad, self.home)

    def test_restore_rejects_symlinked_parent_without_mutation(self):
        saved = momo.install_components(["hyprland", "kitty"], self.home, self.repo)
        (self.home / ".config/kitty").rename(self.base / "moved")
        (self.home / ".config").rename(self.base / "config-saved")
        (self.home / ".config").symlink_to(self.base / "config-saved")
        with self.assertRaisesRegex(momo.InstallerError, "symlinked"):
            momo.restore_session(saved, self.home)

    def test_source_link_outside_component_rejected_before_plan(self):
        (self.repo / "home/.config/hypr/escape").symlink_to("/etc/passwd")
        with self.assertRaisesRegex(momo.InstallerError, "escaping symlink"):
            momo.build_plan(["hyprland"], self.home, self.repo)

    def test_missing_app_is_informational_only(self):
        with mock.patch.object(momo.shutil, "which", return_value=None):
            report = momo.component_requirements(["fish", "kitty"])
        self.assertEqual(report, [("fish", False), ("starship", False), ("kitty", False)])


class ApiSecurityTests(unittest.TestCase):
    def test_api_redirect_to_http_is_rejected(self):
        url = "https://wallhaven.cc/api/v1/w/abc123"
        data = json.dumps({"data": {"id": "abc123"}}).encode()
        with mock.patch.object(momo, "safe_urlopen",
                               return_value=MockHTTP(data, "http://wallhaven.cc/api/v1/w/abc123", "application/json")):
            with self.assertRaisesRegex(momo.InstallerError, "redirected"):
                momo._request_json(url)

    def test_api_redirect_to_other_path_is_rejected(self):
        url = "https://wallhaven.cc/api/v1/w/abc123"
        with mock.patch.object(momo, "safe_urlopen",
                               return_value=MockHTTP(b"{}", "https://wallhaven.cc/not-the-api", "application/json")):
            with self.assertRaisesRegex(momo.InstallerError, "redirected"):
                momo._request_json(url)

    def test_api_malformed_json_produces_expected_error(self):
        url = "https://wallhaven.cc/api/v1/w/abc123"
        with mock.patch.object(momo, "safe_urlopen",
                               return_value=MockHTTP(b"not JSON", url, "application/json")):
            with self.assertRaisesRegex(momo.InstallerError, "invalid JSON"):
                momo._request_json(url)

    def test_redirect_handler_never_follows_redirects(self):
        with self.assertRaisesRegex(momo.InstallerError, "Refusing HTTP redirect"):
            momo._NoRedirect().redirect_request(
                momo.urllib.request.Request("https://wallhaven.cc/api/v1/w/abc123"),
                None, 302, "Found", {}, "http://wallhaven.cc/api/v1/w/abc123")

    def test_api_json_list_produces_expected_error(self):
        url = "https://wallhaven.cc/api/v1/w/abc123"
        with mock.patch.object(momo, "safe_urlopen",
                               return_value=MockHTTP(b"[]", url, "application/json")):
            with self.assertRaisesRegex(momo.InstallerError, "invalid JSON object"):
                momo._request_json(url)


if __name__ == "__main__":
    unittest.main()

class ExtraRegressionTests(unittest.TestCase):
    def test_temporary_http_503_retried(self):
        item = {"id": "abc123", "filename": "wallhaven-abc123.jpg"}
        with tempfile.TemporaryDirectory() as temp:
            with mock.patch.object(momo, "download_one", side_effect=[
                momo.urllib.error.HTTPError("https://wallhaven.cc", 503, "Unavailable", {}, None),
                "Downloaded: wallhaven-abc123.jpg"] ) as f:
                with mock.patch.object(momo.time, "sleep") as sleeper:
                    self.assertEqual(momo.download_wallpapers([item], Path(temp), interval=0), (1, 0))
                    self.assertEqual(f.call_count, 2)
                    sleeper.assert_called_once()

    def test_http_404_not_retried(self):
        item = {"id": "abc123", "filename": "wallhaven-abc123.jpg"}
        with tempfile.TemporaryDirectory() as temp:
            with mock.patch.object(momo, "download_one", side_effect=momo.urllib.error.HTTPError(
                    "https://wallhaven.cc", 404, "Not Found", {}, None)) as f:
                self.assertEqual(momo.download_wallpapers([item], Path(temp), interval=0), (0, 1))
                f.assert_called_once()

    def test_dry_run_never_mutates_or_downloads(self):
        with mock.patch.object(momo, "check_tree", return_value=[]), \
             mock.patch.object(momo.os, "geteuid", return_value=1000), \
             mock.patch.object(momo.shutil, "which", return_value="/usr/bin/gum"), \
             mock.patch.object(momo, "select_options", return_value=(["hyprland"], [])), \
             mock.patch.object(momo, "print_plan") as print_plan, \
             mock.patch.object(momo, "install_components") as install, \
             mock.patch.object(momo, "download_wallpapers") as download, \
             mock.patch.object(momo.sys, "argv", ["install.sh", "--dry-run"]):
            self.assertEqual(momo.main(), 0)
            print_plan.assert_called_once()
            install.assert_not_called()
            download.assert_not_called()

    def test_cancel_on_confirm_never_mutates(self):
        with mock.patch.object(momo, "check_tree", return_value=[]), \
             mock.patch.object(momo.os, "geteuid", return_value=1000), \
             mock.patch.object(momo.shutil, "which", return_value="/usr/bin/gum"), \
             mock.patch.object(momo, "select_options", return_value=(["hyprland"], [])), \
             mock.patch.object(momo, "print_plan"), \
             mock.patch.object(momo, "gum_confirm", return_value=False), \
             mock.patch.object(momo, "install_components") as install, \
             mock.patch.object(momo, "download_wallpapers") as download, \
             mock.patch.object(momo.sys, "argv", ["install.sh"]):
            self.assertEqual(momo.main(), 0)
            install.assert_not_called()
            download.assert_not_called()

class TransactionFailureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.home = base / "home"
        self.repo = base / "repo"
        self.home.mkdir()
        for key, filename in (("hypr", "hyprland.lua"), ("kitty", "kitty.conf")):
            origin = self.repo / "home/.config" / key
            target = self.home / ".config" / key
            origin.mkdir(parents=True)
            target.mkdir(parents=True)
            (origin / filename).write_text(f"new {key}")
            (target / filename).write_text(f"old {key}")
        patcher = mock.patch.dict(os.environ, {"XDG_STATE_HOME": str(base / "state")})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_install_failure_mid_transaction_restores_both_old_versions(self):
        original = Path.rename
        def failing_rename(obj, dst):
            if "momo-stage-" in str(obj) and str(obj).endswith("/.config/kitty"):
                raise OSError("simulated write failure")
            return original(obj, dst)
        with mock.patch.object(Path, "rename", failing_rename):
            with self.assertRaisesRegex(OSError, "simulated"):
                momo.install_components(["hyprland", "kitty"], self.home, self.repo)
        self.assertEqual((self.home / ".config/hypr/hyprland.lua").read_text(), "old hypr")
        self.assertEqual((self.home / ".config/kitty/kitty.conf").read_text(), "old kitty")

    def test_restore_failure_mid_transaction_recovers_current_versions(self):
        saved = momo.install_components(["hyprland", "kitty"], self.home, self.repo)
        original = Path.rename
        def failing_rename(obj, dst):
            if "momo-restore-stage-" in str(obj) and str(obj).endswith("/.config/kitty"):
                raise OSError("simulated restore failure")
            return original(obj, dst)
        with mock.patch.object(Path, "rename", failing_rename):
            with self.assertRaisesRegex(OSError, "simulated restore failure"):
                momo.restore_session(saved, self.home)
        self.assertEqual((self.home / ".config/hypr/hyprland.lua").read_text(), "new hypr")
        self.assertEqual((self.home / ".config/kitty/kitty.conf").read_text(), "new kitty")
        self.assertEqual((saved / ".config/hypr/hyprland.lua").read_text(), "old hypr")
