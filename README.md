# Bulk Thumbnail Creator

**Category:** Threading

## Problem

Picture processing can take a bit of time for some transformations. Especially if the image is large. Create an image program which can take hundreds of images and converts them to a specified size in the background thread while you do other things. For added complexity, have one thread handling re-sizing, have another bulk renaming of thumbnails etc.

## Solution

A `ThreadPoolExecutor` resizes images concurrently (Pillow releases the GIL during decoding/encoding, so threads genuinely overlap), while each task also derives the renamed `<stem>_thumb.jpg` output. Results are collected with `as_completed`, and a failure in one image is reported without aborting the batch.

## How to run

Requires Python 3.8+ and no third-party packages.

```bash
python3 main.py --dir ./photos --output thumbs --size 200 --workers 8
python3 main.py --demo
```

## Example

```text
processed 24 images with 8 workers in 27 ms
thumbnails: 24, failures: 0
sample: image_00_thumb.jpg 128x96
```

## Attribution

The problem statement is from [karan/Projects](https://github.com/karan/Projects), a list of practical projects that anyone can solve in any programming language (MIT License, Copyright (c) 2013 Karan Goel). The Python solution in this repository was implemented by [bspreston-esq](https://github.com/bspreston-esq).

This repository is part of the [Projects-Python-All](https://github.com/bspreston-esq/Projects-Python-All) collection.
