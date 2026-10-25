"""Guard against changing repository context during background Git operations."""
from __future__ import annotations

import os
import tempfile
import tkinter as tk
import unittest

from raidian.core import GitError, Repository
from raidian.gui import Workbench


@unittest.skipUnless(os.name == 'nt' or os.environ.get('DISPLAY'), 'Tk display not available')
class WorkbenchSafetyTests(unittest.TestCase):
    def test_block_repository_changes_during_operations(self) -> None:
        with tempfile.TemporaryDirectory() as dirname:
            Repository.init(dirname)
            try:
                root = tk.Tk()
            except tk.TclError as error:
                self.skipTest(f"Tk display unavailable: {error}")
            root.withdraw()
            try:
                app = Workbench(root, dirname)
                app.busy = True
                with self.assertRaisesRegex(GitError, '진행 중'):
                    app.set_repo(dirname)
                app.busy = False
                app.set_repo(dirname)
                self.assertEqual(app.repo.path.resolve(), Repository(dirname).path)
                self.assertIn('--json agent-guide', app.status_text.get())
            finally:
                root.destroy()


if __name__ == '__main__':
    unittest.main()
