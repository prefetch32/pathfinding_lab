"""
selftest.py -- KIEM THU NGAU NHIEN (differential testing). Chay: python main.py selftest V2 --n 300

Voi moi map ngau nhien, so sanh voi ORACLE (UCS tren trang thai day du, luon toi uu):
  - A2 phai co chi phi BANG oracle (hoac cung bao 'khong co duong')        -> bang chung toi uu
  - B2 phai tim duoc duong khi oracle tim duoc (day du)                     -> bang chung day du
  - 3 heuristic phai admissible va consistent: 0 vi pham                    -> bang chung bo de
  - A1, B1 (nhin V1): dem so lan SAI -- doi chung cho 'vi sao phai cai bien'
"""
import random

from algos import ucs_oracle, A1, B1, A2, B2, A2_manhattan, A2_damage, SearchResult
from envs import GridWorldV2
from utils import h_manhattan, h_damage, h_relaxed, check_heuristic, path_cost, format_table


def random_v2_map(rng, rows, cols):
    grid = [["." for _ in range(cols)] for _ in range(rows)]
    P = rng.randint(2, 5)
    for r in range(rows):
        for c in range(cols):
            x = rng.random()
            if x < 0.14:
                grid[r][c] = "#"
            elif x < 0.18:
                grid[r][c] = "T"
            elif x < 0.30:
                grid[r][c] = "H"
            elif x < 0.45:
                grid[r][c] = str(rng.randrange(P))
    grid[0][0], grid[rows - 1][cols - 1] = "S", "G"
    params = {"b0": rng.randint(2, 6), "q": rng.randint(1, 2), "P": P,
              "ON": rng.randint(1, P), "K": rng.choice([0, 1, 2])}
    return ["".join(row) for row in grid], params


def _wrong(res, opt):
    """Ket qua nay co SAI so voi oracle khong? (mat nghiem hoac chi phi > toi uu)"""
    if opt is None:
        return res.status == SearchResult.FOUND        # bao co duong trong khi khong co: bug
    if res.status != SearchResult.FOUND:
        return True
    return res.cost > opt + 1e-9


def run(version, n, seed):
    if version != "V2":
        print("selftest hien chi ho tro V2")
        return 1
    rng = random.Random(seed)
    stats = {k: 0 for k in ("maps", "has_path", "A2_ok", "A2man_ok", "A2dmg_ok",
                            "B2_complete", "B2_opt", "A1_wrong", "B1_wrong",
                            "h_viol", "invalid_path")}
    for _ in range(n):
        lines, params = random_v2_map(rng, rng.randint(4, 6), rng.randint(5, 7))
        env = GridWorldV2.from_ascii(lines, params)
        oracle = ucs_oracle(env)
        opt = oracle.cost
        stats["maps"] += 1
        stats["has_path"] += opt is not None
        for name, hf in (("man", h_manhattan), ("dmg", h_damage), ("rel", h_relaxed)):
            chk = check_heuristic(env, hf(env))
            stats["h_viol"] += len(chk["admissible_violations"]) + len(chk["consistent_violations"])
        for key, fn in (("A2_ok", A2), ("A2man_ok", A2_manhattan), ("A2dmg_ok", A2_damage)):
            res = fn(env)
            stats[key] += not _wrong(res, opt)
            if res.status == SearchResult.FOUND:
                try:
                    path_cost(env, res.states)
                except ValueError:
                    stats["invalid_path"] += 1
        b2 = B2(env)
        if opt is not None:
            stats["B2_complete"] += b2.status == SearchResult.FOUND
            stats["B2_opt"] += (b2.status == SearchResult.FOUND and b2.cost <= opt + 1e-9)
        else:
            stats["B2_complete"] += b2.status == SearchResult.NO_PATH
            stats["B2_opt"] += b2.status == SearchResult.NO_PATH
        stats["A1_wrong"] += _wrong(A1(env), opt)
        stats["B1_wrong"] += (B1(env).status != SearchResult.FOUND) if opt is not None else 0
    N = stats["maps"]
    rows = [
        ["So map ngau nhien", N, ""],
        ["  trong do co duong (oracle)", stats["has_path"], ""],
        ["A2 chi phi = oracle", "%d/%d" % (stats["A2_ok"], N), "ky vong 100%"],
        ["A2 (h=Manhattan) = oracle", "%d/%d" % (stats["A2man_ok"], N), "ky vong 100%"],
        ["A2 (h=damage) = oracle", "%d/%d" % (stats["A2dmg_ok"], N), "ky vong 100%"],
        ["B2 day du (tim duoc khi co duong)", "%d/%d" % (stats["B2_complete"], N), "ky vong 100%"],
        ["B2 chi phi = toi uu", "%d/%d" % (stats["B2_opt"], N), "KHONG dam bao"],
        ["Vi pham heuristic (3 loai)", stats["h_viol"], "ky vong 0"],
        ["Duong khong hop le", stats["invalid_path"], "ky vong 0"],
        ["A1 (V1) SAI (mat nghiem/mat toi uu)", "%d/%d" % (stats["A1_wrong"], N), "doi chung"],
        ["B1 (V1) mat nghiem", "%d/%d" % (stats["B1_wrong"], N), "doi chung"],
    ]
    print("SELFTEST %s  (n=%d, seed=%d)" % (version, n, seed))
    print(format_table(["Chi so", "Ket qua", "Ghi chu"], rows))
    ok = (stats["A2_ok"] == N and stats["A2man_ok"] == N and stats["A2dmg_ok"] == N
          and stats["B2_complete"] == N and stats["h_viol"] == 0 and stats["invalid_path"] == 0)
    print("=> %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1
