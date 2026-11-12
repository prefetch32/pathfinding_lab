"""
cases/runner.py -- LOGIC CHUNG de chay mot case: so sanh thuat toan, in bang, xuat GIF.

File nay KHONG chua du lieu case. Phien ban bai toan (V1, V2, ...) lay tu tien to cua id
("V2-C3" -> "V2"). Them V3: them vao ENVS, ALGOS, HEURISTICS, GIF_LABELS ben duoi.

Cau truc case:
    CASE = {"id": "V2-C3", "title": ..., "purpose": ..., "expect": ..., "map": [...],
            "params": {"b0": 3, "q": 1, "P": 4, "ON": 2, "K": 1},   # chi V2 tro di
            "twin": ("T", "#"),         # tuy chon: kiem chung song sinh
            "k_sweep": [0, 1, 3]}       # tuy chon: quet he so K (V2)
"""
from algos import (astar_standard, gbfs_standard, gbfs_closed, ucs_oracle, SearchResult,
                   A1, B1, A2, B2, A2_manhattan, A2_damage)
from envs import GridWorldV1, GridWorldV2
from utils import (h_manhattan, h_damage, h_relaxed, check_heuristic, render_ascii,
                   format_table, path_cost)
import visualizer

# ----------------------------------------------------------------------
# Dang ky theo phien ban
# ----------------------------------------------------------------------
L_A_STD = "A  standard (A*)"
L_B_STD = "B  standard (GBFS)"
L_B_CLO = "B  + closed (GBFS cai bien)"
ALGOS_V1 = [(L_A_STD, astar_standard), (L_B_STD, gbfs_standard), (L_B_CLO, gbfs_closed)]

L_A1 = "A1 (A* V1, khoa theo o)"
L_B1 = "B1 (GBFS V1, khoa theo o)"
L_A2 = "A2 (h = relaxed)"
L_A2D = "A2 (h = damage)"
L_A2M = "A2 (h = Manhattan)"
L_B2 = "B2 (h = relaxed)"
ALGOS_V2 = [(L_A1, A1), (L_B1, B1), (L_A2, A2), (L_A2D, A2_damage),
            (L_A2M, A2_manhattan), (L_B2, B2)]

ALGOS = {"V1": ALGOS_V1, "V2": ALGOS_V2}

# Thuat toan nao duoc xuat GIF cho moi phien ban, va ten file
GIF_LABELS = {
    "V1": [L_A_STD, L_B_STD, L_B_CLO],
    "V2": [L_A1, L_B1, L_A2, L_B2],
}
GIF_TAGS = {L_A_STD: "A_standard", L_B_STD: "B_standard", L_B_CLO: "B_closed",
            L_A1: "A1", L_B1: "B1", L_A2: "A2", L_B2: "B2"}

HEURISTICS = {
    "V1": [("Manhattan", h_manhattan)],
    "V2": [("Manhattan", h_manhattan), ("damage", h_damage), ("relaxed", h_relaxed)],
}


def version_of(case):
    return case["id"].split("-")[0].upper()


def make_env(case):
    ver = version_of(case)
    if ver == "V1":
        return GridWorldV1.from_ascii(case["map"], name=case["id"])
    if ver == "V2":
        return GridWorldV2.from_ascii(case["map"], case["params"], name=case["id"])
    raise ValueError("Chua ho tro phien ban %s" % ver)


def _positions(env, states):
    return [env.position(s) for s in states] if states else None


