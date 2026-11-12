"""
algos.py -- CAC THUAT TOAN tim duong (chuan -> cai bien).

Moi thuat toan trong file nay deu la MOT KHUNG DUY NHAT: best_first_search.
Cac thuat toan chi khac nhau o 3 "nut vặn":
    evaluate        : ham danh gia f(g, h)           -> A hay B hay UCS
    revisit_policy  : cach xu ly trang thai gap lai  -> none / first / better_g
    h               : heuristic (V2, V3 se thay bang heuristic cai bien)

Khung 5 buoc (lap lai o moi vong):
    1. Lay nut co key nho nhat ra khoi frontier
    2. Bo qua neu la ban ghi cu (stale)
    3. Goal test
    4. Mo rong: sinh cac nut con qua env.successors
    5. Loc nut con theo revisit_policy roi day vao frontier

Ky hieu (dong bo voi slide):
    A(n) = g(n) + h(n)       -- ham danh gia cua A*
    B(n) = h(n)              -- ham danh gia cua GBFS
    A1, B1  : thuat toan o V1 (khoa closed set THEO O)
    A2, B2  : thuat toan cai bien V2 (khoa theo TRANG THAI DAY DU (x, b, f), h_relaxed)
    A3, B3  : (se them) V3

Muc luc
  1. Node, SearchResult
  2. Ham danh gia  evaluate_A / evaluate_B / evaluate_UCS
  3. Khung chung   best_first_search
  4. Thuat toan V1 astar_standard, gbfs_standard, gbfs_closed, ucs_oracle
  5. Thuat toan V2  A1, B1 (nhin V1 tren bai V2), A2, B2 (cai bien V2) + bien the h
  6. (V3) cai bien -- them o day
"""

from utils import (PriorityQueue, reconstruct_path, h_manhattan, h_damage,
                   h_relaxed, h_zero)

# ======================================================================
# 1. Node, SearchResult
# ======================================================================
class Node:
    """Mot nut tim kiem: trang thai + cach den do."""

    __slots__ = ("state", "parent", "action", "g", "h")

    def __init__(self, state, parent, action, g, h):
        self.state = state
        self.parent = parent
        self.action = action
        self.g = g
        self.h = h


class SearchResult:
    """Ket qua mot lan chay. 'trace' la du lieu cho visualizer sau nay."""

    FOUND = "FOUND"
    NO_PATH = "NO_PATH"            # frontier rong: chung minh khong co duong
    CAP_REACHED = "CAP_REACHED"    # cham tran mo rong: nghi ngo lap vo han

    def __init__(self, algo_name, status, states, actions, cost,
                 expansions, peak_frontier, trace):
        self.algo_name = algo_name
        self.status = status
        self.states = states            # list state tu start den goal (hoac None)
        self.actions = actions
        self.cost = cost                # tong chi phi (hoac None)
        self.expansions = expansions    # so lan mo rong nut
        self.peak_frontier = peak_frontier
        self.trace = trace              # list (state, g, h) theo thu tu mo rong
        # --- cac truong duoc dien them sau khi chay, cho visualizer ---
        self.pushed = []                # pushed[k] = list (state, g, h) cac nut con day vao frontier o lan mo rong k
        self.revisit_policy = None
        self.evaluate = None            # ham f(g, h) cua thuat toan nay

    def expanded_states(self):
        return [t[0] for t in self.trace]


# ======================================================================
# 2. Ham danh gia f
# ======================================================================
def evaluate_A(g, h):
    """f_A = g + h  (A*)."""
    return g + h


def evaluate_B(g, h):
    """f_B = h  (GBFS)."""
    return h


def evaluate_UCS(g, h):
    """f = g  (Dijkstra / UCS) -- dung lam oracle."""
    return g


# ======================================================================
# 3. Khung chung
# ======================================================================
REVISIT_NONE = "none"          # khong nho gi: tree search (GBFS goc)
REVISIT_FIRST = "first"        # moi state chi duoc day vao 1 lan (closed set)
REVISIT_BETTER_G = "better_g"  # day lai neu tim duoc g nho hon (A*, UCS)


def default_cap(env):
    """Tran mo rong mac dinh: du rong de thuat toan dung cham, du nho de bat lap vo han."""
    return 20 * len(env.states()) + 100


def identity_key(state):
    """Khoa closed set mac dinh: chinh trang thai day du."""
    return state


