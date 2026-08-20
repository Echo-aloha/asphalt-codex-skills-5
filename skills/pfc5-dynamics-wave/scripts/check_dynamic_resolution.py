from __future__ import annotations

import argparse
import json


def main() -> int:
    parser = argparse.ArgumentParser(description="Check PFC5 dynamic/wave resolution inputs")
    parser.add_argument("--dimension", type=int, choices=(2, 3), required=True)
    parser.add_argument("--direction", choices=("x", "y", "z"), required=True)
    parser.add_argument("--spacing", type=float, required=True)
    parser.add_argument("--wave-speed", type=float, required=True)
    parser.add_argument("--f-max", type=float, required=True)
    parser.add_argument("--ratio-min", type=float, default=10.0)
    parser.add_argument("--dt", type=float)
    parser.add_argument("--samples-min", type=float, default=20.0)
    args = parser.parse_args()
    if min(args.spacing, args.wave_speed, args.f_max, args.ratio_min) <= 0:
        parser.error("spacing, wave-speed, f-max and ratio-min must be positive")
    errors: list[str] = []
    if args.dimension == 2 and args.direction == "z":
        errors.append("2D models cannot use z as the source direction")
    wavelength = args.wave_speed / args.f_max
    ratio = wavelength / args.spacing
    if ratio < args.ratio_min:
        errors.append(f"wavelength/spacing {ratio:.6g} is below {args.ratio_min:.6g}")
    samples = None
    if args.dt is not None:
        if args.dt <= 0:
            errors.append("dt must be positive")
        else:
            samples = 1.0 / (args.f_max * args.dt)
            if samples < args.samples_min:
                errors.append(f"samples/period {samples:.6g} is below {args.samples_min:.6g}")
    print(json.dumps({
        "ok": not errors,
        "wavelength": wavelength,
        "wavelength_to_spacing": ratio,
        "samples_per_shortest_period": samples,
        "errors": errors,
        "requires_pfc5_runtime_validation": True,
    }, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
