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


def new_slide(title, kicker=None, notes=None):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG
    if kicker:
        text(s, Inches(0.7), Inches(0.5), Inches(10), Inches(0.35), kicker.upper(), size=12, color=TEAL, bold=True)
    text(s, Inches(0.7), Inches(0.85), Inches(12), Inches(0.9), title, size=32, bold=True)
    text(s, Inches(10.1), Inches(7.0), Inches(2.6), Inches(0.3), f"CodeAtlas AI  ·  {len(prs.slides)}", size=10, color=MUTED, align=PP_ALIGN.RIGHT)
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
text(s, Inches(1.1), Inches(4.0), Inches(11), Inches(0.5), "Every Freshservice incident and change, diagnosed and routed automatically.", size=18, color=MUTED)
text(s, Inches(1.1), Inches(6.2), Inches(11), Inches(0.4), [[("Pavan Kumar H", {"bold": True, "color": WHITE}), ("   ·   The Great Agent Hackathon", {"color": MUTED})]], size=16)
s.notes_slide.notes_text_frame.text = "Introduce yourself and the one-line pitch: CodeAtlas diagnoses and routes every Freshservice incident and change before anyone opens it, with engineering context from the knowledge graph."

# 2. Problem
s = new_slide("A ticket says what broke. Nobody knows why.", "The problem",
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
s = new_slide("Why now", "Rationale",
              notes="Three shifts. Freshworks now exposes live tickets and changes to outside agents: REST v2, Workflow Automator events, official MCP servers and FDK apps. Agents have matured from answering to acting: specialised agents hand off work, and a knowledge graph keeps the LLM factual. Meanwhile engineering context keeps fragmenting. Together they make an agent that works inside Freshservice possible today; the strip at the bottom is exactly what we built.")
text(s, Inches(0.7), Inches(1.65), Inches(11.9), Inches(0.4),
     "Three shifts make an AI agent that works inside Freshservice possible today.", size=16, color=MUTED)
pillars = [
    ("Freshworks is open", TEAL, [
        "REST v2 + Workflow Automator push every ticket and change to agents",
        "Official Freshservice & Freshdesk MCP servers (Freshdesk GA Sep 2026)",
        "FDK apps can run agents inside the product UI",
    ]),
    ("Agents now act", INDIGO, [
        "Specialised agents hand off work: impact → ontology → experts",
        "LLM reasoning is cheap; a knowledge graph keeps it factual and cited",
        "Agents write back: notes, routing, change risk",
    ]),
    ("Context is scattered", ROSE, [
        "Ownership and dependencies live in GitHub, runbooks and people's heads",
        "Service desks see ticket text, not the system behind it",
        "Every wrong escalation adds to MTTR and lost revenue",
    ]),
]
cw, cy, chh = Inches(3.8), Inches(2.25), Inches(2.8)
for i, (h, c, bullets) in enumerate(pillars):
    x = Inches(0.7) + i * Inches(4.05)
    box(s, x, cy, cw, chh)
    box(s, x, cy + Inches(0.28), Inches(0.06), Inches(0.4), fill=c, line=None, shape=MSO_SHAPE.RECTANGLE)
    text(s, x + Inches(0.3), cy + Inches(0.26), cw - Inches(0.5), Inches(0.45), h, size=17, bold=True)
    text(s, x + Inches(0.3), cy + Inches(0.85), cw - Inches(0.5), chh - Inches(1.0),
         [[("•  ", {"color": c, "bold": True}), (b, {})] for b in bullets], size=13, color=MUTED, spacing=1.1)
text(s, Inches(0.7), Inches(5.3), Inches(11.9), Inches(0.3), "WHAT THIS MAKES POSSIBLE: CODEATLAS INSIDE FRESHSERVICE", size=11, color=TEAL, bold=True)
flow = [
    ("Ticket or change", "raised in Freshservice", WHITE),
    ("Workflow Automator", "calls CodeAtlas instantly", WHITE),
    ("8 AI agents + graph", "GitHub · KB · LLM reasoning", INDIGO),
    ("Written back", "diagnosis, routing, blast radius", TEAL),
]
fw, fg, fy, fh = Inches(2.7), Inches(0.37), Inches(5.65), Inches(1.0)
for i, (h, sub, c) in enumerate(flow):
    x = Inches(0.7) + i * (fw + fg)
    box(s, x, fy, fw, fh, line=c if c != WHITE else BORDER)
    text(s, x + Inches(0.2), fy + Inches(0.18), fw - Inches(0.4), Inches(0.35), h, size=14, bold=True, color=c)
    text(s, x + Inches(0.2), fy + Inches(0.55), fw - Inches(0.4), Inches(0.35), sub, size=11, color=MUTED)
    if i < len(flow) - 1:
        a = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x + fw + Inches(0.07), fy + fh / 2 - Inches(0.12), Inches(0.23), Inches(0.24))
        a.fill.solid(); a.fill.fore_color.rgb = MUTED; a.line.fill.background()

