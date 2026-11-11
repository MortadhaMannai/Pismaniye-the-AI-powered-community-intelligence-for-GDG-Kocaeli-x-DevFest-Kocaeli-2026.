"""Generate high-resolution architecture PNGs, SVGs, and multi-page PDF guide for PISMANIYE."""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image as RLImage,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "assets"
DOCS_DIR = ROOT / "docs"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# Google Developer-inspired palette
BG_DEEP = (9, 13, 26)
BG_CARD = (22, 32, 58)
BG_ELEVATED = (30, 43, 77)
G_BLUE = (66, 133, 244)
G_RED = (234, 67, 53)
G_YELLOW = (251, 188, 4)
G_GREEN = (52, 168, 83)
SILK_WHITE = (248, 244, 236)
GOLD = (255, 213, 126)
CYAN = (78, 205, 196)
PURPLE = (167, 139, 250)
MUTED = (154, 165, 184)


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _draw_top_ribbon(draw: ImageDraw.ImageDraw, width: int) -> None:
    q = width // 4
    draw.rectangle([0, 0, q, 8], fill=G_BLUE)
    draw.rectangle([q, 0, 2 * q, 8], fill=G_RED)
    draw.rectangle([2 * q, 0, 3 * q, 8], fill=G_YELLOW)
    draw.rectangle([3 * q, 0, width, 8], fill=G_GREEN)


def _draw_box(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    title: str,
    subtitle: str,
    border_color: tuple[int, int, int],
    fill_color: tuple[int, int, int] = BG_CARD,
) -> None:
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=14, fill=fill_color, outline=border_color, width=3)
    draw.text((x1 + 18, y1 + 14), title, fill=SILK_WHITE, font=_font(20))
    draw.text((x1 + 18, y1 + 44), subtitle, fill=MUTED, font=_font(14))


def generate_hero_png() -> Path:
    w, h = 1600, 480
    img = Image.new("RGB", (w, h), BG_DEEP)
    draw = ImageDraw.Draw(img)
    _draw_top_ribbon(draw, w)

    # Subtle thread curves
    for offset in range(0, 40, 10):
        draw.arc([-100, 220 + offset, 900, 520 + offset], start=190, end=350, fill=G_BLUE, width=2)
        draw.arc([700, 180 + offset, 1700, 490 + offset], start=185, end=355, fill=G_RED, width=2)

    draw.rounded_rectangle([520, 45, 1080, 88], radius=20, fill=BG_ELEVATED, outline=G_BLUE, width=2)
    draw.text((590, 56), "GDG KOCAELI  •  DEVFEST KOCAELI 2026", fill=CYAN, font=_font(18))

    draw.text((515, 115), "PISMANIYE", fill=GOLD, font=_font(92))
    draw.text(
        (360, 232),
        "AI-Powered Multi-Agent Community Intelligence & Concierge Platform",
        fill=SILK_WHITE,
        font=_font(26),
    )
    draw.text(
        (525, 278),
        '"Unraveling People. Connecting Possibilities."',
        fill=GOLD,
        font=_font(22),
    )

    pills = [
        ("LangGraph + ADK", G_BLUE),
        ("6 Specialized Agents", G_RED),
        ("Hybrid Vector RAG", G_YELLOW),
        ("XAI Provenance Audit", PURPLE),
        ("Opt-In & Consent Gate", G_GREEN),
    ]
    start_x = 120
    for label, col in pills:
        draw.rounded_rectangle([start_x, 360, start_x + 255, 415], radius=12, fill=BG_CARD, outline=col, width=2)
        draw.text((start_x + 24, 378), label, fill=SILK_WHITE, font=_font(18))
        start_x += 275

    out = ASSETS_DIR / "pismaniye-hero-banner.png"
    img.save(out, "PNG")
    return out


