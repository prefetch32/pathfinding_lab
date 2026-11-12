"""
visualizer.py -- XUAT GIF cho cac case, KHONG dung thu vien ngoai (tu viet bo ma hoa GIF).

Y tuong: moi lan thuat toan MO RONG mot nut = mot frame.
  - o cam     : nut dang duoc mo rong (current)
  - o xanh duong: nut dang cho trong frontier        (ghi g, h, f)
  - o tim nhat: nut da mo rong (closed)               (ghi g, h, f)
  - o xanh la : duong di cuoi cung (path)
  - vien xanh la = start, vien vang = goal
  f chinh la HAM DANH GIA CUA THUAT TOAN: A = g + h, B = h.

V2 (co pha): GIF gom 2 doan.
  1) Doan TIM KIEM (nhu V1; moi o hien nut moi nhat cua o do; header ghi B, F cua nut dang xet)
  2) Doan REPLAY duong di: tac nhan (o xanh dam) di tung luot, bay chu ki NHAP NHAY
     theo pha f (tim dam = dang bat, tim nhat = tat), header ghi pha, mau, chi phi.
  Bay: cam = bay co dinh 'H', tim = bay chu ki (chu so = do lech pha), do + X = bay chet ngay.

Muc luc
  1. Bang mau, font 3x5 (viet tay)
  2. Canvas            -- anh chi so mau trong bo nho + theo doi vung thay doi
  3. Bo ma hoa GIF     -- lzw_encode, GifWriter (frame con = chi vung thay doi)
  4. Ve frame          -- draw_cell, draw_header, draw_footer
  5. API               -- render_gif, render_case_gifs

Chu y: chu tren GIF viet HOA khong dau (font 3x5 chi co A-Z, 0-9, vai ky hieu).
"""
import os

# ======================================================================
# 1. Bang mau + font
# ======================================================================
PALETTE = [
    (236, 238, 242),  # 0  BG
    (190, 194, 204),  # 1  GRID
    (55, 60, 75),     # 2  WALL
    (205, 50, 50),    # 3  TRAP
    (252, 252, 252),  # 4  EMPTY
    (40, 160, 70),    # 5  START border
    (235, 165, 0),    # 6  GOAL border
    (150, 205, 255),  # 7  FRONTIER
    (212, 200, 240),  # 8  EXPANDED
    (255, 130, 60),   # 9  CURRENT
    (110, 220, 140),  # 10 PATH
    (25, 28, 40),     # 11 TEXT
    (255, 255, 255),  # 12 WHITE
    (32, 40, 62),     # 13 HEADER bg
    (245, 175, 70),   # 14 bay sat thuong co dinh (H)
    (205, 190, 230),  # 15 bay chu ki dang TAT
    (170, 40, 150),   # 16 bay chu ki dang BAT
    (30, 90, 210),    # 17 agent
    (200, 235, 210),  # 18 vet da di qua
]
BG, GRID, WALL, TRAP, EMPTY, START_B, GOAL_B = 0, 1, 2, 3, 4, 5, 6
FRONTIER, EXPANDED, CURRENT, PATH, TEXT, WHITE, HEADER_BG = 7, 8, 9, 10, 11, 12, 13
DMG_STATIC, PER_OFF, PER_ON, AGENT, TRAIL = 14, 15, 16, 17, 18

