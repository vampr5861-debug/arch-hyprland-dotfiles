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


class DialogTests(unittest.TestCase):
    def test_dialog_uses_repo_theme_without_global_environment_mutation(self):
        class Result:
            returncode = 0
            stdout = "hyprland\n"
        with mock.patch.object(momo.subprocess, "run", return_value=Result()) as call:
            self.assertEqual(momo.run_dialog("--checklist", "test", "0", "0", "0"), "hyprland")
        args, kwargs = call.call_args
        self.assertIn("--no-shadow", args[0])
        self.assertEqual(kwargs["env"]["DIALOGRC"], str(momo.DIALOG_THEME))
        self.assertNotIn("DIALOGRC", os.environ)

    def test_dialog_error_is_not_confused_with_cancel(self):
        with mock.patch.object(momo.subprocess, "run") as call:
            call.return_value.returncode = 2
            call.return_value.stdout = ""
            with self.assertRaisesRegex(momo.InstallerError, "dialog failed"):
                momo.run_dialog("--msgbox", "test", "0", "0")


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
