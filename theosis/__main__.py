"""CLI: python -m theosis "câu hỏi"  (cũng là console script `theosis`)."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys

from .config import load_config
from .core import theosis


def main() -> None:
    ap = argparse.ArgumentParser(prog="theosis", description="Theosis council engine")
    ap.add_argument("prompt", nargs="?", help='câu hỏi (bỏ trống để đọc từ stdin)')
    ap.add_argument("--rounds", type=int, default=None, help="số vòng audit (mặc định theo config)")
    ap.add_argument("--budget", type=int, default=None, help="trần token; vượt thì merge sớm")
    ap.add_argument("--router", action="store_true", help="tự định tuyến: model chọn model + chiến lược + vòng")
    ap.add_argument("--mode", choices=["auto", "council", "one"], default="auto",
                    help="auto = council nếu ≥2 model, OneTheosis nếu 1 · one = ép OneTheosis (tự audit → enhance ×3)")
    ap.add_argument("--json", action="store_true", help="in cả trail dạng JSON")
    args = ap.parse_args()

    prompt = args.prompt if args.prompt is not None else sys.stdin.read().strip()
    if not prompt:
        ap.error("cần một câu hỏi")

    slots, aggregator, settings = load_config()
    if args.rounds is not None:
        rounds = args.rounds
    elif args.mode == "one":
        rounds = int(settings.get("one_rounds", 3))
    else:
        rounds = int(settings.get("max_rounds", 2))

    final, trail = asyncio.run(
        theosis(prompt, slots, aggregator, max_rounds=rounds,
                max_tokens_budget=args.budget, use_router=args.router, mode=args.mode)
    )

    if args.json:
        print(json.dumps(trail, ensure_ascii=False, indent=2))
    else:
        print(final)


if __name__ == "__main__":
    main()
