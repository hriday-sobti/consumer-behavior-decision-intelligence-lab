"""Compiles the comprehensive, publication-grade analytical project report to a perfectly balanced 6-page PDF using ReportLab."""

import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

PDF_OUTPUT_PATH = Path("docs/customer_behavior_decision_intelligence_report.pdf")
FIGURES_DIR = Path("docs/report_figures")

class NumberedCanvas(canvas.Canvas):
    """Adds running headers and footers with dynamic total page count."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Suppress headers/footers on title cover

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running Header
        self.drawString(45, 11 * 72 - 30, "Consumer Behavior Decision Intelligence Lab | Analytical Project Dossier")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(45, 11 * 72 - 34, 8.5 * 72 - 45, 11 * 72 - 34)

        # Running Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 45, 28, page_str)
        self.drawString(45, 28, "Author: Hriday Singh Sobti | Production Technical Dossier")
        self.line(45, 38, 8.5 * 72 - 45, 38)
        self.restoreState()


def build_pdf_report():
    print(f"Compiling balanced PDF report to {PDF_OUTPUT_PATH}...")
    doc = SimpleDocTemplate(
        str(PDF_OUTPUT_PATH),
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=42,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#1F4E78")   # Deep navy
    c_secondary = colors.HexColor("#2E8B57") # Muted teal
    c_dark = colors.HexColor("#0F172A")      # Slate 900
    c_body = colors.HexColor("#334155")      # Slate 700
    c_gray_bg = colors.HexColor("#F8FAFC")
    c_border = colors.HexColor("#CBD5E1")

    # Typography Hierarchy
    title_style = ParagraphStyle(
        'CoverTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=c_primary, spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'CoverSub', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10.5, leading=14, textColor=c_body, spaceAfter=8
    )
    meta_style = ParagraphStyle(
        'Meta', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11, textColor=c_body, spaceAfter=8
    )
    h1_style = ParagraphStyle(
        'Header1', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=c_primary,
        spaceBefore=10, spaceAfter=4, keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11, textColor=c_body, spaceAfter=5
    )
    callout_style = ParagraphStyle(
        'Callout', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=7.5, leading=10.5, textColor=colors.HexColor("#1E293B"), spaceAfter=0
    )
    table_cell = ParagraphStyle(
        'TableCell', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7, leading=9.5, textColor=c_body
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold', parent=table_cell, fontName='Helvetica-Bold', textColor=c_dark
    )
    table_cell_header = ParagraphStyle(
        'TableHeader', parent=table_cell, fontName='Helvetica-Bold', textColor=colors.white
    )

    story = []

    # =========================================================================
    # COVER / HEADER BANNER
    # =========================================================================
    story.append(Paragraph("Consumer Behavior Decision Intelligence Lab", title_style))
    story.append(Paragraph("A Multi-Dimensional Transactional Behavioral Modeling & Decision-Support System", subtitle_style))
    story.append(Paragraph("<b>Author:</b> Hriday Singh Sobti &nbsp;|&nbsp; <b>Framework:</b> Python 3.10+, PostgreSQL & SQLite, Streamlit, Power BI &nbsp;|&nbsp; <b>Test Verification:</b> 229 Passing Scenarios", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=2, spaceAfter=8))

    # =========================================================================
    # 1. EXECUTIVE SUMMARY
    # =========================================================================
    story.append(Paragraph("1. Executive Summary", h1_style))
    exec_summary_text = (
        "Enterprise transactional ledgers record granular operational sales entries—invoice numbers, product codes, "
        "timestamps, units, and price points—but conceal underlying account purchasing behavior. In raw sales files, recurring wholesale "
        "commercial accounts appear identical in schema to one-off retail consumers. Standard aggregate reporting answers "
        "what products moved, but fails to reveal account-level concentration, order cadence decay, basket drift, or churn risk. "
        "The <b>Consumer Behavior Decision Intelligence Lab (CBDIL)</b> establishes an end-to-end analytical architecture that bridges "
        "raw transaction logs and commercial decision-support. Built on two years of longitudinal transaction records from the "
        "official UCI Online Retail II repository (1,067,371 rows), the system implements four-tier event precedence classification, "
        "multi-schema PostgreSQL modeling, five-dimensional customer feature engineering, silhouette-optimized behavioral clustering, "
        "longitudinal lifecycle state machines across 98,557 customer-months, and six deterministic decision signals. "
        "All analytical conclusions are auditable and supported by 229 automated verification tests."
    )
    story.append(Paragraph(exec_summary_text, body_style))

    # Key Quantitative Metrics Table
    summary_data = [
        [Paragraph("Metric Dimension", table_cell_header), Paragraph("Quantified Value", table_cell_header), Paragraph("Empirical Context / Significance", table_cell_header)],
        [Paragraph("Raw Source Transactions", table_cell_bold), Paragraph("1,067,371 rows", table_cell), Paragraph("Two continuous longitudinal years (Dec 2009 – Dec 2011)", table_cell)],
        [Paragraph("Cleaned Staging Records", table_cell_bold), Paragraph("1,033,034 rows", table_cell), Paragraph("Post composite-key deduplication (removed 34,337 duplicate lines)", table_cell)],
        [Paragraph("Validated Purchase Lines", table_cell_bold), Paragraph("779,423 lines", table_cell), Paragraph("Isolated from 19,494 formal cancellations and 3,462 reversals", table_cell)],
        [Paragraph("Unique Customer Accounts", table_cell_bold), Paragraph("5,878 accounts", table_cell), Paragraph("Distinct identified commercial and retail buyer entities", table_cell)],
        [Paragraph("Eligible Behavioral Cohort", table_cell_bold), Paragraph("4,023 accounts", table_cell), Paragraph("Sufficient history filter: >= 2 orders and >= 90 days tenure", table_cell)],
        [Paragraph("Cumulative Valid Spend", table_cell_bold), Paragraph("£17,374,252.42", table_cell), Paragraph("Gross purchasing value across 36,969 validated order baskets", table_cell)],
        [Paragraph("Value Concentration", table_cell_bold), Paragraph("Top 5% = 53.8% spend", table_cell), Paragraph("Pareto distribution: top 20% generate 83.1% of eligible volume", table_cell)],
        [Paragraph("Selected Behavioral Segments", table_cell_bold), Paragraph("K = 3 Segments", table_cell), Paragraph("Silhouette score = 0.2749, satisfying min 5% cluster share rule", table_cell)],
        [Paragraph("High-Value Softening Risk", table_cell_bold), Paragraph("261 accounts", table_cell), Paragraph("Top spend quintile with >= 25% drop in recent 90-day spend", table_cell)],
    ]
    t_summary = Table(summary_data, colWidths=[120, 100, 302])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_gray_bg]),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 8))

    # =========================================================================
    # 2. NEW CONTRIBUTIONS AND IMPROVEMENTS
    # =========================================================================
    story.append(Paragraph("2. New Contributions and Improvements", h1_style))
    story.append(Paragraph(
        "CBDIL departs substantially from generic customer segmentation tutorials and standard sales dashboards. "
        "The project introduces specific methodological, behavioral, and architectural enhancements:", body_style
    ))

    contrib_data = [
        [Paragraph("Capability / Dimension", table_cell_header), Paragraph("Standard Baseline Approach", table_cell_header), Paragraph("CBDIL Analytical Contribution & Systematic Improvement", table_cell_header)],
        [
            Paragraph("Event Classification", table_cell_bold),
            Paragraph("Cancellations and returns are deleted blindly or mixed into sales.", table_cell),
            Paragraph("Enforces explicit 4-tier precedence (CANCELLATION > REVERSAL > VALID_PURCHASE > INVALID), capturing negative transactions without deflating historical order velocity.", table_cell)
        ],
        [
            Paragraph("Behavioral Dimensions", table_cell_bold),
            Paragraph("Compresses customer behavior into a single composite RFM score.", table_cell),
            Paragraph("Constructs a 5-dimensional behavioral representation: Value, Activity, Assortment Breadth, Interval Stability, and 90-day Momentum.", table_cell)
        ],
        [
            Paragraph("Customer Eligibility", table_cell_bold),
            Paragraph("Single-order or brand-new accounts deleted to fit models.", table_cell),
            Paragraph("Flags accounts with insufficient history (31.5% of population) via metadata flags, maintaining population auditability while isolating unsupervised clustering.", table_cell)
        ],
        [
            Paragraph("Model Selection Rule", table_cell_bold),
            Paragraph("Cluster count selected subjectively by visual inspection.", table_cell),
            Paragraph("Automated selection rule: smallest K whose silhouette score is >= 90% of peak, subject to a minimum 5% cluster share constraint.", table_cell)
        ],
        [
            Paragraph("Longitudinal Dynamics", table_cell_bold),
            Paragraph("Static single-point-in-time lifetime snapshots.", table_cell),
            Paragraph("Constructs 98,557 monthly customer snapshots across 25 months with a 5-state lifecycle engine (Reactivated > Emerging > Dormant > Softening > Engaged).", table_cell)
        ],
        [
            Paragraph("Actionable Decision Layer", table_cell_bold),
            Paragraph("Descriptive summaries without operational next steps.", table_cell),
            Paragraph("Evaluates 6 deterministic decision signals linked to testing playbooks with 20% holdout control designs and guardrail metrics.", table_cell)
        ],
        [
            Paragraph("Governance & Audit", table_cell_bold),
            Paragraph("Validation performed ad-hoc or omitted entirely.", table_cell),
            Paragraph("Continuous audit layer tracking 6 systematic data quality controls directly inside the reporting layer with PASS/WARNING status.", table_cell)
        ],
    ]
    t_contrib = Table(contrib_data, colWidths=[105, 145, 272])
    t_contrib.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_gray_bg]),
    ]))
    story.append(t_contrib)
    story.append(Spacer(1, 8))

    # =========================================================================
    # 3. THE BUSINESS PROBLEM & ANALYTICAL WORKFLOW
    # =========================================================================
    story.append(Paragraph("3. Business Problem & Analytical Workflow", h1_style))
    story.append(Paragraph(
        "Commercial distributors face significant operational vulnerability when revenue is heavily concentrated among wholesale clients. "
        "Because wholesale ordering cycles are naturally lumpy, relying on historical spend totals masks whether a key account is thriving, "
        "stagnating, or actively defecting to a competitor. CBDIL establishes a structured analytical progression:", body_style
    ))
    story.append(Paragraph(
        "<b>Raw Transactions</b> (1.06M rows) &rarr; <b>Data Quality & Deduplication</b> (Class 1-4) &rarr; "
        "<b>Relational Dimensional Modeling</b> (Fact Order & Fact Transaction) &rarr; "
        "<b>5-Dimensional Feature Engineering</b> (Value, Activity, Breadth, Stability, Momentum) &rarr; "
        "<b>Behavioral Segmentation</b> (K=3 Cluster Profiles) &rarr; "
        "<b>Lifecycle State Machines</b> (98.5k snapshots) &rarr; "
        "<b>Decision Signals</b> (261 softening accounts flagged) &rarr; "
        "<b>Interactive Workbenches</b> (Streamlit & Power BI).", callout_style
    ))
    story.append(Spacer(1, 8))

    # =========================================================================
    # 4. DATA QUALITY & EVENT CLASSIFICATION
    # =========================================================================
    story.append(Paragraph("4. Data Quality, Event Classification & Governance", h1_style))
    story.append(Paragraph(
        "Profiling identified significant data quality anomalies that would severely distort naive calculations. "
        "The cleaning pipeline resolves these through deterministic, auditable transformations without modifying raw inputs:", body_style
    ))

    dq_data = [
        [Paragraph("Data Quality Issue", table_cell_header), Paragraph("Affected Rows", table_cell_header), Paragraph("Share", table_cell_header), Paragraph("Analytical Risk", table_cell_header), Paragraph("Implemented Pipeline Treatment", table_cell_header)],
        [Paragraph("Unattributed Rows", table_cell_bold), Paragraph("243,007", table_cell), Paragraph("22.77%", table_cell), Paragraph("Cannot link to customer lifecycle", table_cell), Paragraph("Assigned Class 4 (INVALID_OR_UNUSABLE); excluded from customer features but audited in gross sales.", table_cell)],
        [Paragraph("Duplicate Lines", table_cell_bold), Paragraph("34,337", table_cell), Paragraph("3.22%", table_cell), Paragraph("Overcounts item quantities and spend", table_cell), Paragraph("Deduplicated via composite hash on invoice, SKU, customer, date, quantity, and unit price.", table_cell)],
        [Paragraph("Order Cancellations", table_cell_bold), Paragraph("19,494", table_cell), Paragraph("1.83%", table_cell), Paragraph("Distorts gross purchase order frequency", table_cell), Paragraph("Classified as Class 1 (CANCELLATION) via 'C' prefix; isolated to compute account-level return rates.", table_cell)],
        [Paragraph("Non-Cancellation Negatives", table_cell_bold), Paragraph("3,462", table_cell), Paragraph("0.32%", table_cell), Paragraph("Distorts sales value with damaged goods", table_cell), Paragraph("Classified as Class 2 (REVERSAL_OR_RETURN); separated from gross purchase totals.", table_cell)],
        [Paragraph("Zero / Negative Prices", table_cell_bold), Paragraph("6,207", table_cell), Paragraph("0.58%", table_cell), Paragraph("Samples & bad-debt accounting entries", table_cell), Paragraph("Classified as Class 4; filtered prior to commercial value modeling.", table_cell)],
    ]
    t_dq = Table(dq_data, colWidths=[100, 50, 42, 115, 215])
    t_dq.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_gray_bg]),
    ]))
    story.append(t_dq)
    story.append(Spacer(1, 8))

    # =========================================================================
    # 5. MACRO TRENDS & EMPIRICAL FINDINGS (FIGURES 1 & 2)
    # =========================================================================
    story.append(Paragraph("5. Macro Purchasing Dynamics & Concentration Analysis", h1_style))
    story.append(Paragraph(
        "Analysis of gross spend and order volume across the 24-month observation window reveals strong commercial seasonality "
        "and extreme revenue concentration:", body_style
    ))

    # Embed Figure 1
    fig1_path = FIGURES_DIR / "fig1_monthly_trend.png"
    if fig1_path.exists():
        story.append(Image(str(fig1_path), width=480, height=210))
        story.append(Spacer(1, 3))
        story.append(Paragraph(
            "<b>Figure 1: Monthly Gross Spend and Order Volume Trend (2009-12 to 2011-12).</b> "
            "<i>What it shows:</i> Discrete monthly transaction value (bars, left axis) and total invoice counts (line, right axis). "
            "<i>Insight:</i> Strong annual Q4 seasonality peaking in November (£1.46M in 2010 and £1.51M in 2011) reflecting commercial wholesale "
            "holiday inventory stocking, followed by an operational contraction in January. "
            "<i>Actionable takeaway:</i> Purchasing slowdowns in Q1 represent expected distributor replenishment lulls, whereas decelerations in Q3/Q4 signal abnormal account attrition.",
            callout_style
        ))
        story.append(Spacer(1, 6))

    # Embed Figure 2
    fig2_path = FIGURES_DIR / "fig2_lorenz_curve.png"
    if fig2_path.exists():
        story.append(Image(str(fig2_path), width=430, height=215))
        story.append(Spacer(1, 3))
        story.append(Paragraph(
            "<b>Figure 2: Customer Spend Concentration (Empirical Lorenz Curve).</b> "
            "<i>What it shows:</i> Cumulative customer population percentile vs cumulative gross spend contribution. "
            "<i>Insight:</i> Purchasing revenue conforms to an extreme Pareto distribution: the top 1% of accounts drive 26.4% of total spend, "
            "the top 5% drive 53.8%, and the top 20% generate 83.1% (£13.75M of £16.55M eligible spend). "
            "<i>Actionable takeaway:</i> Financial performance is heavily exposed to a narrow wholesale core, validating the need for dedicated account capacity protection.",
            callout_style
        ))
        story.append(Spacer(1, 8))

    # =========================================================================
    # 6. BEHAVIORAL SEGMENTATION & DEEP DIVE (FIGURE 3)
    # =========================================================================
    story.append(Paragraph("6. Behavioral Segmentation Architecture & Cluster Profiles", h1_style))
    story.append(Paragraph(
        "K-Means clustering was executed on the 4,023 eligible accounts across standardized log-spend, log-orders, recency, "
        "log-SKUs, interpurchase gap, and momentum variables. K=3 was selected deterministically based on silhouette maximization "
        "(0.2749) and minimum cluster size representation:", body_style
    ))

    # Embed Figure 3
    fig3_path = FIGURES_DIR / "fig3_segment_comparison.png"
    if fig3_path.exists():
        story.append(Image(str(fig3_path), width=470, height=195))
        story.append(Spacer(1, 3))
        story.append(Paragraph(
            "<b>Figure 3: Value Contribution Across Empirical Behavioral Segments.</b> "
            "<i>What it shows:</i> Gross historical spend (£ Millions) and relative spend share across the three identified segments. "
            "<i>Insight:</i> The customer base bifurcates sharply: 28.9% of accounts (Segment 2) capture 75.0% of cumulative revenue (£12.41M), "
            "while 44.1% of accounts (Segment 1) account for only 12.4% (£2.05M) despite their numerical dominance.",
            callout_style
        ))
        story.append(Spacer(1, 6))

    seg_table_data = [
        [Paragraph("Segment Name", table_cell_header), Paragraph("Account Count", table_cell_header), Paragraph("Spend Share", table_cell_header), Paragraph("Median Spend", table_cell_header), Paragraph("Median Orders", table_cell_header), Paragraph("Median Recency", table_cell_header), Paragraph("Median SKUs", table_cell_header), Paragraph("Strategic Inquiry", table_cell_header)],
        [
            Paragraph("High-Value Stable", table_cell_bold),
            Paragraph("1,164 (28.9%)", table_cell),
            Paragraph("£12.41M (75.0%)", table_cell),
            Paragraph("£4,967.17", table_cell),
            Paragraph("13 orders", table_cell),
            Paragraph("23 days", table_cell),
            Paragraph("173 SKUs", table_cell),
            Paragraph("What delivery terms and inventory SLAs are required to protect these accounts?", table_cell)
        ],
        [
            Paragraph("Emerging Engagement", table_cell_bold),
            Paragraph("1,084 (27.0%)", table_cell),
            Paragraph("£2.09M (12.6%)", table_cell),
            Paragraph("£1,259.86", table_cell),
            Paragraph("4 orders", table_cell),
            Paragraph("29 days", table_cell),
            Paragraph("65 SKUs", table_cell),
            Paragraph("Which category affinity bundles can accelerate basket adoption in this cohort?", table_cell)
        ],
        [
            Paragraph("Low-Activity / Long-Recency", table_cell_bold),
            Paragraph("1,775 (44.1%)", table_cell),
            Paragraph("£2.05M (12.4%)", table_cell),
            Paragraph("£815.69", table_cell),
            Paragraph("3 orders", table_cell),
            Paragraph("266 days", table_cell),
            Paragraph("40 SKUs", table_cell),
            Paragraph("What proportion represents seasonal holiday buyers vs ceased operations?", table_cell)
        ],
    ]
    t_seg = Table(seg_table_data, colWidths=[90, 60, 65, 55, 45, 50, 45, 112])
    t_seg.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_gray_bg]),
    ]))
    story.append(t_seg)
    story.append(Spacer(1, 8))

    # =========================================================================
    # 7. DECISION SIGNALS & ACTION STRATEGIES (FIGURE 4)
    # =========================================================================
    story.append(Paragraph("7. Deterministic Decision Signals & Action Strategies", h1_style))
    story.append(Paragraph(
        "CBDIL converts behavioral metrics into structured decision triggers by evaluating six deterministic, rule-based signals. "
        "Each signal carries an objective threshold, an account population, a severity tier, and attached audit limitations:", body_style
    ))

    # Embed Figure 4
    fig4_path = FIGURES_DIR / "fig4_decision_signals.png"
    if fig4_path.exists():
        story.append(Image(str(fig4_path), width=470, height=200))
        story.append(Spacer(1, 3))
        story.append(Paragraph(
            "<b>Figure 4: Triggered Decision Signals by Severity Tier.</b> "
            "<i>What it shows:</i> Volume of customer accounts meeting deterministic signal trigger rules, broken down by severity tier (High, Medium, Low). "
            "<i>Insight:</i> While positive growth is widespread (2,044 accounts exhibiting positive momentum), severe retention risks are concentrated "
            "in 261 accounts flagged under HIGH_VALUE_SOFTENING, representing £2.56M in cumulative historical spend.",
            callout_style
        ))
        story.append(Spacer(1, 6))

    signal_table_data = [
        [Paragraph("Signal Identifier", table_cell_header), Paragraph("Exact Trigger Rule", table_cell_header), Paragraph("Accounts", table_cell_header), Paragraph("Cumulative Spend", table_cell_header), Paragraph("Possible Business Action", table_cell_header), Paragraph("Evaluation KPI / Guardrail", table_cell_header)],
        [
            Paragraph("HIGH_VALUE_SOFTENING", table_cell_bold),
            Paragraph("Spend >= P80 (£2,910) and Value Momentum <= -25%", table_cell),
            Paragraph("261", table_cell),
            Paragraph("£2,559,881.18", table_cell),
            Paragraph("Commercial account manager check-in to review pricing and availability.", table_cell),
            Paragraph("90d Spend Recovery % / Return Rate Guardrail", table_cell)
        ],
        [
            Paragraph("HIGH_FREQUENCY_LOW_VALUE", table_cell_bold),
            Paragraph("Orders >= P80 (8 orders) and AOV <= P40 (£233.82)", table_cell),
            Paragraph("325", table_cell),
            Paragraph("£992,802.24", table_cell),
            Paragraph("Implement minimum order size thresholds or freight incentives.", table_cell),
            Paragraph("Average Order Value (AOV) / Order Frequency", table_cell)
        ],
        [
            Paragraph("EMERGING_BROADENING", table_cell_bold),
            Paragraph("State = EMERGING and Product Breadth Momentum > 0%", table_cell),
            Paragraph("440", table_cell),
            Paragraph("£269,788.27", table_cell),
            Paragraph("Present category affinity recommendation bundles during checkout.", table_cell),
            Paragraph("60d Repeat Conversion / Category Return Rate", table_cell)
        ],
        [
            Paragraph("HISTORICAL_VALUE_DORMANT", table_cell_bold),
            Paragraph("Spend >= P80 (£2,910) and State = DORMANT (>120d)", table_cell),
            Paragraph("193", table_cell),
            Paragraph("£1,474,863.53", table_cell),
            Paragraph("Evaluate seasonal re-engagement offer with 20% holdout control.", table_cell),
            Paragraph("Reactivation Rate / Discount Margin Erosion", table_cell)
        ],
        [
            Paragraph("BROAD_ENGAGEMENT_SOFTENING", table_cell_bold),
            Paragraph("SKUs >= P70 (85 SKUs) and Frequency Momentum <= -25%", table_cell),
            Paragraph("345", table_cell),
            Paragraph("£2,180,615.61", table_cell),
            Paragraph("Audit catalog stock-outs across core wholesale lines.", table_cell),
            Paragraph("Frequency Recovery / Order Cancellation Rate", table_cell)
        ],
        [
            Paragraph("POSITIVE_MOMENTUM", table_cell_bold),
            Paragraph("Spend Momentum >= +25% and Freq Momentum >= +25%", table_cell),
            Paragraph("2,044", table_cell),
            Paragraph("£8,400,789.95", table_cell),
            Paragraph("Guarantee supply-chain capacity and priority inventory allocation.", table_cell),
            Paragraph("OTIF Order Fulfillment / Delivery Delay Rate", table_cell)
        ],
    ]
    t_sig = Table(signal_table_data, colWidths=[90, 105, 38, 65, 114, 110])
    t_sig.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_gray_bg]),
    ]))
    story.append(t_sig)
    story.append(Spacer(1, 8))

    # =========================================================================
    # 8. DETAILED DASHBOARD ARCHITECTURE & USER JOURNEY
    # =========================================================================
    story.append(Paragraph("8. Dashboard Architecture & Interactive User Journey", h1_style))
    story.append(Paragraph(
        "The analytical deliverables are operationalized through two cohesive dashboard interfaces: an interactive Streamlit workbench "
        "and a star-schema Power BI semantic reporting model. Both interfaces follow an identical six-page navigation logic:", body_style
    ))

    dash_pages = [
        [Paragraph("Dashboard Page", table_cell_header), Paragraph("Primary User Question Answered", table_cell_header), Paragraph("Key Visuals & Interactive Elements", table_cell_header), Paragraph("Decision Supported", table_cell_header)],
        [
            Paragraph("Page 1: Overview", table_cell_bold),
            Paragraph("What is the overall scale and spend concentration of the customer base?", table_cell),
            Paragraph("KPI cards, Monthly spend/order trend, Empirical Lorenz curve, Lifecycle state bars.", table_cell),
            Paragraph("Macro business health assessment and key-account volume monitoring.", table_cell)
        ],
        [
            Paragraph("Page 2: Segments", table_cell_bold),
            Paragraph("How do customers separate behaviorally across value, recency, and breadth?", table_cell),
            Paragraph("Segment metrics matrix, Recency vs log-spend scatter plot, SKU breadth boxplots.", table_cell),
            Paragraph("Identifying structural differences in wholesale vs retail buyer groups.", table_cell)
        ],
        [
            Paragraph("Page 3: Deep Dive", table_cell_bold),
            Paragraph("What specific behavioral characteristics define an individual segment?", table_cell),
            Paragraph("Recent vs prior 90-day spend comparison bars, active monthly trend, inquiry cards.", table_cell),
            Paragraph("Formulating tailored merchandising and contract terms for specific segments.", table_cell)
        ],
        [
            Paragraph("Page 4: Behavior Over Time", table_cell_bold),
            Paragraph("Where is customer behavior moving month-over-month across lifecycle states?", table_cell),
            Paragraph("Monthly stacked state area chart, state transition matrix heatmap, cohort retention grid.", table_cell),
            Paragraph("Measuring attrition rates from active into softening and dormant states.", table_cell)
        ],
        [
            Paragraph("Page 5: Decision Signals", table_cell_bold),
            Paragraph("Which specific customer accounts warrant proactive review or capacity protection?", table_cell),
            Paragraph("Signal inventory bar chart, severity distribution breakdown, customer drill-down table.", table_cell),
            Paragraph("Isolating high-risk accounts (e.g., 261 softening clients) for targeted outreach.", table_cell)
        ],
        [
            Paragraph("Page 6: Customer Explorer", table_cell_bold),
            Paragraph("Why is a specific customer classified under a particular segment or signal?", table_cell),
            Paragraph("Customer ID searchable dropdown, diagnostic metrics, classification rationale box.", table_cell),
            Paragraph("Pre-contact audit of individual wholesale client purchasing history and risk factors.", table_cell)
        ],
    ]
    t_dash = Table(dash_pages, colWidths=[85, 125, 145, 167])
    t_dash.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_gray_bg]),
    ]))
    story.append(t_dash)
    story.append(Spacer(1, 8))

    # =========================================================================
    # 9. END-TO-END CUSTOMER WALKTHROUGH
    # =========================================================================
    story.append(Paragraph("9. End-to-End Account Walkthrough (Customer #14156)", h1_style))
    story.append(Paragraph(
        "To verify that the system operates as a connected pipeline rather than isolated scripts, consider the empirical trajectory "
        "of Customer #14156:", body_style
    ))
    story.append(Paragraph(
        "1. <b>Raw Ingestion:</b> Account #14156 places 156 discrete orders across Ireland (EIRE) between Dec 2009 and Nov 2011.<br/>"
        "2. <b>Cleaning & Classification:</b> Pipeline deduplicates 14 duplicate line entries and classifies 2,610 valid purchase lines and 89 formal cancellation lines.<br/>"
        "3. <b>Feature Calculation:</b> Total Spend = <b>£313,437.62</b> (Top 0.1% tier); Orders = <b>156</b>; Recency = <b>9 days</b>; Recent 90d Spend = <b>£18,521.29</b>; Prior 90d Spend = <b>£53,838.44</b>; Value Momentum = <b>-65.6% drop</b>.<br/>"
        "4. <b>Behavioral Segmentation:</b> Clustered into <b>Segment 2: High-Value Stable</b> based on high cumulative spend and catalog reach (450+ unique SKUs).<br/>"
        "5. <b>Lifecycle State Machine:</b> Classified as <b>SOFTENING</b> as of reference date due to recent spend drop exceeding 25%.<br/>"
        "6. <b>Decision Signal:</b> Triggers <b>HIGH_VALUE_SOFTENING (High Severity)</b> with attached limitation regarding wholesale replenishment timing.<br/>"
        "7. <b>Operational Action:</b> Linked to Strategy <b>STRAT-01</b> for proactive commercial outreach, evaluated via a 20% holdout control trial with a 90-day recovery window.",
        callout_style
    ))
    story.append(Spacer(1, 8))

    # =========================================================================
    # 10. SYSTEM CONTROLS, BOUNDARIES & CONCLUSION
    # =========================================================================
    story.append(Paragraph("10. System Controls, Limitations & Technical Conclusion", h1_style))
    story.append(Paragraph(
        "The project incorporates an explicit control layer (`reporting.data_control_summary`) evaluating 6 continuous audit checks. "
        "All 229 automated unit and integration tests execute cleanly in under 8 seconds with zero linter errors. "
        "However, five methodological boundaries must be respected when interpreting conclusions:<br/>"
        "1. <b>Wholesale Scope:</b> The merchant represents a commercial giftware distributor; reorder intervals cannot be generalized to consumer banking or SaaS subscriptions.<br/>"
        "2. <b>Observational Bounds:</b> Marketing interventions are unobserved in the source data; decision signals define hypotheses for testing rather than guaranteed causal uplifts.<br/>"
        "3. <b>Wholesale Purchase Lumpiness:</b> Inactivity intervals of 60–90 days frequently reflect standard distributor restocking cycles rather than account cancellation.<br/>"
        "4. <b>Unattributed Volume (22.77%):</b> Guest checkout transactions lacking customer identifiers are isolated from account clustering while preserved in gross financial accounting.<br/>"
        "5. <b>Zero Baseline Discontinuities:</b> Accounts with zero orders in prior baseline periods are evaluated via deterministic default momentum rates rather than artificial interpolation.",
        body_style
    ))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceBefore=2, spaceAfter=6))
    story.append(Paragraph(
        "<b>Technical Conclusion:</b> The Consumer Behavior Decision Intelligence Lab establishes an auditable, reproducible, "
        "and statistically disciplined customer intelligence framework. By transforming raw transactional data into multi-dimensional "
        "features, behavioral segments, lifecycle snapshots, and deterministic decision signals, the system equips commercial and analytics "
        "teams with transparent tools to monitor risk, protect high-value accounts, and test targeted interventions.",
        body_style
    ))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF build successful: {PDF_OUTPUT_PATH} ({os.path.getsize(PDF_OUTPUT_PATH) / 1024:.1f} KB)")

if __name__ == "__main__":
    build_pdf_report()
