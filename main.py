#!/usr/bin/env python3
"""Ship the finished infographic to the output directory.

The entry is a program that writes one image. This program copies the
pre-rendered PNG that ships in the repository to <output>/entry.png, writing
atomically and verifying that the bytes on disk are exactly the shipped bytes.

Standard library only. No network. Deterministic: the same input bytes are
copied on every run.

Output directory resolution order:
    1. --output-dir PATH
    2. $MAKEFUN_OUTPUT_DIR
    3. /output
"""

import argparse
import hashlib
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "assets", "entry.png")
CHUNK = 1 << 20
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_output_dir(cli_value):
    if cli_value:
        return cli_value
    from_env = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if from_env:
        return from_env
    return "/output"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Copy assets/entry.png to <output>/entry.png atomically.")
    parser.add_argument("--output-dir", default=None,
                        help="directory to write entry.png into "
                             "(default: $MAKEFUN_OUTPUT_DIR or /output)")
    args = parser.parse_args(argv)

    out_dir = resolve_output_dir(args.output_dir)
    if not os.path.isfile(SOURCE):
        raise SystemExit("ERROR: shipped image not found: %s" % SOURCE)

    with open(SOURCE, "rb") as probe:
        if probe.read(len(PNG_SIGNATURE)) != PNG_SIGNATURE:
            raise SystemExit("ERROR: shipped file is not a PNG: %s" % SOURCE)

    source_hash = sha256_file(SOURCE)
    source_size = os.path.getsize(SOURCE)

    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        raise SystemExit("ERROR: cannot create output directory %r: %s"
                         % (out_dir, exc))

    dest = os.path.join(out_dir, "entry.png")

    # A non-dot prefix is required by the submission gate; the temp file is
    # made world-readable before it is renamed over the destination.
    fd, tmp_path = tempfile.mkstemp(prefix="entry-", suffix=".png", dir=out_dir)
    try:
        with os.fdopen(fd, "wb") as out_handle, open(SOURCE, "rb") as src:
            for block in iter(lambda: src.read(CHUNK), b""):
                out_handle.write(block)
            out_handle.flush()
            os.fsync(out_handle.fileno())
            os.fchmod(out_handle.fileno(), 0o644)

        copied_hash = sha256_file(tmp_path)
        if copied_hash != source_hash:
            raise SystemExit(
                "ERROR: hash mismatch while copying: expected %s, got %s"
                % (source_hash, copied_hash))
        if os.path.getsize(tmp_path) != source_size:
            raise SystemExit("ERROR: copied file has the wrong size")

        os.replace(tmp_path, dest)
        tmp_path = None
    finally:
        if tmp_path is not None and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    final_hash = sha256_file(dest)
    if final_hash != source_hash:
        raise SystemExit(
            "ERROR: output hash mismatch after rename: expected %s, got %s"
            % (source_hash, final_hash))

    final_mode = os.stat(dest).st_mode & 0o777
    if not final_mode & 0o004:
        raise SystemExit(
            "ERROR: output is not world-readable (mode %03o): %s"
            % (final_mode, dest))

    print("wrote %s (%d bytes, mode %03o, sha256 %s)"
          % (dest, source_size, final_mode, final_hash))
    return 0


if __name__ == "__main__":
    sys.exit(main())
