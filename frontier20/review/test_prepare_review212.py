"""The current review metadata generator cannot turn DRAFT into acceptance."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import importlib.util
import json
import unittest

HERE = Path(__file__).resolve().parent


def subject():
    path = HERE / 'prepare_review212.py'
    spec = importlib.util.spec_from_file_location('prepare_review212_test_subject', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PrepareReview212Tests(unittest.TestCase):
    def test_retained_regressions_have_dedicated_maintained_native_markers(self):
        module = subject()
        records = module.regression_contracts()
        self.assertEqual(len(records), 12)
        module.verify_source_anchors(records)
        self.assertNotIn('FrontierRed212ProbeTests', records)
        self.assertEqual(records['FrontierRedConnectivity204Tests']['artifacts'], ['frontier-red-regression204.json'])
        self.assertEqual(records['VisualOptionsDrawTests']['marker_counts'][
            'PASS Trench actual land pixels/pit alpha/nested sparks/cache frame/target loss/two quality settings'], 2)

    def test_prepare_refuses_to_replace_finalized_contracts(self):
        module = subject()
        with TemporaryDirectory() as temporary:
            module.REVIEW = Path(temporary)
            path = module.REVIEW / 'release212-case-contracts.json'
            initial = json.dumps({'version': '2.1.2', 'internal': 107, 'status': 'READY', 'cases': {}}).encode()
            path.write_bytes(initial)
            with self.assertRaises(AssertionError):
                module.prepare()
            self.assertEqual(path.read_bytes(), initial)
            self.assertEqual(list(module.REVIEW.iterdir()), [path])

    def test_finalize_cannot_accept_draft_selection_or_emit_config(self):
        module = subject()
        with TemporaryDirectory() as temporary:
            module.ROOT = Path(temporary)
            module.REVIEW = module.ROOT / 'review'
            module.REVIEW.mkdir()
            module.load_review = lambda: SimpleNamespace(require_selection=lambda: None)
            path = module.REVIEW / 'release212-cases.json'
            path.write_text(json.dumps({'version': '2.1.2', 'internal': 107, 'status': 'DRAFT'}), 'utf8')
            with self.assertRaises(AssertionError):
                module.finalize('20261113T000000Z', 'post212-python-regression.json')
            self.assertFalse((module.REVIEW / 'release212-config.json').exists())

    def test_new_metadata_never_overwrites_different_existing_bytes(self):
        module = subject()
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / 'fixture.json'
            value = {'version': '2.1.2', 'status': 'DRAFT'}
            module.write_new_or_identical(path, value)
            before = path.read_bytes()
            module.write_new_or_identical(path, value)
            self.assertEqual(path.read_bytes(), before)
            with self.assertRaises(AssertionError):
                module.write_new_or_identical(path, {'version': '2.1.1', 'status': 'READY'})
            self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
