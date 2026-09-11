# Documentation/Videos/

One recorded pull per material, as a **viewing copy**. These are here so anyone reading the
report can watch what the camera saw without cloning 150 GB.

| file | specimen | material | what it shows |
|---|---|---|---|
| `S26_PLA_80mm_gauge.mp4` | S26 | PLA, 100 % infill | The 80 mm-gauge run used for the laboratory validation: the two sprayed markers separating, then fracture. One half of the S25/S26 pair whose frames the XT-205's software re-processed. |
| `S32_PETG.mp4` | S32 | PETG | A PETG pull to fracture — the material that yields furthest before breaking of the three. |
| `S35_TPU.mp4` | S35 | TPU 95A | The TPU run where the DIC channel stopped at 12.6 % strain while the crosshead read 21.5 %: the markers deform and drift out of the gates, which is the coverage limit discussed in the report. |

## These are NOT measurement data

They are lossy H.264 re-encodes (CRF 20) of the original recordings, made only to be
watchable in a browser. **Never measure from them.** The strain numbers in the report come
from the raw frames, which are:

- `Software/UTM_PyQt6/Test data/` in the working copy — uncompressed `rawvideo` AVI plus the
  per-frame stills. Gitignored: the tree is 150 GB.
- the lossless archive, where the same runs are FFV1 and PNG at about 20 % of the size, with
  every pixel intact and verified frame for frame.

The originals of these three: S26 is 60 MB of MJPEG plus 1.66 GB of PNG stills; S32 is
2.52 GB of rawvideo; S35 is 3.44 GB of rawvideo with 7 004 stills. GitHub's per-file ceiling
is 100 MB, which is why only these compressed copies are here.

Re-encode command used:

```
ffmpeg -i video.avi -c:v libx264 -crf 20 -preset slow -pix_fmt yuv420p -movflags +faststart out.mp4
```

Note that the source frames are 419 or 420 px wide by 2348 tall — a tall, narrow strip of the
specimen's gauge, not a conventional frame. That is the field of view the 25 mm lens gives at
≈371 mm stand-off, and it is why the videos look the shape they do.
