"""Exercise new delivery boundaries without compiling, signing or publishing."""
from pathlib import Path
from tempfile import TemporaryDirectory
import importlib.util
import json
import unittest


def delivery():
    path = Path(__file__).with_name("release215_delivery.py")
    spec = importlib.util.spec_from_file_location("ntuf215_delivery_test_subject", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Delivery215Tests(unittest.TestCase):
    def test_plan_is_inert_and_selects_new_identity(self):
        module = delivery()
        plan = module.plan()
        self.assertEqual(plan["version"], "2.1.5")
        self.assertEqual(plan["internal"], 110)
        self.assertEqual(plan["android_version_code"], 3000110)
        self.assertEqual(module.HOST, module.WORKSPACE / "work/ntte-complete")
        self.assertEqual(module.FRONTIER.name, "ntuf-repair-20261122")
        self.assertEqual(module.package_path("Android").name, "NuclearThrone.NTTE-NTUF-Android-2.1.5.apk")
        self.assertEqual(module.package_path("iOS").name, "NuclearThrone.NTTE-NTUF-iOS-2.1.5.ipa")
        self.assertFalse(plan["executes_builds_in_plan"])
        self.assertFalse(plan["publishes"])
        self.assertFalse(plan["historical_acceptance_reused"])
        self.assertFalse(set(module.REUSED_FUNCTIONS) & {"gate", "accept", "configured_evidence", "main", "required_cases", "verify_case"})

    def test_absent_draft_and_old_identity_cannot_unlock_gate(self):
        module = delivery()
        with TemporaryDirectory() as directory:
            module.CONFIG = Path(directory) / "config.json"
            with self.assertRaises(FileNotFoundError):
                module.configured_evidence()
            for config in (
                {"status": "DRAFT", "version": "2.1.5", "internal": 110},
                {"status": "READY", "version": "2.1.4", "internal": 109},
            ):
                module.CONFIG.write_text(json.dumps(config), encoding="utf8")
                with self.assertRaises(AssertionError):
                    module.configured_evidence()

    def test_input_references_cannot_escape_source_workspace(self):
        module = delivery()
        for name in ("../other/receipt.json", "C:/other/receipt.json", "/other/receipt.json"):
            with self.assertRaises(AssertionError):
                module.relative_input(name)
        with self.assertRaises(AssertionError):
            module.relative_input("review/example.json", "tests")
        self.assertEqual(module.relative_input("tests/20261122T000000Z/ExampleTests/receipt.json", "tests"),
                         module.FRONTIER / "tests/20261122T000000Z/ExampleTests/receipt.json")

    def test_native_case_rejects_stale_or_unmuted_or_failed_receipt(self):
        module = delivery()
        compiled = {"vm_sha256": "a" * 64, "input_sha256": "b" * 64}
        base = {"case": "SkeletonRevivalTests", "status": "PASS", "exit": 0,
                "termination_reason": None, **compiled, "muted_resources": 1000,
                "physical_device_tested": False, "desktop": "private, never activated"}
        with TemporaryDirectory() as directory:
            path = Path(directory) / "SkeletonRevivalTests/receipt.json"
            path.parent.mkdir()
            for change in ({"vm_sha256": "c" * 64}, {"input_sha256": "c" * 64},
                           {"status": "FAIL"}, {"exit": 1}, {"muted_resources": 0},
                           {"physical_device_tested": True}, {"desktop": "user desktop"}):
                path.write_text(json.dumps({**base, **change}), encoding="utf8")
                with self.assertRaises(AssertionError):
                    module.verify_case(path, "SkeletonRevivalTests", compiled)

    def test_retained_signing_layout_and_full_readback_gates_present(self):
        module = delivery()
        self.assertEqual(module.CERTIFICATE, "bbf4736b3ccdbc822ffd46d148780a05fec6a20a19d00f67afc3808f596bbe81")
        for name in ("compiler_source_binding", "ios_build_evidence", "native_layout", "verify_android",
                     "android_audit_evidence", "alias_evidence", "verify_delivery", "validate_delivery"):
            self.assertTrue(callable(getattr(module, name)))
        original = {"machine.Platform Settings.Android.Paths." + name: "old/" + name
                    for name in ("jdk_location", "sdk_location", "ndk_location")}
        original["machine.Platform Settings.Android.Keystore.keystore_password"] = "fixture-only-secret"
        copied = module.android_user_settings(original)
        self.assertEqual(copied["machine.Platform Settings.Android.Paths.jdk_location"], module.ANDROID_JDK.as_posix())
        self.assertEqual(copied["machine.Platform Settings.Android.Paths.sdk_location"], module.ANDROID_SDK.as_posix())
        self.assertEqual(copied["machine.Platform Settings.Android.Paths.ndk_location"], module.ANDROID_NDK.as_posix())
        self.assertEqual(copied["machine.Platform Settings.Android.Keystore.keystore_password"], "fixture-only-secret")
        self.assertEqual(original["machine.Platform Settings.Android.Paths.jdk_location"], "old/jdk_location")


if __name__ == "__main__":
    unittest.main()