# Font 3x5: moi ky tu = 5 so 3 bit (hang tren -> duoi)
FONT = {
    "0": (7, 5, 5, 5, 7), "1": (2, 6, 2, 2, 7), "2": (7, 1, 7, 4, 7),
    "3": (7, 1, 7, 1, 7), "4": (5, 5, 7, 1, 1), "5": (7, 4, 7, 1, 7),
    "6": (7, 4, 7, 5, 7), "7": (7, 1, 1, 2, 2), "8": (7, 5, 7, 5, 7),
    "9": (7, 5, 7, 1, 7),
    "A": (2, 5, 7, 5, 5), "B": (6, 5, 6, 5, 6), "C": (3, 4, 4, 4, 3),
    "D": (6, 5, 5, 5, 6), "E": (7, 4, 6, 4, 7), "F": (7, 4, 6, 4, 4),
    "G": (3, 4, 5, 5, 3), "H": (5, 5, 7, 5, 5), "I": (7, 2, 2, 2, 7),
    "J": (1, 1, 1, 5, 2), "K": (5, 5, 6, 5, 5), "L": (4, 4, 4, 4, 7),
    "M": (5, 7, 7, 5, 5), "N": (6, 5, 5, 5, 5), "O": (2, 5, 5, 5, 2),
    "P": (6, 5, 6, 4, 4), "Q": (2, 5, 5, 7, 3), "R": (6, 5, 6, 5, 5),
    "S": (3, 4, 2, 1, 6), "T": (7, 2, 2, 2, 2), "U": (5, 5, 5, 5, 7),
    "V": (5, 5, 5, 5, 2), "W": (5, 5, 7, 7, 5), "X": (5, 5, 2, 5, 5),
    "Y": (5, 5, 2, 2, 2), "Z": (7, 1, 2, 4, 7),
    ":": (0, 2, 0, 2, 0), "/": (1, 1, 2, 4, 4), "+": (0, 2, 7, 2, 0),
    "*": (5, 2, 7, 2, 5), "=": (0, 7, 0, 7, 0), ".": (0, 0, 0, 0, 2),
    "-": (0, 0, 7, 0, 0), "(": (1, 2, 2, 2, 1), ")": (4, 2, 2, 2, 4),
    "|": (2, 2, 2, 2, 2), " ": (0, 0, 0, 0, 0),
}


# ======================================================================
# 2. Canvas
# ======================================================================
class Canvas:
    """Anh width x height, moi diem la chi so mau (0..15). Nho vung thay doi."""

    def __init__(self, width, height, fill=BG):
        self.width, self.height = width, height
        self.rows = [bytearray([fill]) * width for _ in range(height)]
        self.dirty = None  # [x0, y0, x1, y1]

    def _mark(self, x0, y0, x1, y1):
        if self.dirty is None:
            self.dirty = [x0, y0, x1, y1]
        else:
            d = self.dirty
            d[0], d[1] = min(d[0], x0), min(d[1], y0)
            d[2], d[3] = max(d[2], x1), max(d[3], y1)

    def fill_rect(self, x0, y0, x1, y1, color):
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.width, x1), min(self.height, y1)
        if x1 <= x0 or y1 <= y0:
            return
        chunk = bytes([color]) * (x1 - x0)
        for y in range(y0, y1):
            self.rows[y][x0:x1] = chunk
        self._mark(x0, y0, x1, y1)

    def text(self, x, y, s, color, scale=2):
        """Ve chuoi s (tu dong HOA). Moi ky tu rong 3*scale, cach nhau 1*scale... +scale."""
        for ch in s.upper():
            glyph = FONT.get(ch, FONT[" "])
            for ry, bits in enumerate(glyph):
                for rx in range(3):
                    if bits & (4 >> rx):
                        px, py = x + rx * scale, y + ry * scale
                        self.fill_rect(px, py, px + scale, py + scale, color)
            x += 4 * scale
        return x

    def take_dirty(self):
        d, self.dirty = self.dirty, None
        return d

    def region(self, x0, y0, x1, y1):
        return b"".join(bytes(self.rows[y][x0:x1]) for y in range(y0, y1))


