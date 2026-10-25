"""Validate Raidian Windows release artifacts before anyone publishes them.

This checks provenance, archive contents, x64 PE headers and SHA-256 hashes.
Passing does not replace an actual Windows GUI smoke test.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

from scripts.verify_pe import machine


class ValidationError(ValueError):
    """A human-readable release validation failure."""


def checksum(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(part)
    return hasher.hexdigest()


def validate(directory: Path, tag: str = "v0.1.0", source_commit: str | None = None) -> dict[str, str]:
    """Ensure every distributable file genuinely corresponds to its manifest."""
    if not re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+", tag):
        raise ValidationError("정식 SemVer 태그(v0.1.0 형식)만 사용할 수 있습니다.")
    names = {"Raidian.exe", "Raidian-CLI.exe", f"Raidian-{tag}-windows-x64-portable.zip"}
    manifest = directory / "SHA256SUMS.txt"
    if not manifest.is_file():
        raise ValidationError("SHA256SUMS.txt 파일이 없습니다.")
    actual_hashes: dict[str, str] = {}
    for line in manifest.read_text(encoding="ascii").splitlines():
        match = re.fullmatch(r"([a-fA-F0-9]{64})  ([A-Za-z0-9._-]+)", line.strip())
        if not match or match[2] in actual_hashes:
            raise ValidationError("SHA256SUMS.txt 형식 또는 중복 항목 오류")
        actual_hashes[match[2]] = match[1].lower()
    if set(actual_hashes) != names:
        raise ValidationError(f"체크섬 항목이 정확히 일치하지 않습니다: {names ^ set(actual_hashes)}")
    for name, expected in actual_hashes.items():
        path = directory / name
        if not path.is_file() or checksum(path) != expected:
            raise ValidationError(f"체크섬 불일치 또는 파일 없음: {name}")
    for name in ("Raidian.exe", "Raidian-CLI.exe"):
        if machine(directory / name) != 0x8664:
            raise ValidationError(f"Windows x64 PE 형식 오류: {name}")

    archive_path = directory / f"Raidian-{tag}-windows-x64-portable.zip"
    with zipfile.ZipFile(archive_path, "r") as archive:
        members = archive.namelist()
        mandatory = {"Raidian.exe", "Raidian-CLI.exe", "README-PORTABLE.txt", "LICENSE", "BUILD-INFO.json"}
        if len(members) != len(set(members)) or set(members) != mandatory:
            raise ValidationError("포터블 ZIP 구성 오류(중복/누락/불필요한 파일)")
        if archive.testzip() is not None:
            raise ValidationError("ZIP CRC 검사 실패")
        for name in ("Raidian.exe", "Raidian-CLI.exe"):
            if hashlib.sha256(archive.read(name)).hexdigest() != actual_hashes[name]:
                raise ValidationError(f"ZIP 내부 EXE 체크섬 불일치: {name}")
        try:
            info = json.loads(archive.read("BUILD-INFO.json").decode("utf-8-sig"))
        except (json.JSONDecodeError, UnicodeError) as error:
            raise ValidationError(f"BUILD-INFO.json 오류: {error}") from error

    revision = info.get("sourceCommit", "")
    if not isinstance(revision, str) or not re.fullmatch(r"[a-fA-F0-9]{40}", revision):
        raise ValidationError("BUILD-INFO.json에 정상적인 소스 커밋 SHA가 없습니다.")
    if source_commit is not None and revision.lower() != source_commit.lower():
        raise ValidationError("빌드할 때의 Git SHA와 릴리스할 Git SHA가 다릅니다.")
    if info.get("platform") != "windows-amd64" or info.get("version") != tag:
        raise ValidationError("빌드 대상 플랫폼 또는 태그가 일치하지 않습니다.")
    if info.get("builder") not in ("PyInstaller", "Nuitka-MingGW"):
        raise ValidationError("빌드 도구 정보가 올바르지 않습니다.")
    return {"tag": tag, "sourceCommit": revision, "builder": info["builder"],
            "archive": str(archive_path), "sha256": actual_hashes[archive_path.name]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Raidian Windows Release 검증")
    parser.add_argument("--directory", type=Path, default=Path(__file__).resolve().parents[1] / "dist")
    parser.add_argument("--tag", default="v0.1.0")
    parser.add_argument("--source-commit", help="검증 대상 Git main SHA")
    args = parser.parse_args(argv)
    try:
        print(json.dumps({"ok": True, "data": validate(args.directory, args.tag, args.source_commit)},
                         ensure_ascii=False, indent=2))
        return 0
    except (ValidationError, OSError, zipfile.BadZipFile, KeyError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
