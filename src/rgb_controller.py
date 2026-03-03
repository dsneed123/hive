"""
RGB LED Matrix Controller for Hive
Drives a 64x64 HUB75 panel on Raspberry Pi via rgbmatrix.
Falls back to terminal text output on dev machines without hardware.
"""

import time
import math
from datetime import datetime

from src.database import (
    init_db,
    get_active_account,
    get_snapshots,
    get_emails,
    get_events,
    get_email_mode,
)

# --- Hardware detection ---
try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
    HAS_MATRIX = True
except ImportError:
    HAS_MATRIX = False

# --- Constants ---
PANEL = 64
SCREEN_DURATION = 8
DATA_REFRESH = 60
FRAME_DELAY = 0.05
FONT_DIR = "/home/tars/rpi-rgb-led-matrix/fonts"

# Color palette
AMBER   = (245, 158, 11)
ROSE    = (239, 68, 68)
BLUE    = (59, 130, 246)
EMERALD = (16, 185, 129)
HONEY   = (251, 191, 36)
VIOLET  = (139, 92, 246)
CYAN    = (6, 182, 212)
WHITE   = (255, 255, 255)
DIM     = (80, 80, 80)
DARK    = (40, 40, 40)

SCREENS = ["dashboard", "analytics", "emails", "calendar", "clock"]


