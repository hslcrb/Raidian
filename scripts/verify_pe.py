"""Lightweight PE/AMD64 validation for generated Windows executables.

This checks the container architecture, *not* functional behavior or security.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import struct


def machine(path: str | Path) -> int:
    file = Path(path)
    with file.open("rb") as stream:
        header = stream.read(64)
        if len(header) < 64 or header[:2] != b"MZ":
            raise ValueError("Windows MZ 헤더가 없습니다.")
        offset = struct.unpack_from("<I", header, 0x3C)[0]
        if offset > file.stat().st_size - 6:
            raise ValueError("PE 헤더 위치가 올바르지 않습니다.")
        stream.seek(offset)
        signature = stream.read(6)
        if signature[:4] != b"PE\x00\x00":
            raise ValueError("PE 서명이 없습니다.")
        return struct.unpack_from("<H", signature, 4)[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Raidian PE x64 검증 도구")
    parser.add_argument("paths", nargs="+")
    options = parser.parse_args(argv)
    for path in options.paths:
        actual = machine(path)
        if actual != 0x8664:
            raise SystemExit(f"{path}: Windows x64 EXE가 아닙니다 (machine={actual:#06x})")
        print(f"✔ PE AMD64: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
