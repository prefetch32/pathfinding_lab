#!/usr/bin/env python3
"""
main.py -- CUA VAO DUY NHAT cua du an. Chay tu bat ky dau cung duoc.

Cach dung:
  python main.py list                  liet ke tat ca case
  python main.py V1-C2                 chay mot case, in ban do + bang so sanh
  python main.py V1-C2 --gif           ... va xuat 2 GIF (A* va GBFS + closed)
  python main.py V1 --gif              chay tat ca case thuoc V1
  python main.py V1 --summary          chi in bang tong hop
  python main.py V1-C2 --paths         in them duong di va nut mo rong dang ASCII
  (moi case xuat 3 GIF: A*, GBFS goc, GBFS + closed khi dung --gif)
  python main.py all --summary         chay moi case trong du an
  python main.py selftest V2 --n 300   kiem thu ngau nhien: A2 co khop oracle khong
"""
import argparse
import importlib
import os
import pkgutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)   # de import duoc algos, envs, utils, cases... tu moi noi

import cases                                   # noqa: E402
from cases import runner                       # noqa: E402
from utils import format_table                 # noqa: E402


def discover_cases():
    """Quet thu muc cases/, lay moi module co bien CASE. Tra ve dict {id: CASE}."""
    found = {}
    for info in pkgutil.iter_modules(cases.__path__):
        if info.name == "runner":
            continue
        mod = importlib.import_module("cases." + info.name)
        if hasattr(mod, "CASE"):
            found[mod.CASE["id"]] = mod.CASE
    return dict(sorted(found.items()))


def select(found, target):
    """'all' -> tat ca; 'V1' -> moi case nhom V1; 'V1-C2' -> dung case do."""
    if target.lower() == "all":
        return list(found.values())
    t = target.upper()
    return [c for cid, c in found.items()
            if cid.upper() == t or cid.split("-")[0].upper() == t]


def main(argv=None):
    p = argparse.ArgumentParser(description="Chay case tim duong: A* va GBFS.")
    p.add_argument("target", help="list | all | V1 | V1-C2 | selftest ...")
    p.add_argument("extra", nargs="?", default="V2", help="(selftest) phien ban can kiem thu")
    p.add_argument("--n", type=int, default=300, help="(selftest) so map ngau nhien")
    p.add_argument("--seed", type=int, default=1, help="(selftest) hat giong ngau nhien")
    p.add_argument("--gif", action="store_true", help="xuat 3 GIF (A*, GBFS goc, GBFS + closed)")
    p.add_argument("--k", type=float, default=None, help="(V2) ghi de he so K tu dong lenh")
    p.add_argument("--tag", default="", help="nhan them vao ten file GIF, vd k0 -> v2_c8__A2_k0.gif")
    p.add_argument("--paths", action="store_true", help="in duong di va nut mo rong")
    p.add_argument("--summary", action="store_true", help="chi in bang tong hop")
    args = p.parse_args(argv)

    if args.target.lower() == "selftest":
        import selftest
        return selftest.run(args.extra.upper(), args.n, args.seed)

    found = discover_cases()
    if args.target.lower() == "list":
        for cid, c in found.items():
            print("%-8s %s" % (cid, c["title"]))
        return 0

    chosen = select(found, args.target)
    if not chosen:
        print("Khong tim thay case '%s'. Chay 'python main.py list' de xem danh sach." % args.target)
        return 1

    gif_dir = os.path.join(ROOT, "output_gifs")
    want_gif = args.gif
    summary = []
    for case in chosen:
        if args.k is not None and "params" in case:
            case = dict(case, params=dict(case["params"], K=args.k))
        out = runner.run_case(case, show_paths=args.paths, quiet=args.summary)
        if want_gif:
            runner.make_gifs(case, out, gif_dir, tag=args.tag)
        if "twin" in case:
            runner.twin_check(case, replace=case["twin"])
        if "k_sweep" in case:
            runner.k_sweep(case)
        short = {"FOUND": None, "CAP_REACHED": "CAP", "NO_PATH": "NO"}
        opt = out["optimal"]
        row = [case["id"], "%g" % opt if opt is not None else "none"]
        for r in out["rows"]:
            tag = short[r[1]] if short[r[1]] else r[2]
            row.append("%s/%s" % (tag, r[4]))
        summary.append((runner.version_of(case), row))

    if len(chosen) > 1 or args.summary:
        for ver in sorted({v for v, _ in summary}):
            labels = [label for label, _ in runner.ALGOS[ver]]
            rows = [r for v, r in summary if v == ver]
            print("\n" + "=" * 78)
            print("TONG HOP %s  (o = chi phi/so nut mo rong; NO = khong co duong; CAP = cham tran)" % ver)
            print(format_table(["Case", "Toi uu"] + labels, rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