# ======================================================================
# 3. Bo ma hoa GIF (LZW tu viet)
# ======================================================================
def lzw_encode(indices, min_code_size):
    """Nen LZW chuan GIF. indices: bytes cac chi so mau. Tra ve bytes (chua chia sub-block)."""
    clear = 1 << min_code_size
    eoi = clear + 1
    out = bytearray()
    acc = 0
    nbits = 0

    def emit(code, size):
        nonlocal acc, nbits
        acc |= code << nbits
        nbits += size
        while nbits >= 8:
            out.append(acc & 255)
            acc >>= 8
            nbits -= 8

    code_size = min_code_size + 1
    next_code = eoi + 1
    table = {}
    emit(clear, code_size)
    prefix = indices[0]
    for byte in indices[1:]:
        key = (prefix << 8) | byte
        code = table.get(key)
        if code is not None:
            prefix = code
            continue
        emit(prefix, code_size)
        if next_code < 4096:
            table[key] = next_code
            if next_code == (1 << code_size):
                code_size += 1
            next_code += 1
        else:                                   # bang day: xoa va bat dau lai
            emit(clear, code_size)
            table = {}
            code_size = min_code_size + 1
            next_code = eoi + 1
        prefix = byte
    emit(prefix, code_size)
    emit(eoi, code_size)
    if nbits:
        out.append(acc & 255)
    return bytes(out)


def _u16(n):
    return bytes((n & 255, (n >> 8) & 255))


def _sub_blocks(data):
    out = bytearray()
    for i in range(0, len(data), 255):
        chunk = data[i:i + 255]
        out.append(len(chunk))
        out += chunk
    out.append(0)
    return bytes(out)


class GifWriter:
    """Ghi GIF89a nhieu frame. Moi frame chi la MOT VUNG CHU NHAT (delta), disposal = giu nguyen."""

    def __init__(self, width, height, palette, loop=0):
        palette = list(palette)
        self.BITS = max(2, (len(palette) - 1).bit_length())      # 32 mau -> 5 bit
        palette += [(0, 0, 0)] * ((1 << self.BITS) - len(palette))
        self.width, self.height = width, height
        self.buf = bytearray(b"GIF89a")
        self.buf += _u16(width) + _u16(height)
        self.buf.append(0x80 | 0x70 | (self.BITS - 1))   # co bang mau toan cuc, 4 bit
        self.buf += bytes((0, 0))                        # mau nen, ti le
        for r, g, b in palette:
            self.buf += bytes((r, g, b))
        # NETSCAPE: lap vo han (loop = 0)
        self.buf += b"\x21\xFF\x0BNETSCAPE2.0\x03\x01" + _u16(loop) + b"\x00"

    def add_frame(self, x, y, w, h, pixels, delay_cs):
        """pixels: bytes w*h chi so mau. delay_cs: don vi 1/100 giay."""
        self.buf += b"\x21\xF9\x04" + bytes((0x04,)) + _u16(delay_cs) + b"\x00\x00"
        self.buf += b"\x2C" + _u16(x) + _u16(y) + _u16(w) + _u16(h) + b"\x00"
        self.buf.append(self.BITS)
        self.buf += _sub_blocks(lzw_encode(pixels, self.BITS))

    def save(self, path):
        with open(path, "wb") as f:
            f.write(bytes(self.buf) + b"\x3B")


# ======================================================================
# 4. Ve frame
# ======================================================================
CELL = 40           # kich thuoc mot o (px)
HEADER_H = 52
FOOTER_H = 26
LABEL_SCALE = 2     # font g,h,f tren o
LINE_PITCH = 11


def _cell_origin(r, c):
    return c * CELL, HEADER_H + r * CELL


def _trap_kind(kind):
    if kind == "H":
        return "static"
    if kind.isdigit():
        return "periodic"
    return None


