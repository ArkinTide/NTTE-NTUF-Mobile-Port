"""Keep the real pre-game observer distinct from ordinary smoke dispatch."""
from pathlib import Path
import hashlib
import importlib.util
import json
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("post202_case_review", ROOT / "review/verify_post202_repairs.py")
REVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REVIEW)
CASE = "FrontierMenuAudioBootTests"
START = "NTUF MENU AUDIO true cold-boot observer started without synthetic GameCont"
END = "PASS FRONTIER actual cold-boot Logo, mode menu, character selection and Back audio lifecycle"
NAME = "ntuf-menu-audio-cold-boot.json"


class NativeCaseIdentity(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name)
        self.rows = [dict(phase=phase, rate=60, live_portal_voices=1, new_portal_plays=0,
                          old_source_stopped=True, pitch=1, voice_gain=1, sample_gain=.5,
                          wall_seconds=3, track_advance=3)
                     for phase in ("actual-cold-boot-mode-menu", "actual-cold-boot-after-character-back")]
        self.evidence = dict(kind="actual application cold-boot menu voice lifecycle", rows=self.rows,
                             physical_device_tested=False, audio_output_captured=False,
                             voices=[{"name":"sndLogoLoop"}], snapshots=[{"name":"sndPortalLoop"}])
        self.save()
        self.smoke = "\n".join([START, *("NTUF MENU AUDIO native idle " + json.dumps(row) for row in self.rows), END])

    def save(self):
        raw = json.dumps(self.evidence).encode("utf8")
        (self.path / NAME).write_bytes(raw)
        self.artifacts = {NAME:hashlib.sha256(raw).hexdigest()}

    def verify(self, smoke=None, artifacts=None, case=CASE):
        REVIEW.verify_case_identity(case, self.smoke if smoke is None else smoke,
            self.artifacts if artifacts is None else artifacts, self.path)

    def test_actual_cold_entry_is_accepted(self):
        self.verify()

    def test_ordinary_case_still_requires_exact_dispatch(self):
        self.verify(smoke="CASE OrdinaryTests", artifacts={}, case="OrdinaryTests")
        with self.assertRaises(AssertionError): self.verify(case="OrdinaryTests")
        with self.assertRaises(AssertionError): self.verify(smoke="CASE DifferentTests", case="OrdinaryTests")

    def test_cold_case_cannot_use_synthetic_entry(self):
        with self.assertRaises(AssertionError): self.verify(smoke="CASE " + CASE + "\n" + self.smoke)
        with self.assertRaises(AssertionError): self.verify(smoke="FULL INTERNAL BEGIN @30\n" + self.smoke)

    def test_cold_case_requires_unique_start_and_completion(self):
        for text in (self.smoke.replace(START,""), self.smoke.replace(END,""), self.smoke+"\n"+START):
            with self.assertRaises(AssertionError): self.verify(smoke=text)

    def test_cold_case_requires_bound_actual_artifact(self):
        with self.assertRaises(AssertionError): self.verify(artifacts={})
        (self.path / NAME).write_text("{}", encoding="utf8")
        with self.assertRaises(AssertionError): self.verify()

    def test_cold_artifact_must_match_actual_rows(self):
        self.evidence["rows"] = []
        self.save()
        with self.assertRaises(AssertionError): self.verify()

    def test_other_lifecycle_or_phone_claim_is_rejected(self):
        self.evidence["kind"] = "synthetic gameplay menu"
        self.save()
        with self.assertRaises(AssertionError): self.verify()
        self.evidence["kind"] = "actual application cold-boot menu voice lifecycle"
        self.evidence["audio_output_captured"] = True
        self.save()
        with self.assertRaises(AssertionError): self.verify()


if __name__ == "__main__": unittest.main()
