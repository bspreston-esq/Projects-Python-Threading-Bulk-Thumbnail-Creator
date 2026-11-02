#!/usr/bin/env python3
"""Resize hundreds of images in a thread pool while renaming the outputs."""
import argparse
import os
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

def make_thumbnail(source: str, destination: str, size=(128, 128)) -> str:
    """Resize one image to fit `size` and save it as JPEG."""
    with Image.open(source) as image:
        image = image.convert("RGB")
        image.thumbnail(size)
        image.save(destination, "JPEG", quality=85)
    return destination

def bulk_thumbnails(files, output_dir: str, size=(128, 128), workers: int = 8):
    """Process files concurrently; returns (succeeded, failed)."""
    os.makedirs(output_dir, exist_ok=True)
    succeeded, failed = [], []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {}
        for path in files:
            stem = os.path.splitext(os.path.basename(path))[0]
            destination = os.path.join(output_dir, f"{stem}_thumb.jpg")
            futures[pool.submit(make_thumbnail, path, destination, size)] = path
        for future in as_completed(futures):
            source = futures[future]
            try:
                succeeded.append(future.result())
            except Exception as exc:  # one bad file must not kill the batch
                failed.append((source, str(exc)))
    return succeeded, failed

def demo() -> None:
    if Image is None:
        print("Pillow is not installed; install it with: pip install pillow")
        return
    with tempfile.TemporaryDirectory() as tmp:
        source_dir = os.path.join(tmp, "source")
        output_dir = os.path.join(tmp, "thumbs")
        os.makedirs(source_dir)
        colours = [(200, 40, 40), (40, 160, 60), (40, 80, 200), (180, 160, 30)]
        files = []
        for index in range(24):
            path = os.path.join(source_dir, f"image_{index:02d}.png")
            Image.new("RGB", (640, 480), colours[index % len(colours)]).save(path)
            files.append(path)
        start = time.perf_counter()
        succeeded, failed = bulk_thumbnails(files, output_dir, workers=8)
        elapsed = time.perf_counter() - start
        sample = Image.open(succeeded[0])
        print(f"processed {len(files)} images with 8 workers in {elapsed*1000:.0f} ms")
        print(f"thumbnails: {len(succeeded)}, failures: {len(failed)}")
        print(f"sample: {os.path.basename(succeeded[0])} {sample.size[0]}x{sample.size[1]}")

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir")
    parser.add_argument("--output", default="thumbnails")
    parser.add_argument("--size", type=int, default=128)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()

    if args.demo or not args.dir:
        demo()
        return
    files = [os.path.join(args.dir, name) for name in sorted(os.listdir(args.dir))
             if os.path.splitext(name)[1].lower() in (".png", ".jpg", ".jpeg", ".gif", ".bmp")]
    succeeded, failed = bulk_thumbnails(files, args.output, (args.size, args.size), args.workers)
    print(f"{len(succeeded)} thumbnails written to {args.output}, {len(failed)} failed")
    for source, error in failed:
        print(f"  failed: {source}: {error}")

if __name__ == "__main__":
    main()