def generate_architecture_diagram_png_and_svg() -> Path:
    w, h = 1600, 1020
    img = Image.new("RGB", (w, h), BG_DEEP)
    draw = ImageDraw.Draw(img)
    _draw_top_ribbon(draw, w)

    draw.text(
        (60, 28),
        "PISMANIYE — END-TO-END MULTI-AGENT SYSTEM ARCHITECTURE",
        fill=GOLD,
        font=_font(28),
    )
    draw.text(
        (60, 66),
        "Dual Interfaces  ->  FastAPI & OpenTelemetry  ->  LangGraph + Google ADK  ->  6 Agents + XAI  ->  PrivacyGuard & Hybrid RAG",
        fill=CYAN,
        font=_font(16),
    )

    # Layer 1: Dual Interfaces
    _draw_box(
        draw,
        (60, 115, 760, 210),
        "1A. Flagship Cinematic CLI & Textual TUI",
        "Python 3.11+ • Typer • Rich Live Execution Tree • Textual Cockpit • Unicode QR",
        G_BLUE,
    )
    _draw_box(
        draw,
        (840, 115, 1540, 210),
        "1B. Responsive Community Web App & Organizer Dashboard",
        "Mobile-First SPA • QR Code Handoff • Live XAI Drawer • RBAC Organizer Controls",
        G_GREEN,
    )

    # Arrows Layer 1 -> Layer 2
    draw.line([(410, 210), (410, 250)], fill=G_BLUE, width=4)
    draw.line([(1190, 210), (1190, 250)], fill=G_GREEN, width=4)

    # Layer 2: Shared API & Telemetry
    _draw_box(
        draw,
        (60, 250, 1540, 345),
        "2. Shared FastAPI Gateway, Security Middleware & OpenTelemetry Event Bus",
        "REST + Live Events • CSP & Security Headers • Constant-Time HMAC RBAC • OpenTelemetry Span Exporter",
        G_YELLOW,
        BG_ELEVATED,
    )

    draw.line([(800, 345), (800, 385)], fill=G_YELLOW, width=4)

    # Layer 3: Supervisor Router
    _draw_box(
        draw,
        (360, 385, 1240, 470),
        "3. LangGraph StateGraph Orchestrator + Google ADK Agent Bridge",
        "Supervisor Router Node classifies intent -> Dynamically sequences specialist nodes -> Emits live telemetry",
        GOLD,
    )

    # Layer 4: 6 Specialized Agents (2 rows of 3)
    agents = [
        ("Event Agent", "Schedules, Rooms & Conflict Resolver", G_BLUE, (60, 510, 520, 605)),
        ("People Agent", "Opt-In Speaker, GDE & Peer Discovery", G_RED, (570, 510, 1030, 605)),
        ("Knowledge Agent", "Hybrid Dense + Lexical RAG Citations", G_YELLOW, (1080, 510, 1540, 605)),
        ("Kocaeli Agent", "Time-Boxed Local Itinerary & Transit", G_GREEN, (60, 630, 520, 725)),
        ("Matchmaker Agent", "3-Factor Scoring & Consent Gate", PURPLE, (570, 630, 1030, 725)),
        ("Community Agent", "Post-DevFest Learning & Study Jams", CYAN, (1080, 630, 1540, 725)),
    ]
    for title, sub, col, box in agents:
        _draw_box(draw, box, f"• {title}", sub, col)

    # Layer 5: XAI Auditor & PrivacyGuard
    _draw_box(
        draw,
        (60, 765, 770, 865),
        "4A. XAI Auditing & Provenance Engine (`pismaniye explain`)",
        "Factor Breakdowns • Source Citations • Epistemic Uncertainty • Verification Badges",
        PURPLE,
        BG_ELEVATED,
    )
    _draw_box(
        draw,
        (830, 765, 1540, 865),
        "4B. PrivacyGuard, Consent Gate & Right-to-Erasure",
        "Opt-In Directory Filter • Schema + Regex PII Redaction • Explicit Intro Consent",
        G_GREEN,
        BG_ELEVATED,
    )

    # Layer 6: Cloud & Deterministic Storage Adapters
    _draw_box(
        draw,
        (60, 895, 1540, 985),
        "5. Modular Google Cloud & Deterministic Local Adapters",
        "Google GenAI SDK (Gemini 2.5) • Vertex AI Embeddings • Cloud Firestore • Cloud Storage • Cloud Run • Deterministic Seed=2026",
        G_BLUE,
    )

    out_png = ASSETS_DIR / "architecture-system-diagram.png"
    img.save(out_png, "PNG")

    # Also write a crisp companion SVG
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 720" width="100%" height="100%">
  <rect width="1200" height="720" rx="16" fill="#090D1A" stroke="#23325B" stroke-width="2"/>
  <rect x="0" y="0" width="300" height="6" fill="#4285F4"/>
  <rect x="300" y="0" width="300" height="6" fill="#EA4335"/>
  <rect x="600" y="0" width="300" height="6" fill="#FBBC04"/>
  <rect x="900" y="0" width="300" height="6" fill="#34A853"/>
  <text x="600" y="42" font-family="sans-serif" font-size="22" font-weight="bold" fill="#FFD57E" text-anchor="middle">PISMANIYE — MULTI-AGENT SYSTEM ARCHITECTURE</text>
  <rect x="50" y="65" width="520" height="75" rx="10" fill="#16203A" stroke="#4285F4" stroke-width="2"/>
  <text x="310" y="98" font-family="sans-serif" font-size="16" font-weight="bold" fill="#F8F4EC" text-anchor="middle">Cinematic CLI &amp; Textual TUI (Typer + Rich + Textual)</text>
  <text x="310" y="122" font-family="sans-serif" font-size="12" fill="#9AA5B8" text-anchor="middle">Live Execution Graph • Real Tool Timings • Trace &amp; XAI Inspector</text>
  <rect x="630" y="65" width="520" height="75" rx="10" fill="#16203A" stroke="#34A853" stroke-width="2"/>
  <text x="890" y="98" font-family="sans-serif" font-size="16" font-weight="bold" fill="#F8F4EC" text-anchor="middle">Responsive Community Web App &amp; Organizer Dashboard</text>
  <text x="890" y="122" font-family="sans-serif" font-size="12" fill="#9AA5B8" text-anchor="middle">Mobile QR Handoff • Agenda Builder • RBAC Organizer Controls</text>
  <rect x="50" y="165" width="1100" height="65" rx="10" fill="#1E2B4D" stroke="#FBBC04" stroke-width="2"/>
  <text x="600" y="195" font-family="sans-serif" font-size="16" font-weight="bold" fill="#F8F4EC" text-anchor="middle">Shared FastAPI Gateway + Security Headers + OpenTelemetry Event Bus</text>
  <text x="600" y="216" font-family="sans-serif" font-size="12" fill="#4ECDC4" text-anchor="middle">Constant-Time HMAC RBAC • Dynamic SVG QR Generator • Span Exporter</text>
  <rect x="200" y="255" width="800" height="65" rx="10" fill="#16203A" stroke="#FFD57E" stroke-width="2"/>
  <text x="600" y="285" font-family="sans-serif" font-size="16" font-weight="bold" fill="#FFD57E" text-anchor="middle">◈ LangGraph StateGraph Orchestrator + Google ADK Bridge</text>
  <text x="600" y="306" font-family="sans-serif" font-size="12" fill="#F8F4EC" text-anchor="middle">Supervisor Router Node dispatches specialized agents &amp; streams real state transitions</text>
  <!-- 6 Agents -->
  <rect x="50" y="345" width="340" height="70" rx="10" fill="#16203A" stroke="#4285F4" stroke-width="2"/>
  <text x="220" y="375" font-family="sans-serif" font-size="15" font-weight="bold" fill="#F8F4EC" text-anchor="middle">◆ Event Agent</text>
  <text x="220" y="398" font-family="sans-serif" font-size="12" fill="#9AA5B8" text-anchor="middle">Schedule, Rooms &amp; Conflict Resolver</text>
  <rect x="430" y="345" width="340" height="70" rx="10" fill="#16203A" stroke="#EA4335" stroke-width="2"/>
  <text x="600" y="375" font-family="sans-serif" font-size="15" font-weight="bold" fill="#F8F4EC" text-anchor="middle">● People Agent</text>
  <text x="600" y="398" font-family="sans-serif" font-size="12" fill="#9AA5B8" text-anchor="middle">Opt-In Speaker, GDE &amp; Peer Discovery</text>
  <rect x="810" y="345" width="340" height="70" rx="10" fill="#16203A" stroke="#FBBC04" stroke-width="2"/>
  <text x="980" y="375" font-family="sans-serif" font-size="15" font-weight="bold" fill="#F8F4EC" text-anchor="middle">▲ Knowledge Agent</text>
  <text x="980" y="398" font-family="sans-serif" font-size="12" fill="#9AA5B8" text-anchor="middle">Hybrid Vector + Lexical RAG Citations</text>
  <rect x="50" y="435" width="340" height="70" rx="10" fill="#16203A" stroke="#34A853" stroke-width="2"/>
  <text x="220" y="465" font-family="sans-serif" font-size="15" font-weight="bold" fill="#F8F4EC" text-anchor="middle">✦ Kocaeli Agent</text>
  <text x="220" y="488" font-family="sans-serif" font-size="12" fill="#9AA5B8" text-anchor="middle">Time-Boxed Local Itinerary &amp; Transit</text>
  <rect x="430" y="435" width="340" height="70" rx="10" fill="#16203A" stroke="#A78BFA" stroke-width="2"/>
  <text x="600" y="465" font-family="sans-serif" font-size="15" font-weight="bold" fill="#F8F4EC" text-anchor="middle">♾ Matchmaker Agent</text>
  <text x="600" y="488" font-family="sans-serif" font-size="12" fill="#9AA5B8" text-anchor="middle">3-Factor Scoring &amp; Intro Consent Gate</text>
  <rect x="810" y="435" width="340" height="70" rx="10" fill="#16203A" stroke="#4ECDC4" stroke-width="2"/>
  <text x="980" y="465" font-family="sans-serif" font-size="15" font-weight="bold" fill="#F8F4EC" text-anchor="middle">⬢ Community Agent</text>
  <text x="980" y="488" font-family="sans-serif" font-size="12" fill="#9AA5B8" text-anchor="middle">Post-DevFest Learning &amp; Study Jams</text>
  <!-- XAI & Privacy -->
  <rect x="50" y="530" width="530" height="70" rx="10" fill="#1E2B4D" stroke="#A78BFA" stroke-width="2"/>
  <text x="315" y="560" font-family="sans-serif" font-size="15" font-weight="bold" fill="#F8F4EC" text-anchor="middle">⚖ XAI Auditor &amp; Provenance Inspector</text>
  <text x="315" y="582" font-family="sans-serif" font-size="12" fill="#FFD57E" text-anchor="middle">Factor Breakdowns • Epistemic Uncertainty • Verification Badges</text>
  <rect x="620" y="530" width="530" height="70" rx="10" fill="#1E2B4D" stroke="#34A853" stroke-width="2"/>
  <text x="885" y="560" font-family="sans-serif" font-size="15" font-weight="bold" fill="#F8F4EC" text-anchor="middle">🛡 PrivacyGuard &amp; Consent Enforcement</text>
  <text x="885" y="582" font-family="sans-serif" font-size="12" fill="#81C995" text-anchor="middle">Opt-In Directory Only • Zero PII Leak • Right-to-Erasure</text>
  <!-- Cloud -->
  <rect x="50" y="620" width="1100" height="70" rx="10" fill="#16203A" stroke="#4285F4" stroke-width="2"/>
  <text x="600" y="650" font-family="sans-serif" font-size="15" font-weight="bold" fill="#8AB4F8" text-anchor="middle">Google Cloud &amp; Deterministic Local Adapters</text>
  <text x="600" y="672" font-family="sans-serif" font-size="12" fill="#F8F4EC" text-anchor="middle">Gemini 2.5 (`google-genai`) • Vertex AI (`text-embedding-004`) • Firestore • Cloud Storage • Cloud Run • Deterministic Seed=2026</text>