def draw_cell(cv, env, state, info, evaluate):
    """Ve lai mot o (state = o). info = None hoac [status, g, h]; status: frontier/expanded/current/path."""
    r, c = state
    x0, y0 = _cell_origin(r, c)
    kind = env.describe_cell(state)
    trap = _trap_kind(kind)
    cv.fill_rect(x0, y0, x0 + CELL, y0 + CELL, GRID)                 # vien luoi
    if kind == "#":
        cv.fill_rect(x0 + 1, y0 + 1, x0 + CELL - 1, y0 + CELL - 1, WALL)
        return
    if kind == "T":
        cv.fill_rect(x0 + 1, y0 + 1, x0 + CELL - 1, y0 + CELL - 1, TRAP)
        cv.text(x0 + 8, y0 + 10, "X", WHITE, scale=6)
        return
    color = EMPTY
    if trap == "static":
        color = DMG_STATIC
    elif trap == "periodic":
        color = PER_OFF
    if info is not None:
        color = {"frontier": FRONTIER, "expanded": EXPANDED,
                 "current": CURRENT, "path": PATH}[info[0]]
    border = 3 if kind in ("S", "G") else 1
    if kind in ("S", "G"):
        cv.fill_rect(x0 + 1, y0 + 1, x0 + CELL - 1, y0 + CELL - 1,
                     START_B if kind == "S" else GOAL_B)
    cv.fill_rect(x0 + border, y0 + border, x0 + CELL - border, y0 + CELL - border, color)
    if trap is not None:
        if info is None:                      # chua co nhan: ve ky tu bay to o giua
            cv.text(x0 + 14, y0 + 10, kind, TEXT, scale=4)
        else:                                 # co nhan: chi danh dau nho o goc duoi phai
            mcol = DMG_STATIC if trap == "static" else PER_ON
            cv.fill_rect(x0 + CELL - 13, y0 + CELL - 13, x0 + CELL - 3, y0 + CELL - 3, mcol)
            cv.text(x0 + CELL - 12, y0 + CELL - 12, kind, WHITE if trap == "periodic" else TEXT, 1)
    if info is not None:
        _status, g, h = info
        lines = ("G%g" % g, "H%g" % h, "F%g" % evaluate(g, h))
        for i, line in enumerate(lines):
            cv.text(x0 + 5, y0 + 5 + i * LINE_PITCH, line, TEXT, LABEL_SCALE)


def draw_cell_replay(cv, env, cell, f, visited, agent_cell):
    """Ve o o che do REPLAY (V2): bay chu ki bat/tat theo pha f, agent la o xanh dam."""
    r, c = cell
    x0, y0 = _cell_origin(r, c)
    kind = env.describe_cell(cell)
    trap = _trap_kind(kind)
    cv.fill_rect(x0, y0, x0 + CELL, y0 + CELL, GRID)
    if kind == "#":
        cv.fill_rect(x0 + 1, y0 + 1, x0 + CELL - 1, y0 + CELL - 1, WALL)
        return
    if kind == "T":
        cv.fill_rect(x0 + 1, y0 + 1, x0 + CELL - 1, y0 + CELL - 1, TRAP)
        cv.text(x0 + 8, y0 + 10, "X", WHITE, scale=6)
        return
    on = False
    if trap == "static":
        color, on = DMG_STATIC, True
    elif trap == "periodic":
        on = env.trap_on(cell, f)
        color = PER_ON if on else PER_OFF
    else:
        color = TRAIL if cell in visited else EMPTY
    border = 3 if kind in ("S", "G") else 1
    if kind in ("S", "G"):
        cv.fill_rect(x0 + 1, y0 + 1, x0 + CELL - 1, y0 + CELL - 1,
                     START_B if kind == "S" else GOAL_B)
    cv.fill_rect(x0 + border, y0 + border, x0 + CELL - border, y0 + CELL - border, color)
    if trap is not None and cell != agent_cell:
        cv.text(x0 + 14, y0 + 10, kind, WHITE if (trap == "periodic" and on) else TEXT, scale=4)
    if cell == agent_cell:
        cv.fill_rect(x0 + 9, y0 + 9, x0 + CELL - 9, y0 + CELL - 9, AGENT)


def draw_header(cv, width, line1, line2):
    cv.fill_rect(0, 0, width, HEADER_H, HEADER_BG)
    cv.text(8, 8, line1, WHITE, scale=3)
    cv.text(8, 32, line2, WHITE, scale=2)


def draw_footer(cv, width, y, items=None):
    """Chu thich mau. items: list (mau, nhan). Mac dinh la chu thich doan tim kiem."""
    items = items or ((FRONTIER, "FRONTIER"), (EXPANDED, "EXPANDED"),
                      (CURRENT, "CURRENT"), (PATH, "PATH"))
    cv.fill_rect(0, y, width, y + FOOTER_H, BG)
    x = 8
    for color, label in items:
        cv.fill_rect(x, y + 6, x + 14, y + 20, GRID)
        cv.fill_rect(x + 1, y + 7, x + 13, y + 19, color)
        x = cv.text(x + 20, y + 7, label, TEXT, 2) + 14