def best_first_search(env, h, evaluate, revisit_policy, algo_name,
                      max_expansions=None, key=None):
    """key(state) -> khoa dung cho closed set. Mac dinh: trang thai day du.

    A1, B1 truyen key = env.position (chi nho O): day la 'cach nhin V1'.
    """
    if max_expansions is None:
        max_expansions = default_cap(env)
    key = key or identity_key

    start = env.initial_state()
    frontier = PriorityQueue()
    counter = 0                     # tie-break cuoi: vao truoc ra truoc (FIFO)
    start_node = Node(start, None, None, 0, h(start))
    frontier.push((evaluate(0, start_node.h), start_node.h, counter), start_node)

    best_g = {key(start): 0}        # dung cho better_g
    reached = {key(start)}          # dung cho first
    expansions, peak, trace = 0, 1, []
    pushed_log = []

    def finish(status, node=None):
        if node is None:
            res = SearchResult(algo_name, status, None, None, None,
                               expansions, peak, trace)
        else:
            states, actions = reconstruct_path(node)
            res = SearchResult(algo_name, status, states, actions, node.g,
                               expansions, peak, trace)
        res.pushed = pushed_log
        res.revisit_policy = revisit_policy
        res.evaluate = evaluate
        return res

    while not frontier.is_empty():
        # --- Buoc 1: lay nut co key nho nhat ---
        _key, node = frontier.pop()
        s = node.state

        # --- Buoc 2: bo ban ghi cu (chi co y nghia voi better_g) ---
        if revisit_policy == REVISIT_BETTER_G and node.g > best_g[key(s)]:
            continue

        # --- Buoc 3: goal test ---
        if env.is_goal(s):
            return finish(SearchResult.FOUND, node)
        if expansions >= max_expansions:
            return finish(SearchResult.CAP_REACHED)

        # --- Buoc 4: mo rong ---
        expansions += 1
        trace.append((s, node.g, node.h))
        pushed_now = []
        for action, s2, cost in env.successors(s):
            g2 = node.g + cost

            # --- Buoc 5: loc theo revisit_policy ---
            k2 = key(s2)
            if revisit_policy == REVISIT_FIRST:
                if k2 in reached:
                    continue
                reached.add(k2)
            elif revisit_policy == REVISIT_BETTER_G:
                if g2 >= best_g.get(k2, float("inf")):
                    continue
                best_g[k2] = g2
            # REVISIT_NONE: khong loc gi

            h2 = h(s2)
            counter += 1
            child = Node(s2, node, action, g2, h2)
            frontier.push((evaluate(g2, h2), h2, counter), child)
            pushed_now.append((s2, g2, h2))
        pushed_log.append(pushed_now)
        peak = max(peak, len(frontier))

    return finish(SearchResult.NO_PATH)


# ======================================================================
# 4. Thuat toan V1
# ======================================================================
def astar_standard(env, h=None, max_expansions=None):
    """A* chuan: f_A = g + h, day lai khi tim duoc g tot hon."""
    h = h or h_manhattan(env)
    return best_first_search(env, h, evaluate_A, REVISIT_BETTER_G,
                             "A* standard", max_expansions)


def gbfs_standard(env, h=None, max_expansions=None):
    """GBFS chuan (tree search): f_B = h, KHONG co closed set -> co the lap vo han."""
    h = h or h_manhattan(env)
    return best_first_search(env, h, evaluate_B, REVISIT_NONE,
                             "GBFS standard", max_expansions)


def gbfs_closed(env, h=None, max_expansions=None):
    """GBFS cai bien V1: f_B = h, them closed set -> day du (complete), khong toi uu."""
    h = h or h_manhattan(env)
    return best_first_search(env, h, evaluate_B, REVISIT_FIRST,
                             "GBFS + closed", max_expansions)


def ucs_oracle(env, max_expansions=None):
    """Dijkstra/UCS tren TRANG THAI DAY DU: luon toi uu -- lam chuan so sanh."""
    return best_first_search(env, h_zero(env), evaluate_UCS, REVISIT_BETTER_G,
                             "UCS (oracle)", max_expansions)


# ======================================================================
# 5. V2
#    A1, B1 = thuat toan V1 chay tren bai V2: closed set chi nho O (key = env.position).
#             Chung khong thay mau b va pha f nen co the mat nghiem / mat toi uu.
#    A2, B2 = cai bien V2: closed set khoa theo (x, b, f) va dung h_relaxed.
#    Cac bien the h_* chi de lam thi nghiem cat bo (ablation).
# ======================================================================
def A1(env, h=None, max_expansions=None):
    """A* V1 tren bai V2: key = o."""
    h = h or h_manhattan(env)
    return best_first_search(env, h, evaluate_A, REVISIT_BETTER_G, "A1",
                             max_expansions, key=env.position)


def B1(env, h=None, max_expansions=None):
    """GBFS + closed V1 tren bai V2: key = o."""
    h = h or h_manhattan(env)
    return best_first_search(env, h, evaluate_B, REVISIT_FIRST, "B1",
                             max_expansions, key=env.position)


def A2(env, h=None, max_expansions=None, name="A2"):
    """A* cai bien V2: key = trang thai day du, h = h_relaxed (mac dinh)."""
    h = h or h_relaxed(env)
    return best_first_search(env, h, evaluate_A, REVISIT_BETTER_G, name, max_expansions)


def B2(env, h=None, max_expansions=None, name="B2"):
    """GBFS cai bien V2: key = trang thai day du, h = h_relaxed (mac dinh)."""
    h = h or h_relaxed(env)
    return best_first_search(env, h, evaluate_B, REVISIT_FIRST, name, max_expansions)


def A2_manhattan(env, max_expansions=None):
    """Thi nghiem cat bo: A2 nhung h = Manhattan (chi sua trang thai, chua sua h)."""
    return A2(env, h_manhattan(env), max_expansions, name="A2 (h=Manhattan)")


def A2_damage(env, max_expansions=None):
    """Thi nghiem cat bo: A2 voi h = M + K*D*."""
    return A2(env, h_damage(env), max_expansions, name="A2 (h=damage)")


# ======================================================================
# 6. (V3): them A3, B3 theo mau A2, B2 o day
# ======================================================================


# ======================================================================
# 6. Bang tra cuu
# ======================================================================
ALGORITHMS = {
    "A_standard": astar_standard,
    "B_standard": gbfs_standard,
    "B_closed": gbfs_closed,
    "UCS_oracle": ucs_oracle,
    "A1": A1, "B1": B1, "A2": A2, "B2": B2,
}
