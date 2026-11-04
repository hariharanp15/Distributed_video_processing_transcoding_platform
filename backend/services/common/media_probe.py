"""Small dependency-free MP4 metadata reader for local mode.

FFprobe remains the preferred production source; this reads the standard
`mvhd` and `tkhd` atoms so duration and dimensions are available before
FFmpeg is installed.
"""
from pathlib import Path
import struct

def _atom_payload(data: bytes, atom: bytes):
    marker = data.find(atom)
    return data[marker + 4:] if marker >= 4 else None

def probe_mp4(path: str) -> tuple[int, int, int]:
    data = Path(path).read_bytes()
    duration = width = height = 0
    mvhd = _atom_payload(data, b"mvhd")
    if mvhd and len(mvhd) >= 28:
        version = mvhd[0]
        if version == 0 and len(mvhd) >= 20:
            timescale, ticks = struct.unpack(">II", mvhd[12:20])
        elif version == 1 and len(mvhd) >= 32:
            timescale, ticks = struct.unpack(">IQ", mvhd[20:32])
        else: timescale = ticks = 0
        duration = int(ticks / timescale) if timescale else 0
    tkhd = _atom_payload(data, b"tkhd")
    if tkhd:
        offset = 76 if tkhd[0] == 0 else 88
        if len(tkhd) >= offset + 8:
            width, height = struct.unpack(">II", tkhd[offset:offset + 8])
            width >>= 16; height >>= 16
    return duration, width, height