# ======================================================================
# 5. API
# ======================================================================
def _slug(name):
    keep = []
    for ch in name.lower():
        keep.append(ch if ch.isalnum() else "_")
    out = "".join(keep)
    while "__" in out:
        out = out.replace("__", "_")
    return out.strip("_")


def render_gif(env, res, out_path, case_id="", max_frames=80, delay_cs=18,
               final_delay_cs=300, cap_show_steps=150, replay=True, replay_delay_cs=35):
    """Ve mot SearchResult thanh GIF. Tra ve duong dan file."""
    width = env.num_cols * CELL
    height = HEADER_H + env.num_rows * CELL + FOOTER_H
    cv = Canvas(width, height, BG)
    gif = GifWriter(width, height, PALETTE)
    evaluate = res.evaluate or (lambda g, h: g + h)
    allow_revisit = (res.revisit_policy == "none")   # tree search: o da mo van co the vao frontier lai
    pos = env.position

    info = {}      # o -> [status, g, h]   (V2: nut MOI NHAT tai o do)
    h_of = {}

    # --- frame 0: toan bo ban do ---
    cv.fill_rect(0, 0, width, height, BG)
    for r in range(env.num_rows):
        for c in range(env.num_cols):
            draw_cell(cv, env, (r, c), None, evaluate)
    draw_footer(cv, width, HEADER_H + env.num_rows * CELL)
    steps = len(res.trace)
    capped = res.status == res.CAP_REACHED
    if capped:
        steps = min(steps, cap_show_steps)
    if res.trace:
        s0, g0, h0 = res.trace[0]
        info[pos(s0)] = ["frontier", g0, h0]
        h_of[pos(s0)] = h0
        draw_cell(cv, env, pos(s0), info[pos(s0)], evaluate)
    title = ("%s  %s" % (case_id, res.algo_name)).strip()
    draw_header(cv, width, title, "EXPANDED 0   FRONTIER 1   READY")
    cv.take_dirty()
    gif.add_frame(0, 0, width, height, cv.region(0, 0, width, height), delay_cs)

    # --- moi lan mo rong = 1 cap nhat; chi phat frame moi `stride` buoc ---
    stride = max(1, -(-steps // max_frames))
    prev_current = None
    for k in range(steps):
        s, g, h = res.trace[k]
        p = pos(s)
        touched = set()
        if prev_current is not None and info[prev_current][0] == "current":
            info[prev_current][0] = "expanded"
            touched.add(prev_current)
        info[p] = ["current", g, h]
        h_of[p] = h
        touched.add(p)
        for (s2, g2, h2) in res.pushed[k]:
            p2 = pos(s2)
            h_of[p2] = h2
            if p2 == p:
                continue
            cur = info.get(p2)
            if cur is not None and cur[0] in ("expanded", "current") and not allow_revisit:
                continue
            info[p2] = ["frontier", g2, h2]
            touched.add(p2)
        prev_current = p
        for st in touched:
            draw_cell(cv, env, st, info[st], evaluate)
        if (k + 1) % stride == 0 or k == steps - 1:
            n_front = sum(1 for v_ in info.values() if v_[0] == "frontier")
            extra = env.state_text(s)
            draw_header(cv, width, title,
                        ("EXPANDED %d   FRONTIER %d   G %g   %s" % (k + 1, n_front, g, extra)).strip())
            _emit(cv, gif, delay_cs)

    # --- frame ket qua ---
    has_phases = getattr(env, "HAS_PHASES", False)
    if res.status == res.FOUND:
        g_along = 0
        for i, st in enumerate(res.states):
            if i > 0:
                g_along += min(c for (_a, nxt, c) in env.successors(res.states[i - 1])
                               if nxt == st)
            info[pos(st)] = ["path", g_along, h_of.get(pos(st), 0)]
            draw_cell(cv, env, pos(st), info[pos(st)], evaluate)
        line2 = "FOUND   COST %g   EXPANDED %d" % (res.cost, res.expansions)
        if has_phases:
            line2 = "FOUND  COST %g  STEPS %d  DMG %d" % (
                res.cost, len(res.states) - 1, env.path_damage(res.states))
    elif res.status == res.NO_PATH:
        line2 = "NO PATH   EXPANDED %d" % res.expansions
    else:
        line2 = "STOPPED AT CAP (%d STEPS) - LIKELY LOOP" % res.expansions
    draw_header(cv, width, title, line2)
    _emit(cv, gif, final_delay_cs if not (has_phases and replay and res.status == res.FOUND) else 120)

    # --- doan REPLAY (chi V2, khi tim thay duong) ---
    if replay and has_phases and res.status == res.FOUND:
        _replay(cv, gif, env, res, width, title, replay_delay_cs, final_delay_cs)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    gif.save(out_path)
    return out_path


def _replay(cv, gif, env, res, width, title, delay_cs, final_delay_cs):
    """Phat lai duong di tung luot: agent di, bay chu ki nhap nhay theo pha f."""
    states = res.states
    visited = set()
    periodic_cells = list(env.periodic_traps)
    f0 = states[0][2]
    for r in range(env.num_rows):
        for c in range(env.num_cols):
            draw_cell_replay(cv, env, (r, c), f0, visited, None)
    draw_footer(cv, width, HEADER_H + env.num_rows * CELL,
                ((AGENT, "AGENT"), (PER_ON, "TRAP ON"), (PER_OFF, "TRAP OFF"),
                 (DMG_STATIC, "H ALWAYS"), (TRAIL, "VISITED")))
    draw_header(cv, width, title, "REPLAY  PHASE %d  HP %d" % (f0, states[0][1]))
    cv.take_dirty()
    cv.dirty = [0, 0, width, cv.height]
    _emit(cv, gif, delay_cs)

    cost = 0
    prev_cell = None
    for i, s in enumerate(states):
        cell, b, f = s
        if i > 0:
            cost += min(c for (_a, nxt, c) in env.successors(states[i - 1]) if nxt == s)
        touched = set(periodic_cells)
        touched.add(cell)
        if prev_cell is not None:
            visited.add(prev_cell)
            touched.add(prev_cell)
        for t in touched:
            draw_cell_replay(cv, env, t, f, visited, cell)
        act = ""
        if i > 0:
            act = "WAIT" if cell == prev_cell else "MOVE"
        draw_header(cv, width, title,
                    ("REPLAY STEP %d  %s  PHASE %d  HP %d  COST %g" % (i, act, f, b, cost)).strip())
        _emit(cv, gif, final_delay_cs if i == len(states) - 1 else delay_cs)
        prev_cell = cell


def _emit(cv, gif, delay_cs):
    d = cv.take_dirty()
    if d is None:
        return
    x0, y0, x1, y1 = d
    gif.add_frame(x0, y0, x1 - x0, y1 - y0, cv.region(x0, y0, x1, y1), delay_cs)


def render_case_gifs(case_id, env, results, out_dir, labels=None, tags=None, suffix="", **kwargs):
    """Moi thuat toan trong `labels` -> mot file GIF rieng: <out_dir>/<case_id>__<tag>.gif.

    results: dict {label: SearchResult} (lay tu cases.common.run_case(...)["results"]).
    tags   : dict {label: ten ngan trong ten file}; mac dinh lay slug cua label.
    """
    paths = []
    for label in (labels or list(results)):
        tag = (tags or {}).get(label) or _slug(label)
        if suffix:
            tag = "%s_%s" % (tag, suffix)
        fname = "%s__%s.gif" % (case_id.lower().replace("-", "_"), tag)
        paths.append(render_gif(env, results[label], os.path.join(out_dir, fname),
                                case_id=case_id, **kwargs))
    return paths
