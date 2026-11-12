"""
envs.py -- LUAT cua moi truong / the gioi (khong chua thuat toan).

Muc luc
  1. SearchEnv     -- giao dien chung ma algos.py va utils.py dua vao
  2. GridWorldV1   -- bai co ban: tuong + bay chet nguoi, co dinh, chi phi 1
  3. (V2) GridWorldV2 -- them sat thuong, hp, bay chu ki, hanh dong cho
  4. (V3) GridWorldV3 -- them o gop (cum), chi phi noi bo cum = 0

Ky hieu ban do ASCII:  '.' trong  '#' tuong (W)  'T' bay chet nguoi (H)
                       'S' start (X0)            'G' dich (g)
Hanh dong: "U" "D" "L" "R"  (viet hoa de khong nham voi r = row).
"""

# ======================================================================
# 1. Giao dien chung
# ======================================================================
class SearchEnv:
    """Moi bai toan (V1, V2, V3) phai cai dat cac ham duoi day.

    algos.py CHI goi cac ham nay => them bai moi khong phai sua thuat toan.
    """

    name = "env"

    def initial_state(self):
        raise NotImplementedError

    def goal_state(self):
        raise NotImplementedError

    def is_goal(self, state):
        raise NotImplementedError

    def successors(self, state):
        """Tra ve list (action, next_state, cost). Hanh dong khong hop le: khong liet ke."""
        raise NotImplementedError

    def states(self):
        """Moi trang thai ma agent co the dung. Dung de duyet / dat tran an toan."""
        raise NotImplementedError

    # ---- cac ham MAC DINH cho bai ma trang thai chinh la o (V1) -------
    # V2 (state = (o, b, f)) va V3 ghi de cac ham nay.
    def position(self, state):
        """O (r, c) ma trang thai dang dung. V1: chinh la state."""
        return state

    def goal_position(self):
        return self.goal_state()

    def goal_states(self):
        """Tap trang thai dich (V2: dich o bat ky (b, f) nao)."""
        return [self.goal_state()]

    def state_text(self, state):
        """Chu mo ta them cho visualizer (V2: 'B5 F2')."""
        return ""

    def relaxation(self):
        """Do thi THU GIAN dung cho h_relaxed (utils). None = khong co."""
        return None

    def predecessors(self, state):
        """list (prev_state, cost) sao cho prev --cost--> state. Mac dinh: quet toan bo (cham, dung)."""
        out = []
        for p in self.states():
            for (_a, nxt, c) in self.successors(p):
                if nxt == state:
                    out.append((p, c))
        return out


# ======================================================================
# 2. V1: gridworld co ban
# ======================================================================
class GridWorldV1(SearchEnv):
    """Bai co ban.  S = luoi \\ W,  T chan o bay H,  C(s,a,s') = w0 = 1.

    Luu y: ve toan hoc H van thuoc S (cach B), con trong code states() chi tra
    cac o hop le (khong tuong, khong bay) vi bay khong bao gio duoc buoc vao.
    """

    ACTIONS = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
    STEP_COST = 1  # w0

    def __init__(self, num_rows, num_cols, start, goal, walls, traps, name="V1"):
        self.name = name
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.start = start
        self.goal = goal
        self.walls = frozenset(walls)
        self.traps = frozenset(traps)
        self._check_valid()
        self._states = [
            (r, c)
            for r in range(num_rows)
            for c in range(num_cols)
            if (r, c) not in self.walls and (r, c) not in self.traps
        ]

    # ---- kiem tra dau vao ------------------------------------------
    def _check_valid(self):
        for label, cell in (("start", self.start), ("goal", self.goal)):
            if not self.in_bounds(cell):
                raise ValueError("%s ngoai luoi: %s" % (label, cell))
            if cell in self.walls or cell in self.traps:
                raise ValueError("%s nam tren tuong/bay: %s" % (label, cell))

    # ---- tien ich o ------------------------------------------------
    def in_bounds(self, cell):
        return 0 <= cell[0] < self.num_rows and 0 <= cell[1] < self.num_cols

    def describe_cell(self, cell):
        if cell == self.start:
            return "S"
        if cell == self.goal:
            return "G"
        if cell in self.walls:
            return "#"
        if cell in self.traps:
            return "T"
        return "."

    # ---- giao dien SearchEnv ---------------------------------------
    def initial_state(self):
        return self.start

    def goal_state(self):
        return self.goal

    def is_goal(self, state):
        return state == self.goal

    def successors(self, state):
        out = []
        for action, (dr, dc) in self.ACTIONS.items():
            nxt = (state[0] + dr, state[1] + dc)
            if self.in_bounds(nxt) and nxt not in self.walls and nxt not in self.traps:
                out.append((action, nxt, self.STEP_COST))
        return out

    def states(self):
        return list(self._states)

    def predecessors(self, state):
        # V1 doi xung: di duoc s'->s thi di duoc s->s'
        return [(nxt, c) for (_a, nxt, c) in self.successors(state)]

    # ---- tao tu ASCII ----------------------------------------------
    @classmethod
    def from_ascii(cls, lines, name="V1"):
        """Tao env tu list chuoi (moi chuoi la mot hang)."""
        lines = [ln for ln in lines if ln.strip() != ""]
        widths = {len(ln) for ln in lines}
        if len(widths) != 1:
            raise ValueError("Cac hang ban do khong cung do dai: %s" % sorted(widths))
        walls, traps, start, goal = set(), set(), None, None
        for r, ln in enumerate(lines):
            for c, ch in enumerate(ln):
                if ch == "#":
                    walls.add((r, c))
                elif ch == "T":
                    traps.add((r, c))
                elif ch == "S":
                    start = (r, c)
                elif ch == "G":
                    goal = (r, c)
                elif ch != ".":
                    raise ValueError("Ky tu la '%s' tai (%d,%d)" % (ch, r, c))
        if start is None or goal is None:
            raise ValueError("Ban do thieu S hoac G")
        return cls(len(lines), len(lines[0]), start, goal, walls, traps, name)


