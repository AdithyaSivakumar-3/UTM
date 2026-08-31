"""Why 20.9 px/mm — the field-of-view arithmetic, for our rig and for the XT-205.

The short answer is that px/mm was never chosen as a number. It falls out of the lens, the working
distance and the sensor crop. What WAS chosen is the field of view, and px/mm is what that choice
leaves behind.

The trade is exact and one-for-one: on a given sensor, magnifying more resolves finer strain and
sees less specimen. A tensile test to fracture needs the markers to stay in frame until the
specimen breaks, so the field of view is the binding constraint and the resolution is what is left
over. The XT-205 sits at the other end of that trade, and this module works out what it cost.

Everything here is arithmetic on numbers taken from the rig's own configuration and from the
measurement caches; nothing is typed in twice.
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "Software", "UTM_PyQt6"))

CACHE = os.path.abspath(os.path.join(HERE, "..", "pxmm_reasoning.json"))

# Read the crop from the rig rather than restating it: if the shipped ROI changes, this follows.
from camera_manager import CameraManager as _CM                        # noqa: E402

ROI = list(_CM.ROI)                       # [OffsetX, OffsetY, Width, Height]
AXIS_PX = max(ROI[2], ROI[3])             # the long side is the loading axis
SENSOR_AXIS_PX = 2448                     # acA2440-35um, full width

GAUGE_MM = 80.0
BOX_HALF_OURS = 75                        # what the tab suggests for our ~60 px markers
BOX_HALF_MOT = 105                        # what the XT-205 run actually used
TRAVEL_BACKSTOP_MM = 30.0                 # the rig's own hard travel limit

# The two optical constants. The focal length is the rig's, recorded in README.md ("25 mm lens");
# the pixel pitch is the acA2440's datasheet figure (Sony IMX250, 2448 x 2048 on 8.45 x 7.07 mm)
# and is the ONE number here that was not measured on this rig.
LENS_F_MM = 25.0
PIXEL_PITCH_UM = 3.45


def working_distance(ppm, f_mm=LENS_F_MM, pitch_um=PIXEL_PITCH_UM):
    """Lens-to-specimen distance that produces a given px/mm, for a thin lens.

    px/mm on the specimen is nothing but the optical magnification divided by the pixel pitch:
    one pixel covers pitch/M millimetres of specimen. So M = pitch x px/mm, and the thin-lens
    conjugate relation gives the object distance as f(1 + 1/M).

    Returns (M, object distance, total object-to-sensor distance) in mm. A thin lens is an
    approximation — a real 25 mm lens has a principal-plane separation that shifts these by a
    few millimetres — so the number is a prediction to check with a tape measure, not a spec.
    """
    m = pitch_um * 1e-3 * ppm             # pitch in mm x px per mm = magnification
    obj = f_mm * (1.0 + 1.0 / m)
    return m, obj, obj + f_mm * (1.0 + m)


def _strain_to_edge(frame_px, gauge_px, box_half):
    """Strain at which a marker's tracking box runs out of frame.

    The pair separates about its centre, so each marker takes half the elongation. A box cannot be
    centred closer than half+2 px to the edge — Box.clamp() pins it there — so the usable travel per
    end is the spare space minus that. This is the limit that ENDED the XT-205 run, not a
    theoretical one.
    """
    spare_per_end = (frame_px - gauge_px) / 2.0
    usable = spare_per_end - (box_half + 2)
    return max(0.0, 2.0 * usable / gauge_px)


def build():
    mot = json.load(io.open(os.path.join(HERE, "..", "mot_postproc_compare.json"),
                            encoding="utf-8"))
    est = json.load(io.open(os.path.join(HERE, "..", "estimator_measurements.json"),
                            encoding="utf-8"))

    ours_l0 = est["method"]["S26"]["auto"]["l0"]
    ours_ppm = ours_l0 / GAUGE_MM
    mot_l0 = 2234.4
    mot_frame = 2464
    mot_ppm = mot_l0 / 80.0033

    out = {
        "ours": {
            "frame_px": AXIS_PX, "gauge_px": ours_l0, "ppm": ours_ppm,
            "fov_mm": AXIS_PX / ours_ppm, "box_half": BOX_HALF_OURS,
            "per_px_ue": 1e6 / ours_l0,
            "strain_to_edge": _strain_to_edge(AXIS_PX, ours_l0, BOX_HALF_OURS),
            "strain_to_edge_full_sensor":
                _strain_to_edge(SENSOR_AXIS_PX, ours_l0, BOX_HALF_OURS),
            "noise_ue": est["method"]["S26"]["auto"]["noise_ue"],
        },
        "mot": {
            "frame_px": mot_frame, "gauge_px": mot_l0, "ppm": mot_ppm,
            "fov_mm": mot_frame / mot_ppm, "box_half": BOX_HALF_MOT,
            "per_px_ue": 1e6 / mot_l0,
            "strain_to_edge": _strain_to_edge(mot_frame, mot_l0, BOX_HALF_MOT),
            "noise_ue": next(r["noise_ue"] for r in mot["rows"] if r["key"] == "pp"),
        },
        "travel_backstop_strain": TRAVEL_BACKSTOP_MM / GAUGE_MM,
        "ef_s25": mot.get("gauge_share", {}) and est["accuracy"]["S25"]["ef_pct"] / 100.0,
        "ef_s26": est["accuracy"]["S26"]["ef_pct"] / 100.0,
        "sensor_axis_px": SENSOR_AXIS_PX, "roi": ROI,
    }
    # Sub-pixel factor: how much of the achieved precision is NOT explained by magnification.
    for k in ("ours", "mot"):
        out[k]["subpixel_factor"] = out[k]["per_px_ue"] / out[k]["noise_ue"]

    # Where the number comes from optically, and what it would take to move it. The second entry
    # is the counterfactual: our own camera, our own lens, standing where it would have to stand
    # to match the XT-205's magnification.
    out["optics"] = {"f_mm": LENS_F_MM, "pitch_um": PIXEL_PITCH_UM}
    for k in ("ours", "mot"):
        m, obj, tot = working_distance(out[k]["ppm"])
        out["optics"][k] = {"mag": m, "obj_mm": obj, "total_mm": tot,
                            "um_per_px": 1000.0 / out[k]["ppm"]}
    o = out["optics"]
    o["move_closer_mm"] = o["ours"]["obj_mm"] - o["mot"]["obj_mm"]
    # How much a hand-placement error costs, at our operating point: d(px/mm)/d(WD).
    _, obj_hi, _ = working_distance(out["ours"]["ppm"] + 0.5)
    o["mm_per_half_ppm"] = out["optics"]["ours"]["obj_mm"] - obj_hi

    io.open(CACHE, "w", encoding="utf-8", newline="").write(json.dumps(out, indent=1))
    return out


def load():
    if not os.path.exists(CACHE):
        return build()
    return json.load(io.open(CACHE, encoding="utf-8"))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    d = build()
    print("ROI %s -> %d px along the loading axis" % (d["roi"], d["ours"]["frame_px"]))
    print()
    print("%-28s %12s %12s" % ("", "PPD-UTM", "MOT XT-205"))
    print("-" * 54)
    for lab, key, fmt in (("px per mm", "ppm", "%.2f"),
                          ("gauge, px", "gauge_px", "%.0f"),
                          ("frame, px", "frame_px", "%.0f"),
                          ("field of view, mm", "fov_mm", "%.1f"),
                          ("one pixel, ue", "per_px_ue", "%.0f"),
                          ("box half-size, px", "box_half", "%.0f"),
                          ("achieved noise, ue", "noise_ue", "%.1f"),
                          ("sub-pixel factor", "subpixel_factor", "%.0fx")):
        print("%-28s %12s %12s" % (lab, fmt % d["ours"][key], fmt % d["mot"][key]))
    print("%-28s %11.1f%% %11.2f%%" % ("markers leave frame at",
                                       100 * d["ours"]["strain_to_edge"],
                                       100 * d["mot"]["strain_to_edge"]))
    print()
    print("our travel backstop is %.1f %% strain; the shipped crop lasts to %.1f %%, "
          "the full sensor to %.1f %%"
          % (100 * d["travel_backstop_strain"], 100 * d["ours"]["strain_to_edge"],
             100 * d["ours"]["strain_to_edge_full_sensor"]))
    print("S25 fractured at %.2f %%, S26 at %.2f %% — %.0fx inside the frame limit"
          % (100 * d["ef_s25"], 100 * d["ef_s26"],
             d["ours"]["strain_to_edge"] / d["ef_s26"]))
    o = d["optics"]
    print("\noptics: %.0f mm lens, %.2f um pixels" % (o["f_mm"], o["pitch_um"]))
    for k, name in (("ours", "PPD-UTM"), ("mot", "at the XT-205's px/mm")):
        print("  %-22s M = %.4f  ->  lens %.0f mm from the specimen (%.1f um per px)"
              % (name, o[k]["mag"], o[k]["obj_mm"], o[k]["um_per_px"]))
    print("  the XT-205's magnification is %.0f mm of camera travel away, not new hardware"
          % o["move_closer_mm"])
    print("  and %.0f mm of placement error is worth 0.5 px/mm" % o["mm_per_half_ppm"])
    print("\nwrote %s" % os.path.relpath(CACHE, REPO))
