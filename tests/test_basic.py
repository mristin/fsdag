# pylint: disable=missing-docstring
import json
import pathlib
import tempfile
import unittest
from typing import List

import fsdag


class TestBasic(unittest.TestCase):
    def test_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir_path = pathlib.Path(tmp_dir)

            action_log = []  # type: List[str]

            class Something(fsdag.Node[None]):
                def _path(self) -> pathlib.Path:
                    return tmp_dir_path / "done"

                def _save(self, artefact: None) -> None:
                    self._path().write_text("done")
                    action_log.append("saved")

                def _load(self) -> None:
                    action_log.append("loaded")

                def _compute(self) -> None:
                    action_log.append("computed")

            something = Something()
            self.assertEqual([], action_log)

            something.resolve()
            self.assertEqual(["computed", "saved"], action_log)

            # NOTE (mristin):
            # No action is expected if the artefact is cached after the computation.
            action_log = []
            something.resolve()
            self.assertEqual([], action_log)

            another_something = Something()
            another_something.resolve()
            self.assertEqual(["loaded"], action_log)

            # NOTE (mristin):
            # No action is expected if the artefact is cached after the loading.
            action_log = []
            another_something.resolve()
            self.assertEqual([], action_log)

    def test_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir_path = pathlib.Path(tmp_dir)

            action_log = []  # type: List[str]

            class Something(fsdag.Node[List[int]]):
                def _path(self) -> pathlib.Path:
                    return tmp_dir_path / "something.json"

                def _save(self, artefact: List[int]) -> None:
                    self._path().write_text(json.dumps(artefact))
                    action_log.append("saved")

                def _load(self) -> List[int]:
                    action_log.append("loaded")
                    return json.loads(self._path().read_text())  # type: ignore

                def _compute(self) -> List[int]:
                    action_log.append("computed")
                    return [1, 2, 3]

            something = Something()
            self.assertEqual([], action_log)

            result = something.resolve()
            self.assertListEqual([1, 2, 3], result)
            self.assertEqual(["computed", "saved"], action_log)

            # NOTE (mristin):
            # No action is expected if the artefact is cached after the computation.
            action_log = []
            result = something.resolve()
            self.assertListEqual([1, 2, 3], result)
            self.assertEqual([], action_log)

            action_log = []
            another_something = Something()
            result = another_something.resolve()
            self.assertListEqual([1, 2, 3], result)
            self.assertEqual(["loaded"], action_log)

            # NOTE (mristin):
            # No action is expected if the artefact is cached after loading.
            action_log = []
            result = another_something.resolve()
            self.assertListEqual([1, 2, 3], result)
            self.assertEqual([], action_log)


if __name__ == "__main__":
    unittest.main()