# ======================================================================
# 3. V2: mau b, bay sat thuong (co dinh / chu ki), hanh dong cho W
# ======================================================================
class GridWorldV2(SearchEnv):
    """Bai mo rong 1.  Ky hieu dong bo voi slide:

        trang thai  s = (x, b, f)   x = o (r, c), b = mau, f = pha = t mod P
        hanh dong   U D L R W       (W = cho tai cho)
        mau         b0 ban dau; b' = b - p(x', f');  hop le khi b' >= 1
        sat thuong  p(x, f) = q neu bay o x dang bat tai pha f, nguoc lai 0
        bay chu ki  bat khi (f - o_x) mod P < ON   (o_x = do lech pha cua bay x)
        bay co dinh la truong hop ON = P (luon bat)
        chi phi     C = 1 + K * p(x', f')     (K >= 0: he so quy doi mau -> chi phi)
        pha         f' = (f + 1) mod P  sau MOI luot (di hay cho)

    Ban do ASCII:  '.' trong  '#' tuong (W)  'T' bay chet ngay (E, khong di qua)
                   'H' bay sat thuong co dinh      '0'..'9' bay chu ki, chu so = do lech pha o_x
                   'S' start  'G' dich
    Quy uoc: dung o start luc t = 0 khong tinh sat thuong.
    """

    ACTIONS = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1), "W": (0, 0)}
    HAS_PHASES = True   # visualizer dung de bat che do replay

    def __init__(self, num_rows, num_cols, start, goal, walls, death_traps,
                 static_traps, periodic_traps, b0, q, P, ON, K, name="V2"):
        self.name = name
        self.num_rows, self.num_cols = num_rows, num_cols
        self.start, self.goal = start, goal
        self.walls = frozenset(walls)
        self.death_traps = frozenset(death_traps)
        self.static_traps = frozenset(static_traps)
        self.periodic_traps = dict(periodic_traps)       # {o: do_lech_pha}
        self.b0, self.q, self.P, self.ON, self.K = b0, q, P, ON, K
        self._check_valid()
        self._cells = [(r, c) for r in range(num_rows) for c in range(num_cols)
                       if (r, c) not in self.walls and (r, c) not in self.death_traps]
        self._states = [(x, b, f) for x in self._cells
                        for b in range(1, b0 + 1) for f in range(P)]

    def _check_valid(self):
        if not (isinstance(self.b0, int) and self.b0 >= 1):
            raise ValueError("b0 phai la so nguyen >= 1")
        if not (isinstance(self.q, int) and self.q >= 1):
            raise ValueError("q phai la so nguyen >= 1")
        if not (isinstance(self.P, int) and self.P >= 1):
            raise ValueError("P phai la so nguyen >= 1")
        if not (isinstance(self.ON, int) and 1 <= self.ON <= self.P):
            raise ValueError("ON phai thoa 1 <= ON <= P")
        if self.K < 0:
            raise ValueError("K phai >= 0")
        for x, off in self.periodic_traps.items():
            if not (0 <= off < self.P):
                raise ValueError("do lech pha %s tai %s phai thuoc [0, P)" % (off, x))
        for label, cell in (("start", self.start), ("goal", self.goal)):
            if not self.in_bounds(cell):
                raise ValueError("%s ngoai luoi: %s" % (label, cell))
            if (cell in self.walls or cell in self.death_traps
                    or cell in self.static_traps or cell in self.periodic_traps):
                raise ValueError("%s phai nam tren o thuong: %s" % (label, cell))

    # ---- tien ich o ------------------------------------------------
    def in_bounds(self, cell):
        return 0 <= cell[0] < self.num_rows and 0 <= cell[1] < self.num_cols

    def passable(self, cell):
        return self.in_bounds(cell) and cell not in self.walls and cell not in self.death_traps

    def neighbors(self, cell):
        """Cac o ke di duoc (khong tinh cho)."""
        out = []
        for a, (dr, dc) in self.ACTIONS.items():
            if a == "W":
                continue
            nxt = (cell[0] + dr, cell[1] + dc)
            if self.passable(nxt):
                out.append(nxt)
        return out

    def trap_on(self, cell, f):
        """Bay tai o dang bat o pha f?"""
        if cell in self.static_traps:
            return True
        off = self.periodic_traps.get(cell)
        return off is not None and (f - off) % self.P < self.ON

    def damage(self, cell, f):
        """Ham sat thuong p(x, f)."""
        return self.q if self.trap_on(cell, f) else 0

    def min_damage(self, cell):
        """Sat thuong NHO NHAT o o nay qua moi pha (can duoi, dung cho h_damage)."""
        if cell in self.static_traps:
            return self.q
        if cell in self.periodic_traps:
            return self.q if self.ON == self.P else 0
        return 0

    def describe_cell(self, cell):
        if cell == self.start:
            return "S"
        if cell == self.goal:
            return "G"
        if cell in self.walls:
            return "#"
        if cell in self.death_traps:
            return "T"
        if cell in self.static_traps:
            return "H"
        if cell in self.periodic_traps:
            return str(self.periodic_traps[cell])
        return "."

    # ---- giao dien SearchEnv ---------------------------------------
    def initial_state(self):
        return (self.start, self.b0, 0)

    def goal_state(self):
        return (self.goal, self.b0, 0)       # chi dai dien; dich that la goal_states()

    def goal_position(self):
        return self.goal

    def goal_states(self):
        return [(self.goal, b, f) for b in range(1, self.b0 + 1) for f in range(self.P)]

    def is_goal(self, state):
        return state[0] == self.goal

    def position(self, state):
        return state[0]

    def state_text(self, state):
        return "B%d F%d" % (state[1], state[2])

    def successors(self, state):
        x, b, f = state
        f2 = (f + 1) % self.P
        out = []
        for action, (dr, dc) in self.ACTIONS.items():
            x2 = (x[0] + dr, x[1] + dc)
            if not self.passable(x2):
                continue
            d = self.damage(x2, f2)
            b2 = b - d
            if b2 < 1:
                continue                      # chet: luot nay khong hop le
            out.append((action, (x2, b2, f2), 1 + self.K * d))
        return out

    def predecessors(self, state):
        """Nguoc cua successors, tinh truc tiep (nhanh hon quet toan bo)."""
        x2, b2, f2 = state
        f = (f2 - 1) % self.P
        d = self.damage(x2, f2)
        b = b2 + d
        if b > self.b0:
            return []
        out = []
        for action, (dr, dc) in self.ACTIONS.items():
            x = (x2[0] - dr, x2[1] - dc)
            if self.passable(x):
                out.append(((x, b, f), 1 + self.K * d))
        return out

    def states(self):
        return list(self._states)

    # ---- do thi thu gian: bo mau b, giu nguyen o, pha, chi phi ------
    def relaxation(self):
        nodes = [(x, f) for x in self._cells for f in range(self.P)]

        def succ(node):
            x, f = node
            f2 = (f + 1) % self.P
            out = []
            for a, (dr, dc) in self.ACTIONS.items():
                x2 = (x[0] + dr, x[1] + dc)
                if self.passable(x2):
                    out.append(((x2, f2), 1 + self.K * self.damage(x2, f2)))
            return out

        return {
            "nodes": nodes,
            "successors": succ,
            "goals": [(self.goal, f) for f in range(self.P)],
            "project": lambda s: (s[0], s[2]),
        }

    # ---- thong ke duong di -----------------------------------------
    def path_damage(self, states):
        """Tong mau mat doc theo duong (b dau - b cuoi)."""
        return states[0][1] - states[-1][1]

    def count_waits(self, states):
        return sum(1 for a, b2 in zip(states, states[1:]) if a[0] == b2[0])

    # ---- tao tu ASCII ----------------------------------------------
    @classmethod
    def from_ascii(cls, lines, params, name="V2"):
        """params: dict gom b0, q, P, ON, K."""
        lines = [ln for ln in lines if ln.strip() != ""]
        if len({len(ln) for ln in lines}) != 1:
            raise ValueError("Cac hang ban do khong cung do dai")
        walls, deaths, statics, periodic = set(), set(), set(), {}
        start = goal = None
        for r, ln in enumerate(lines):
            for c, ch in enumerate(ln):
                if ch == "#":
                    walls.add((r, c))
                elif ch == "T":
                    deaths.add((r, c))
                elif ch == "H":
                    statics.add((r, c))
                elif ch.isdigit():
                    periodic[(r, c)] = int(ch)
                elif ch == "S":
                    start = (r, c)
                elif ch == "G":
                    goal = (r, c)
                elif ch != ".":
                    raise ValueError("Ky tu la '%s' tai (%d,%d)" % (ch, r, c))
        if start is None or goal is None:
            raise ValueError("Ban do thieu S hoac G")
        return cls(len(lines), len(lines[0]), start, goal, walls, deaths, statics,
                   periodic, params["b0"], params["q"], params["P"], params["ON"],
                   params["K"], name)


# ======================================================================
# 4. V3 (se them): GridWorldV3 -- cum o gop, canh noi bo chi phi 0
# ======================================================================