# ----------------------------------------------------------------------
# Chay mot case
# ----------------------------------------------------------------------
def run_case(case, algos=None, show_paths=False, quiet=False):
    """Chay moi thuat toan tren mot case. Tra ve dict {env, optimal, results, rows}."""
    ver = version_of(case)
    algos = algos or ALGOS[ver]
    env = make_env(case)
    oracle = ucs_oracle(env)                 # chi phi toi uu (Dijkstra tren trang thai day du)
    opt = oracle.cost
    has_stats = hasattr(env, "path_damage")

    results, rows = {}, []
    for label, fn in algos:
        res = fn(env)
        extra = []
        if res.status == SearchResult.FOUND:
            assert abs(path_cost(env, res.states) - res.cost) < 1e-9   # kiem tra doc lap
            ratio = "%.2f" % (res.cost / opt) if opt else "-"
            cost = "%g" % res.cost
            if has_stats:
                extra = [len(res.states) - 1, env.count_waits(res.states), env.path_damage(res.states)]
        else:
            ratio, cost = "-", "-"
            if has_stats:
                extra = ["-", "-", "-"]
        results[label] = res
        rows.append([label, res.status, cost, ratio, res.expansions, res.peak_frontier] + extra)

    out = {"env": env, "optimal": opt, "results": results, "rows": rows}
    if quiet:
        return out

    print("=" * 78)
    print("%s | %s" % (case["id"], case["title"]))
    print("Muc dich : %s" % case["purpose"])
    print("Ky vong  : %s" % case["expect"])
    if "params" in case:
        print("Tham so  : %s" % ", ".join("%s=%s" % kv for kv in case["params"].items()))
    print("-" * 78)
    print(render_ascii(env))
    if ver == "V2":
        print("Ky hieu: # tuong  T bay chet ngay  H bay co dinh  0-9 bay chu ki (so = do lech pha)")
    print("-" * 78)
    flags = []
    for name, hf in HEURISTICS[ver]:
        chk = check_heuristic(env, hf(env))
        flags.append("%s adm=%s con=%s" % (name, chk["is_admissible"], chk["is_consistent"]))
    print("Toi uu (UCS oracle): %s" % ("%g" % opt if opt is not None else "khong co duong"))
    print("Heuristic: " + " | ".join(flags))
    headers = ["Thuat toan", "Trang thai", "Chi phi", "Chi phi/Toi uu",
               "So nut mo rong", "Frontier max"]
    if has_stats:
        headers += ["So luot", "So cho", "Mat mau"]
    print(format_table(headers, rows))
    if show_paths:
        for label, res in results.items():
            print("\n[%s] '*' duong di, 'o' o da mo rong" % label)
            print(render_ascii(env, _positions(env, res.states),
                               _positions(env, [t[0] for t in res.trace])))
    return out


# ----------------------------------------------------------------------
# GIF
# ----------------------------------------------------------------------
def make_gifs(case, out, gif_dir, include_b_standard=True, tag=""):
    """Xuat GIF cho mot case da chay. tag (tuy chon) nam o cuoi ten file."""
    labels = GIF_LABELS[version_of(case)]
    paths = visualizer.render_case_gifs(case["id"], out["env"], out["results"],
                                        gif_dir, labels=labels, tags=GIF_TAGS,
                                        suffix=tag)
    for p in paths:
        print("GIF:", p)
    return paths


# ----------------------------------------------------------------------
# Kiem chung bo sung
# ----------------------------------------------------------------------
def twin_check(case, replace=("T", "#")):
    """Thay ky hieu replace[0] bang replace[1] trong map roi chay lai (V1: bay chet ngay == tuong)."""
    algos = ALGOS[version_of(case)]
    twin = dict(case)
    twin["id"] = case["id"] + "-twin"
    twin["map"] = [ln.replace(replace[0], replace[1]) for ln in case["map"]]
    a = run_case(case, algos=algos, quiet=True)
    b = run_case(twin, algos=algos, quiet=True)
    same = True
    print("\nTWIN CHECK (%s -> %s):" % replace)
    for label, _ in algos:
        ra, rb = a["results"][label], b["results"][label]
        ok = (ra.status, ra.cost, ra.expansions) == (rb.status, rb.cost, rb.expansions)
        same = same and ok
        print("  %-30s %s" % (label, "GIONG" if ok else "KHAC"))
    print("=> %s" % ("PASS" if same else "FAIL"))
    return same


def k_sweep(case):
    """V2: quet he so K, in so luot / mat mau / chi phi cua A2 va doi chieu voi oracle."""
    rows = []
    for k in case["k_sweep"]:
        c = dict(case)
        c["params"] = dict(case["params"], K=k)
        env = make_env(c)
        res, oracle = A2(env), ucs_oracle(env)
        if res.status == SearchResult.FOUND:
            rows.append([k, len(res.states) - 1, env.count_waits(res.states),
                         env.path_damage(res.states), "%g" % res.cost, res.expansions,
                         "KHOP" if abs(res.cost - oracle.cost) < 1e-9 else "LECH"])
        else:
            rows.append([k, "-", "-", "-", "-", res.expansions, res.status])
    print("\nQUET HE SO K (A2): K lon -> uu tien it mat mau hon duong ngan")
    print(format_table(["K", "So luot", "So cho", "Mat mau", "Chi phi", "Nut mo rong", "Oracle"], rows))
    return rows