def _fmt(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


# ─────────────────────────────────────────────────────────────────────
# Data layer
# ─────────────────────────────────────────────────────────────────────

class HiveData:
    def __init__(self):
        self.username = "hive"
        self.followers = 0
        self.following = 0
        self.likes = 0
        self.videos = 0
        self.engagement = 0.0
        self.emails_total = 0
        self.emails_collab = 0
        self.emails_promo = 0
        self.emails_spam = 0
        self.emails_other = 0
        self.email_mode = "test"
        self.events_today = []
        self.events_month = 0
        self.last_refresh = 0

    def refresh(self):
        now = time.time()
        if now - self.last_refresh < DATA_REFRESH:
            return
        self.last_refresh = now

        try:
            acct = get_active_account()
            self.username = acct.get("username", "hive") if acct else "hive"

            snaps = get_snapshots(username=self.username, days=30)
            if snaps:
                s = snaps[-1]
                self.followers = s.get("followers", 0)
                self.following = s.get("following", 0)
                self.likes = s.get("likes", 0)
                self.videos = s.get("videos", 0)

            if self.followers > 0:
                self.engagement = (self.likes / self.followers) * 100

            emails = get_emails(category="all", page=1, per_page=1000)
            self.emails_total = len(emails)
            self.emails_collab = sum(1 for e in emails if e.get("category") == "collaboration")
            self.emails_promo = sum(1 for e in emails if e.get("category") == "promotion")
            self.emails_spam = sum(1 for e in emails if e.get("category") == "spam")
            self.emails_other = self.emails_total - self.emails_collab - self.emails_promo - self.emails_spam
            self.email_mode = get_email_mode()

            today = datetime.now()
            evts = get_events(month=today.month, year=today.year)
            self.events_month = len(evts)
            today_str = today.strftime("%Y-%m-%d")
            self.events_today = [e for e in evts if e.get("date") == today_str][:4]
        except Exception:
            # Matrix init drops filesystem privileges — DB may be unreachable.
            # Keep using cached data from the pre-init load.
            pass


# ─────────────────────────────────────────────────────────────────────
# Controller
# ─────────────────────────────────────────────────────────────────────

class HiveRGBController:
    def __init__(self):
        self.matrix = None
        self.canvas = None
        self.data = HiveData()
        self.screen_index = 0
        self.screen_start = 0.0
        self.running = False
        self.scroll_x = 0
        self.fonts = {}

    def setup(self):
        init_db()
        self.data.refresh()
        if HAS_MATRIX:
            self._load_fonts()
            self._setup_matrix()
            print("RGB matrix initialized (64x64 HUB75)")
        else:
            print("[dev mode] No rgbmatrix hardware — terminal output")

    def _setup_matrix(self):
        opts = RGBMatrixOptions()
        opts.rows = PANEL
        opts.cols = PANEL
        opts.chain_length = 1
        opts.parallel = 1
        opts.hardware_mapping = "regular"
        opts.gpio_slowdown = 4
        opts.brightness = 90
        opts.disable_hardware_pulsing = True
        self.matrix = RGBMatrix(options=opts)
        self.canvas = self.matrix.CreateFrameCanvas()

    def _load_fonts(self):
        for name, fn in [("sm", "5x8.bdf"), ("md", "6x10.bdf"), ("lg", "7x13B.bdf")]:
            f = graphics.Font()
            f.LoadFont(f"{FONT_DIR}/{fn}")
            self.fonts[name] = f

    def _c(self, rgb):
        return graphics.Color(*rgb)

    # --- Run loop ---

    def run(self):
        self.running = True
        self.screen_start = time.time()
        self.screen_index = 0
        while self.running:
            now = time.time()
            self.data.refresh()
            if now - self.screen_start >= SCREEN_DURATION:
                self.screen_index = (self.screen_index + 1) % len(SCREENS)
                self.screen_start = now
                self.scroll_x = 0
            screen = SCREENS[self.screen_index]
            if HAS_MATRIX:
                self.canvas.Clear()
                getattr(self, f"_draw_{screen}")()
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
                time.sleep(FRAME_DELAY)
            else:
                self._print_terminal(screen)
                left = SCREEN_DURATION - (time.time() - self.screen_start)
                if left > 0:
                    time.sleep(left)

    def stop(self):
        self.running = False
        if self.matrix:
            self.matrix.Clear()
        print("RGB display stopped.")

    # --- Drawing helpers ---
    # sm = 5x8  → 5px wide, 8px tall  → 12 chars in 64px
    # md = 6x10 → 6px wide, 10px tall → 10 chars in 64px
    # lg = 7x13B→ 7px wide, 13px tall →  9 chars in 64px

    def _txt(self, font, x, y, color, text):
        graphics.DrawText(self.canvas, self.fonts[font], x, y, self._c(color), str(text))

    def _line(self, x0, y0, x1, y1, color):
        graphics.DrawLine(self.canvas, x0, y0, x1, y1, self._c(color))

    def _rect(self, x, y, w, h, color):
        c = self._c(color)
        for row in range(y, y + h):
            graphics.DrawLine(self.canvas, x, row, x + w - 1, row, c)

    def _hline(self, y, color=DARK):
        """Full-width 1px separator."""
        self._line(0, y, 63, y, color)

    def _bar(self, x, y, w, h, color):
        """Colored accent bar."""
        self._rect(x, y, w, h, color)

    # --- Screen 1: Dashboard ---

    def _draw_dashboard(self):
        d = self.data
        now = datetime.now()

        # Top accent
        self._hline(0, HONEY)
        self._hline(1, HONEY)

        # HIVE centered in large bold  (4 * 7 = 28px → x = 18)
        self._txt("lg", 18, 14, HONEY, "HIVE")

        # @username centered in medium (max 10 chars, 6px each)
        name = f"@{d.username}"[:10]
        nx = max(0, (PANEL - len(name) * 6) // 2)
        self._txt("md", nx, 24, WHITE, name)

        # Separator
        self._hline(27, DIM)

        # 4 stats — 2 columns, colored value with label underneath
        # Left col x=2, right col x=33
        # Row 1: y=30..42  Row 2: y=44..56
        self._txt("md", 2, 38, AMBER, _fmt(d.followers))
        self._txt("sm", 2, 44, DIM, "Fans")

        self._txt("md", 33, 38, ROSE, _fmt(d.likes))
        self._txt("sm", 33, 44, DIM, "Likes")

        self._txt("md", 2, 54, BLUE, _fmt(d.following))
        self._txt("sm", 2, 60, DIM, "Fol.")

        self._txt("md", 33, 54, EMERALD, _fmt(d.videos))
        self._txt("sm", 33, 60, DIM, "Vids")

        # Bottom accent
        self._hline(63, HONEY)

    # --- Screen 2: Analytics ---

    def _draw_analytics(self):
        d = self.data

        self._hline(0, VIOLET)

        self._txt("sm", 2, 8, HONEY, "Analytics")

        # 4 metric rows — each gets: accent bar, label, value, progress bar
        # Label (sm, 5px wide): "Fans"=4*5=20, "Likes"=5*5=25, etc.
        # Value (md, 6px wide) right-aligned
        metrics = [
            ("Fans", d.followers, AMBER),
            ("Likes", d.likes, ROSE),
            ("Fol.", d.following, BLUE),
            ("Vids", d.videos, EMERALD),
        ]
        mx = max((v for _, v, _ in metrics), default=1) or 1

        y = 14
        for label, val, color in metrics:
            # Left accent bar
            self._bar(0, y, 2, 10, color)
            # Label
            self._txt("sm", 4, y + 7, DIM, label)
            # Value right-aligned
            vs = _fmt(val)
            self._txt("md", 62 - len(vs) * 6, y + 8, color, vs)
            # Progress bar (1px, subtle)
            bw = max(1, int((val / mx) * 30))
            self._rect(4, y + 9, bw, 1, color)
            y += 12

        # Engagement
        self._hline(61, DIM)
        self._txt("sm", 2, 62, DIM, "Engage")
        es = f"{d.engagement:.1f}%"
        self._txt("sm", 62 - len(es) * 5, 62, VIOLET, es)
        self._hline(63, VIOLET)

    # --- Screen 3: Emails ---

    def _draw_emails(self):
        d = self.data

        self._hline(0, BLUE)

        self._txt("sm", 2, 8, HONEY, "Inbox")
        ts = str(d.emails_total)
        self._txt("md", 62 - len(ts) * 6, 9, WHITE, ts)

        self._hline(12, DIM)

        cats = [
            ("Collab", d.emails_collab, BLUE),
            ("Promo", d.emails_promo, AMBER),
            ("Spam", d.emails_spam, ROSE),
            ("Other", d.emails_other, DIM),
        ]

        y = 17
        for label, count, color in cats:
            self._bar(0, y, 2, 9, color)
            self._txt("sm", 5, y + 7, WHITE, label)
            cs = str(count)
            self._txt("md", 62 - len(cs) * 6, y + 8, color, cs)
            y += 10

        self._hline(58, DIM)
        mode = d.email_mode.upper()
        mc = EMERALD if mode == "REPLY" else AMBER
        self._txt("sm", 2, 63, DIM, "Mode")
        self._txt("md", 62 - len(mode) * 6, 63, mc, mode)
        self._hline(63, BLUE)

    # --- Screen 4: Calendar ---

    def _draw_calendar(self):
        d = self.data
        now = datetime.now()

        self._hline(0, CYAN)

        self._txt("sm", 2, 8, HONEY, "Calendar")
        ds = now.strftime("%d %b")
        self._txt("sm", 62 - len(ds) * 5, 8, CYAN, ds)

        self._hline(12, DIM)

        tcol = {"post": AMBER, "idea": BLUE, "note": DIM}

        if d.events_today:
            y = 17
            for ev in d.events_today[:4]:
                et = ev.get("event_type", "note")
                color = tcol.get(et, DIM)
                self._bar(0, y, 2, 9, color)
                # Title: max 8 chars (8*5=40px)
                title = ev.get("title", "")[:8]
                self._txt("sm", 5, y + 7, WHITE, title)
                # Time if present (5 chars at x=44)
                t = ev.get("time", "")
                if t:
                    self._txt("sm", 44, y + 7, DIM, t[:5])
                y += 10
        else:
            self._txt("md", 4, 34, DIM, "No events")

        self._hline(58, DIM)
        self._txt("sm", 2, 63, DIM, "Month")
        ms = str(d.events_month)
        self._txt("md", 62 - len(ms) * 6, 63, WHITE, ms)
        self._hline(63, CYAN)

    # --- Screen 5: Clock ---

    def _draw_clock(self):
        d = self.data
        now = datetime.now()

        self._hline(0, CYAN)

        # Large bold time (7x13B: "HH" = 14px, ":" = 7px, "MM" = 14px = 35px → x=14)
        h = now.strftime("%H")
        m = now.strftime("%M")
        blink = now.second % 2 == 0

        self._txt("lg", 14, 17, WHITE, h)
        if blink:
            self._txt("lg", 28, 17, CYAN, ":")
        self._txt("lg", 35, 17, WHITE, m)

        # Date centered (sm: 5px/char)
        ds = now.strftime("%b %d %Y")
        self._txt("sm", max(0, (PANEL - len(ds) * 5) // 2), 28, DIM, ds)

        # Day of week centered (md: 6px/char, max 9 chars)
        day = now.strftime("%A")[:9]
        self._txt("md", max(0, (PANEL - len(day) * 6) // 2), 40, WHITE, day)

        self._hline(44, DIM)

        # Account
        self._txt("sm", 2, 53, DIM, "Account")
        acct = f"@{d.username}"[:8]
        self._txt("sm", 62 - len(acct) * 5, 53, HONEY, acct)

        # System status with pulsing dot
        self._txt("sm", 2, 62, DIM, "System")
        p = int(128 + 127 * math.sin(time.time() * 3))
        self._rect(38, 58, 3, 3, (0, p, 0))
        self._txt("sm", 44, 62, EMERALD, "OK")

        self._hline(63, CYAN)

    # --- Terminal fallback ---

    def _print_terminal(self, screen):
        d = self.data
        now = datetime.now()
        print(f"\n{'─' * 40}")
        print(f"  HIVE — {screen.upper()}")
        print(f"{'─' * 40}")
        if screen == "dashboard":
            print(f"  @{d.username}")
            print(f"  Fans: {_fmt(d.followers)}  Likes: {_fmt(d.likes)}")
            print(f"  Fol.: {_fmt(d.following)}  Vids: {_fmt(d.videos)}")
        elif screen == "analytics":
            print(f"  Fans:  {_fmt(d.followers)}")
            print(f"  Likes: {_fmt(d.likes)}")
            print(f"  Fol.:  {_fmt(d.following)}")
            print(f"  Vids:  {_fmt(d.videos)}")
            print(f"  Engage: {d.engagement:.1f}%")
        elif screen == "emails":
            print(f"  Total: {d.emails_total}")
            print(f"  Collab: {d.emails_collab}  Promo: {d.emails_promo}")
            print(f"  Spam: {d.emails_spam}  Other: {d.emails_other}")
            print(f"  Mode: {d.email_mode.upper()}")
        elif screen == "calendar":
            print(f"  {now.strftime('%d %b %Y')}")
            for ev in d.events_today:
                print(f"  [{ev.get('event_type')}] {ev.get('title')} {ev.get('time','')}")
            if not d.events_today:
                print("  No events today")
            print(f"  Month: {d.events_month}")
        elif screen == "clock":
            print(f"  {now.strftime('%H:%M:%S')}")
            print(f"  {now.strftime('%A, %b %d %Y')}")
            print(f"  @{d.username}  SYS OK")
        print(f"{'─' * 40}")
