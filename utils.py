"""
utils.py -- Cac ham / cau truc du lieu DUNG CHUNG cho moi file khac.

Nguyen tac: file nay KHONG biet gi ve luat cua tung bai (V1, V2, V3).
No chi lam viec qua giao dien cua env (xem envs.SearchEnv).

Muc luc
  1. PriorityQueue      -- binary heap viet tay (khong dung heapq)
  2. Khoang cach        -- manhattan
  3. Heuristic factory  -- h_zero, h_manhattan, h_damage, h_relaxed (V3 them o day)
  4. Duong di           -- reconstruct_path, path_cost
  5. Phan tich heuristic-- reverse_dijkstra, check_heuristic
  6. Hien thi           -- render_ascii, format_table

Quy uoc chung:
  state  : tuple hashable. V1 la (r, c).
  action : chuoi, V1 la "U", "D", "L", "R" (viet hoa de khong nham voi r = row).
  h      : ham h(state) -> so >= 0.
"""

INF = float("inf")


# ======================================================================
# 1. PriorityQueue (binary min-heap viet tay)
# ======================================================================
class PriorityQueue:
    """Hang doi uu tien: phan tu co key NHO NHAT ra truoc.

    key la tuple, vd (f, h, counter). So sanh tuple theo thu tu tu dien,
    nen cac so sanh hoa (tie-break) duoc quyet dinh boi cac phan tu sau f.
    """

    def __init__(self):
        self._heap = []  # moi phan tu: (key, item)

    def __len__(self):
        return len(self._heap)

    def is_empty(self):
        return len(self._heap) == 0

    def push(self, key, item):
        self._heap.append((key, item))
        self._sift_up(len(self._heap) - 1)

    def pop(self):
        """Lay ra (key, item) co key nho nhat."""
        heap = self._heap
        top = heap[0]
        last = heap.pop()
        if heap:
            heap[0] = last
            self._sift_down(0)
        return top

    def _sift_up(self, i):
        heap = self._heap
        while i > 0:
            parent = (i - 1) // 2
            if heap[i][0] < heap[parent][0]:
                heap[i], heap[parent] = heap[parent], heap[i]
                i = parent
            else:
                break

    def _sift_down(self, i):
        heap = self._heap
        n = len(heap)
        while True:
            left, right, smallest = 2 * i + 1, 2 * i + 2, i
            if left < n and heap[left][0] < heap[smallest][0]:
                smallest = left
            if right < n and heap[right][0] < heap[smallest][0]:
                smallest = right
            if smallest == i:
                break
            heap[i], heap[smallest] = heap[smallest], heap[i]
            i = smallest