</svg>
"""
    (ASSETS_DIR / "architecture-system-diagram.svg").write_text(svg_content, encoding="utf-8")
    return out_png


def generate_workflows_diagram_png_and_svg() -> Path:
    w, h = 1600, 860
    img = Image.new("RGB", (w, h), BG_DEEP)
    draw = ImageDraw.Draw(img)
    _draw_top_ribbon(draw, w)

    draw.text(
        (60, 28),
        "PISMANIYE — THE 4 SIGNATURE AGENTIC WORKFLOWS & EXECUTION PIPELINES",
        fill=GOLD,
        font=_font(28),
    )

    wf_cards = [
        (
            "WORKFLOW A: MEET THE RIGHT EXPERT",
            '"I\'m interested in Agentic AI, Gemini, and production AI systems. Who should I meet?"',
            [
                "1. Supervisor extracts interests: ['Agentic AI', 'Gemini', 'production AI systems']",
                "2. People Agent filters opt-in speakers, GDEs & attendees (excludes PRIVATE profiles)",
                "3. Matchmaker Agent scores: 0.40*overlap + 0.35*complementarity + 0.25*mentorship",
                "4. Stages personalized intro in PENDING_REQUESTER_CONSENT (Zero email/phone exposed)",
                "5. XAI Auditor logs factor breakdown & provenance (`pismaniye explain <decision_id>`)",
            ],
            PURPLE,
            (60, 100, 770, 440),
        ),
        (
            "WORKFLOW B: MY DEVFEST DAY",
            '"Create my ideal DevFest agenda. I\'m interested in Google Cloud and AI."',
            [
                "1. Event Agent retrieves all 7 DevFest Kocaeli 2026 sessions & room capacities",
                "2. Scores each session by topic alignment + format weight (Keynote / Workshop / Talk)",
                "3. Detects 11:15–12:00 parallel conflict (Hall B Cloud Run AI vs Main Hall Flutter)",
                "4. Resolves conflict transparently & explains why each session was selected",
                "5. Knowledge Agent attaches grounded talk abstracts & venue logistics",
            ],
            G_BLUE,
            (830, 100, 1540, 440),
        ),
        (
            "WORKFLOW C: DISCOVER KOCAELI",
            '"I\'m a visiting GDE. I have three free hours. Help me discover Kocaeli."',
            [
                "1. Kocaeli Agent parses 3.0 free hours (180 min) & reserves 15m venue return buffer",
                "2. Evaluates round-trip transit + visit duration & verified opening hours",
                "3. Stop 1: Sekapark Coastal Promenade (10m transit + 60m visit = 70m)",
                "4. Stop 2: Historic İzmit Clock Tower (15m transit + 45m visit = 130m + 15m return = 145m)",
                "5. Defers Ormanya & Kartepe (requires ~220m) with clear time-budget explanation",
            ],
            G_GREEN,
            (60, 480, 770, 820),
        ),
        (
            "WORKFLOW D: COMMUNITY KNOWLEDGE",
            '"I want to start learning Agentic AI after DevFest."',
            [
                "1. Community Agent analyzes learning goals & skill progression",
                "2. Stage 1: GDG Kocaeli 4-Week Foundations of Agentic AI & Gemini Pathway (~12h)",
                "3. Stage 2: Monthly 'Build with AI' Study Jam & Architecture Clinic (~3h)",
                "4. Stage 3: Production RAG & Evaluation Notebooks Archive (~2.5h)",
                "5. Stage 4: GDG Kocaeli Speaker Incubator & DevFest 2027 Open-Source Contribution",
            ],
            CYAN,
            (830, 480, 1540, 820),
        ),
    ]

    for title, prompt, steps, col, (x1, y1, x2, y2) in wf_cards:
        draw.rounded_rectangle([x1, y1, x2, y2], radius=16, fill=BG_CARD, outline=col, width=3)
        draw.text((x1 + 22, y1 + 18), title, fill=col, font=_font(21))
        draw.text((x1 + 22, y1 + 52), prompt, fill=GOLD, font=_font(14))
        curr_y = y1 + 92
        for s in steps:
            draw.text((x1 + 24, curr_y), s, fill=SILK_WHITE, font=_font(15))
            curr_y += 46

    out_png = ASSETS_DIR / "workflow-execution-diagram.png"
    img.save(out_png, "PNG")

    svg_wf = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 540" width="100%" height="100%">
  <rect width="1200" height="540" rx="16" fill="#090D1A" stroke="#23325B" stroke-width="2"/>
  <text x="600" y="42" font-family="sans-serif" font-size="22" font-weight="bold" fill="#FFD57E" text-anchor="middle">THE 4 SIGNATURE AGENTIC WORKFLOWS</text>
  <rect x="40" y="65" width="540" height="205" rx="12" fill="#16203A" stroke="#A78BFA" stroke-width="2"/>
  <text x="65" y="98" font-family="sans-serif" font-size="16" font-weight="bold" fill="#A78BFA">WORKFLOW A: MEET THE RIGHT EXPERT</text>
  <text x="65" y="125" font-family="sans-serif" font-size="13" fill="#F8F4EC">• People Agent filters opt-in speakers, GDEs &amp; attendees</text>
  <text x="65" y="150" font-family="sans-serif" font-size="13" fill="#F8F4EC">• Matchmaker scores overlap + complementarity + mentorship</text>
  <text x="65" y="175" font-family="sans-serif" font-size="13" fill="#F8F4EC">• Stages intro in PENDING_REQUESTER_CONSENT (Zero PII leak)</text>
  <text x="65" y="200" font-family="sans-serif" font-size="13" fill="#81C995">• Audited by XAI Engine (`pismaniye explain latest`)</text>

  <rect x="620" y="65" width="540" height="205" rx="12" fill="#16203A" stroke="#4285F4" stroke-width="2"/>
  <text x="645" y="98" font-family="sans-serif" font-size="16" font-weight="bold" fill="#8AB4F8">WORKFLOW B: MY DEVFEST DAY</text>
  <text x="645" y="125" font-family="sans-serif" font-size="13" fill="#F8F4EC">• Event Agent scores all sessions against user interests</text>
  <text x="645" y="150" font-family="sans-serif" font-size="13" fill="#F8F4EC">• Automatically resolves 11:15 parallel track conflict</text>
  <text x="645" y="175" font-family="sans-serif" font-size="13" fill="#F8F4EC">• Explains selection rationale &amp; room logistics</text>
  <text x="645" y="200" font-family="sans-serif" font-size="13" fill="#81C995">• Grounded on session &amp; workshop RAG chunks</text>

  <rect x="40" y="295" width="540" height="205" rx="12" fill="#16203A" stroke="#34A853" stroke-width="2"/>
  <text x="65" y="328" font-family="sans-serif" font-size="16" font-weight="bold" fill="#81C995">WORKFLOW C: DISCOVER KOCAELI (3 HOURS)</text>
  <text x="65" y="355" font-family="sans-serif" font-size="13" fill="#F8F4EC">• Kocaeli Agent calculates 180m budget + 15m return buffer</text>
  <text x="65" y="380" font-family="sans-serif" font-size="13" fill="#F8F4EC">• Selects Sekapark (70m) + İzmit Clock Tower (60m) = 145m</text>
  <text x="65" y="405" font-family="sans-serif" font-size="13" fill="#F8F4EC">• Verifies opening hours &amp; defers longer trips (Ormanya 220m)</text>
  <text x="65" y="430" font-family="sans-serif" font-size="13" fill="#FFD57E">• Cultural &amp; culinary heritage context included</text>

  <rect x="620" y="295" width="540" height="205" rx="12" fill="#16203A" stroke="#4ECDC4" stroke-width="2"/>
  <text x="645" y="328" font-family="sans-serif" font-size="16" font-weight="bold" fill="#4ECDC4">WORKFLOW D: COMMUNITY KNOWLEDGE</text>
  <text x="645" y="355" font-family="sans-serif" font-size="13" fill="#F8F4EC">• Community Agent builds 4-stage post-DevFest learning path</text>
  <text x="645" y="380" font-family="sans-serif" font-size="13" fill="#F8F4EC">• Connects DevFest talks to monthly Build with AI Study Jams</text>
  <text x="645" y="405" font-family="sans-serif" font-size="13" fill="#F8F4EC">• Links RAG notebooks &amp; GDG Kocaeli Speaker Incubator</text>
  <text x="645" y="430" font-family="sans-serif" font-size="13" fill="#FFD57E">• Reusable for DevFest Kocaeli 2027 &amp; future meetups</text>
</svg>
"""
    (ASSETS_DIR / "workflow-execution-diagram.svg").write_text(svg_wf, encoding="utf-8")
    return out_png


