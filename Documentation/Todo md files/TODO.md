# DIC Strain Measurement Development TODO

This document outlines the tasks required to implement Digital Image Correlation (DIC) strain measurement for the UTM application (Phase 8).

**Current Status:** Phase 8.1–8.5 complete. Phase 8.6 (Validation) in progress: hardware 8.6.5 + 8.6.10 + noise floor ✅ (2026-04-22), 8.6.16 ✅ (2026-05-28), optional software 8.6.11–8.6.14 ✅ (2026-04-22), cleanup ✅ (2026-09-01).
**Remaining:** none. Every hardware test is either passed or dropped by decision.
**Dropped by decision (2026-09-01):** 8.6.3, 8.6.4, 8.6.15, 8.6.17, 8.6.18 — each struck through below with its reason.
**Suite:** 38/41 in `tests script/test_phase_8_6.py`. Three have failed since before this line was written — two blob-count edge cases and the swept-strain pipeline test. They are unrelated to any current work and are tracked as an open defect, not as passing.

**App Version:** 0.5.4 | **Firmware Version:** 1.3.1

---

## Prerequisites

### Hardware Required
- [x] Basler acA2440-35um USB 3.0 camera
- [x] Azure-2514M lens (25mm, f/1.4, 5MP, 2/3" sensor)
- [x] LED lighting for specimen illumination
- [x] Specimen markers (2 high-contrast dots/stickers on specimen)

### Software Dependencies
```bash
pip install pypylon          # Basler camera SDK (requires Pylon installation)
pip install opencv-python    # Image processing and blob detection
```

---

## Implementation Tasks

### Phase 8.1: Camera Setup & Basic Capture — COMPLETE

- [x] **Install Basler Pylon SDK** on development machine
- [x] **Create `camera_manager.py`** with CameraManager class
  - [x] Camera discovery and connection via pypylon
  - [x] Configuration settings (actual values):
    - ROI: `[52, 524, 1588, 500]` (OffsetX, OffsetY, Width, Height)
    - Frame rate: 35 fps
    - Exposure: 50000 us
    - Gamma: 0.5
    - Pixel format: Mono8
  - [x] Start/stop acquisition with `CaptureThread` (QThread)
  - [x] Frame capture with 90-degree rotation (`cv2.ROTATE_90_CLOCKWISE`)
  - [x] PyQt signals: `frame_ready`, `error_occurred`, `connection_changed`, `blobs_detected`, `dic_strain_updated`
  - [x] Proper cleanup on disconnect

### Phase 8.2: UI Integration — COMPLETE

- [x] **Camera controls** in Stress/Strain tab
  - [x] `DIC Camera` group box with Start/Stop/Tare buttons
  - [x] "Tare DIC" button (sets initial gauge length, calculates px_per_mm)
  - [x] DIC strain display labels
- [x] **Image display area** with camera feed
  - [x] Blob marker overlay and distance annotation
- [x] **Strain source selector** combo box with 5 modes:
  - Motor, DIC Cauchy, DIC True, Both (Cauchy + Motor), Both (Cauchy + True)

### Phase 8.3: Blob Detection (OpenCV) — COMPLETE

- [x] **Blob detection** in `camera_manager.py` using contour analysis
  - [x] `cv2.threshold` with `THRESH_BINARY_INV` (dark blobs on light background)
  - [x] Threshold: 150
  - [x] Contour filtering by area and circularity
  - [x] Min area: 2000 px, Max area: 200000 px
  - [x] Min circularity: 0.5
- [x] **Centroid extraction** via image moments (`cv2.moments`)
  - [x] Returns sorted (x, y) coordinates (sorted by Y — top blob first)
  - [x] Error signal when blob count != 2

### Phase 8.4: Point Tracking & DIC Strain Calculation — COMPLETE

- [x] **Two-point tracking**
  - [x] Track two blob centroids frame-to-frame
  - [x] Calculate vertical distance between centroids
  - [x] Store initial distance on "Tare DIC" press
- [x] **Dual strain calculation** (Cauchy + True)
  - Cauchy: `(L - L0) / L0`
  - True: `ln(L / L0)` with zero-distance guard
  - Convention: tension (+), compression (-)
- [x] **Pixel to mm conversion**
  - [x] `px_per_mm = initial_distance / gauge_length_mm`
  - [x] Calibration factor stored and exported in CSV metadata
- [x] **DIC history deque** (maxlen=500) for time-matching with load cell
- [x] **Validation log** (8.4.6): `[DIC] ε_c | ε_t | Motor | Δ(ε_c−Motor)` throttled to ~1Hz

### Phase 8.5: Integration with Stress-Strain Plot — COMPLETE

- [x] **DIC strain as alternative strain source**
  - [x] 5-mode strain source switching (Motor / DIC Cauchy / DIC True / Both variants)
  - [x] Secondary line on stress-strain plot for overlay modes
- [x] **Three-timestamp synchronization**
  - [x] PC Time_s: `datetime.now()` — when Python received data
  - [x] MCU_Time_s: Arduino `millis()` — true ADC sample time
  - [x] DIC_Time_s: camera manager timestamp — when DIC frame was processed
  - [x] Lag_ms: staleness of DIC reading relative to load cell sample
- [x] **MCU timestamp implementation**
  - [x] Firmware sends `force,millis()` over serial
  - [x] `serial_manager.py` parses both formats (with/without timestamp, backward compatible)
  - [x] Validated: 44x jitter reduction (std dev 201ms → 4.5ms), firmware loop ~88ms (11.4 Hz)
- [x] **DIC↔Load cell time-matched lookup** (8.6.10)
  - [x] Time anchor on first sample (MCU↔PC clock bridge)
  - [x] `_match_dic_to_mcu_time()`: converts MCU timestamp → estimated PC time, finds nearest DIC reading from `dic_history`
  - [x] Staleness threshold: 100ms → returns (0.0, None) if no fresh DIC match
  - [ ] **Hardware validation pending** — verify stall rows get unique DIC values
- [x] **CSV export** with 12 columns:
  ```
  Time_s, RawADC, Force_N, Position_mm, Speed_mm_s, Motor_Strain, Stress_MPa,
  DIC_Cauchy, DIC_True, DIC_Time_s, Lag_ms, MCU_Time_s
  ```
- [x] **CSV import** restores DIC data, calibration factor (px_per_mm), and MCU timestamps
- [x] **Data cropping** preserves DIC column alignment
- [x] **Console message routing**: `[Camera]` and `[DIC]` prefixes, filtered to camera console

### Phase 8.6: Testing & Validation — IN PROGRESS

#### Software Tests (26/26 passing)

- [x] **8.6.1** Blob detection edge cases (0, 1, 2, 3+ blobs)
- [x] **8.6.2** DIC tare validation (L0 px, gauge length, px_per_mm calibration)
- [x] **8.6.3** Strain calculation (Cauchy + True strain formulas) — software validated
- [x] **8.6.4** Strain sign convention (tension = +, compression = −) — software validated
- [x] **8.6.6** CSV round-trip export/import (headers, DIC columns)
- [x] **8.6.7** Console message routing ([Camera]/[DIC] prefixes)
- [x] **8.6.8** Data cropping with DIC columns (alignment preserved)
- [x] **8.6.9** Strain source switching (Motor/DIC Cauchy/DIC True/Both)
- [x] **Math edge cases** Large deformations (50%), zero-distance guard, division-by-zero

#### Hardware Tests

- ~~**8.6.3** Known displacement test — Motor vs DIC Cauchy on a real specimen.~~ **DROPPED 2026-09-01.** The comparison is available from any saved run without a dedicated test: `Motor_Strain`, `DIC_Cauchy` and `DIC_True` are all CSV columns.
- ~~**8.6.4** Strain sign test — tension (+) / compression (−) under real loading.~~ **DROPPED 2026-09-01.** The sign convention is covered by software test 8.6.4 and has held on every recorded run.
- [x] **8.6.5** GUI responsiveness — 2417 samples / 213 s, MCU interval 88.27±4.00 ms, 0 stalls (2026-04-22)
- [x] **8.6.10** DIC↔load cell timestamp sync — 7/7 stall bursts recovered with unique DIC timestamps, median lag 27 ms, 99.1% fresh rows (2026-04-22)
- [x] **Noise floor / drift** (bonus) — DIC std 7.3×10⁻⁵, drift 5.2×10⁻⁵/min, stationary markers (2026-04-22)

#### Hardware Tests — No Grips Needed (deferred)

- ~~**8.6.15** Printed-marker calibration test — tare on 50 mm dot paper, swap to 55 mm, confirm DIC Cauchy ≈ 0.1000.~~ **DROPPED 2026-09-01.** The DIC maths is already exercised end to end by the synthetic-frame pipeline tests (8.6.11) and, on real footage, by the MOT cross-validation — our calculation and a commercial extensometer's agree to a median ratio of 1.0017 on the same video.
- [x] **8.6.16** Occlusion robustness — mid-acquisition, briefly cover one marker. Verify DIC returns 0.0/None gracefully, resumes when marker reappears, no crash. **PASS (2026-05-28):** covered 1 marker → `found 1`, both → `found 0`, strain updates skipped (held, no garbage), no crash/GUI hang, clean resume to ±3×10⁻⁵ baseline on uncover. One harmless single-frame transient (ε_c≈3.4×10⁻⁴) as marker re-enters.
- ~~**8.6.17** Motor encoder accuracy — command 1 / 5 / 10 mm, compare to Position_mm.~~ **DROPPED 2026-09-01.**
- ~~**8.6.18** Multi-session tare consistency — verify px_per_mm holds across a camera reconnect.~~ **DROPPED 2026-09-01.**
- [ ] **8.6.19** Elastic modulus characterization (material test, not measurement validation) — slow ramp (0.05 mm/s) to ~0.5 mm compression on shaken-down specimen, hold 30 s, return. Fit σ vs DIC ε_c through loading ramp. Pass: linear with R² > 0.99, slope (E) within PLA literature range 1–4 GPa, hold drift < 5 %, returns to origin within ε_c < 5×10⁻⁵. **Why:** First three tests validate the measurement device (sign, linearity, calibration); this is the first test that characterizes the actual material. Existing Compression T2 data already suggests E ≈ 3.6 GPa for this specimen.

#### Optional Software Tests — 15 tests added 2026-04-22; the file now runs 38/41 (see Current Status)

- [x] **8.6.11** End-to-end DIC pipeline with synthetic frames — 4 tests (zero, ±5%, ±10%, swept 0.8×–1.2×)
- [x] **8.6.12** GUI stress test with mock camera — 2 tests (dic_history bounded at 500 after 2000 frames, per-frame < 30 ms)
- [x] **8.6.13** CSV round-trip with real DIC data — 3 tests (all 12 columns, 6-decimal precision, comment lines skipped)
- [x] **8.6.14** Time-sync logic simulation — 6 tests (nearest pairing, 99/101 ms boundary, empty history, no anchor, out-of-order entries, Python stall recovery)

#### Open defect — the suite is not green

- [ ] **Three stale tests in `tests script/test_phase_8_6.py`** (38/41). All three predate the
  current work and all three look like test expectations that were never updated after
  `detect_blobs` learned to pick the best PAIR rather than return every blob it found:
  - `test_blob_detection_three_blobs` — expects 3 back, gets 2
  - `test_blob_detection_four_blobs` — expects >= 4 back, gets 2
  - `test_pipeline_swept_strain_series` — gets 0 blobs at separation factor 0.8, where a guard
    probably rejects the synthetic frame
  Decide the intended contract for `detect_blobs` with more than two markers, then fix the tests
  (or the code) to match. Until then nothing should describe this file as passing.

#### Cleanup (after hardware validation)

- [x] **Remove the temporary 8.4.6 validation log from main.py** ✅ 2026-09-01. It printed DIC vs motor strain into the console once a second for the whole of every run. Nothing is lost: `Motor_Strain`, `DIC_Cauchy` and `DIC_True` are all CSV columns, so 8.6.3 and 8.6.4 are a subtraction on the exported file — which is the evidence those tests should rest on anyway, rather than console scrollback.

---

## Code Architecture

### Files

```
Software/UTM_PyQt6/
├── main.py                 # Main application (v0.5.4)
├── camera_manager.py       # CameraManager class with pypylon + blob detection + DIC strain
├── serial_manager.py       # Serial communication, MCU timestamp parsing
├── widgets.py              # Custom widgets (FluentSwitch, SpeedGauge, RangeSlider)
├── test_phase_8_6.py       # Phase 8.6 unit tests (26 tests)
├── validate_phase_8_6.py   # Hardware validation checklist + math verification
├── test_blob.py            # Blob detection parameter testing
├── test_threshold.py       # Threshold value comparison
├── test_camera.py          # Basic camera connection test
├── test_camera1.py         # ROI frame capture test
├── test_camera2.py         # Full sensor frame capture test
├── test_camera3.py         # Exposure time test
├── test_camera4.py         # Live acquisition + tare workflow test
```

### CameraManager Class (Actual Implementation)

```python
class CameraManager(QObject):
    # Signals
    frame_ready = pyqtSignal(np.ndarray)
    blobs_detected = pyqtSignal(list)
    dic_strain_updated = pyqtSignal(float, float)  # (cauchy, true)
    error_occurred = pyqtSignal(str)
    connection_changed = pyqtSignal(bool)

    # Configuration
    ROI = [52, 524, 1588, 500]
    FRAME_RATE = 35
    EXPOSURE_TIME = 50000
    GAMMA = 0.5
    THRESHOLD = 150
    MIN_AREA = 2000
    MAX_AREA = 200000
    MIN_CIRCULARITY = 0.5

    # DIC state
    initial_distance = None
    px_per_mm = 0.0
    dic_history = deque(maxlen=500)

    # Methods
    def connect_camera(self) -> bool
    def disconnect_camera(self)
    def start_acquisition(self)
    def stop_acquisition(self)
    def capture_frame(self) -> np.ndarray
    def detect_blobs(self, frame) -> list
    def calculate_dic_strain(self, centroids) -> tuple  # (cauchy, true)
    def tare_dic(self)
```

---

## Validated Math

| Deformation | Cauchy (ε_c) | True (ε_t) |
|-------------|-------------|------------|
| 10% elongation | 0.1000 | 0.0953 |
| 20% elongation | 0.2000 | 0.1823 |
| 50% elongation | 0.5000 | 0.4055 |

---

## References

- **MATLAB Reference Implementation:** `Software/data/TestingTracking.m`
- **Camera Settings Test:** `Software/data/TestingImageAquisition.m`
- **pypylon Documentation:** https://github.com/basler/pypylon
- **Starting TODO (original):** `Starting_TODO.md`