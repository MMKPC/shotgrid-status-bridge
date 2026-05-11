"""
tests/test_sg_offline.py
Offline tests — mocks shotgun_api3. No ShotGrid server needed.
Run with: pytest tests/
"""

import sys
import types
import unittest


# ── shotgun_api3 mock ─────────────────────────────────────────────────────────

class _FakeSG:
    def __init__(self, *a, **kw): pass

    def find_one(self, entity_type, filters, fields):
        if entity_type == "Asset":
            return {"id": 1, "code": "SM_Rock", "sg_status_list": "ip", "tasks": []}
        if entity_type == "Task":
            return {"id": 10, "content": "Model", "sg_status_list": "ip"}
        return None

    def find(self, entity_type, filters, fields):
        return [{"id": 1, "code": "SM_Rock", "sg_status_list": "ip"}]

    def update(self, entity_type, entity_id, data):
        return {"id": entity_id, **data}

    def create(self, entity_type, data):
        return {"id": 99, **data}

    def upload(self, *a, **kw):
        pass


def _install_sg_mock():
    sg_mod            = types.ModuleType("shotgun_api3")
    sg_mod.Shotgun    = _FakeSG
    sys.modules["shotgun_api3"] = sg_mod
    for k in list(sys.modules.keys()):
        if "sg_bridge" in k:
            del sys.modules[k]


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestShotGridClient(unittest.TestCase):

    def setUp(self):
        _install_sg_mock()
        from sg_bridge.client import ShotGridClient
        self.sg = ShotGridClient("https://fake.shotgrid.autodesk.com",
                                 "pipeline_script", "abc123")

    def test_find_asset_returns_dict(self):
        result = self.sg.find_asset(1, "SM_Rock")
        self.assertIsNotNone(result)
        self.assertEqual(result["code"], "SM_Rock")

    def test_list_assets_returns_list(self):
        result = self.sg.list_assets(1)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_update_task_status(self):
        result = self.sg.update_task_status(10, "fin")
        self.assertEqual(result["sg_status_list"], "fin")

    def test_find_task_returns_dict(self):
        result = self.sg.find_task(1, "SM_Rock", "Model")
        self.assertIsNotNone(result)
        self.assertEqual(result["content"], "Model")

    def test_create_version(self):
        result = self.sg.create_version(1, 1, "SM_Rock_v001", "Auto version")
        self.assertEqual(result["id"], 99)
        self.assertEqual(result["code"], "SM_Rock_v001")

    def test_add_note(self):
        result = self.sg.add_note(1, "Asset", 1, "Review", "Looks good")
        self.assertEqual(result["id"], 99)


if __name__ == "__main__":
    unittest.main()