def generate_pdf_guide(hero_png: Path, arch_png: Path, wf_png: Path) -> Path:
    pdf_path = DOCS_DIR / "PISMANIYE_Architecture_Design_and_User_Guide.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
        title="PISMANIYE — Architecture, Design & Step-by-Step User Guide",
        author="Mohamed Mortadha Mannai (@MortadhaMannai)",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=25,
        textColor=colors.HexColor("#0E172E"),
        spaceAfter=8,
    )
    h2_style = ParagraphStyle(
        "DocH2",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1A56DB"),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
        spaceAfter=6,
    )
    code_style = ParagraphStyle(
        "DocCode",
        parent=styles["Code"],
        fontSize=8.5,
        leading=12,
        backColor=colors.HexColor("#F1F5F9"),
        borderPadding=6,
        spaceAfter=8,
    )

    story = []

    # Page 1: Cover & Vision
    story.append(RLImage(str(hero_png), width=7.2 * inch, height=2.16 * inch))
    story.append(Spacer(1, 14))
    story.append(
        Paragraph(
            "PISMANIYE — Architecture, Visual Design & Step-by-Step User Guide",
            title_style,
        )
    )
    story.append(
        Paragraph(
            "<b>Author & Principal Architect:</b> Mohamed Mortadha Mannai (@MortadhaMannai)<br/>"
            "<b>Role:</b> Generative AI Engineer, SFEIR Paris | Google Developer Expert, Cloud AI | "
            "AWS AI Builder | PhD Candidate in Explainable AI (xAI) | International AI Speaker | AI Author | GCP Certified<br/>"
            "<b>Community:</b> GDG Kocaeli &amp; DevFest Kocaeli 2026<br/>"
            '<b>Tagline:</b> <i>"Unraveling People. Connecting Possibilities."</i>',
            body_style,
        )
    )

    story.append(Paragraph("1. Product Vision & Visual Design Identity", h2_style))
    story.append(
        Paragraph(
            "Pismaniye is an AI-powered multi-agent community intelligence and concierge platform inspired by "
            "Kocaeli's iconic Turkish dessert, Pişmaniye, whose intertwined silk threads symbolize bringing together "
            "international speakers, Google Developer Experts (GDEs), organizers, and local developers. "
            "It provides two synchronized interfaces over a shared stateful LangGraph + Google ADK + Hybrid RAG backend: "
            "(1) a Flagship Cinematic CLI/TUI for live stage technical talks, and (2) a Responsive Mobile-First Web App "
            "and RBAC-protected Organizer Dashboard accessible via QR code.",
            body_style,
        )
    )

    palette_data = [
        ["Visual Element", "Hex Color", "Design Usage in CLI & Web UI"],
        ["Obsidian Navy Canvas", "#090D1A / #16203A", "High-contrast dark terminal & card surfaces"],
        ["Google Developer Blue", "#4285F4", "Event Agent, primary interactive accents & borders"],
        ["Google Developer Red", "#EA4335", "People Agent, speaker/GDE role badges & alerts"],
        ["Google Developer Yellow", "#FBBC04", "Knowledge Agent (RAG), sample data badges & QR frame"],
        ["Google Developer Green", "#34A853", "Kocaeli Agent, verified organizer badges & PASS checks"],
        ["Pişmaniye Silk & Gold", "#F8F4EC / #FFD57E", "Supervisor Router, thread dividers & typography"],
    ]
    t_pal = Table(palette_data, colWidths=[1.8 * inch, 1.3 * inch, 4.1 * inch])
    t_pal.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0E172E")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ]
        )
    )
    story.append(t_pal)
    story.append(PageBreak())

    # Page 2: System Architecture Diagram & 6 Specialized Agents
    story.append(Paragraph("2. Multi-Agent System Architecture & Orchestration", h2_style))
    story.append(RLImage(str(arch_png), width=7.2 * inch, height=4.59 * inch))
    story.append(Spacer(1, 10))

    agent_table_data = [
        ["Agent", "ID", "Core Responsibilities & Grounded Tools"],
        ["Supervisor Router", "supervisor", "Intent classification & dynamic LangGraph StateGraph routing"],
        ["Event Agent", "event_agent", "Schedule lookup, venue logistics & 11:15 parallel track conflict resolution"],
        ["People Agent", "people_agent", "Opt-in speaker, GDE, organizer & attendee discovery by interest"],
        ["Knowledge Agent", "knowledge_agent", "Hybrid dense cosine + lexical/tag RAG retrieval with source URIs"],
        ["Kocaeli Agent", "kocaeli_agent", "Time-boxed local cultural & culinary itinerary planner with transit buffers"],
        ["Matchmaker Agent", "matchmaker_agent", "3-factor compatibility scoring, icebreakers & explicit consent gate"],
        ["Community Agent", "community_agent", "4-stage post-DevFest learning path, Study Jams & CFP onboarding"],
        ["XAI Auditor", "xai_auditor", "Audits factor scores, RAG citations, epistemic uncertainty & privacy checks"],
    ]
    t_ag = Table(agent_table_data, colWidths=[1.4 * inch, 1.3 * inch, 4.5 * inch])
    t_ag.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A56DB")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ]
        )
    )
    story.append(t_ag)
    story.append(PageBreak())

    # Page 3: 4 Signature Workflows & Security Architecture
    story.append(Paragraph("3. The 4 Signature Agentic Workflows", h2_style))
    story.append(RLImage(str(wf_png), width=7.2 * inch, height=3.87 * inch))
    story.append(Spacer(1, 10))

    story.append(Paragraph("4. Trust, Privacy, Safety & Zero-Secret Security", h2_style))
    story.append(
        Paragraph(
            "• <b>Zero Secrets in Repository:</b> Verified by automated CI regex scanning (`tests/test_security_audit.py`).<br/>"
            "• <b>Opt-In Directory Only:</b> `PrivacyGuard` filters out any `PRIVATE` or `opt_in_networking=False` profile prior to agent execution.<br/>"
            "• <b>Zero PII Exposure:</b> `private_email` and `private_phone` are excluded at the Pydantic schema boundary and scrubbed via regex redaction.<br/>"
            "• <b>Explicit Consent Gate:</b> Matchmaker introductions are staged in `PENDING_REQUESTER_CONSENT` and never sent without explicit consent.<br/>"
            "• <b>Hardened Web &amp; Container Stack:</b> Constant-time `hmac.compare_digest` RBAC token verification, strict CSP/HTTP security headers, QR URI scheme validation, and non-root Docker execution (`UID 10001`).",
            body_style,
        )
    )
    story.append(PageBreak())

    # Page 4: Step-by-Step User & Deployment Guide
    story.append(Paragraph("5. Step-by-Step Guide: How to Clone, Run & Deploy Yourself", h2_style))
    story.append(
        Paragraph(
            "Anyone can run Pismaniye on their own workstation, GitHub Codespaces, Google Cloud Shell, Docker, "
            "or Google Cloud Run in `local_deterministic` mode (zero API keys required) or `google_cloud` mode:",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "# Step 1: Clone &amp; Install<br/>"
            "git clone https://github.com/MortadhaMannai/Pismaniye-the-AI-powered-community-intelligence-for-GDG-Kocaeli-x-DevFest-Kocaeli-2026..git<br/>"
            "cd Pismaniye-the-AI-powered-community-intelligence-for-GDG-Kocaeli-x-DevFest-Kocaeli-2026.<br/>"
            "python3 -m venv .venv &amp;&amp; source .venv/bin/activate<br/>"
            'pip install --upgrade pip setuptools wheel &amp;&amp; pip install -e ".[dev]"<br/><br/>'
            "# Step 2: Run the Cinematic CLI &amp; All 12 Commands<br/>"
            "pismaniye launch --event devfest-kocaeli-2026<br/>"
            "pismaniye launch --event devfest-kocaeli-2026 --interactive<br/>"
            "pismaniye launch --event devfest-kocaeli-2026 --tui<br/>"
            'pismaniye ask "I\'m interested in Agentic AI, Gemini, and production AI systems. Who should I meet?"<br/>'
            "pismaniye agents<br/>"
            "pismaniye event schedule<br/>"
            'pismaniye people discover --interest "Agentic AI"<br/>'
            'pismaniye people match --interest "Gemini" --grant-consent<br/>'
            "pismaniye kocaeli explore --hours 3<br/>"
            'pismaniye knowledge search "LangGraph"<br/>'
            "pismaniye trace latest<br/>"
            "pismaniye explain latest<br/>"
            "pismaniye doctor<br/>"
            "pismaniye demo<br/><br/>"
            "# Step 3: Launch the Community Web App &amp; Organizer Dashboard (binds 0.0.0.0:8080)<br/>"
            "pismaniye serve --port 8080<br/><br/>"
            "# Step 4: Run Automated Test &amp; Security Audit Suite<br/>"
            "pytest -v &amp;&amp; mypy pismaniye",
            code_style,
        )
    )

    doc.build(story)
    return pdf_path


if __name__ == "__main__":
    h_png = generate_hero_png()
    a_png = generate_architecture_diagram_png_and_svg()
    w_png = generate_workflows_diagram_png_and_svg()
    pdf = generate_pdf_guide(h_png, a_png, w_png)
    print(f"Generated: {h_png.name}, {a_png.name}, {w_png.name}, {pdf.name}")
