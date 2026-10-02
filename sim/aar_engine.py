"""
Multi-Domain Tactical Decision-Making Trainer - After Action Review (AAR) Engine
Captures event logs, calculates decision friction & latency metrics, and generates
exportable, presentation-grade interactive debrief reports.
"""

import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict

@dataclass
class AAREvent:
    id: str
    sim_time: float
    wall_time: float
    event_type: str           # ORDER_ISSUED, INJECT_TRIGGERED, COMMS_BLOCKED, ENGAGEMENT, CASUALTY
    severity: str             # INFO, WARNING, CRITICAL
    actor: str                # Role or 'SYSTEM' or 'OPFOR'
    title: str
    description: str
    ground_truth_state: Dict[str, Any] = field(default_factory=dict)
    perceived_state: Dict[str, Any] = field(default_factory=dict)
    rationale: str = ""
    divergence_metric: float = 0.0 # Error distance (meters) between truth and perceived target

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class AAREngine:
    def __init__(self, scenario_title: str = "Operation Shattered Shield"):
        self.scenario_title = scenario_title
        self.exercise_start_time: float = time.time()
        self.events: List[AAREvent] = []
        self.decisions_logged: List[Dict[str, Any]] = []
        self.injects_triggered: List[Dict[str, Any]] = []

    def record_event(
        self,
        event_type: str,
        sim_time: float,
        actor: str,
        title: str,
        description: str,
        severity: str = "INFO",
        ground_truth: Optional[Dict[str, Any]] = None,
        perceived: Optional[Dict[str, Any]] = None,
        rationale: str = "",
        divergence: float = 0.0
    ) -> AAREvent:
        event = AAREvent(
            id=f"EVT-{len(self.events) + 1:04d}",
            sim_time=sim_time,
            wall_time=time.time(),
            event_type=event_type,
            severity=severity,
            actor=actor,
            title=title,
            description=description,
            ground_truth_state=ground_truth or {},
            perceived_state=perceived or {},
            rationale=rationale,
            divergence_metric=divergence
        )
        self.events.append(event)
        return event

    def compute_metrics(self) -> Dict[str, Any]:
        """
        Computes analytical training metrics:
        - Average decision latency
        - Friendly fire / divergence incidents
        - Total dropped vs delivered comms
        - Survivability & objective score
        """
        total_orders = sum(1 for e in self.events if e.event_type == "ORDER_ISSUED")
        spoofed_engagements = sum(1 for e in self.events if e.divergence_metric > 80.0)
        comms_events = [e for e in self.events if e.event_type in ["COMMS_SENT", "COMMS_DROPPED"]]
        dropped_comms = sum(1 for e in self.events if e.event_type == "COMMS_DROPPED")

        # Calculate time between first jamming event and first response order
        first_jam = next((e for e in self.events if "JAMMER" in e.event_type or "EW" in e.event_type), None)
        reaction_time_sec = 0.0
        if first_jam:
            subsequent_orders = [e for e in self.events if e.event_type == "ORDER_ISSUED" and e.sim_time >= first_jam.sim_time]
            if subsequent_orders:
                reaction_time_sec = subsequent_orders[0].sim_time - first_jam.sim_time

        # Calculate overall Mission Command Effectiveness Score (0 - 100)
        penalty = (spoofed_engagements * 20) + (dropped_comms * 2)
        score = max(15, min(100, 100 - penalty + (total_orders * 5)))

        return {
            "scenario_title": self.scenario_title,
            "exercise_duration_sim_sec": self.events[-1].sim_time if self.events else 0.0,
            "total_events_logged": len(self.events),
            "total_orders_issued": total_orders,
            "spoofed_divergence_actions": spoofed_engagements,
            "dropped_comms_count": dropped_comms,
            "first_jamming_reaction_sec": round(reaction_time_sec, 1),
            "command_effectiveness_score": round(score, 1),
            "doctrine_rating": "SUPERIOR" if score >= 85 else "ADEQUATE" if score >= 65 else "CRITICAL GAPS OBSERVED"
        }

    def generate_html_report(self) -> str:
        """
        Generates a comprehensive, self-contained standalone HTML/CSS After Action Review report.
        """
        metrics = self.compute_metrics()
        
        event_rows_html = []
        for e in self.events:
            sev_class = "severity-info"
            if e.severity == "CRITICAL":
                sev_class = "severity-critical"
            elif e.severity == "WARNING":
                sev_class = "severity-warning"

            divergence_badge = ""
            if e.divergence_metric > 50.0:
                divergence_badge = f'<span class="badge badge-danger">TARGET DIVERGENCE: {int(e.divergence_metric)}m</span>'

            rationale_html = ""
            if e.rationale:
                rationale_html = f'<div class="event-rationale"><strong>Commander Rationale:</strong> "{e.rationale}"</div>'

            event_rows_html.append(f"""
            <tr class="{sev_class}">
                <td class="font-mono">T+{int(e.sim_time // 60):02d}:{int(e.sim_time % 60):02d}</td>
                <td><span class="badge badge-actor">{e.actor}</span></td>
                <td><strong>{e.title}</strong><br><small>{e.description}</small>{rationale_html}</td>
                <td>{divergence_badge}</td>
                <td><span class="badge">{e.severity}</span></td>
            </tr>
            """)

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AAR Report - {self.scenario_title}</title>
    <style>
        :root {{
            --bg-primary: #ffffff;
            --bg-card: #ffffff;
            --border: #000000;
            --text-main: #000000;
            --text-dim: #52525b;
            --blue-acc: #000000;
            --red-acc: #b91c1c;
            --amber-acc: #b45309;
            --green-acc: #15803d;
        }}
        body {{
            background: var(--bg-primary);
            color: var(--text-main);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
            margin: 0;
            padding: 30px;
        }}
        .report-header {{
            border-bottom: 2px solid var(--border);
            padding-bottom: 20px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .report-header h1 {{
            margin: 0;
            color: var(--blue-acc);
            font-size: 24px;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: var(--bg-card);
            border: 2px solid var(--border);
            border-radius: 6px;
            padding: 16px;
            box-shadow: 3px 3px 0px rgba(0, 0, 0, 0.08);
        }}
        .metric-title {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            color: var(--text-dim);
            letter-spacing: 0.5px;
        }}
        .metric-val {{
            font-size: 28px;
            font-weight: 900;
            color: var(--text-main);
            margin-top: 6px;
            font-family: monospace;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: var(--bg-card);
            border-radius: 6px;
            overflow: hidden;
            border: 2px solid var(--border);
        }}
        th, td {{
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid var(--border);
            font-size: 13px;
        }}
        th {{
            background: #f4f4f5;
            text-transform: uppercase;
            color: var(--text-dim);
            font-size: 11px;
            letter-spacing: 0.5px;
            font-weight: 800;
        }}
        .font-mono {{ font-family: monospace; }}
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            background: #f4f4f5;
            border: 1px solid #000;
            color: #000;
        }}
        .badge-actor {{ background: #000000; color: #ffffff; }}
        .badge-danger {{ background: #fef2f2; border-color: #b91c1c; color: #b91c1c; }}
        .severity-critical {{ background: #fff5f5; }}
        .severity-warning {{ background: #fffbeb; }}
        .event-rationale {{
            margin-top: 6px;
            padding: 6px 10px;
            background: #f4f4f5;
            border-left: 3px solid #000000;
            font-size: 12px;
            color: #000000;
            border-radius: 0 4px 4px 0;
            font-style: italic;
        }}
        .btn-print {{
            background: #000000;
            color: #ffffff;
            border: 2px solid #000000;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: 700;
            cursor: pointer;
        }}
        @media print {{
            body {{ background: #fff; color: #000; padding: 0; }}
            .btn-print {{ display: none; }}
            .metric-card, table {{ background: #fff; border: 1px solid #ccc; }}
            th, td {{ border-bottom: 1px solid #eee; color: #000; }}
            .event-rationale {{ background: #f0f9ff; color: #0369a1; }}
        }}
    </style>
</head>
<body>
    <div class="report-header">
        <div>
            <h1>AFTER ACTION REVIEW // EXERCISE DEBRIEF</h1>
            <div style="color: var(--text-dim); margin-top: 4px; font-size: 13px;">
                Scenario: <strong>{self.scenario_title}</strong> &bull; Generated: {time.strftime('%Y-%m-%d %H:%M:%SZ', time.gmtime())}
            </div>
        </div>
        <button class="btn-print" onclick="window.print()">PRINT / EXPORT PDF</button>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-title">Effectiveness Score</div>
            <div class="metric-val" style="color: {'var(--green-acc)' if metrics['command_effectiveness_score'] >= 75 else 'var(--amber-acc)'};">
                {metrics['command_effectiveness_score']}%
            </div>
            <small style="color: var(--text-dim);">{metrics['doctrine_rating']}</small>
        </div>
        <div class="metric-card">
            <div class="metric-title">EW Reaction Time</div>
            <div class="metric-val">{metrics['first_jamming_reaction_sec']}s</div>
            <small style="color: var(--text-dim);">Jamming to Mitigating Order</small>
        </div>
        <div class="metric-card">
            <div class="metric-title">Spoof / Divergence Incidents</div>
            <div class="metric-val" style="color: {'var(--red-acc)' if metrics['spoofed_divergence_actions'] > 0 else 'var(--green-acc)'};">
                {metrics['spoofed_divergence_actions']}
            </div>
            <small style="color: var(--text-dim);">Actions on Spoofed Data</small>
        </div>
        <div class="metric-card">
            <div class="metric-title">Dropped Comms</div>
            <div class="metric-val">{metrics['dropped_comms_count']}</div>
            <small style="color: var(--text-dim);">Severed Transmissions</small>
        </div>
        <div class="metric-card">
            <div class="metric-title">Total Orders Issued</div>
            <div class="metric-val">{metrics['total_orders_issued']}</div>
            <small style="color: var(--text-dim);">Team Decision Actions</small>
        </div>
    </div>

    <h2 style="font-size: 16px; text-transform: uppercase; color: var(--blue-acc); margin-top: 30px; letter-spacing: 0.5px;">
        Chronological Event Timeline & Decision Points
    </h2>

    <table>
        <thead>
            <tr>
                <th style="width: 80px;">Sim Time</th>
                <th style="width: 140px;">Actor / Unit</th>
                <th>Event & Trainee Action</th>
                <th style="width: 180px;">Perception Divergence</th>
                <th style="width: 90px;">Status</th>
            </tr>
        </thead>
        <tbody>
            {"".join(event_rows_html) if event_rows_html else '<tr><td colspan="5" style="text-align:center;color:var(--text-dim);">No exercise events recorded.</td></tr>'}
        </tbody>
    </table>
</body>
</html>
"""
        return html_template

    def generate_pdf_report(self) -> bytes:
        """
        Generates a standard-compliant, standalone PDF 1.4 document containing:
        - Executive classification & scenario metadata
        - Command effectiveness scorecard & analytical metrics
        - Detailed chronological decision & event audit trail with commander rationale
        - Evaluator sign-off block
        Zero external dependencies; runs on Python standard library.
        """
        metrics = self.compute_metrics()

        def safe_pdf_str(text: str) -> str:
            raw = str(text or "")
            cleaned = raw.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\')
            return ''.join(c if (32 <= ord(c) < 127) else ' ' for c in cleaned)

        class PDFBuilder:
            def __init__(self):
                self.pages = []
                self.current_page = []

            def start_page(self):
                if self.current_page:
                    self.pages.append(self.current_page)
                self.current_page = []

            def add_cmd(self, cmd: str):
                self.current_page.append(cmd)

            def draw_rect(self, x: float, y: float, w: float, h: float,
                          r: float, g: float, b: float,
                          stroke: bool = False, sr: float = 0, sg: float = 0, sb: float = 0, sw: float = 1):
                self.add_cmd(f"{r:.3f} {g:.3f} {b:.3f} rg {x:.1f} {y:.1f} {w:.1f} {h:.1f} re f")
                if stroke:
                    self.add_cmd(f"{sr:.3f} {sg:.3f} {sb:.3f} RG {sw:.1f} w {x:.1f} {y:.1f} {w:.1f} {h:.1f} re S")

            def draw_line(self, x1: float, y1: float, x2: float, y2: float,
                          r: float, g: float, b: float, w: float = 1):
                self.add_cmd(f"{r:.3f} {g:.3f} {b:.3f} RG {w:.1f} w {x1:.1f} {y1:.1f} m {x2:.1f} {y2:.1f} l S")

            def draw_text(self, text: str, x: float, y: float,
                          font: str = "/F1", size: float = 10,
                          r: float = 0, g: float = 0, b: float = 0):
                t = safe_pdf_str(text)
                self.add_cmd(f"BT {font} {size:.1f} Tf {r:.3f} {g:.3f} {b:.3f} rg {x:.1f} {y:.1f} Td ({t}) Tj ET")

            def compile(self) -> bytes:
                if self.current_page:
                    self.pages.append(self.current_page)

                num_pages = max(1, len(self.pages))
                page_obj_ids = [4 + i * 2 for i in range(num_pages)]
                content_obj_ids = [5 + i * 2 for i in range(num_pages)]

                objects = []
                # obj 1: Catalog
                objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
                # obj 2: Pages
                kids = " ".join(f"{pid} 0 R" for pid in page_obj_ids)
                objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {num_pages} >>".encode("latin-1"))
                # obj 3: Fonts
                fonts = (
                    b"<< /Font << "
                    b"/F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> "
                    b"/F2 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >> "
                    b"/F3 << /Type /Font /Subtype /Type1 /BaseFont /Courier >> "
                    b"/F4 << /Type /Font /Subtype /Type1 /BaseFont /Courier-Bold >> "
                    b">> >>"
                )
                objects.append(fonts)

                for i in range(num_pages):
                    cmds = self.pages[i] if i < len(self.pages) else []
                    content_bytes = "\n".join(cmds).encode("latin-1")
                    pid = page_obj_ids[i]
                    cid = content_obj_ids[i]

                    page_obj = (
                        f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                        f"/Resources 3 0 R /Contents {cid} 0 R >>"
                    ).encode("latin-1")
                    objects.append(page_obj)

                    stream_obj = (
                        f"<< /Length {len(content_bytes)} >>\nstream\n".encode("latin-1") +
                        content_bytes +
                        b"\nendstream"
                    )
                    objects.append(stream_obj)

                pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
                xref_offsets = []
                for i, obj in enumerate(objects):
                    xref_offsets.append(len(pdf))
                    pdf.extend(f"{i + 1} 0 obj\n".encode("latin-1"))
                    pdf.extend(obj)
                    pdf.extend(b"\nendobj\n")

                xref_start = len(pdf)
                pdf.extend(b"xref\n")
                pdf.extend(f"0 {len(objects) + 1}\n".encode("latin-1"))
                pdf.extend(b"0000000000 65535 f \n")
                for off in xref_offsets:
                    pdf.extend(f"{off:010d} 00000 n \n".encode("latin-1"))

                pdf.extend(b"trailer\n")
                pdf.extend(f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode("latin-1"))
                pdf.extend(b"startxref\n")
                pdf.extend(f"{xref_start}\n%%EOF\n".encode("latin-1"))

                return bytes(pdf)

        pdf = PDFBuilder()
        pdf.start_page()

        # Top Classification Banner
        pdf.draw_rect(36, 744, 540, 24, 0.06, 0.09, 0.16)
        pdf.draw_text("RESTRICTED // MULTI-DOMAIN DMUU TRAINER // EXERCISE DEBRIEF REPORT", 46, 752, font="/F2", size=9, r=0.22, g=0.74, b=0.97)
        pdf.draw_text(f"NATO / C2 STANDARDS", 460, 752, font="/F1", size=8, r=0.6, g=0.7, b=0.8)

        # Header Title Area
        pdf.draw_rect(36, 680, 540, 60, 0.10, 0.14, 0.22)
        pdf.draw_text("AFTER ACTION REVIEW (AAR) DEBRIEF", 46, 720, font="/F2", size=16, r=1.0, g=1.0, b=1.0)
        pdf.draw_text(f"SCENARIO: {metrics.get('scenario_title', self.scenario_title).upper()}", 46, 704, font="/F2", size=10, r=0.22, g=0.74, b=0.97)
        
        sim_sec = int(metrics.get("exercise_duration_sim_sec", 0))
        meta_str = f"DURATION: T+{sim_sec // 60:02d}:{sim_sec % 60:02d} | TOTAL EVENTS: {metrics.get('total_events_logged', 0)} | DOCTRINE RATING: {metrics.get('doctrine_rating', 'ADEQUATE')}"
        pdf.draw_text(meta_str, 46, 690, font="/F1", size=8, r=0.75, g=0.82, b=0.9)

        # Scorecard Tiles (5 metrics)
        score_y = 612
        card_w = 100
        card_h = 56
        gap = 10
        xs = [36 + i * (card_w + gap) for i in range(5)]

        # Card 1: Effectiveness Score
        eff_score = metrics.get("command_effectiveness_score", 100)
        score_col = (0.13, 0.65, 0.35) if eff_score >= 75 else (0.85, 0.45, 0.08)
        pdf.draw_rect(xs[0], score_y, card_w, card_h, 0.94, 0.96, 0.98, stroke=True, sr=0.8, sg=0.85, sb=0.9)
        pdf.draw_text("COMMAND SCORE", xs[0] + 6, score_y + 42, font="/F2", size=7, r=0.4, g=0.5, b=0.6)
        pdf.draw_text(f"{eff_score}%", xs[0] + 6, score_y + 18, font="/F2", size=18, r=score_col[0], g=score_col[1], b=score_col[2])
        pdf.draw_text(metrics.get("doctrine_rating", "ADEQUATE"), xs[0] + 6, score_y + 6, font="/F1", size=6, r=0.45, g=0.5, b=0.55)

        # Card 2: EW Reaction Latency
        pdf.draw_rect(xs[1], score_y, card_w, card_h, 0.94, 0.96, 0.98, stroke=True, sr=0.8, sg=0.85, sb=0.9)
        pdf.draw_text("EW REACTION", xs[1] + 6, score_y + 42, font="/F2", size=7, r=0.4, g=0.5, b=0.6)
        pdf.draw_text(f"{metrics.get('first_jamming_reaction_sec', 0)}s", xs[1] + 6, score_y + 18, font="/F2", size=18, r=0.15, g=0.2, b=0.3)
        pdf.draw_text("Jamming to Mitigating Order", xs[1] + 6, score_y + 6, font="/F1", size=6, r=0.45, g=0.5, b=0.55)

        # Card 3: Divergence Incidents
        div_count = metrics.get("spoofed_divergence_actions", 0)
        div_col = (0.85, 0.15, 0.15) if div_count > 0 else (0.13, 0.65, 0.35)
        pdf.draw_rect(xs[2], score_y, card_w, card_h, 0.94, 0.96, 0.98, stroke=True, sr=0.8, sg=0.85, sb=0.9)
        pdf.draw_text("TARGET DIVERGENCE", xs[2] + 6, score_y + 42, font="/F2", size=7, r=0.4, g=0.5, b=0.6)
        pdf.draw_text(f"{div_count}", xs[2] + 6, score_y + 18, font="/F2", size=18, r=div_col[0], g=div_col[1], b=div_col[2])
        pdf.draw_text("Actions on Spoofed Data", xs[2] + 6, score_y + 6, font="/F1", size=6, r=0.45, g=0.5, b=0.55)

        # Card 4: Dropped Comms
        pdf.draw_rect(xs[3], score_y, card_w, card_h, 0.94, 0.96, 0.98, stroke=True, sr=0.8, sg=0.85, sb=0.9)
        pdf.draw_text("DROPPED COMMS", xs[3] + 6, score_y + 42, font="/F2", size=7, r=0.4, g=0.5, b=0.6)
        pdf.draw_text(f"{metrics.get('dropped_comms_count', 0)}", xs[3] + 6, score_y + 18, font="/F2", size=18, r=0.15, g=0.2, b=0.3)
        pdf.draw_text("Severed Transmissions", xs[3] + 6, score_y + 6, font="/F1", size=6, r=0.45, g=0.5, b=0.55)

        # Card 5: Orders Issued
        pdf.draw_rect(xs[4], score_y, card_w, card_h, 0.94, 0.96, 0.98, stroke=True, sr=0.8, sg=0.85, sb=0.9)
        pdf.draw_text("ORDERS ISSUED", xs[4] + 6, score_y + 42, font="/F2", size=7, r=0.4, g=0.5, b=0.6)
        pdf.draw_text(f"{metrics.get('total_orders_issued', 0)}", xs[4] + 6, score_y + 18, font="/F2", size=18, r=0.08, g=0.48, b=0.78)
        pdf.draw_text("Directives Logged", xs[4] + 6, score_y + 6, font="/F1", size=6, r=0.45, g=0.5, b=0.55)

        def draw_table_header(y_pos: float):
            pdf.draw_rect(36, y_pos, 540, 18, 0.12, 0.18, 0.28)
            pdf.draw_text("TIME", 42, y_pos + 5, font="/F2", size=8, r=1.0, g=1.0, b=1.0)
            pdf.draw_text("ACTOR / ROLE", 95, y_pos + 5, font="/F2", size=8, r=1.0, g=1.0, b=1.0)
            pdf.draw_text("SEV", 185, y_pos + 5, font="/F2", size=8, r=1.0, g=1.0, b=1.0)
            pdf.draw_text("EVENT & COMMANDER DECISION RATIONALE", 225, y_pos + 5, font="/F2", size=8, r=1.0, g=1.0, b=1.0)
            pdf.draw_text("DIVERGENCE", 495, y_pos + 5, font="/F2", size=8, r=1.0, g=1.0, b=1.0)

        # Timeline Header
        current_y = 590
        pdf.draw_text("CHRONOLOGICAL DECISION TIMELINE & EVENT AUDIT", 36, current_y, font="/F2", size=11, r=0.1, g=0.15, b=0.25)
        current_y -= 22
        draw_table_header(current_y)
        current_y -= 18

        # Render Events
        events_to_render = self.events if self.events else [
            AAREvent(
                id="EVT-0000",
                sim_time=0.0,
                wall_time=time.time(),
                event_type="EXERCISE_STARTED",
                severity="INFO",
                actor="SYSTEM",
                title="Exercise Commenced",
                description="Simulation initialized in contested electromagnetic spectrum."
            )
        ]

        row_idx = 0
        for e in events_to_render:
            has_rationale = bool(e.rationale)
            row_height = 36 if has_rationale else 22

            # Check page break
            if current_y - row_height < 50:
                # Add page footer before break
                pdf.draw_line(36, 40, 576, 40, 0.8, 0.85, 0.9)
                pdf.draw_text("DMUU TRAINER // DEBRIEF CONTINUES ON NEXT PAGE", 36, 28, font="/F1", size=7, r=0.5, g=0.55, b=0.6)

                pdf.start_page()
                # Secondary page top banner
                pdf.draw_rect(36, 754, 540, 18, 0.06, 0.09, 0.16)
                pdf.draw_text(f"RESTRICTED // {metrics.get('scenario_title', self.scenario_title).upper()} // TIMELINE CONT.", 46, 759, font="/F2", size=8, r=0.22, g=0.74, b=0.97)
                current_y = 730
                draw_table_header(current_y)
                current_y -= 18

            bg_r, bg_g, bg_b = (0.97, 0.98, 0.99) if (row_idx % 2 == 0) else (1.0, 1.0, 1.0)
            pdf.draw_rect(36, current_y - row_height + 18, 540, row_height, bg_r, bg_g, bg_b, stroke=True, sr=0.88, sg=0.91, sb=0.94, sw=0.5)

            # Left severity indicator bar
            bar_col = (0.2, 0.6, 0.9) # INFO
            if e.severity == "CRITICAL":
                bar_col = (0.85, 0.15, 0.15)
            elif e.severity == "WARNING":
                bar_col = (0.9, 0.6, 0.05)
            pdf.draw_rect(36, current_y - row_height + 18, 3, row_height, bar_col[0], bar_col[1], bar_col[2])

            m = int(e.sim_time // 60)
            s = int(e.sim_time % 60)
            time_str = f"T+{m:02d}:{s:02d}"
            pdf.draw_text(time_str, 42, current_y + 4, font="/F3", size=8, r=0.2, g=0.25, b=0.35)
            pdf.draw_text(e.actor[:12], 95, current_y + 4, font="/F2", size=8, r=0.1, g=0.2, b=0.4)
            pdf.draw_text(e.severity[:4], 185, current_y + 4, font="/F2", size=7, r=bar_col[0], g=bar_col[1], b=bar_col[2])

            title_txt = e.title[:45]
            pdf.draw_text(title_txt, 225, current_y + 4, font="/F2", size=8, r=0.08, g=0.12, b=0.18)

            if e.divergence_metric > 30.0:
                pdf.draw_text(f"ERR: {int(e.divergence_metric)}m", 495, current_y + 4, font="/F2", size=8, r=0.85, g=0.15, b=0.15)
            else:
                pdf.draw_text("VERIFIED", 495, current_y + 4, font="/F1", size=7, r=0.3, g=0.6, b=0.3)

            if has_rationale:
                rat_txt = f'Rationale: "{e.rationale[:58]}"'
                pdf.draw_text(rat_txt, 225, current_y - 10, font="/F1", size=7, r=0.15, g=0.4, b=0.65)

            current_y -= row_height
            row_idx += 1

        # Sign-off block at bottom of final page
        if current_y < 90:
            pdf.start_page()
            current_y = 720

        current_y -= 15
        pdf.draw_rect(36, current_y - 48, 540, 48, 0.94, 0.96, 0.98, stroke=True, sr=0.8, sg=0.85, sb=0.9)
        pdf.draw_text("EXCON EVALUATOR SIGN-OFF & CERTIFICATION", 46, current_y - 12, font="/F2", size=8, r=0.1, g=0.2, b=0.35)
        pdf.draw_text("This AAR debrief certifies trainee performance under contested electronic warfare and cyber degradation.", 46, current_y - 24, font="/F1", size=7, r=0.4, g=0.45, b=0.5)
        pdf.draw_text("EVALUATOR SIGNATURE: _______________________      DATE: ___________________", 46, current_y - 40, font="/F3", size=8, r=0.2, g=0.25, b=0.3)

        return pdf.compile()
