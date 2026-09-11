"""MOT session 2 — the XT-205's own record of a 45 mm gauge pull, as data.

Two files, one time base:

    strain-sample3.csv   the extensometer's strain, extension and the gauge length it measured,
                         at 20 Hz. Rows before the markers are found read "Invalid" in EVERY
                         column, which is why they must be dropped as a ROW rather than per
                         column — dropping per column silently desynchronises time from strain.
    sample3.daq          the acquisition log. Column 0 is time on the same clock as the CSV, and
                         column 4 is the load in kN. The other 48 columns are unused channels
                         that read "Invalid" throughout.

The load column is identified by its shape, not by a header, because the .daq carries none: it is
the only channel that rises from zero to 3.57, holds a plateau, and collapses in a single sample.
On an 80 mm² section 3.57 kN is 44.6 MPa, which is where PLA belongs; no other column is even the
right order of magnitude.

Test conditions, from the operator: 2 mm/min crosshead, 300 N preload, 45 mm gauge.
2 mm/min is 0.033 mm/s — a THIRD of our own 0.10 mm/s, which is a real difference for a polymer
and is carried through to every comparison rather than being averaged away.
"""
import csv
import io
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
DIR = os.path.join(REPO, "Validation docs", "MOT Test 2", "Videoextesometer MOT")

CSV = os.path.join(DIR, "strain-sample3.csv")
DAQ = os.path.join(DIR, "sample3.daq")

AREA_MM2 = 80.0                 # CAD nominal, the same basis every number in this project uses
GAUGE_MM = 45.0
SPEED_MM_MIN = 2.0              # operator-reported
PRELOAD_N = 300.0               # operator-reported
LOAD_COL = 4                    # kN
E_WINDOW = (0.05, 0.40)         # % strain — the project's fixed modulus window

_cache = {}


def _read_daq():
    t, f = [], []
    for ln in io.open(DAQ, encoding="utf-8", errors="replace"):
        if ln.startswith("#") or not ln.strip():
            continue
        p = ln.rstrip("\r\n").split("\t")
        try:
            tt, ff = float(p[0]), float(p[LOAD_COL])
        except (ValueError, IndexError):
            continue
        t.append(tt)
        f.append(ff * 1000.0)               # kN -> N
    return np.array(t), np.array(f)


def _read_strain():
    """Time, strain %, and the gauge length the instrument reports.

    A row is kept only if BOTH time and strain parse. The instrument writes "Invalid" across a
    whole row before it has found the markers, and taking the columns independently would leave
    3351 times against 3308 strains — arrays that still zip, still plot, and are wrong by 43
    samples of lag.
    """
    t, e, g = [], [], []
    for r in csv.reader(io.open(CSV, encoding="utf-8-sig")):
        if len(r) < 4:
            continue
        try:
            tt, ee = float(r[0]), float(r[1])
        except ValueError:
            continue
        try:
            gg = float(r[3])
        except ValueError:
            gg = np.nan
        t.append(tt)
        e.append(ee)
        g.append(gg)
    return np.array(t), np.array(e), np.array(g)


