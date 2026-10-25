"""Release safety checks using synthetic PE data, *not* real Windows binaries."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zipfile

from scripts.validate_release import ValidationError, validate

SHA = "9" * 40


def fake_pe() -> bytes:
    buf = bytearray(128)
    buf[:2] = b"MZ"
    struct.pack_into("<I", buf, 0x3C, 64)
    buf[64:70] = b"PE\0\0\x64\x86"
    return bytes(buf)


class ReleaseValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory(prefix="raidian-release-")
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name)
        payload = fake_pe()
        contents = {"Raidian.exe": payload, "Raidian-CLI.exe": payload,
                    "LICENSE": b"MIT", "README-PORTABLE.txt": b"Raidian portable",
                    "BUILD-INFO.json": ("\ufeff" + json.dumps({
                        "sourceCommit": SHA, "builder": "Nuitka-MingGW",
                        "version": "v0.1.0", "platform": "windows-amd64"}, ensure_ascii=False)).encode("utf-8")}
        for name in ("Raidian.exe", "Raidian-CLI.exe"):
            (self.directory / name).write_bytes(contents[name])
        archive = self.directory / "Raidian-v0.1.0-windows-x64-portable.zip"
        with zipfile.ZipFile(archive, "w") as target:
            for name, value in contents.items():
                target.writestr(name, value)
        names = ["Raidian.exe", "Raidian-CLI.exe", archive.name]
        sums = [f"{hashlib.sha256((self.directory / name).read_bytes()).hexdigest()}  {name}" for name in names]
        (self.directory / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="ascii")

    def test_provenance_and_hashes_verified(self) -> None:
        result = validate(self.directory, "v0.1.0", SHA)
        self.assertEqual(result["builder"], "Nuitka-MingGW")
        self.assertEqual(result["sourceCommit"], SHA)

    def test_mismatched_git_commit_rejected(self) -> None:
        with self.assertRaisesRegex(ValidationError, "Git SHA"):
            validate(self.directory, source_commit="0" * 40)

    def test_modified_archive_rejected(self) -> None:
        with (self.directory / "Raidian-v0.1.0-windows-x64-portable.zip").open("ab") as stream:
            stream.write(b"malicious extra bytes")
        with self.assertRaisesRegex(ValidationError, "체크섬"):
            validate(self.directory, source_commit=SHA)

    def test_missing_zip_member_rejected(self) -> None:
        archive = self.directory / "Raidian-v0.1.0-windows-x64-portable.zip"
        with zipfile.ZipFile(archive, "w") as target:
            target.writestr("Raidian.exe", fake_pe())
        lines = (self.directory / "SHA256SUMS.txt").read_text().splitlines()
        lines[-1] = f"{hashlib.sha256(archive.read_bytes()).hexdigest()}  {archive.name}"
        (self.directory / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n")
        with self.assertRaisesRegex(ValidationError, "ZIP 구성"):
            validate(self.directory, source_commit=SHA)

    def test_tag_validation_rejected(self) -> None:
        with self.assertRaisesRegex(ValidationError, "SemVer"):
            validate(self.directory, tag="-v0.1.0")


if __name__ == "__main__":
    unittest.main()
