"""Scratch-only ORACLE GENERATOR used by the mutation proof (case E).

This is a deliberately naive second implementation of the four card formulas,
written from the card text only with integer/float arithmetic instead of Decimal.
Its purpose is to prove that the frozen evidence is REPRODUCIBLE: regenerating the
expected values with an independent (naive) implementation must yield the same
numbers as the frozen oracle.json, and must then be shown to be referenceable.

This file never imports the product either.

Run:
  python -X utf8 -B recovery/selfcheck/naive_oracle.py --card M25
"""

from __future__ import annotations

import argparse
import json


def m25():
    opening, new, retired = 200, 40, 20
    new_frac, ret_lost, attach, per_unit = 0.25, 0.5, 0.5, 3
    assert opening + new - retired == 220
    exposure = opening + new * new_frac - retired * ret_lost
    return [exposure * attach * per_unit]


def m26():
    opening, new, closed = 20, 5, 2
    new_frac, close_lost, productivity, per_mature = 0.4, 0.5, 0.75, 10
    assert opening + new - closed == 23
    mature = opening - closed * close_lost
    newxp = new * new_frac * productivity
    return [(mature + newxp) * per_mature]


def m27():
    mw, hours, cf, curtail = 2, 8760, 0.5, 0.0
    contracted, contract_price, merchant_price, other = 0.5, 40, 20, 1200
    delivered = mw * hours * cf * (1 - curtail)
    blended = contracted * contract_price + (1 - contracted) * merchant_price
    return [delivered * blended + other]


def m28(sign):
    opening, inflows, outflows, market = 1000, 200, 100, -50
    in_frac, out_lost, mkt_frac, fee, perf = 0.25, 0.75, 0.5, 0.01, 2
    assert opening + inflows - outflows + market == 1050
    # sign = +1 : the card's reading of a SIGNED market move (market_change = -50 reduces
    #             the time-weighted base) -> 950 * 0.01 + 2 = 11.5
    # sign = -1 : the mis-signed variant that treats the printed "-50" as a magnitude to
    #             subtract -> 1050 * 0.01 + 2 = 12.5
    average = opening + inflows * in_frac - outflows * out_lost + sign * market * mkt_frac
    return [average * fee + perf]


BUILDERS = {"M25": m25, "M26": m26, "M27": m27, "M28": m28}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(BUILDERS))
    parser.add_argument("--sign", type=int, default=1, choices=(1, -1),
                        help="M28 only: +1 = card reading, -1 = deliberately mis-signed variant")
    args = parser.parse_args()
    values = BUILDERS[args.card](args.sign) if args.card == "M28" else BUILDERS[args.card]()
    print(json.dumps({"card_id": args.card, "sign": args.sign,
                      "naive_positive_expected_float": values}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
