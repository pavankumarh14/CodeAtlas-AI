from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

BG = RGBColor(0x0B, 0x11, 0x20)
CARD = RGBColor(0x15, 0x1E, 0x32)
BORDER = RGBColor(0x2A, 0x36, 0x50)
WHITE = RGBColor(0xF8, 0xFA, 0xFC)
MUTED = RGBColor(0x94, 0xA3, 0xB8)
INDIGO = RGBColor(0x81, 0x8C, 0xF8)
TEAL = RGBColor(0x2D, 0xD4, 0xBF)
ROSE = RGBColor(0xFB, 0x71, 0x85)
AMBER = RGBColor(0xFB, 0xBF, 0x24)
FONT = "Helvetica Neue"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
W = prs.slide_width


def text(slide, x, y, w, h, runs, size=16, color=WHITE, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.15):
    """runs: str, or list of paragraphs; each paragraph is str or list of (text, {opts})."""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    paras = runs if isinstance(runs, list) else [runs]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        parts = para if isinstance(para, list) else [(para, {})]
        for part, opts in parts:
            r = p.add_run()
            r.text = part
            f = r.font
            f.name = FONT
            f.size = Pt(opts.get("size", size))
            f.bold = opts.get("bold", bold)
            f.color.rgb = opts.get("color", color)
        if i < len(paras) - 1:
            p.space_after = Pt(opts.get("after", 8) if parts else 8)
    return tb


