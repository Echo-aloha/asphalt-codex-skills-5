from __future__ import annotations

import argparse
import json


def clamp(value: float, limit: float) -> float:
    return max(-limit, min(limit, value))


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute one bounded PFC5 servo velocity step")
    parser.add_argument("--target", type=float, required=True)
    parser.add_argument("--reaction", type=float, required=True)
    parser.add_argument("--stiffness", type=float, required=True)
    parser.add_argument("--dt", type=float, required=True)
    parser.add_argument("--alpha", type=float, default=0.2)
    parser.add_argument("--vmax", type=float, required=True)
    parser.add_argument("--sign", type=float, choices=(-1.0, 1.0), default=1.0)
    args = parser.parse_args()
    if args.stiffness <= 0 or args.dt <= 0 or args.vmax <= 0:
        parser.error("stiffness, dt and vmax must be positive")
    if not 0 < args.alpha <= 1:
        parser.error("alpha must be in (0, 1]")
    error = args.target - args.reaction
    gain = args.alpha / (args.stiffness * args.dt)
    unclamped = args.sign * gain * error
    velocity = clamp(unclamped, args.vmax)
    print(json.dumps({
        "error": error,
        "gain": gain,
        "velocity_unclamped": unclamped,
        "velocity": velocity,
        "clamped": velocity != unclamped,
        "sign_requires_runtime_probe": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
