# -*- coding: utf-8 -*-
"""Build a losslessly compressed copy of the whole repository beside it.

THE SOURCE IS NEVER WRITTEN TO. Every file is either copied, re-encoded into the copy, or
skipped; nothing in the original is moved, renamed or deleted. Run with --dry to see the
projection without writing anything.

WHAT IS KEPT
    Every data file, everywhere: CSV, JSON, run.json, PDF, PPTX, DOCX, MD, PY, photographs,
    generated reports, the git history. The keep list below governs PIXELS ONLY -- a
    specimen whose video is dropped still keeps its numbers.

WHAT IS RE-ENCODED, losslessly
    rawvideo / ffv1 .avi -> FFV1 in MKV. Measured 2.7x on the rig's videos and 4.6x on the
    laboratory's. Bit-exact: the laboratory files' pal8 palette is a pure grey ramp, so the
    gray conversion loses nothing, and FFV1 stores slice CRCs.
    .tif stills -> PNG. Measured 42 % of the original, pixel for pixel.

WHAT IS DROPPED
    video_speckle.avi / video_boost.avi     viewing copies; the MOT README states they are
                                            not what the detector measured
    the duplicate laboratory recording under Test data/Fracture tests/Videoextesometer MOT/
    the duplicate capture folders under MOT .../rig reference docs/S*/<timestamp>/
    for each kept run, whichever of {video, stills} holds FEWER frames -- verified frame for
    frame to be the same pixels, so the survivor loses nothing. S35 is the reason this is
    checked per run and not assumed: its stills hold 7004 frames against the video's 3488.
    pixels of specimens not on the keep list
    build artifacts: *.exe, __pycache__, .pytest_cache, .pio build output
"""
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = (r"C:\Users\sivadi\OneDrive - Jonkoping University\Dokument\Python codes"
       r"\UTM-main current")
DST = r"C:\Users\sivadi\Downloads\UTM-main compressed"      # outside OneDrive: nothing syncs

KEEP_SPECIMENS = {"S13", "S24", "S25", "S26", "S27", "S28", "S30", "S32", "S33", "S34",
                  "S35", "S37", "S38", "S39"}
MEDIA = (".avi", ".mkv", ".tif", ".tiff")
DUP_LAB = "Test data/Fracture tests/Videoextesometer MOT"
DUP_MOT = re.compile(r"MOT Validation docs/MOT Test \d/PPD UTM DIC rig reference docs/"
                     r"S\d+/\d{8}_")
ARTIFACT = ("__pycache__", ".pytest_cache", "/.pio/build", "/.pio/libdeps")


def specimen(p):
    m = (re.search(r"Specimen_(S\d+)", p) or re.search(r"rig reference docs/(S\d+)", p)
         or re.search(r"Trial for lateral strain/(S\d+)", p))
    return m.group(1) if m else None


def probe(path, count=False):
    args = ["ffprobe", "-v", "error", "-select_streams", "v:0"]
    if count:
        args += ["-count_packets", "-show_entries", "stream=nb_read_packets"]
    else:
        args += ["-show_entries", "stream=codec_name"]
    args += ["-of", "csv=p=0", path]
    out = subprocess.run(args, capture_output=True, text=True).stdout.strip()
    return int(out) if count and out.isdigit() else out


def survey_runs():
    """For each capture run: which side (video or stills) holds more frames."""
    keep_video, keep_stills = set(), set()
    bases = [os.path.join(SRC, "Software", "UTM_PyQt6", "Test data", "Fracture tests"),
             os.path.join(SRC, "Software", "UTM_PyQt6", "Test data",
                          "Trial for lateral strain")]
    for base in bases:
        for run in sorted(os.listdir(base)):
            d = os.path.join(base, run)
            if not os.path.isdir(d):
                continue
            m = re.search(r"(S\d+)", run)
            if not m or m.group(1) not in KEEP_SPECIMENS:
                continue
            spec = m.group(1)
            vids = (glob.glob(os.path.join(d, "**", "video.avi"), recursive=True) +
                    glob.glob(os.path.join(d, "**", "video.mkv"), recursive=True))
            tifs = glob.glob(os.path.join(d, "**", "*.tif"), recursive=True)
            if not vids or not tifs:
                keep_video.add(spec)                  # only one side exists: keep it
                keep_stills.add(spec)
                continue
            codec = probe(vids[0])
            nv, ns = probe(vids[0], count=True), len(tifs)
            if codec in ("rawvideo", "ffv1") and nv >= ns:
                keep_video.add(spec)                  # the video covers every still
            else:
                keep_stills.add(spec)                 # stills are the superset (S35), or the
                if codec == "mjpeg":                  # video is lossy: keep the pixels
                    keep_video.add(spec)              # ... and the small mjpeg file too
            print("   %-5s codec=%-9s video=%-6d stills=%-6d -> keep %s"
                  % (spec, codec, nv, ns,
                     "video" + (" + stills" if spec in keep_stills else "")
                     if spec in keep_video else "stills"))
    return keep_video, keep_stills