# ======================================================================
# 2. Khoang cach
# ======================================================================
def manhattan(a, b):
    """Khoang cach Manhattan giua hai o (r, c)."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ======================================================================
# 3. Heuristic factory: moi ham nhan env, tra ve h(state)
# ======================================================================
def h_zero(env):
    """h = 0 (bien A thanh UCS/Dijkstra)."""
    return lambda s: 0


def h_manhattan(env):
    """h = Manhattan tu o hien tai toi o dich. V1 va moc so sanh cho V2."""
    goal = env.goal_position()
    return lambda s: manhattan(env.position(s), goal)


def h_damage(env):
    """h = M(x) + K * D*(x)   (V2).

    D*(x) = tong sat thuong TOI THIEU tu o x den dich, tinh bang MOT lan
    Dijkstra nguoc tren luoi tinh, voi chi phi buoc vao mot o = sat thuong NHO NHAT
    cua o do qua moi pha. Admissible va consistent vi hai thanh phan chi phi
    (1 moi luot, K * sat thuong) duoc uoc luong rieng, moi thanh phan consistent.
    """
    goal = env.goal_position()
    K = env.K
    dist = {goal: 0}
    pq = PriorityQueue()
    counter = 0
    pq.push((0, counter), goal)
    done = set()
    while not pq.is_empty():
        (d, _c), x = pq.pop()
        if x in done:
            continue
        done.add(x)
        step = env.min_damage(x)          # chi phi de BUOC VAO x
        for y in env.neighbors(x):
            nd = d + step
            if nd < dist.get(y, INF):
                dist[y] = nd
                counter += 1
                pq.push((nd, counter), y)

    def h(s):
        x = env.position(s)
        dstar = dist.get(x, INF)
        if dstar == INF:
            return INF
        return manhattan(x, goal) + (K * dstar if K else 0)

    return h


def h_relaxed(env):
    """h = khoang cach CHINH XAC trong do thi THU GIAN (V2: bo mau b, giu o va pha).

    env.relaxation() cho do thi thu gian G' co cung chi phi canh nhung it rang buoc hon.
    Theo bo de thu gian: h = h*_{G'} luon admissible va consistent.
    """
    rel = env.relaxation()
    if rel is None:
        raise ValueError("env nay khong cung cap relaxation()")
    nodes, succ, goals, project = rel["nodes"], rel["successors"], rel["goals"], rel["project"]
    rev = {n: [] for n in nodes}
    for n in nodes:
        for n2, c in succ(n):
            rev[n2].append((n, c))
    dist = {}
    pq = PriorityQueue()
    counter = 0
    for g in goals:
        dist[g] = 0
        pq.push((0, counter), g)
    done = set()
    while not pq.is_empty():
        (d, _c), n = pq.pop()
        if n in done:
            continue
        done.add(n)
        for prev, c in rev[n]:
            nd = d + c
            if nd < dist.get(prev, INF):
                dist[prev] = nd
                counter += 1
                pq.push((nd, counter), prev)
    return lambda s: dist.get(project(s), INF)


# ---- V3: them h_cluster_aware(env) o day ------------------------------


# ======================================================================
# 4. Duong di
# ======================================================================
def reconstruct_path(node):
    """Di nguoc theo node.parent. Tra ve (list state, list action)."""
    states, actions = [], []
    while node is not None:
        states.append(node.state)
        if node.action is not None:
            actions.append(node.action)
        node = node.parent
    states.reverse()
    actions.reverse()
    return states, actions


def path_cost(env, states):
    """Tinh lai chi phi tu danh sach state, DONG THOI kiem tra tinh hop le.

    Moi buoc phai la mot canh co that trong env.successors. Neu khong,
    nem ValueError -- day la bo kiem tra doc lap cho thuat toan.
    """
    total = 0
    for s, s_next in zip(states, states[1:]):
        costs = [c for (_a, nxt, c) in env.successors(s) if nxt == s_next]
        if not costs:
            raise ValueError("Buoc di khong hop le: %s -> %s" % (s, s_next))
        total += min(costs)
    return total


# ======================================================================
# 5. Phan tich heuristic (admissible / consistent)
# ======================================================================
def reverse_dijkstra(env):
    """h*(s) = chi phi toi uu tu s den goal, tinh bang Dijkstra NGUOC tu goal.

    Tra ve dict {state: h*}. State khong co trong dict = khong toi duoc goal.
    """
    dist = {}
    done = set()
    pq = PriorityQueue()
    counter = 0
    for g in env.goal_states():
        dist[g] = 0
        pq.push((0, counter), g)
    while not pq.is_empty():
        (d, _c), s = pq.pop()
        if s in done:
            continue
        done.add(s)
        for prev, cost in env.predecessors(s):
            nd = d + cost
            if nd < dist.get(prev, INF):
                dist[prev] = nd
                counter += 1
                pq.push((nd, counter), prev)
    return dist


def check_heuristic(env, h):
    """Dem so vi pham admissible va consistent cua h tren toan bo env.

    admissible : h(s) <= h*(s)             voi moi s toi duoc goal
    consistent : h(s) <= c(s,a,s') + h(s') voi moi canh (s, a, s')
    Ky vong cho chung minh: ca hai danh sach vi pham deu RONG.
    """
    h_star = reverse_dijkstra(env)
    adm_viol, con_viol = [], []
    for s, hs in h_star.items():
        if h(s) > hs:
            adm_viol.append((s, h(s), hs))
    for s in env.states():
        for (_a, s2, c) in env.successors(s):
            if h(s) > c + h(s2):
                con_viol.append((s, s2, h(s), c + h(s2)))
    return {
        "h_star": h_star,
        "admissible_violations": adm_viol,
        "consistent_violations": con_viol,
        "is_admissible": len(adm_viol) == 0,
        "is_consistent": len(con_viol) == 0,
    }


# ======================================================================
# 6. Hien thi
# ======================================================================
def render_ascii(env, path=None, expanded=None):
    """Ve ban do dang chu. '*' = duong di, 'o' = o da duoc mo rong.

    path / expanded la danh sach O (r, c). Voi V2 hay dung env.position(s) de doi state -> o.
    """
    path_set = set(path) if path else set()
    exp_set = set(expanded) if expanded else set()
    lines = []
    for r in range(env.num_rows):
        row = []
        for c in range(env.num_cols):
            ch = env.describe_cell((r, c))
            if ch not in ("S", "G", "#", "T") and (r, c) in path_set:
                ch = "*"                    # duong di (ke ca khi di qua bay)
            elif ch == "." and (r, c) in exp_set:
                ch = "o"                    # o da mo rong
            row.append(ch)
        lines.append("".join(row))
    return "\n".join(lines)


def format_table(headers, rows):
    """In bang van ban can cot. rows: list cac list gia tri."""
    cells = [[str(x) for x in headers]] + [[str(x) for x in r] for r in rows]
    widths = [max(len(row[i]) for row in cells) for i in range(len(headers))]
    out = []
    for k, row in enumerate(cells):
        out.append("  ".join(row[i].ljust(widths[i]) for i in range(len(headers))))
        if k == 0:
            out.append("  ".join("-" * widths[i] for i in range(len(headers))))
    return "\n".join(out)