# 4. Competition
s = new_slide("Competitive landscape", "Who else solves this",
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
s = new_slide("How it works", "Proposed solution",
              notes="Left to right: Freshservice tickets, groups and KB flow in through REST v2 and our MCP-style connector. They join the knowledge graph and vector store alongside repos and docs. Eight agents reason over it with graph traversal, semantic search and an LLM. The result goes back into Freshservice as a private note, triggered automatically by Workflow Automator.")
cols = [
    ("Sources", ["Freshservice tickets, groups, KB  (live)", "GitHub repos & ZIP / Excel intake", "Jira · Confluence · Slack  (Phase 2)"], TEAL),
    ("Living ontology", ["Neo4j knowledge graph", "Services · Teams · Owners · APIs · Incidents · Runbooks", "Vector store for semantic search"], INDIGO),
    ("8 AI agents", ["Incident Context · Requirement Impact", "Expert Discovery · Blast Radius", "Ontology Mentor · Storyteller · Gaps · Doc Q&A"], INDIGO),
    ("Back in Freshservice", ["Private diagnosis note + auto-routing to the right group", "Blast-radius note on every new Change", "Auto-triggered by Workflow Automator", "Explainable: trace + sources"], TEAL),
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

# Architecture
s = new_slide("Architecture", "How the pieces connect",
              notes="Frontend pages call the FastAPI backend. The orchestrator routes each request to one agent or a multi-agent pipeline. Agents reason over the Neo4j graph and vector store, GitHub changes and the Gemini LLM. Freshservice Workflow Automator calls in on ticket and change events; CodeAtlas writes back notes and group assignments through REST v2.")
box(s, Inches(0.7), Inches(1.85), Inches(11.9), Inches(5.0), fill=WHITE, line=None, radius=0.02)
s.shapes.add_picture("/Users/pavankumarh/Documents/CodeAtlas-AI/docs/architecture-1.png", Inches(1.95), Inches(1.95), height=Inches(4.8))

# Freshservice module map
s = new_slide("Every module plugs into Freshservice", "Integration map",
              notes="Freshservice knows what broke, who reported it and who is on call. CodeAtlas knows how the system is wired, what changed and who wrote the code. Three flows are live on our tenant today; CMDB is designed but our trial plan does not include it.")
flows = [
    ("Ticket is raised", "Incident Context Agent", "Diagnosis note + auto-route to the right group", "LIVE", TEAL),
    ("Change is created", "Impact → Ontology → Expert pipeline", "Blast radius, risk, CAB reviewers", "LIVE", TEAL),
    ("Sync", "Freshservice connector", "Tickets → Incidents, groups → Teams", "LIVE", TEAL),
    ("KB search", "Incident Context Agent", "KB articles cited in each diagnosis", "LIVE", TEAL),
    ("CMDB relationships", "Knowledge Graph", "Code-derived dependencies as CI links", "DESIGNED", AMBER),
    ("Problems & KB drafts", "Knowledge Gap Agent", "Recurring incidents → Problem, KB drafts", "PHASE 2", MUTED),
]
text(s, Inches(0.95), Inches(1.9), Inches(3), Inches(0.3), "FRESHSERVICE EVENT", size=11, color=MUTED, bold=True)
text(s, Inches(3.75), Inches(1.9), Inches(3.2), Inches(0.3), "CODEATLAS", size=11, color=MUTED, bold=True)
text(s, Inches(7.05), Inches(1.9), Inches(4), Inches(0.3), "WRITTEN BACK", size=11, color=MUTED, bold=True)
for i, (event, who, result, lbl, c) in enumerate(flows):
    y = Inches(2.25) + i * Inches(0.75)
    box(s, Inches(0.7), y, Inches(11.9), Inches(0.62))
    text(s, Inches(0.95), y + Inches(0.17), Inches(2.7), Inches(0.35), event, size=14, bold=True)
    text(s, Inches(3.75), y + Inches(0.18), Inches(3.2), Inches(0.35), who, size=13, color=INDIGO)
    text(s, Inches(7.05), y + Inches(0.18), Inches(4.2), Inches(0.35), result, size=12, color=MUTED)
    tag(s, Inches(11.3), y + Inches(0.16), lbl, color=c, w=Inches(1.1))

# 6. Live demo
s = new_slide("Live demo", "See it work",
              notes="Create the ticket and the change fresh during the demo so judges see the before/after. Backup if the tunnel fails: the brain icon on the Freshservice Integration page runs the same diagnosis and posts the same note.")
steps = [
    ("Raise a ticket", "In Freshservice: \"DB connection pool exhausted on Payment Service after deploy\""),
    ("Diagnose + route", "Workflow Automator fires → note posted, ticket lands in Database Team"),
    ("Show the trace", "Freshservice Integration page → brain icon → live agent trace · Activity Log"),
    ("Raise a change", "In Freshservice: \"Upgrade SMTP relay config for Notification Service\""),
    ("Blast radius", "3-agent pipeline → impact, downstream services, CAB reviewers on the change"),
    ("Explore", "Knowledge Graph → Notification Service → Blast Radius highlights the same services"),
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
s = new_slide("Who it's for", "Target customers & users",
              notes="Primary buyer: mid-size software companies running engineering incidents in Freshservice. Secondary: MSPs who constantly face unfamiliar client systems. Then walk the four users left to right: each gets something different from the same knowledge graph, and three of the four get it without leaving Freshservice.")
card(s, Inches(0.7), Inches(1.9), Inches(5.8), Inches(1.75), "Primary",
     "Mid-size software & digital companies (200–2,000 employees) running IT/engineering incidents in Freshservice, with 20+ microservices and several teams.", accent=TEAL, body_size=14)
card(s, Inches(6.8), Inches(1.9), Inches(5.8), Inches(1.75), "Secondary",
     "Freshservice MSPs supporting many client environments who need fast context on unfamiliar systems.", accent=INDIGO, body_size=14)
text(s, Inches(0.7), Inches(3.9), Inches(11.9), Inches(0.3), "WHO USES IT, AND WHAT THEY GET", size=11, color=TEAL, bold=True)
users = [
    ("Service-desk agents", "Tickets arrive diagnosed and already in the right group, with no guessing which team owns it.", "Ticket note + auto-routing", TEAL),
    ("On-call / SRE", "Suspected cause, the recent commit or config change behind it, past incidents, runbook, who to call.", "Ticket note · Incident Room", ROSE),
    ("Change managers / CAB", "Blast radius, risk and suggested reviewers on every new change, before it is approved.", "Change note · Knowledge Graph", AMBER),
    ("Tech leads & new hires", "Impact of a new requirement, owners and experts, and a map of how the system fits together.", "Analyzer · Experts · Graph", INDIGO),
]
uw, ug, uy, uh = Inches(2.8), Inches(0.233), Inches(4.2), Inches(1.75)
for i, (role, gets, where, c) in enumerate(users):
    x = Inches(0.7) + i * (uw + ug)
    box(s, x, uy, uw, uh)
    box(s, x, uy, uw, Inches(0.06), fill=c, line=None, shape=MSO_SHAPE.RECTANGLE)
    text(s, x + Inches(0.2), uy + Inches(0.2), uw - Inches(0.4), Inches(0.3), role, size=14, bold=True)
    text(s, x + Inches(0.2), uy + Inches(0.55), uw - Inches(0.4), Inches(0.85), gets, size=11, color=MUTED, spacing=1.1)
    text(s, x + Inches(0.2), uy + uh - Inches(0.35), uw - Inches(0.4), Inches(0.25), where, size=10, color=c, bold=True)
box(s, Inches(0.7), Inches(6.12), Inches(11.9), Inches(0.72), fill=RGBColor(0x0F, 0x2A, 0x2E), line=TEAL)
text(s, Inches(1.0), Inches(6.17), Inches(11.3), Inches(0.62),
     "Every incident and change arrives with engineering context: faster resolution, the right owner first time, and no surprises when a change ships.",
     size=15, anchor=MSO_ANCHOR.MIDDLE)

# Value proposition
s = new_slide("Why customers will want it", "Value proposition",
              notes="Read the statement as written; it is the answer to 'why would I buy this'. Then contrast: doing nothing means people hunt for context; the alternatives are either heavy (ServiceNow CMDB), disconnected from tickets (developer portals), or blind to the system (built-in copilots). Close on the proof strip: everything on it is shown live in the demo.")
box(s, Inches(0.7), Inches(1.85), Inches(11.9), Inches(1.45), fill=RGBColor(0x0F, 0x2A, 0x2E), line=TEAL)
text(s, Inches(1.0), Inches(1.95), Inches(11.3), Inches(1.25),
     [[("Every Freshservice ticket and change arrives already diagnosed, routed to the right team and risk-assessed, ", {"bold": True, "color": WHITE}),
       ("without anyone leaving Freshservice. Teams stop hunting for context across GitHub, runbooks and chat, resolve faster, and know what breaks before a change ships.", {"color": WHITE})]],
     size=18, anchor=MSO_ANCHOR.MIDDLE)
compare = [
    ("Instead of doing nothing", ROSE, [
        ("Today", "L1 guesses the team; tickets bounce between queues"),
        ("Today", "On-call spends the first part of every incident hunting for context"),
        ("Today", "Changes are approved without knowing what depends on them"),
    ]),
    ("Instead of an alternative", INDIGO, [
        ("ServiceNow CMDB", "heavy rollout, relationships kept up by hand"),
        ("Developer portals", "know owners, but never see a ticket"),
        ("Built-in AI copilots", "read ticket text, not the system behind it"),
    ]),
]
for i, (h, c, rows) in enumerate(compare):
    x = Inches(0.7) + i * Inches(6.1)
    box(s, x, Inches(3.55), Inches(5.8), Inches(2.2))
    box(s, x, Inches(3.55 + 0.28), Inches(0.06), Inches(0.4), fill=c, line=None, shape=MSO_SHAPE.RECTANGLE)
    text(s, x + Inches(0.3), Inches(3.55 + 0.25), Inches(5.2), Inches(0.4), h, size=17, bold=True)
    text(s, x + Inches(0.3), Inches(3.55 + 0.8), Inches(5.2), Inches(1.3),
         [[(f"{k}: " if k != "Today" else "✕  ", {"color": c, "bold": True}), (v, {})] for k, v in rows], size=13, color=MUTED, spacing=1.1)
text(s, Inches(0.7), Inches(5.95), Inches(11.9), Inches(0.3), "CODEATLAS INSTEAD  ·  SHOWN LIVE IN THE DEMO", size=11, color=TEAL, bold=True)
proofs = ["Ticket auto-routed, zero clicks", "Change note shows blast radius", "Every claim cites its evidence"]
for i, pr in enumerate(proofs):
    x = Inches(0.7) + i * Inches(4.0)
    box(s, x, Inches(6.25), Inches(3.8), Inches(0.55), line=TEAL)
    text(s, x + Inches(0.2), Inches(6.25 + 0.15), Inches(3.4), Inches(0.3), "✓  " + pr, size=12, color=WHITE, bold=True)

# 8. Business model
s = new_slide("Business model", "Pricing · go-to-market · cost",
              notes="All figures are working assumptions to be validated with design partners. Pricing: a free tier gets the graph into Freshservice; Pro is where it runs itself on every ticket; Enterprise adds change risk and more connectors. Go-to-market lives inside the Freshworks ecosystem: Marketplace, a 5-minute connect, and a demo of a ticket diagnosing itself. Economics: roughly $100K to reach a production MVP against an illustrative $288K ARR, with LLM cost in cents per diagnosis.")
text(s, Inches(0.7), Inches(1.75), Inches(11.9), Inches(0.3), "PRICING  ·  FRESHWORKS MARKETPLACE ADD-ON FOR FRESHSERVICE PRO & ENTERPRISE", size=11, color=TEAL, bold=True)
tiers = [
    ("FREE", "Free", MUTED, ["Knowledge graph explorer", "Manual AI Diagnose, 25 tickets / month", "Gets the graph into Freshservice"]),
    ("PRO", "$8 / agent / month", TEAL, ["Auto-diagnosis on every new ticket", "Auto-routing to the right group", "30-day free trial"]),
    ("ENTERPRISE  ·  LATER", "Custom", AMBER, ["Change blast radius & CAB reviewers", "Jira · Confluence · Slack connectors", "CMDB sync on eligible plans"]),
]
tw, tg, ty, th = Inches(3.8), Inches(0.25), Inches(2.05), Inches(1.9)
for i, (name, price, c, feats) in enumerate(tiers):
    x = Inches(0.7) + i * (tw + tg)
    box(s, x, ty, tw, th, line=c if c != MUTED else BORDER)
    text(s, x + Inches(0.25), ty + Inches(0.18), tw - Inches(0.5), Inches(0.25), name, size=11, color=c, bold=True)
    text(s, x + Inches(0.25), ty + Inches(0.42), tw - Inches(0.5), Inches(0.45), price, size=22, bold=True, color=WHITE)
    text(s, x + Inches(0.25), ty + Inches(1.0), tw - Inches(0.5), Inches(0.85),
         [[("•  ", {"color": c, "bold": True}), (f, {})] for f in feats], size=12, color=MUTED, spacing=1.05)
gy, gh = Inches(4.2), Inches(2.3)
box(s, Inches(0.7), gy, Inches(7.05), gh)
box(s, Inches(0.7), gy + Inches(0.25), Inches(0.06), Inches(0.4), fill=INDIGO, line=None, shape=MSO_SHAPE.RECTANGLE)
text(s, Inches(1.0), gy + Inches(0.22), Inches(6.5), Inches(0.4), "Go-to-market: inside the Freshworks ecosystem", size=16, bold=True)
steps = [
    ("Discover", "Marketplace listing + in-product banner for eligible admins"),
    ("Try", "Connect in 5 minutes: paste API key → Sync → see your graph"),
    ("Convert", "Trial email to Pro/Enterprise admins + \"a ticket diagnoses itself\" video"),
    ("Prove", "3–5 design partners, case studies with measured MTTR drop"),
]
text(s, Inches(1.0), gy + Inches(0.75), Inches(6.5), Inches(1.5),
     [[(f"{i + 1}. {k}   ", {"color": INDIGO, "bold": True}), (v, {})] for i, (k, v) in enumerate(steps)], size=12, color=MUTED, spacing=1.05)
cx = Inches(8.0)
box(s, cx, gy, Inches(4.6), gh)
box(s, cx, gy + Inches(0.25), Inches(0.06), Inches(0.4), fill=AMBER, line=None, shape=MSO_SHAPE.RECTANGLE)
text(s, cx + Inches(0.3), gy + Inches(0.22), Inches(4.1), Inches(0.4), "Cost & economics", size=16, bold=True)
text(s, cx + Inches(0.3), gy + Inches(0.75), Inches(4.1), Inches(1.5), [
    [("MVP  ", {"color": AMBER, "bold": True}), ("~$90–110K in ~3 months", {})],
    [("Team  ", {"color": AMBER, "bold": True}), ("3 engineers + part-time design & PM", {})],
    [("Scope  ", {"color": AMBER, "bold": True}), ("auth, multi-tenant, Marketplace review", {})],
    [("Run  ", {"color": AMBER, "bold": True}), ("LLM cost in cents per diagnosis", {})],
    [("ARR  ", {"color": AMBER, "bold": True}), ("≈ $288K illustrative (100 × 30 × $8 × 12)", {})],
], size=12, color=MUTED, spacing=1.05)
tag(s, Inches(0.7), Inches(6.62), "ASSUMPTIONS", w=Inches(1.5))
text(s, Inches(2.35), Inches(6.66), Inches(7.5), Inches(0.3), "Prices, costs and ARR are working estimates, to be validated with design partners.", size=11, color=MUTED)

# 9. Metrics
s = new_slide("How we'll know it worked", "Success metrics · 6 months after launch",
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
s = new_slide("Risks & roadmap", "What could go wrong · what's next",
              notes="Be upfront: diagnosis quality depends on graph quality, and we mitigate with the Knowledge Gap agent. Privacy: private notes and a no-LLM mode. Roadmap turns mocked connectors live and adds a native FDK sidebar and change-risk assessment.")
risks = [
    ("Graph quality drives diagnosis quality", "Knowledge Gap agent flags missing owners, runbooks and docs"),
    ("Trust & privacy of ticket data", "Private notes only; rule-based mode needs no LLM"),
    ("Willingness to pay beyond built-in AI", "Validate with design partners before pricing is final"),
    ("Auto-routing sends a ticket to the wrong queue", "Only assigns unassigned tickets; reason is written in the note"),
    ("API rate limits & plan restrictions", "Graceful degradation (e.g. CMDB needs higher plans)"),
]
text(s, Inches(0.7), Inches(1.95), Inches(6), Inches(0.4), "RISKS  →  MITIGATION", size=12, color=ROSE, bold=True)
for i, (r, m) in enumerate(risks):
    y = Inches(2.4) + i * Inches(0.88)
    box(s, Inches(0.7), y, Inches(6.6), Inches(0.78))
    text(s, Inches(0.95), y + Inches(0.1), Inches(6.2), Inches(0.35), r, size=14, bold=True)
    text(s, Inches(0.95), y + Inches(0.43), Inches(6.2), Inches(0.35), m, size=12, color=MUTED)
text(s, Inches(7.7), Inches(1.95), Inches(5), Inches(0.4), "PHASE 2 ROADMAP", size=12, color=TEAL, bold=True)
road = ["Live Jira · Confluence · Slack connectors", "Freshdesk: link customer tickets to engineering incidents",
        "Native FDK sidebar app on tickets & changes", "CMDB sync · Problems from recurring incidents · on-call aware escalation",
        "Graph learns from every resolved ticket"]
box(s, Inches(7.7), Inches(2.4), Inches(4.9), Inches(4.05))
for i, rd in enumerate(road):
    y = Inches(2.65) + i * Inches(0.75)
    dot = box(s, Inches(7.95), y + Inches(0.08), Inches(0.16), Inches(0.16), fill=TEAL, line=None, shape=MSO_SHAPE.OVAL)
    text(s, Inches(8.3), y, Inches(4.1), Inches(0.7), rd, size=14)

# 11. Appendix: built vs planned
s = new_slide("Appendix: what's built vs. planned", "For reviewer Q&A",
              notes="Being upfront about what's mocked builds trust. Freshservice is fully live; the other connectors share the same adapter interface and are Phase 2.")
items = [
    ("LIVE", TEAL, "Freshservice tickets, groups, KB search, diagnosis notes, auto-routing, Workflow Automator (REST v2)"),
    ("LIVE", TEAL, "Freshservice Changes: 3-agent impact pipeline + graph blast radius posted as a change note"),
    ("LIVE", TEAL, "GitHub recent releases, commits, config diffs (secrets redacted) in every diagnosis"),
    ("BUILT", INDIGO, "Neo4j graph (+ in-memory fallback), vector search, 8 agents, orchestrator, explainability, repo/ZIP intake"),
    ("MOCKED", AMBER, "Jira, Confluence, Slack, Freshdesk connectors (same adapter interface)"),
    ("BLOCKED", ROSE, "Freshservice agents & assets / CMDB: not available on the trial plan/role"),
    ("PHASE 2", MUTED, "FDK sidebar app; official Freshworks MCP server wiring"),
]
for i, (lbl, c, desc) in enumerate(items):
    y = Inches(1.95) + i * Inches(0.7)
    box(s, Inches(0.7), y, Inches(11.9), Inches(0.6))
    tag(s, Inches(0.95), y + Inches(0.15), lbl, color=c, w=Inches(1.15))
    text(s, Inches(2.4), y + Inches(0.17), Inches(10), Inches(0.4), desc, size=13)

prs.save("/Users/pavankumarh/Documents/CodeAtlas-AI/docs/CodeAtlas-AI-Pitch-Deck.pptx")
print("saved", len(prs.slides), "slides")
