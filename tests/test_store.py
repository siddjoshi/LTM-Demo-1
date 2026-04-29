import json
import tempfile
import unittest
from pathlib import Path

from ltm_demo.store import LTMStore, StoreError


class TestLTMStore(unittest.TestCase):
    def test_add_save_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "store.json"
            s1 = LTMStore(path)
            m1 = s1.add("Hello world", tags=["Work", "urgent", "work"], pinned=True, meta={"a": 1})
            s1.save()

            s2 = LTMStore(path)
            s2.load()
            m2 = s2.get(m1.id)

            self.assertEqual(m2.text, "Hello world")
            self.assertEqual(m2.tags, ("urgent", "work"))
            self.assertTrue(m2.pinned)
            self.assertEqual(m2.meta, {"a": 1})

    def test_update_delete(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "store.json"
            s = LTMStore(path)
            m = s.add("a")
            s.update(m.id, text="b", tags=["x"], pinned=True)
            self.assertEqual(s.get(m.id).text, "b")
            self.assertEqual(s.get(m.id).tags, ("x",))
            self.assertTrue(s.get(m.id).pinned)
            s.delete(m.id)
            with self.assertRaises(StoreError):
                s.get(m.id)

    def test_search(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "store.json"
            s = LTMStore(path)
            m1 = s.add("buy milk", tags=["home"])
            m2 = s.add("buy bread", tags=["home", "pinned"], pinned=True)
            m3 = s.add("deploy service", tags=["work"])

            hits = s.search("buy")
            self.assertEqual([m.id for m in hits], [m2.id, m1.id])
            hits_tag = s.search("", tag="work")
            self.assertEqual([m.id for m in hits_tag], [m3.id])

    def test_save_format_is_json(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "store.json"
            s = LTMStore(path)
            s.add("x")
            s.save()
            raw = json.loads(path.read_text("utf-8"))
            self.assertIn("memories", raw)
            self.assertEqual(raw["version"], 1)


if __name__ == "__main__":
    unittest.main()

