import argparse
import json
import logging
import os
import shutil
import brotli

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%H:%M:%S"
)


def process_file(src_path: str, dst_path: str, incremental: bool) -> None:
    target_path = dst_path[:-3] if src_path.endswith('.br') else dst_path
    if incremental and os.path.exists(target_path):
        logging.info(f"Skipped: {target_path}")
        return
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    if src_path.endswith('.br'):
        with open(src_path, 'rb') as f:
            raw = brotli.decompress(f.read())
        data = json.loads(raw)
        with open(dst_path[:-3], 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logging.info(f"Decompressed: {src_path} -> {dst_path[:-3]}")
    else:
        shutil.copy2(src_path, dst_path)
        logging.info(f"Copied: {src_path} -> {dst_path}")


def traverse(start_path: str, src_root: str, dst_root: str, incremental: bool) -> None:
    if os.path.isfile(start_path):
        rel = os.path.relpath(start_path, src_root)
        process_file(start_path, os.path.join(dst_root, rel), incremental)
        return
    for root, _, files in os.walk(start_path):
        for file in files:
            sf = os.path.join(root, file)
            rel = os.path.relpath(sf, src_root)
            df = os.path.join(dst_root, rel)
            process_file(sf, df, incremental)


def main() -> None:
    parser = argparse.ArgumentParser(description='Assets decompression tool')
    parser.add_argument(
        '--incremental',
        '-i',
        action='store_true',
        help='Incremental mode (skip existing files)',
    )
    parser.add_argument(
        'paths', nargs='+', help='Paths to process (files/directories under assets)'
    )
    args = parser.parse_args()

    SRC = 'assets'
    DST = 'assets_decompress'
    SRC_ABS = os.path.abspath(SRC)
    DST_ABS = os.path.abspath(DST)

    mode = "Incremental" if args.incremental else "Full"
    logging.info(f"Startup | Source: {SRC} | Target: {DST} | Mode: {mode}")

    for p in args.paths:
        input_abs = os.path.abspath(p)
        if not input_abs.startswith(SRC_ABS + os.sep):
            logging.error(f"Invalid path: {p}")
            continue

        if os.path.exists(input_abs):
            traverse(input_abs, SRC_ABS, DST_ABS, args.incremental)
        else:
            logging.warning(f"Path does not exist: {input_abs}")

    logging.info("Processing completed")


if __name__ == '__main__':
    main()
