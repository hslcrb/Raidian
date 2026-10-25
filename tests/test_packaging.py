"""Cross-platform packaging, documentation and current MCP protocol checks."""
from __future__ import annotations

import contextlib
import io
from pathlib import Path
import struct
import tempfile
import unittest
import xml.etree.ElementTree as ET

from raidian.mcp import MODERN_PROTOCOL, Server
from raidian.core import Repository
from scripts.console import main as portable_main
from scripts.verify_pe import machine

ROOT = Path(__file__).resolve().parents[1]


class PackageContract(unittest.TestCase):
    def test_portable_console_version(self) -> None:
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            with self.assertRaises(SystemExit) as exited:
                portable_main(["--version"])
        self.assertEqual(exited.exception.code, 0)
        self.assertIn("0.1.0", stream.getvalue())

    def test_portable_console_agent_guide(self) -> None:
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            self.assertEqual(portable_main(["--json", "agent-guide"]), 0)
        self.assertIn('"ok": true', stream.getvalue())

    def test_modern_mcp_discovery_and_tools(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            server = Server(Repository.init(directory))
            meta = {"io.modelcontextprotocol/protocolVersion": MODERN_PROTOCOL,
                    "io.modelcontextprotocol/clientCapabilities": {}}
            discover = server.handle({"jsonrpc": "2.0", "id": "d1", "method": "server/discover",
                                      "params": {"_meta": meta}})
            self.assertIn(MODERN_PROTOCOL, discover["result"]["supportedVersions"])
            self.assertEqual(discover["result"]["resultType"], "complete")
            listing = server.handle({"jsonrpc": "2.0", "id": "d2", "method": "tools/list",
                                     "params": {"_meta": meta}})
            self.assertEqual(listing["result"]["resultType"], "complete")
            self.assertTrue(any(t["name"] == "git_status" for t in listing["result"]["tools"]))
            error = server.handle({"jsonrpc": "2.0", "id": "d3", "method": "tools/list",
                                   "params": {"_meta": {"io.modelcontextprotocol/protocolVersion": "2070-01-01"}}})
            self.assertEqual(error["error"]["code"], -32022)
            legacy = server.handle({"id": "d4", "method": "initialize",
                                    "params": {"protocolVersion": "2025-11-25"}})
            self.assertEqual(legacy["result"]["protocolVersion"], "2025-11-25")

    def test_mcp_modern_tools_call_readonly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            server = Server(Repository.init(directory))
            meta = {"io.modelcontextprotocol/protocolVersion": MODERN_PROTOCOL}
            response = server.handle({"id": 1, "method": "tools/call",
                 "params": {"_meta": meta, "name": "git_status", "arguments": {}}})
            self.assertEqual(response["result"]["resultType"], "complete")
            self.assertFalse(response["result"]["isError"])
            response2 = server.handle({"id": 2, "method": "tools/call",
                 "params": {"_meta": meta, "name": "git_commit", "arguments": {"confirm": True}}})
            self.assertTrue(response2["result"]["isError"])

    def test_brand_svg_well_formed(self) -> None:
        for filename in ["raidian-hero.svg", "raidian-mark.svg"]:
            root = ET.parse(ROOT / "assets" / "brand" / filename).getroot()
            self.assertTrue(root.attrib.get("viewBox"))
            self.assertTrue(any(el.tag.endswith("title") for el in root.iter()))
            self.assertTrue(any(el.tag.endswith("desc") for el in root.iter()))

    def test_workflow_is_commented_out(self) -> None:
        workflow = (ROOT / ".github/workflows/windows-build.yml").read_text()
        self.assertTrue(all(not row.strip() or row.lstrip().startswith("#") for row in workflow.splitlines()))

    def test_pe_parser_validates_architecture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fake.exe"
            data = bytearray(128)
            data[:2] = b"MZ"
            struct.pack_into("<I", data, 0x3C, 64)
            data[64:70] = b"PE\0\0\x64\x86"
            path.write_bytes(data)
            self.assertEqual(machine(path), 0x8664)
            data[64:70] = b"PE\0\0\x4c\x01"
            path.write_bytes(data)
            self.assertNotEqual(machine(path), 0x8664)
            path.write_bytes(b"not an exe")
            with self.assertRaises(ValueError):
                machine(path)

    def test_documentation_links_exist(self) -> None:
        for file in ("docs/USER_GUIDE.md", "docs/AGENTS.md", "docs/ARCHITECTURE.md",
                     "docs/BRAND.md", "docs/BUILD_WINDOWS.md", "docs/RELEASING.md",
                     "docs/RELEASE_NOTES_v0.1.0.md", "docs/VALIDATION.md", "CHANGELOG.md",
                     "scripts/build_windows.ps1", "scripts/publish_release.ps1"):
            self.assertTrue((ROOT / file).is_file(), file)


if __name__ == "__main__":
    unittest.main()