def plan(rel, size, keep_video, keep_stills):
    """(action, reason) for one file. action: copy | ffv1 | png | skip"""
    p = rel.replace("\\", "/")
    low = p.lower()
    base = os.path.basename(low)
    ext = os.path.splitext(low)[1]
    if any(a in "/" + low for a in ARTIFACT) or low.endswith(".exe"):
        return "skip", "build artifact"
    is_media = ext in MEDIA or (ext == ".png" and ("/frames" in low or "frames/" in low))
    if not is_media:
        return "copy", "data file"                     # every data file, everywhere
    if DUP_LAB in p:
        return "skip", "duplicate laboratory recording"
    if DUP_MOT.search(p):
        return "skip", "duplicate capture folder"
    if base in ("video_speckle.avi", "video_boost.avi"):
        return "skip", "viewing copy"
    spec = specimen(p)
    if "Videoextesometer MOT" in p and ext in (".avi", ".mkv"):
        return "ffv1", "laboratory recording"
    if spec is None:
        return "copy", "media outside a specimen run"
    if base in ("video.avi", "video.mkv"):
        if spec not in keep_video:
            return "skip", "video not needed for %s" % spec
        return ("copy" if probe(os.path.join(SRC, rel)) == "mjpeg" else "ffv1"), \
            "video of %s" % spec
    if ext in (".tif", ".tiff"):
        if spec not in keep_stills:
            return "skip", "stills duplicated by the video of %s" % spec
        return "png", "stills of %s" % spec
    if spec not in keep_stills and spec not in keep_video:
        return "skip", "frames not needed for %s" % spec
    return "copy", "frames of %s" % spec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    assert os.path.isdir(SRC)
    print("source: %s\ncopy:   %s\n" % (SRC, DST))
    print("per-run coverage check (frame counts decoded, not read from metadata):")
    keep_video, keep_stills = survey_runs()

    todo = []
    for dp, dns, fns in os.walk(SRC):
        for f in fns:
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, SRC)
            try:
                size = os.path.getsize(full)
            except OSError:
                continue
            action, why = plan(rel, size, keep_video, keep_stills)
            todo.append((action, why, rel, size))

    from collections import defaultdict
    agg = defaultdict(lambda: [0, 0])
    for action, why, rel, size in todo:
        a = agg[action]
        a[0] += 1
        a[1] += size
    print("\nplan:")
    for action in ("copy", "ffv1", "png", "skip"):
        n, b = agg[action]
        print("   %-5s %7d files %9.2f GB in" % (action, n, b / 1e9))
    est = agg["copy"][1] + agg["ffv1"][1] * 0.30 + agg["png"][1] * 0.42
    print("   projected copy size: %.1f GB" % (est / 1e9))
    if args.dry:
        print("\nDRY RUN -- nothing written.")
        return

    t0 = time.time()
    done = defaultdict(int)
    written = 0
    for i, (action, why, rel, size) in enumerate(todo, 1):
        src = os.path.join(SRC, rel)
        dst = os.path.join(DST, rel)
        if action == "skip":
            done["skip"] += 1
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if action == "copy":
            if not os.path.exists(dst) or os.path.getsize(dst) != size:
                shutil.copy2(src, dst)
        elif action == "ffv1":
            dst = os.path.splitext(dst)[0] + ".mkv"
            if not os.path.exists(dst):
                subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-c:v", "ffv1",
                                "-level", "3", "-g", "1", "-slices", "4", "-slicecrc", "1",
                                "-pix_fmt", "gray", dst], check=True)
            print("      ffv1  %-58s %.2f -> %.2f GB"
                  % (os.path.basename(rel)[:58], size / 1e9, os.path.getsize(dst) / 1e9))
        elif action == "png":
            dst = os.path.splitext(dst)[0] + ".png"
            if not os.path.exists(dst):
                from PIL import Image
                Image.open(src).save(dst, "PNG", optimize=True)
        done[action] += 1
        written += os.path.getsize(dst)
        if i % 2000 == 0:
            print("   %d/%d files, %.1f GB written, %.0f s"
                  % (i, len(todo), written / 1e9, time.time() - t0))
    print("\ndone in %.0f s: %d copied, %d re-encoded to FFV1, %d stills to PNG, %d skipped"
          % (time.time() - t0, done["copy"], done["ffv1"], done["png"], done["skip"]))


if __name__ == "__main__":
    main()