def load():
    if _cache:
        return _cache

    t_f, f = _read_daq()
    t_e, e, g = _read_strain()

    # ---- fracture: the single largest load drop, and the cut is the sample BEFORE it.
    #
    # The +1 sample is already past the break, and on this record that matters more than usual:
    # when the specimen parts, the two halves recoil and the extensometer's markers spring back
    # with them. Strain reads 5.33 % at 165.2 s and 2.78 % two samples later — a 2.3 % "drop" that
    # is the specimen coming apart, not deforming. Taking the post-break sample would report that
    # recoil as the failure strain and understate it by half.
    i_fr = int(np.argmin(np.diff(f)))
    t_fr = float(t_f[i_fr])

    keep_f = t_f <= t_fr
    keep_e = t_e <= t_fr
    t_f, f = t_f[keep_f], f[keep_f]
    t_e, e, g = t_e[keep_e], e[keep_e], g[keep_e]

    # stress on the load clock, strain interpolated onto it: the load is the denser, cleaner
    # channel and interpolating IT onto strain would smooth the very peak being measured.
    sig = f / AREA_MM2
    e_on_f = np.interp(t_f, t_e, e)

    i_pk = int(np.argmax(f))
    uts, uts_e, t_pk = float(sig[i_pk]), float(e_on_f[i_pk]), float(t_f[i_pk])

    # ---- E over the project's fixed window, on the extensometer's own strain
    m = (e_on_f >= E_WINDOW[0]) & (e_on_f <= E_WINDOW[1])
    if m.sum() >= 5:
        A = np.polyfit(e_on_f[m] / 100.0, sig[m], 1)
        E = float(A[0]) / 1000.0                      # MPa per unit strain -> GPa
        icept = float(A[1])
        pred = np.polyval(A, e_on_f[m] / 100.0)
        ss = float(1 - ((sig[m] - pred) ** 2).sum() / ((sig[m] - sig[m].mean()) ** 2).sum())
    else:
        E = icept = ss = float("nan")

    # ---- 0.2 % offset yield: where the curve meets the E line shifted by 0.2 % strain
    sy = sy_e = float("nan")
    if np.isfinite(E):
        off = (E * 1000.0) * ((e_on_f / 100.0) - 0.002) + icept
        d = sig - off
        cross = np.nonzero((d[:-1] > 0) & (d[1:] <= 0))[0]
        if len(cross):
            j = int(cross[0])
            sy, sy_e = float(sig[j]), float(e_on_f[j])

    # ---- THE STRAIN ZERO, and the correction the whole session exists to make possible.
    #
    # The 300 N preload is applied INSIDE this record, not before it: load reads ~0 N for the first
    # two seconds and only crosses 300 N at t = 8.85 s, by which point the extensometer already
    # reads 0.116 % strain. So their zero is a ZERO-LOAD zero and carries the toe — grip take-up
    # and specimen straightening — inside the strain, while our Px0 is frozen AFTER a ~310 N
    # preload and starts from an already-seated specimen.
    #
    # That is not a fault in either record; it is a convention, and it is the one difference the
    # validation pack said had to be settled before the numbers could be compared. It is settled
    # here by RE-ZEROING their strain at the instant their load first reaches the preload, which
    # puts both machines on our convention. Both sets are kept: the as-recorded numbers are what
    # their software reports, the re-zeroed ones are what may be compared with ours.
    i_pre = int(np.argmax(f >= PRELOAD_N)) if (f >= PRELOAD_N).any() else 0
    t_pre, e_pre = float(t_f[i_pre]), float(e_on_f[i_pre])
    e_rz = e_on_f - e_pre

    m2 = (e_rz >= E_WINDOW[0]) & (e_rz <= E_WINDOW[1])
    if m2.sum() >= 5:
        A2 = np.polyfit(e_rz[m2] / 100.0, sig[m2], 1)
        E_rz, icept2 = float(A2[0]) / 1000.0, float(A2[1])
        pred2 = np.polyval(A2, e_rz[m2] / 100.0)
        ss2 = float(1 - ((sig[m2] - pred2) ** 2).sum() / ((sig[m2] - sig[m2].mean()) ** 2).sum())
    else:
        E_rz = icept2 = ss2 = float("nan")

    sy_rz = sy_e_rz = float("nan")
    if np.isfinite(E_rz):
        off2 = (E_rz * 1000.0) * ((e_rz / 100.0) - 0.002) + icept2
        d2 = sig - off2
        c2 = np.nonzero((d2[:-1] > 0) & (d2[1:] <= 0))[0]
        if len(c2):
            j2 = int(c2[0])
            sy_rz, sy_e_rz = float(sig[j2]), float(e_rz[j2])

    # ---- how much of the crosshead's travel actually reached the gauge
    #
    # Measured against NOMINAL travel (speed x time), because the .daq carries no crosshead
    # channel. If their crosshead ever lagged its command the true travel is smaller and this
    # share is an UNDER-estimate; on a screw-driven machine at 2 mm/min that lag is negligible.
    i_ef = int(np.argmax(e_on_f))
    travel = (SPEED_MM_MIN / 60.0) * (float(t_f[i_ef]) - t_pre)
    stretch = (float(e_rz[i_ef]) / 100.0) * GAUGE_MM
    share_total = float(stretch / travel * 100.0) if travel > 0 else float("nan")

    out = dict(
        t_f=t_f, f=f, sig=sig, e_on_f=e_on_f, e_rz=e_rz,
        t_e=t_e, e=e, gauge=g,
        area=AREA_MM2, gauge_mm=GAUGE_MM,
        speed_mm_min=SPEED_MM_MIN, speed_mm_s=SPEED_MM_MIN / 60.0, preload=PRELOAD_N,
        uts=uts, uts_e=uts_e, t_peak=t_pk,
        E=E, E_R2=ss, E_window=E_WINDOW,
        sy=sy, sy_e=sy_e,
        # Failure strain is the MAXIMUM reached inside the pull, and the fracture stress is the
        # stress at that same instant. The last sample before the load drop can already sit on the
        # tearing shoulder, where strain has begun to release while the load is still falling.
        ef=float(e_on_f.max()), sigf=float(sig[int(np.argmax(e_on_f))]),
        t_ef=float(t_f[int(np.argmax(e_on_f))]), t_fr=t_fr,
        # the same landmarks on our convention: strain re-zeroed at their 300 N preload
        t_pre=t_pre, e_pre=e_pre, i_pre=i_pre,
        E_rz=E_rz, E_R2_rz=ss2, sy_rz=sy_rz, sy_e_rz=sy_e_rz,
        uts_e_rz=float(e_rz[i_pk]), ef_rz=float(e_rz[i_ef]),
        share_total=share_total, travel=travel, stretch=stretch,
        peak_N=float(f[i_pk]),
        gauge_reported=float(np.nanmedian(g)),
        n_load=int(len(t_f)), n_strain=int(len(t_e)),
        dur=float(t_f[-1] - t_f[0]),
        rate_hz=float((len(t_f) - 1) / (t_f[-1] - t_f[0])),
    )
    # mean strain rate over the elastic ramp, for the like-for-like note against our 0.10 mm/s
    ramp = e_on_f <= 1.0
    if ramp.sum() > 10:
        out["strain_rate"] = float(np.polyfit(t_f[ramp], e_on_f[ramp] / 100.0, 1)[0])
    else:
        out["strain_rate"] = float("nan")

    _cache.update(out)
    return out


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    d = load()
    print("MOT session 2 — XT-205, 45 mm gauge")
    print("  files      : %s + %s" % (os.path.basename(CSV), os.path.basename(DAQ)))
    print("  conditions : %.0f mm/min (%.4f mm/s), %.0f N preload, gauge reported %.4f mm"
          % (d["speed_mm_min"], d["speed_mm_s"], d["preload"], d["gauge_reported"]))
    print("  record     : %d load rows, %d strain rows, %.2f s, %.2f Hz"
          % (d["n_load"], d["n_strain"], d["dur"], d["rate_hz"]))
    print()
    print("  UTS        : %.2f MPa  (%.0f N) at %.2f %% strain, t = %.1f s"
          % (d["uts"], d["peak_N"], d["uts_e"], d["t_peak"]))
    print("  sigma_y    : %.2f MPa at %.2f %% (0.2 %% offset)" % (d["sy"], d["sy_e"]))
    print("  E          : %.3f GPa  (R2 %.4f, %.2f-%.2f %% window)"
          % (d["E"], d["E_R2"], d["E_window"][0], d["E_window"][1]))
    print("  fracture   : %.2f %% strain at %.2f MPa, t = %.1f s"
          % (d["ef"], d["sigf"], d["t_fr"]))
    print("  strain rate: %.2e /s over the elastic ramp" % d["strain_rate"])
    print()
    print("  their strain zero is at ZERO LOAD: %.0f N is reached at t = %.2f s, by which point"
          % (d["preload"], d["t_pre"]))
    print("  the extensometer already reads %.4f %% — that toe is inside every number above."
          % d["e_pre"])
    print("  re-zeroed at %.0f N, on OUR convention:" % d["preload"])
    print("    E        : %.3f GPa  (R2 %.4f)   was %.3f" % (d["E_rz"], d["E_R2_rz"], d["E"]))
    print("    sigma_y  : %.2f MPa at %.2f %%      was %.2f MPa at %.2f %%"
          % (d["sy_rz"], d["sy_e_rz"], d["sy"], d["sy_e"]))
    print("    UTS eps  : %.2f %%                  was %.2f %%" % (d["uts_e_rz"], d["uts_e"]))
    print("    fracture : %.2f %%                  was %.2f %%" % (d["ef_rz"], d["ef"]))
    print("  gauge share: %.1f %% of crosshead travel reached the gauge "
          "(%.3f mm of %.3f mm)" % (d["share_total"], d["stretch"], d["travel"]))
