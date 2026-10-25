"""Real local Git repository tests; no network or credentials needed."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from raidian.cli import main
from raidian.core import GitError, Repository, decode
from raidian.mcp import Server


def git(path: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=path, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode("utf-8").strip()


class GitFixtures(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="레이디안 테스트 ")
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        self.repo = Repository.init(self.path)
        git(self.path, "config", "user.name", "레이디안 개발자")
        git(self.path, "config", "user.email", "raidian@example.com")

    def write(self, name: str, content: str) -> None:
        target = self.path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def test_korean_filename_and_auto_commit_message(self) -> None:
        self.write("한글 이름과 공백.txt", "한글 테스트입니다\n")
        self.assertEqual(self.repo.status()[0]["path"], "한글 이름과 공백.txt")
        result = self.repo.commit("")
        self.assertIn("feat: 새 파일 추가", result)
        self.assertEqual(self.repo.status(), [])
        self.assertEqual(self.repo.history(1)[0]["message"], "feat: 새 파일 추가")

    def test_rename_uses_original_path(self) -> None:
        self.write("파일.txt", "가나다")
        self.repo.commit()
        git(self.path, "mv", "파일.txt", "이름 바꾼 파일.txt")
        entry = self.repo.status()[0]
        self.assertEqual(entry["path"], "이름 바꾼 파일.txt")
        self.assertEqual(entry["from"], "파일.txt")

    def test_no_ff_merge_commit_retains_two_parents(self) -> None:
        self.write("readme.txt", "base")
        self.repo.commit()
        self.repo.nested_branch("feature", "gui")
        self.write("feature.txt", "new")
        self.repo.commit()
        self.repo.switch("main")
        self.repo.merge("chatgpt-extrahigh/feature/gui")
        self.assertEqual(len(git(self.path, "rev-list", "--parents", "-n", "1", "HEAD").split()), 3)
        self.assertEqual((self.path / "feature.txt").read_text(), "new")

    def test_copy_commit_and_revert_preserve_history(self) -> None:
        self.write("base.txt", "base")
        self.repo.commit()
        self.repo.create_branch("experiment")
        self.write("feature.txt", "feature")
        self.repo.commit("feat: 선택 이력")
        target = self.repo.history(1)[0]["sha"]
        self.repo.switch("main")
        self.repo.cherry_pick(target)
        self.assertEqual((self.path / "feature.txt").read_text(), "feature")
        self.repo.revert(self.repo.history(1)[0]["sha"])
        self.assertFalse((self.path / "feature.txt").exists())
        self.assertEqual(len(self.repo.history()), 3)

    def test_dirty_tree_prevents_switch_or_merge(self) -> None:
        self.write("base", "a")
        self.repo.commit()
        self.repo.create_branch("other", switch=False)
        self.write("untracked", "content")
        with self.assertRaisesRegex(GitError, "변경 사항"):
            self.repo.switch("other")
        with self.assertRaisesRegex(GitError, "변경 사항"):
            self.repo.merge("other")

    def test_multi_remote(self) -> None:
        self.repo.remote_add("origin", "https://example.invalid/repo.git")
        self.repo.remote_add("mirror", "https://example.invalid/mirror.git")
        names = {r["name"] for r in self.repo.remotes()}
        self.assertEqual(names, {"origin", "mirror"})
        self.repo.remote_remove("mirror")
        self.assertEqual({r["name"] for r in self.repo.remotes()}, {"origin"})

    def test_empty_commit_rejected(self) -> None:
        with self.assertRaisesRegex(GitError, "변경 사항"):
            self.repo.commit()

    def test_invalid_branch_name(self) -> None:
        with self.assertRaises(GitError):
            self.repo.nested_branch("...", "task")

    def test_decoder(self) -> None:
        self.assertEqual(decode("안녕하세요".encode("utf-8")), "안녕하세요")
        self.assertEqual(decode("파일".encode("cp949")), "파일")

    def test_mcp_read_only_and_confirmation(self) -> None:
        server = Server(self.repo)
        self.assertTrue(all("git_commit" != x["name"] for x in server.handle(
            {"id": 1, "method": "tools/list"})["result"]["tools"]))
        res = server.handle({"id": 2, "method": "tools/call", "params": {
            "name": "git_commit", "arguments": {"confirm": True}}})
        self.assertTrue(res["result"]["isError"])
        writer = Server(self.repo, True)
        res2 = writer.handle({"id": 3, "method": "tools/call", "params": {
            "name": "git_commit", "arguments": {"confirm": False}}})
        self.assertTrue(res2["result"]["isError"])
        self.write("한글.md", "문서")
        good = writer.handle({"id": 4, "method": "tools/call", "params": {
            "name": "git_commit", "arguments": {"confirm": True}}})
        self.assertFalse(good["result"]["isError"])
        self.assertIn("feat: 새 파일 추가", good["result"]["structuredContent"]["data"])

    def test_mcp_json_rpc_init(self) -> None:
        response = Server(self.repo).handle({"jsonrpc": "2.0", "id": 2,
                "method": "initialize", "params": {"protocolVersion": "2025-06-18"}})
        self.assertEqual(response["result"]["protocolVersion"], "2025-06-18")
        self.assertEqual(response["result"]["serverInfo"]["name"], "raidian")
        self.assertIsNone(Server(self.repo).handle({"method": "notifications/initialized"}))


if __name__ == "__main__":
    unittest.main()