def box(slide, x, y, w, h, fill=CARD, line=BORDER, radius=0.06, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    s = slide.shapes.add_shape(shape, x, y, w, h)
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(1)
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    s.shadow.inherit = False
    return s


def new_slide(title, kicker=None, notes=None, num=None):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG
    if kicker:
        text(s, Inches(0.7), Inches(0.5), Inches(10), Inches(0.35), kicker.upper(), size=12, color=TEAL, bold=True)
    text(s, Inches(0.7), Inches(0.85), Inches(12), Inches(0.9), title, size=32, bold=True)
    if num:
        text(s, Inches(11.6), Inches(7.0), Inches(1.1), Inches(0.3), f"CodeAtlas AI  ·  {num}", size=10, color=MUTED, align=PP_ALIGN.RIGHT)
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def card(slide, x, y, w, h, heading, body, accent=INDIGO, heading_size=17, body_size=14):
    box(slide, x, y, w, h)
    bar = box(slide, x, y + Inches(0.25), Inches(0.06), Inches(0.5), fill=accent, line=None, shape=MSO_SHAPE.RECTANGLE)
    text(slide, x + Inches(0.3), y + Inches(0.22), w - Inches(0.55), Inches(0.6), heading, size=heading_size, bold=True)
    text(slide, x + Inches(0.3), y + Inches(0.8), w - Inches(0.55), h - Inches(0.95), body, size=body_size, color=MUTED)


def tag(slide, x, y, label, color=AMBER, w=Inches(1.25)):
    t = box(slide, x, y, w, Inches(0.3), fill=BG, line=color, radius=0.5)
    text(slide, x, y + Inches(0.045), w, Inches(0.25), label, size=10, color=color, bold=True, align=PP_ALIGN.CENTER)


# 1. Title
s = prs.slides.add_slide(BLANK)
s.background.fill.solid()
s.background.fill.fore_color.rgb = BG
box(s, Inches(0.7), Inches(2.35), Inches(0.12), Inches(2.1), fill=TEAL, line=None, shape=MSO_SHAPE.RECTANGLE)
text(s, Inches(1.1), Inches(2.2), Inches(11), Inches(1.2), "CodeAtlas AI", size=60, bold=True)
text(s, Inches(1.1), Inches(3.35), Inches(11), Inches(0.6), "The Living Engineering Ontology and Knowledge Graph Platform", size=24, color=INDIGO)
text(s, Inches(1.1), Inches(4.0), Inches(11), Inches(0.5), "Every Freshservice incident, diagnosed before anyone opens it.", size=18, color=MUTED)
text(s, Inches(1.1), Inches(6.2), Inches(11), Inches(0.4), [[("Pavan Kumar H", {"bold": True, "color": WHITE}), ("   ·   The Great Agent Hackathon", {"color": MUTED})]], size=16)
s.notes_slide.notes_text_frame.text = "Introduce yourself and the one-line pitch: CodeAtlas gives every Freshservice incident the engineering context it's missing, and posts it back automatically."

# 2. Problem
s = new_slide("A ticket says what broke. Nobody knows why.", "The problem", num=2,
              notes="Walk through the real ticket from our tenant. The five questions are what every on-call engineer asks first, and today the answers live in GitHub, Jira, Confluence, Slack and people's heads.")
box(s, Inches(0.7), Inches(2.1), Inches(5.6), Inches(3.9))
text(s, Inches(1.0), Inches(2.35), Inches(5), Inches(0.3), "FRESHSERVICE  ·  INCIDENT #80", size=11, color=MUTED, bold=True)
text(s, Inches(1.0), Inches(2.75), Inches(5), Inches(1.2), "Database connection pool exhausted on payment gateway", size=22, bold=True)
tag(s, Inches(1.0), Inches(4.05), "OPEN", color=INDIGO, w=Inches(0.9))
tag(s, Inches(2.05), Inches(4.05), "UNASSIGNED", color=ROSE, w=Inches(1.4))
text(s, Inches(1.0), Inches(4.7), Inches(5), Inches(1.1),
     "Knowledge is scattered across GitHub, Jira, Confluence, Slack, past tickets and tribal knowledge.", size=14, color=MUTED)
qs = ["Which service is this?", "Who owns it?", "What depends on it?", "Has this happened before?", "Which runbook do I follow?"]
for i, q in enumerate(qs):
    y = Inches(2.1) + i * Inches(0.8)
    box(s, Inches(6.8), y, Inches(5.8), Inches(0.65))
    text(s, Inches(7.05), y + Inches(0.17), Inches(0.5), Inches(0.4), "?", size=18, color=ROSE, bold=True)
    text(s, Inches(7.5), y + Inches(0.17), Inches(5), Inches(0.4), q, size=17)
text(s, Inches(0.7), Inches(6.35), Inches(12), Inches(0.5),
     [[("The challenge isn't finding information. ", {"color": MUTED}), ("It's understanding how it connects.", {"bold": True, "color": TEAL})]], size=18)

# 3. Why now
s = new_slide("Why now", "Rationale", num=3,
              notes="Three reasons. Freshworks now ships official MCP servers and REST v2 plus workflow webhooks, so agents can act on live tickets. LLMs are cheap and accurate when grounded in a graph. And systems keep fragmenting.")
cards = [
    ("Freshworks opened the door", "Official Freshservice & Freshdesk MCP servers (Freshdesk MCP generally available Sep 2026), REST v2 and Workflow Automator webhooks let agents read and act on live tickets.", TEAL),
    ("LLMs are ready, if grounded", "LLM reasoning is cheap and fluent. A knowledge graph keeps it factual: answers cite real services, owners and incidents.", INDIGO),
    ("Systems keep fragmenting", "More microservices, more tools, more handoffs. Spreadsheet catalogues and tribal knowledge don't scale, and slow incidents cost revenue.", ROSE),
]
for i, (h, b, c) in enumerate(cards):
    card(s, Inches(0.7) + i * Inches(4.07), Inches(2.2), Inches(3.8), Inches(3.9), h, b, accent=c, body_size=15)

# 4. Competition
s = new_slide("Competitive landscape", "Who else solves this", num=4,
              notes="Suites like ServiceNow are powerful but heavy. Developer portals know ownership but don't touch incidents. Built-in helpdesk AI only sees ticket text. Our edge: a live engineering graph plus agents acting inside Freshservice.")
rows = [
    ("Alternative", "Strength", "Gap"),
    ("ServiceNow (CMDB + Now Assist)", "Deep ITSM + CMDB suite", "Heavy, costly, long rollout; CMDB needs manual upkeep"),
    ("Developer portals (Backstage, Compass)", "Service catalogue & ownership", "Not connected to live ITSM incidents; no diagnosis"),
    ("Built-in helpdesk AI copilots", "Summarise / reply within a ticket", "Sees only ticket text: no dependencies, owners, blast radius"),
    ("Do nothing (Slack, wikis, \"ask Alex\")", "Free, familiar", "Slow, inconsistent, depends on a few people"),
]
tbl = s.shapes.add_table(len(rows), 3, Inches(0.7), Inches(1.95), Inches(11.9), Inches(3.4)).table
tbl.columns[0].width = Inches(4.0)
tbl.columns[1].width = Inches(3.3)
tbl.columns[2].width = Inches(4.6)
for r, row in enumerate(rows):
    for c, val in enumerate(row):
        cell = tbl.cell(r, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = BORDER if r == 0 else CARD
        cell.margin_left = cell.margin_right = Inches(0.15)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = val
        run.font.name = FONT
        run.font.size = Pt(13 if r else 12)
        run.font.bold = r == 0 or c == 0
        run.font.color.rgb = WHITE if (r == 0 or c == 0) else MUTED
box(s, Inches(0.7), Inches(5.65), Inches(11.9), Inches(1.05), fill=RGBColor(0x0F, 0x2A, 0x2E), line=TEAL)
text(s, Inches(1.0), Inches(5.8), Inches(11.4), Inches(0.8),
     [[("Our edge  ", {"bold": True, "color": TEAL}),
       ("A living graph of the engineering system, plus agents that act inside Freshservice. Every new ticket gets a diagnosis note automatically, without leaving the service desk.", {"color": WHITE})]],
     size=16, anchor=MSO_ANCHOR.MIDDLE)

# 5. Solution / architecture
s = new_slide("How it works", "Proposed solution", num=5,
              notes="Left to right: Freshservice tickets, groups and KB flow in through REST v2 and our MCP-style connector. They join the knowledge graph and vector store alongside repos and docs. Eight agents reason over it with graph traversal, semantic search and an LLM. The result goes back into Freshservice as a private note, triggered automatically by Workflow Automator.")
cols = [
    ("Sources", ["Freshservice tickets, groups, KB  (live)", "GitHub repos & ZIP / Excel intake", "Jira · Confluence · Slack  (Phase 2)"], TEAL),
    ("Living ontology", ["Neo4j knowledge graph", "Services · Teams · Owners · APIs · Incidents · Runbooks", "Vector store for semantic search"], INDIGO),
    ("8 AI agents", ["Incident Context · Requirement Impact", "Expert Discovery · Blast Radius", "Ontology Mentor · Storyteller · Gaps · Doc Q&A"], INDIGO),
    ("Back in Freshservice", ["Private diagnosis note on the ticket", "Auto-triggered by Workflow Automator webhook", "Explainable: trace + sources"], TEAL),
]
cw, gap, y0, ch = Inches(2.75), Inches(0.3), Inches(2.0), Inches(3.3)
for i, (h, items, c) in enumerate(cols):
    x = Inches(0.7) + i * (cw + gap)
    box(s, x, y0, cw, ch, line=c)
    text(s, x + Inches(0.25), y0 + Inches(0.25), cw - Inches(0.5), Inches(0.75), h, size=17, bold=True, color=c)
    text(s, x + Inches(0.25), y0 + Inches(1.1), cw - Inches(0.5), ch - Inches(1.25), items, size=13, color=WHITE, spacing=1.1)
    if i < 3:
        a = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x + cw + Inches(0.03), y0 + ch / 2 - Inches(0.15), Inches(0.24), Inches(0.3))
        a.fill.solid(); a.fill.fore_color.rgb = MUTED; a.line.fill.background()
text(s, Inches(0.7), Inches(5.6), Inches(11.9), Inches(0.5),
     [[("Hybrid intelligence: ", {"bold": True, "color": WHITE}), ("graph traversal + semantic search + LLM reasoning, with a rule-based fallback when no LLM is available.", {"color": MUTED})]], size=15)
text(s, Inches(0.7), Inches(6.15), Inches(11.9), Inches(0.5),
     [[("MVP: ", {"bold": True, "color": TEAL}), ("incidents → graph → auto-diagnosis · impact analysis · expert finder · blast radius · knowledge gaps · graph explorer", {"color": MUTED})]], size=14)

# 6. Live demo
s = new_slide("Live demo", "See it work", num=6,
              notes="Switch to http://localhost:8000. Follow the demo script in docs/TGAH-Business-Case.md. Backup: Incident Room with query 'payment gateway connection pool error'.")
steps = [
    ("Connect", "Dashboard → Test Connection to the live Freshservice tenant"),
    ("Sync", "Tickets → Incidents, groups → Teams, linked to affected services"),
    ("Explore", "Knowledge Graph → Payment Gateway Service → Blast Radius"),
    ("Diagnose", "AI Diagnose a new ticket → private note appears in Freshservice"),
    ("Automate", "Workflow Automator: Ticket is Raised → webhook → note, no clicks"),
    ("Plan", "Analyzer: \"Add WhatsApp notifications\": agent handoffs + trace"),
]
for i, (h, b) in enumerate(steps):
    col, row = i % 2, i // 2
    x = Inches(0.7) + col * Inches(6.05)
    y = Inches(2.0) + row * Inches(1.5)
    box(s, x, y, Inches(5.85), Inches(1.3))
    circ = box(s, x + Inches(0.25), y + Inches(0.35), Inches(0.6), Inches(0.6), fill=INDIGO, line=None, shape=MSO_SHAPE.OVAL)
    text(s, x + Inches(0.25), y + Inches(0.47), Inches(0.6), Inches(0.4), str(i + 1), size=17, bold=True, align=PP_ALIGN.CENTER)
    text(s, x + Inches(1.1), y + Inches(0.22), Inches(4.5), Inches(0.4), h, size=17, bold=True)
    text(s, x + Inches(1.1), y + Inches(0.62), Inches(4.55), Inches(0.6), b, size=13, color=MUTED)

# 7. Who & why
s = new_slide("Who it's for, and why they'll want it", "Target customers & value", num=7,
              notes="Primary buyer: mid-size software companies running engineering incidents in Freshservice. Secondary: MSPs who constantly face unfamiliar client systems. The value in one line is on the slide.")
card(s, Inches(0.7), Inches(2.0), Inches(5.8), Inches(2.3), "Primary",
     "Mid-size software & digital companies (200–2,000 employees) running IT/engineering incidents in Freshservice, with 20+ microservices and several teams.", accent=TEAL, body_size=15)
card(s, Inches(6.8), Inches(2.0), Inches(5.8), Inches(2.3), "Secondary",
     "Freshservice MSPs supporting many client environments who need fast context on unfamiliar systems.", accent=INDIGO, body_size=15)
text(s, Inches(0.7), Inches(4.55), Inches(11.9), Inches(0.35), "USERS:  service-desk agents  ·  on-call / SRE  ·  tech leads & architects  ·  new engineers", size=12, color=MUTED, bold=True)
box(s, Inches(0.7), Inches(5.1), Inches(11.9), Inches(1.6), fill=RGBColor(0x0F, 0x2A, 0x2E), line=TEAL)
text(s, Inches(1.0), Inches(5.25), Inches(11.3), Inches(1.3),
     "Every incident arrives already diagnosed: likely service, dependencies, past incidents, runbook and escalation path. Teams resolve faster, escalate to the right owner first time, and know what breaks before a change ships.",
     size=18, anchor=MSO_ANCHOR.MIDDLE)

# 8. Business model
s = new_slide("Business model", "Pricing · go-to-market · cost", num=8,
              notes="All figures are working assumptions to be validated with design partners. Pricing is a Marketplace add-on per agent; the free tier drives adoption; the demo video shows a ticket that diagnoses itself.")
card(s, Inches(0.7), Inches(2.0), Inches(3.8), Inches(3.9), "Pricing",
     ["Marketplace add-on for Freshservice Pro & Enterprise", "$8 / agent / month", "Free tier: 25 diagnoses / month", "30-day trial of auto-diagnosis"], accent=TEAL, body_size=14)
card(s, Inches(4.77), Inches(2.0), Inches(3.8), Inches(3.9), "Go-to-market",
     ["Freshworks Marketplace listing + in-product banner", "5-minute onboarding: API key → Sync", "Email trial offer to Pro/Enterprise admins", "3–5 design partners for case studies"], accent=INDIGO, body_size=14)
card(s, Inches(8.84), Inches(2.0), Inches(3.8), Inches(3.9), "Cost to MVP",
     ["3 engineers + part-time designer & PM", "~3 months to production MVP", "~$90–110K (salaries, LLM, hosting)", "Illustrative ARR: 100 customers × 30 agents × $8 × 12 ≈ $288K"], accent=AMBER, body_size=14)
tag(s, Inches(0.7), Inches(6.25), "ASSUMPTIONS", w=Inches(1.5))
text(s, Inches(2.35), Inches(6.29), Inches(10), Inches(0.35), "Prices, costs and ARR are working estimates, to be validated with design partners.", size=12, color=MUTED)

# 9. Metrics
s = new_slide("How we'll know it worked", "Success metrics · 6 months after launch", num=9,
              notes="MTTR is the headline metric. Coverage shows the automation is really running. Correct first escalation shows the graph's ownership data is right. Conversion shows willingness to pay.")
kpis = [("−25%", "MTTR on diagnosed incidents", TEAL), ("≥ 80%", "New incidents auto-diagnosed", INDIGO),
        ("+20%", "Resolved by first team routed", INDIGO), ("≥ 20%", "Trial → paid conversion", TEAL)]
for i, (v, l, c) in enumerate(kpis):
    x = Inches(0.7) + i * Inches(3.03)
    box(s, x, Inches(2.2), Inches(2.8), Inches(3.2))
    text(s, x, Inches(2.8), Inches(2.8), Inches(1.0), v, size=48, bold=True, color=c, align=PP_ALIGN.CENTER)
    text(s, x + Inches(0.25), Inches(4.1), Inches(2.3), Inches(1.0), l, size=15, color=WHITE, align=PP_ALIGN.CENTER)
tag(s, Inches(0.7), Inches(5.9), "TARGETS", w=Inches(1.2))
text(s, Inches(2.05), Inches(5.94), Inches(10), Inches(0.35), "Targets are assumptions; baseline measured on non-diagnosed incidents.", size=12, color=MUTED)

# 10. Risks & roadmap
s = new_slide("Risks & roadmap", "What could go wrong · what's next", num=10,
              notes="Be upfront: diagnosis quality depends on graph quality, and we mitigate with the Knowledge Gap agent. Privacy: private notes and a no-LLM mode. Roadmap turns mocked connectors live and adds a native FDK sidebar and change-risk assessment.")
risks = [
    ("Graph quality drives diagnosis quality", "Knowledge Gap agent flags missing owners, runbooks and docs"),
    ("Trust & privacy of ticket data", "Private notes only; rule-based mode needs no LLM"),
    ("Willingness to pay beyond built-in AI", "Validate with design partners before pricing is final"),
    ("API rate limits & plan restrictions", "Graceful degradation (e.g. CMDB needs higher plans)"),
]
text(s, Inches(0.7), Inches(1.95), Inches(6), Inches(0.4), "RISKS  →  MITIGATION", size=12, color=ROSE, bold=True)
for i, (r, m) in enumerate(risks):
    y = Inches(2.4) + i * Inches(1.05)
    box(s, Inches(0.7), y, Inches(6.6), Inches(0.9))
    text(s, Inches(0.95), y + Inches(0.13), Inches(6.2), Inches(0.35), r, size=14, bold=True)
    text(s, Inches(0.95), y + Inches(0.5), Inches(6.2), Inches(0.35), m, size=12, color=MUTED)
text(s, Inches(7.7), Inches(1.95), Inches(5), Inches(0.4), "PHASE 2 ROADMAP", size=12, color=TEAL, bold=True)
road = ["Live GitHub · Jira · Confluence · Slack connectors", "Freshdesk: link customer tickets to engineering incidents",
        "Native FDK sidebar app on the Freshservice ticket", "Change risk & blast radius for CAB approvals",
        "Graph learns from every resolved ticket"]
box(s, Inches(7.7), Inches(2.4), Inches(4.9), Inches(4.05))
for i, rd in enumerate(road):
    y = Inches(2.65) + i * Inches(0.75)
    dot = box(s, Inches(7.95), y + Inches(0.08), Inches(0.16), Inches(0.16), fill=TEAL, line=None, shape=MSO_SHAPE.OVAL)
    text(s, Inches(8.3), y, Inches(4.1), Inches(0.7), rd, size=14)

# 11. Appendix: built vs planned
s = new_slide("Appendix: what's built vs. planned", "For reviewer Q&A", num=11,
              notes="Being upfront about what's mocked builds trust. Freshservice is fully live; the other connectors share the same adapter interface and are Phase 2.")
items = [
    ("LIVE", TEAL, "Freshservice tickets, groups, KB search, note posting, Workflow Automator webhook (REST v2)"),
    ("BUILT", INDIGO, "Neo4j graph (+ in-memory fallback), vector search, 8 agents, orchestrator, explainability"),
    ("BUILT", INDIGO, "GitHub public-repo import; ZIP / Excel / CSV intake into the graph"),
    ("MOCKED", AMBER, "GitHub PR, Jira, Confluence, Slack, Freshdesk connectors (same adapter interface)"),
    ("BLOCKED", ROSE, "Freshservice agents & assets / CMDB: not available on the trial plan/role"),
    ("PHASE 2", MUTED, "FDK sidebar app; official Freshworks MCP server wiring"),
]
for i, (lbl, c, desc) in enumerate(items):
    y = Inches(2.0) + i * Inches(0.78)
    box(s, Inches(0.7), y, Inches(11.9), Inches(0.65))
    tag(s, Inches(0.95), y + Inches(0.17), lbl, color=c, w=Inches(1.15))
    text(s, Inches(2.4), y + Inches(0.18), Inches(10), Inches(0.4), desc, size=14)

prs.save("/Users/pavankumarh/Documents/CodeAtlas-AI/docs/CodeAtlas-AI-Pitch-Deck.pptx")
print("saved", len(prs.slides), "slides")
