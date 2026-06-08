"""
IEEE-Compliant Figure Redesign — Fig. 1 & Fig. 2
Enhanced with premium color coding, resolved overlapping lines/descriptions, and absolute clarity.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Polygon
from matplotlib.lines import Line2D
import numpy as np
from pathlib import Path

OUT = Path(r"C:\Users\ACER\Downloads\Skripsi")
DPI = 300  # High print resolution for IEEE standard

# ── Color Palette ──────────────────────────────────────────────
BK       = '#212121'   # elegant dark charcoal instead of harsh black
WHITE    = '#FFFFFF'

# Swimlane Band & Label Backgrounds (Soft curating pastels)
L1_BG    = '#F4F9FF'; L1_LBL  = '#D9ECFF'  # Blue (Acquisition & Fusion)
L2_BG    = '#F4FBF7'; L2_LBL  = '#D4F5E6'  # Green (Analysis)
L3_BG    = '#FFFBF5'; L3_LBL  = '#FFE8D1'  # Amber/Orange (Orchestration)
L4_BG    = '#FCF8FD'; L4_LBL  = '#F2DAF7'  # Lavender (Execution & Feedback)

# Component Color Tokens (Fill & Border)
BLUE_F   = '#E1F5FE'; BLUE_B   = '#0288D1'  # Data Acquisition / n8n / IDS
GREEN_F  = '#E8F5E9'; GREEN_B  = '#2E7D32'  # Automated / ML / SIEM
AMBER_F  = '#FFF3E0'; AMBER_B  = '#E65100'  # Decision logic
PINK_F   = '#FFF0F2'; PINK_B   = '#D81B60'  # HOTL (Human-on-the-Loop)
GRAY_F   = '#F5F5F5'; GRAY_B   = '#616161'  # Manual logs / Audit
EXT_F    = '#ECEFF1'; EXT_B    = '#455A64'  # External trigger / PH
PURP_F   = '#EDE7F6'; PURP_B   = '#651FFF'  # Retraining Loop
IND_F    = '#E8EAF6'; IND_B    = '#3F51B5'  # Validation Gate

# Line / Connection Colors
LINE_DEF = '#37474F'  # default line (dark slate)
LINE_AUT = '#2E7D32'  # autonomous route (green)
LINE_HOT = '#C2185B'  # human route (pink/magenta)
LINE_MAN = '#616161'  # manual/log route (gray)
LINE_FDB = '#651FFF'  # feedback/model update (purple)

# ═══════════════════════════════════════════════════════════════
# PRIMITIVES
# ═══════════════════════════════════════════════════════════════
def proc_box(ax, x, y, w, h, label, sub='', style='solid',
             fill=WHITE, border_color=BK, lw=1.5, fs=8.5, zorder=3):
    """Draws rounded rectangle box with crisp text styling."""
    ls = {'solid': (0,()), 'dashed': (0,(5,3)), 'dotted': (0,(1.5,2))}[style]
    ax.add_patch(FancyBboxPatch((x, y), w, h,
        boxstyle="round,pad=0.07,rounding_size=0.07",
        fc=fill, ec=border_color, lw=lw, ls=ls, zorder=zorder))
    dy = 0.13 if sub else 0
    ax.text(x+w/2, y+h/2+dy, label, ha='center', va='center',
            fontsize=fs, fontweight='bold', color=BK, zorder=zorder+1,
            multialignment='center')
    if sub:
        ax.text(x+w/2, y+h/2-0.2, sub, ha='center', va='center',
                fontsize=max(5.5, fs-1.8), color='#37474F', zorder=zorder+1,
                multialignment='center')

def hexagon(ax, cx, cy, w, h, label, sub='', fill=EXT_F, border_color=EXT_B, fs=7.5, zorder=3):
    """Hexagon shape for external triggers / schedules."""
    hw, hh = w/2, h/2
    ind = 0.18  # indent
    xs = [cx-hw, cx-hw+ind, cx+hw-ind, cx+hw, cx+hw-ind, cx-hw+ind]
    ys = [cy,    cy+hh,     cy+hh,     cy,    cy-hh,     cy-hh    ]
    ax.add_patch(Polygon(list(zip(xs,ys)), closed=True,
                         fc=fill, ec=border_color, lw=1.2, ls=(0,(3,2)), zorder=zorder))
    dy = 0.1 if sub else 0
    ax.text(cx, cy+dy, label, ha='center', va='center',
            fontsize=fs, fontweight='bold', color=BK, zorder=zorder+1,
            multialignment='center')
    if sub:
        ax.text(cx, cy-0.17, sub, ha='center', va='center',
                fontsize=fs-1.5, color='#455A64', zorder=zorder+1)

def seg(ax, pts, lw=1.2, color=LINE_DEF, ls='-'):
    """Draws a polyline through points without arrowhead."""
    for i in range(len(pts)-1):
        ax.plot([pts[i][0],pts[i+1][0]], [pts[i][1],pts[i+1][1]],
                color=color, lw=lw, ls=ls, zorder=6, solid_capstyle='butt')

def arrh(ax, p1, p2, lw=1.2, color=LINE_DEF):
    """Draws arrowhead from p1 pointing toward p2."""
    ax.annotate('', xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle='->', color=color, lw=lw,
                                connectionstyle='arc3,rad=0', shrinkA=0, shrinkB=0))

def route(ax, pts, label='', ls='-', lw=1.2, color=LINE_DEF, lseg=0):
    """Orthogonal route with arrowhead on last segment; white text background."""
    seg(ax, pts[:-1], lw=lw, color=color, ls=ls)
    arrh(ax, pts[-2], pts[-1], lw=lw, color=color)
    if label:
        i = min(lseg, len(pts)-2)
        lx = (pts[i][0]+pts[i+1][0])/2
        ly = (pts[i][1]+pts[i+1][1])/2
        horiz = abs(pts[i+1][0]-pts[i][0]) > abs(pts[i+1][1]-pts[i][1])
        ox, oy = (0, 0.08) if horiz else (0.08, 0)
        ax.text(lx+ox, ly+oy, label, ha='center' if horiz else 'left',
                va='bottom' if horiz else 'center',
                fontsize=6.2, color=color, fontweight='bold',
                bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none', alpha=1, zorder=10))

def lane(ax, yb, bh, lpad, W, title, subtitle, bg_color, lbl_color):
    """Draws one swimlane with clear boundaries."""
    ax.add_patch(FancyBboxPatch((lpad, yb), W-lpad-0.25, bh,
        boxstyle="square,pad=0", fc=bg_color, ec='#CFD8DC', lw=0.8, zorder=0))
    ax.add_patch(FancyBboxPatch((0.1, yb), lpad-0.2, bh,
        boxstyle="square,pad=0", fc=lbl_color, ec='#B0BEC5', lw=0.8, zorder=0))
    cx = 0.1+(lpad-0.2)/2
    ax.text(cx, yb+bh/2+0.18, title, ha='center', va='center',
            fontsize=8.5, fontweight='bold', color=BK)
    ax.text(cx, yb+bh/2-0.22, subtitle, ha='center', va='center',
            fontsize=6.5, color='#455A64', multialignment='center')

# ═══════════════════════════════════════════════════════════════
# FIG 1 — Color-Coded Non-Overlapping Architecture
# ═══════════════════════════════════════════════════════════════
def fig1_ieee():
    W, H = 16.5, 11.2
    fig, ax = plt.subplots(figsize=(W, H))
    ax.set_xlim(0, W); ax.set_ylim(0, H)
    ax.axis('off'); fig.patch.set_facecolor('white')

    LPAD = 2.05
    BH   = 0.80   # standard box height
    BHS  = 0.68   # small box height (routing nodes in L3)

    # ── Title ──────────────────────────────────────────────────
    ax.text(W/2, H-0.3,
        'Fig. 1.  Cognitive SOC Architecture: Four-Layer Pipeline (HOTL Paradigm)',
        ha='center', fontsize=11, fontweight='bold', color=BK)

    # ── Swimlane bands (y_bottom, height) ──────────────────────
    L1_YB, L1_BH = 8.8, 1.6    # Layer 1
    L2_YB, L2_BH = 6.6, 1.8    # Layer 2
    L3_YB, L3_BH = 3.5, 2.7    # Layer 3 (taller: 3 routing rows)
    L4_YB, L4_BH = 0.4, 2.7    # Layer 4

    lane(ax, L1_YB, L1_BH, LPAD, W, 'LAYER 1', 'Data Acquisition\n& Fusion', L1_BG, L1_LBL)
    lane(ax, L2_YB, L2_BH, LPAD, W, 'LAYER 2', 'Threat Analysis\n& Correlation', L2_BG, L2_LBL)
    lane(ax, L3_YB, L3_BH, LPAD, W, 'LAYER 3', 'Orchestration &\nDecision Logic', L3_BG, L3_LBL)
    lane(ax, L4_YB, L4_BH, LPAD, W, 'LAYER 4', 'Execution &\nAdaptive Feedback', L4_BG, L4_LBL)

    # ── LAYER 1: TIP → ETL → Temporal Fusion ───────────────
    L1_YC = L1_YB + L1_BH/2   # 9.6
    L1_BB = L1_YC - BH/2

    X1 = LPAD+0.2; W1 = 1.85   # TIP
    X2 = X1+W1+0.3; W2 = 2.15  # ETL
    X3 = X2+W2+0.3; W3 = 2.45  # Temporal Fusion

    proc_box(ax, X1, L1_BB, W1, BH, 'TIP TIP', 'REST API Source', fill=BLUE_F, border_color=BLUE_B)
    proc_box(ax, X2, L1_BB, W2, BH, 'ETL & Normalize', 'T_norm: e_i -> B_i\n(Eq. 1)', fill=BLUE_F, border_color=BLUE_B)
    proc_box(ax, X3, L1_BB, W3, BH, 'Temporal Fusion\n& Dedup', 'F_fuse, dt=3600s  (Eq. 2)', fill=BLUE_F, border_color=BLUE_B, fs=8)

    route(ax, [(X1+W1, L1_YC), (X2, L1_YC)], label='JSON feed', color=BLUE_B)
    route(ax, [(X2+W2, L1_YC), (X3, L1_YC)], label='B_i bundles', color=BLUE_B)

    # ── LAYER 2: Feature Eng → RF → Confidence ─────────────────
    L2_YC = L2_YB + L2_BH/2   # 7.5
    L2_BB = L2_YC - BH/2

    XA = LPAD+0.2; WA = 2.0    # Feature Eng
    XB = XA+WA+0.3; WB = 2.55  # Random Forest
    XC = XB+WB+0.3; WC = 2.25  # Confidence

    proc_box(ax, XA, L2_BB, WA, BH, 'Feature Engineering', 'f_i in R^15  (TABEL II)', fill=GREEN_F, border_color=GREEN_B)
    proc_box(ax, XB, L2_BB, WB, BH, 'Random Forest\nClassifier', 'Eq. 3-4  |  T trees, majority vote', fill=GREEN_F, border_color=GREEN_B, fs=8)
    proc_box(ax, XC, L2_BB, WC, BH, 'Confidence\nEstimation', 'conf(f_i)  (Eq. 4)', fill=GREEN_F, border_color=GREEN_B)

    route(ax, [(XA+WA, L2_YC), (XB, L2_YC)], color=GREEN_B)
    route(ax, [(XB+WB, L2_YC), (XC, L2_YC)], color=GREEN_B)

    # ── L1 -> L2 inter-layer (through gap at y=8.3) ─────────────
    GAP12 = 8.3   # y of routing channel
    route(ax,
          [(X3+W3/2, L1_BB),         # bottom center of Fusion
           (X3+W3/2, GAP12),          # down to gap
           (XA+WA/2, GAP12),          # left through gap
           (XA+WA/2, L2_BB+BH)],      # up into Feature Eng top
          label='IOC stream', color=LINE_DEF, lseg=1)

    # ── LAYER 3: Decision D + 3 routing rows + IDS Rule ────────
    L3_ROW_T = L3_YB + L3_BH - 0.55 - BHS/2   # top row center    ~ 5.56
    L3_ROW_M = L3_YB + L3_BH/2                  # mid row center    ~ 4.85
    L3_ROW_B = L3_YB + 0.55 + BHS/2             # bottom row center ~ 4.14

    # Decision D box spans full band height on the left
    XD = LPAD+0.2; WD = 2.0
    proc_box(ax, XD, L3_YB+0.15, WD, L3_BH-0.3,
             'Decision\nFunction  D',
             'Eq. 5\n4-case piecewise\n+ Safety Override', fs=8.5, border_color=AMBER_B, fill=AMBER_F, lw=2.0)

    # Routing boxes (3 rows, right of Decision - WIDENED GAP TO AVOID TEXT CLASH)
    XR = XD+WD+0.4; WR = 1.85
    proc_box(ax, XR, L3_ROW_T-BHS/2, WR, BHS, 'autonomous_block', 'conf > 0.85', fill=GREEN_F, border_color=GREEN_B)
    proc_box(ax, XR, L3_ROW_M-BHS/2, WR, BHS, 'escalate_HOTL', 'theta_low<=conf<=theta_high', style='dashed', fill=PINK_F, border_color=PINK_B)
    proc_box(ax, XR, L3_ROW_B-BHS/2, WR, BHS, 'log_review', 'conf < 0.60  (non-Crit.)', fill=GRAY_F, border_color=GRAY_B)

    # IDS Rule Generation (widen space from routing boxes to 0.6 to avoid label overlap)
    XI = XR+WR+0.6; WI = 2.1
    proc_box(ax, XI, L3_ROW_T-BHS/2, WI, BHS, 'IDS Rule Generation', 'XML -> Wazuh  (Jalur B)', fill=BLUE_F, border_color=BLUE_B)

    # Decision -> routing (3 orthogonal branches - REMOVED CLASHING INTERMEDIARY TEXT LABELS)
    DEC_RIGHT = XD+WD
    route(ax, [(DEC_RIGHT, L3_ROW_T), (XR, L3_ROW_T)], label='', color=LINE_AUT)
    route(ax, [(DEC_RIGHT, L3_ROW_M), (XR, L3_ROW_M)], label='', color=LINE_HOT)
    route(ax, [(DEC_RIGHT, L3_ROW_B), (XR, L3_ROW_B)], label='', color=LINE_MAN)

    # autonomous_block -> IDS Rule (label 'High/Critical' fits perfectly in the widened gap)
    route(ax, [(XR+WR, L3_ROW_T), (XI, L3_ROW_T)], label='High/Critical', color=LINE_AUT)

    # ── L2 -> L3 inter-layer (through gap at y=6.2) ─────────────
    GAP23 = 6.25  # routing channel y
    DEC_CX = XD + WD/2
    CON_CX = XC + WC/2
    route(ax,
          [(CON_CX, L2_BB),         # bottom of Confidence
           (CON_CX, GAP23),          # down to gap
           (DEC_CX, GAP23),          # left
           (DEC_CX, L3_YB+L3_BH-0.15)],  # into Decision from top
          label='(y_hat, conf_i)', color=LINE_DEF, lseg=1)

    # ── LAYER 4: Two sub-rows ───────────────────────────────────
    L4_UP_YC = L4_YB + L4_BH*0.72    # ~ 2.34
    L4_UP_BB = L4_UP_YC - BH/2
    L4_LO_YC = L4_YB + L4_BH*0.24    # ~ 1.05
    L4_LO_BB = L4_LO_YC - BH/2

    # Execution nodes
    XW = LPAD+0.2; WW = 1.85   # Wazuh
    XT = XW+WW+0.25; WT = 2.1  # Telegram (HOTL, dashed)
    XU = XT+WT+0.25; WU = 1.8  # Audit

    proc_box(ax, XW, L4_UP_BB, WW, BH, 'Wazuh SIEM', 'Rule Deploy\nRESTful API', fill=GREEN_F, border_color=GREEN_B)
    proc_box(ax, XT, L4_UP_BB, WT, BH, 'Telegram Bot\n(HOTL Interface)', 'Push notify\nInteractive btns', style='dashed', fill=PINK_F, border_color=PINK_B)
    proc_box(ax, XU, L4_UP_BB, WU, BH, 'Audit Log\n(SQLite)', 'Version tracking', fill=GRAY_F, border_color=GRAY_B)

    # Page-Hinkley trigger box (external, dotted)
    XPH = XU+WU+0.3; WPH = 2.0
    proc_box(ax, XPH, L4_UP_BB, WPH, BH, 'Page-Hinkley\nDrift Detect',
             'Eq. 10  |  d=0.005, l=50', fill=EXT_F, border_color=EXT_B, style='dotted', fs=7.8)

    # Feedback chain (lower row)
    XF = LPAD+0.2; WF = 2.2    # Feedback Buffer
    XRT = XF+WF+0.25; WRT = 2.0 # Retraining
    XGT = XRT+WRT+0.25; WGT = 2.0 # Deployment Gate
    XMD = XGT+WGT+0.25; WMD = 2.1 # Model Update

    proc_box(ax, XF,  L4_LO_BB, WF,  BH, 'Feedback Buffer  B_t', 'Corrections  (Eq. 11)', fill=AMBER_F, border_color=AMBER_B)
    proc_box(ax, XRT, L4_LO_BB, WRT, BH, 'Augmented\nRetraining', 'T_retrain  (Eq. 8)', fill=PURP_F, border_color=PURP_B)
    proc_box(ax, XGT, L4_LO_BB, WGT, BH, 'Deployment Gate', 'Wilcoxon  a=0.05\n(Eq. 9)', fill=IND_F, border_color=IND_B)
    proc_box(ax, XMD, L4_LO_BB, WMD, BH, 'RF Model Update', 'M_RF^(v+1)\nwarm_start=False', fill=GREEN_F, border_color=GREEN_B)

    route(ax, [(XF+WF, L4_LO_YC), (XRT, L4_LO_YC)], color=LINE_FDB)
    route(ax, [(XRT+WRT, L4_LO_YC), (XGT, L4_LO_YC)], color=LINE_FDB)
    route(ax, [(XGT+WGT, L4_LO_YC), (XMD, L4_LO_YC)], label='p < 0.05', color=LINE_FDB)

    # ── L3 -> L4 non-overlapping routing (CRITICAL FIXED ROUTING PATHS) ──
    # Spaced y-levels within the L3/L4 gap (3.1 to 3.5)
    GAP_BLK = 3.38
    GAP_ESC = 3.26
    GAP_LOG = 3.14
    GAP_IDS = 3.02

    WAZ_CX = XW + WW/2
    TEL_CX = XT + WT/2
    AUD_CX = XU + WU/2

    # 1. block -> Wazuh
    # Goes left out of the box to x = 4.45 (clear channel on left), down to GAP_BLK, then left to Wazuh.
    # Label is placed vertically on segment 2 (vertical segment in channel) to prevent overlap.
    route(ax, [(XR, L3_ROW_T-BHS/2+0.1),
               (XR-0.2, L3_ROW_T-BHS/2+0.1),
               (XR-0.2, GAP_BLK),
               (WAZ_CX-0.2, GAP_BLK),
               (WAZ_CX-0.2, L4_UP_BB+BH)], label='block', color=LINE_AUT, lseg=1)

    # 2. escalate_HOTL -> Telegram
    # Goes right out of the box to x = 6.70 (clear channel on right), down to GAP_ESC, then left to Telegram.
    # Label is placed vertically on segment 2 to avoid crossing the other vertical lines.
    route(ax, [(XR+WR, L3_ROW_M),
               (XR+WR+0.2, L3_ROW_M),
               (XR+WR+0.2, GAP_ESC),
               (TEL_CX, GAP_ESC),
               (TEL_CX, L4_UP_BB+BH)], label='escalate', color=LINE_HOT, lseg=1)

    # 3. log_review -> Audit
    # Bottom box: has no boxes underneath it. Can go straight down from bottom-center.
    # Label is placed vertically on segment 0.
    route(ax, [(XR+WR/2, L3_ROW_B-BHS/2),
               (XR+WR/2, GAP_LOG),
               (AUD_CX, GAP_LOG),
               (AUD_CX, L4_UP_BB+BH)], label='log', color=LINE_MAN, lseg=0)

    # 4. IDS Rule Gen -> Wazuh
    # Under IDS box is completely empty space. Can go straight down from bottom-center to GAP_IDS.
    IDS_CX = XI + WI/2
    route(ax, [(IDS_CX, L3_ROW_T-BHS/2),
               (IDS_CX, GAP_IDS),
               (WAZ_CX+0.4, GAP_IDS),
               (WAZ_CX+0.4, L4_UP_BB+BH)], label='IDS rules', color=LINE_AUT, lseg=1)

    # ── Telegram Feedback & PH Alarm to Buffer (non-overlapping) ──
    MID_L4 = (L4_UP_BB + L4_LO_BB+BH) / 2   # ~ 1.495
    FBF_CX = XF + WF/2

    # Telegram -> Feedback Buffer
    route(ax, [(TEL_CX, L4_UP_BB),             # bottom of Telegram
               (TEL_CX, MID_L4-0.06),
               (FBF_CX-0.4, MID_L4-0.06),
               (FBF_CX-0.4, L4_LO_BB+BH)],
          label='analyst corrections', ls='--', color=LINE_HOT, lseg=1)

    # Page-Hinkley -> Feedback Buffer
    PH_CX = XPH + WPH/2
    route(ax, [(PH_CX, L4_UP_BB),
               (PH_CX, MID_L4+0.06),
               (FBF_CX+0.4, MID_L4+0.06),
               (FBF_CX+0.4, L4_LO_BB+BH)],
          label='drift alarm', ls=':', color=EXT_B, lseg=1)

    # ── Feedback Loop: Model Update -> RF Classifier ─────────────
    FB_X = W - 0.45   # right channel x
    RF_CX = XB + WB/2
    pts_fb = [
        (XMD+WMD, L4_LO_YC),          # right of Model Update
        (FB_X, L4_LO_YC),              # right channel
        (FB_X, L2_BB+BH+0.12),         # up to L2 level
        (RF_CX+0.5, L2_BB+BH+0.12),   # left to above RF
        (RF_CX+0.5, L2_BB+BH),         # into RF
    ]
    seg(ax, pts_fb[:-1], lw=1.6, ls='--', color=LINE_FDB)
    arrh(ax, pts_fb[-2], pts_fb[-1], lw=1.6, color=LINE_FDB)
    ax.text(FB_X+0.08, (L4_LO_YC+L2_BB+BH)/2,
            'Model M_RF^(v+1)\n--> RF Classifier', ha='left', va='center', fontsize=6.5, color=LINE_FDB, fontweight='bold',
            bbox=dict(boxstyle='square,pad=0.15', fc='white', ec=LINE_FDB, lw=0.6))

    # ── Legend (MOVED SLIGHTLY LEFT TO AVOID FEEDBACK LINE CLASH) ──
    legend_els = [
        mpatches.Patch(fc=GREEN_F, ec=GREEN_B, lw=1.5, label='Fully Autonomous Process (Active defense / Wazuh SIEM)'),
        mpatches.Patch(fc=PINK_F, ec=PINK_B, lw=1.5, ls=(0,(5,3)), label='HOTL Interface / Analyst Escalation (Telegram Interface)'),
        mpatches.Patch(fc=AMBER_F, ec=AMBER_B, lw=1.5, label='Decision Engine & Feedback Buffer (Context evaluation)'),
        mpatches.Patch(fc=EXT_F, ec=EXT_B, lw=1.2, ls=(0,(1.5,2)), label='External Monitoring & Diagnostics (Page-Hinkley Drift)'),
        Line2D([0],[0], color=LINE_AUT, lw=1.5, label='Autonomous Action Flow (block / deploy rules)'),
        Line2D([0],[0], color=LINE_HOT, lw=1.5, ls='--', label='HOTL Analyst Interactive Feedback Path'),
        Line2D([0],[0], color=LINE_FDB, lw=1.6, ls='--', label='Augmented Training Feedback Loop (Model promotion)'),
    ]
    ax.legend(handles=legend_els, loc='center right', fontsize=7.5,
              framealpha=1.0, edgecolor='#B0BEC5',
              bbox_to_anchor=(0.935, 0.5), ncol=1, title='System Flow & Component Legend', title_fontsize=8.2)

    out = OUT / 'fig1_architecture.png'
    fig.savefig(out, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'[OK] fig1 updated with color & layout: {out}')


# ═══════════════════════════════════════════════════════════════
# FIG 2 — Color-Coded State Transition Loop (Layer 4)
# ═══════════════════════════════════════════════════════════════
def fig2_state():
    W, H = 14, 10.5
    fig, ax = plt.subplots(figsize=(W, H))
    ax.set_xlim(0, W); ax.set_ylim(0, H)
    ax.axis('off'); fig.patch.set_facecolor('white')

    ax.text(W/2, H-0.35,
        'Fig. 2.  Adaptive Feedback Loop — State-Transition Diagram (Layer 4)',
        ha='center', fontsize=11, fontweight='bold', color=BK)
    ax.text(W/2, H-0.72,
        'Cognitive SOC  |  Page-Hinkley Drift Detection  |  Wilcoxon Deployment Gate',
        ha='center', fontsize=8.5, color='#455A64')

    SW, SH = 2.8, 0.82   # state box width/height

    # Grid columns
    MC = 4.2   # main column center x
    DC = 9.5   # drift column center x

    # Row y-centers (top to bottom):
    R0 = 9.0   # S0: Operating
    R1 = 7.4   # S1: Monitoring
    R2 = 5.7   # S2: Accumulating
    R3 = 4.0   # S4: Retraining & Weekly Scheduler
    R4 = 2.4   # S5: Validation
    R5 = 0.85  # S6: Deploy

    def sx(cx): return cx - SW/2   # box x from center
    def sy(cy): return cy - SH/2   # box y from center

    # ── States ───────────────────────────────────────────────────
    # S0 — Operating
    proc_box(ax, sx(MC), sy(R0), SW, SH, 'S0: OPERATING', 'M_RF^(v) Active', fill=BLUE_F, border_color=BLUE_B, lw=2.0)
    # S1 — Monitoring
    proc_box(ax, sx(MC), sy(R1), SW, SH, 'S1: MONITORING', 'PH_t computed per IOC\n(Eq. 10)', fill=BLUE_F, border_color=BLUE_B)
    # S2 — Accumulating
    proc_box(ax, sx(MC), sy(R2), SW, SH, 'S2: ACCUMULATING', 'Buffer B_t -> n_min\n(Eq. 11)', fill=AMBER_F, border_color=AMBER_B)
    # S3 — Drift Alarm (right column)
    proc_box(ax, sx(DC), sy(R1), SW, SH, 'S3: DRIFT ALARM', 'PH_t - min PH_j > l\nl = 50', fill=PINK_F, border_color=PINK_B)
    # S4 — Retraining
    proc_box(ax, sx(MC), sy(R3), SW, SH, 'S4: RETRAINING', 'T_retrain = T_hist u B_t\n(Eq. 8)', fill=PURP_F, border_color=PURP_B)
    # S5 — Validation
    proc_box(ax, sx(MC), sy(R4), SW, SH, 'S5: VALIDATION', 'Wilcoxon signed-rank\na=0.05  (Eq. 9)', fill=IND_F, border_color=IND_B)
    # S6 — Deploy
    proc_box(ax, sx(DC), sy(R5), SW, SH, 'S6: DEPLOY', 'M_RF^(v+1) -> Layer 2\nVersion logged', fill=GREEN_F, border_color=GREEN_B, lw=2.0)

    # ── External triggers (hexagon) ──────────────────────────────
    # Weekly Scheduler (triggers retraining safeguard)
    hexagon(ax, DC, R3, 2.5, 0.78, 'Weekly Scheduler', 'Periodic safeguard\n(if |B_t| never >= 50)', fill=GRAY_F, border_color=GRAY_B)
    
    # System Start arrow (SHORTER TO PREVENT SUBTITLE OVERLAP)
    ax.annotate('', xy=(MC, R0+SH/2), xytext=(MC, R0+SH/2+0.35),
                arrowprops=dict(arrowstyle='->', color=BLUE_B, lw=1.8))
    ax.text(MC+0.1, R0+SH/2+0.18, 'System Start', ha='left', fontsize=8, color=BLUE_B, fontweight='bold')

    # ── Transitions (orthogonal & NON-OVERLAPPING CRITICAL FIX) ──
    # S0 -> S1 (straight down)
    route(ax, [(MC, R0-SH/2), (MC, R1+SH/2)], label='Each IOC processed', color=LINE_DEF)

    # S1 -> S3 (horizontal right)
    route(ax, [(MC+SW/2, R1), (sx(DC), R1)], label='PH_t - min > l=50  (drift)', color=LINE_HOT)

    # S1 -> S2 (straight down)
    route(ax, [(MC, R1-SH/2), (MC, R2+SH/2)], label='Analyst feedback', color=LINE_HOT)

    # S2 -> S4 (straight down)
    route(ax, [(MC, R2-SH/2), (MC, R3+SH/2)], label='|B_t| >= n_min = 50', color=LINE_DEF)

    # ── S3 -> S4 ROUTING (FIXED COLLISION WITH WEEKLY SCHEDULER) ──
    # S3 center is at 9.5. Weekly Scheduler center is at 9.5.
    # Route around it: S3 bottom goes down to y=4.8 (well above scheduler),
    # left to x=4.7 (MC + 0.5), and then directly down into S4 top.
    route(ax,
          [(DC, R1-SH/2),           # bottom of S3 (9.5, 6.99)
           (DC, 4.80),               # down to clear scheduler top
           (MC+0.5, 4.80),           # left above scheduler to MC+0.5
           (MC+0.5, R3+SH/2)],       # down into S4 top (4.7, 4.41)
          label='Expedite retraining', color=LINE_HOT, lseg=2)

    # Weekly Scheduler -> S4 (straight horizontal from scheduler left to S4 right)
    # Hexagon left edge is 9.5 - 1.25 = 8.25. S4 right edge is 4.2 + 1.4 = 5.6.
    route(ax, [(DC-1.25, R3), (MC+SW/2, R3)],
          label='7-day safeguard', ls='--', color=LINE_MAN)

    # S4 -> S5 (straight down)
    route(ax, [(MC, R3-SH/2), (MC, R4+SH/2)], label='Candidate M^(v+1)', color=LINE_DEF)

    # S5 -> S6 PASS (right, down to S6)
    route(ax,
          [(MC+SW/2, R4),           # right of S5 (5.6, 2.4)
           (sx(DC), R4),            # right to DC level (8.1, 2.4)
           (sx(DC), R5+SH/2)],      # down to S6 (8.1, 1.26)
          label='p < 0.05  ->  Deploy', color=LINE_AUT, lseg=0)

    # S5 -> S2 FAIL (left side channel, up back to S2)
    FAIL_X = MC - SW/2 - 0.6   # left channel (2.2)
    route(ax,
          [(MC-SW/2, R4),            # left of S5
           (FAIL_X, R4),             # left channel
           (FAIL_X, R2),             # up to S2
           (MC-SW/2, R2)],           # into S2 left
          label='p >= 0.05  |  Keep M^(v)\nCollect more feedback', ls='--', color=LINE_HOT, lseg=2)

    # S6 -> S0 (long feedback loop via right channel)
    FB_X = DC + SW/2 + 0.5
    route(ax,
          [(DC+SW/2, R5),            # right of S6
           (FB_X, R5),               # right channel
           (FB_X, R0),               # up to S0
           (MC+SW/2, R0)],           # left into S0
          label='M^(v+1) -> Active  |  v := v+1', color=LINE_FDB, lseg=2)

    # ── Page-Hinkley formula annotation ─────────────────────────
    ph_x = DC - SW/2 - 0.2
    ax.text(ph_x, (R1+R3)/2 + 0.1, 'PH_t = SUM_i(conf_i - conf_bar_t - d)\nd=0.005  |  Alarm: PH_t - min(PH_j) > 50',
            ha='right', va='center', fontsize=7, color='#37474F', style='italic',
            bbox=dict(boxstyle='round,pad=0.3', fc='#ECEFF1', ec='#B0BEC5', lw=0.7))

    # ── Annotation: not triggered in experiment (MOVED TO ROW R4 TO AVOID LEGEND OVERLAP) ──
    ax.text(8.2, 2.45,
        'Note: During the 14-day experiment, 31 analyst corrections were\n'
        'collected (< n_min = 50). Retraining was not triggered empirically.\n'
        'Prospective simulation: F1-Score macro: 0.934 -> 0.941\n'
        '(p = 0.18, statistically non-significant in 14-day window).',
        ha='left', va='top', fontsize=7, color='#37474F',
        bbox=dict(boxstyle='round,pad=0.4', fc='#FFFDE7', ec='#FFB300', lw=0.8))

    # ── Legend (MOVED TO BOTTOM-LEFT TO PREVENT COLLISION WITH S6 & FEEDBACK ARC) ──
    legend_els = [
        mpatches.Patch(fc=BLUE_F, ec=BLUE_B, lw=1.5, label='Active Production Environment'),
        mpatches.Patch(fc=AMBER_F, ec=AMBER_B, lw=1.5, label='Feedback Accumulation Buffer B_t'),
        mpatches.Patch(fc=PURP_F, ec=PURP_B, lw=1.5, label='Candidate Retraining & Refinement Space'),
        mpatches.Patch(fc=IND_F, ec=IND_B, lw=1.5, label='Deployment / Statistical Significance Gate'),
        mpatches.Patch(fc=GREEN_F, ec=GREEN_B, lw=2.0, label='Successful Model Promotion & Activation'),
        Line2D([0],[0], color=LINE_DEF, lw=1.3, label='Standard state transition'),
        Line2D([0],[0], color=LINE_HOT, lw=1.3, label='Analyst/Drift triggered action'),
        Line2D([0],[0], color=LINE_FDB, lw=1.5, ls='--', label='Retrained Model promotion loop'),
    ]
    ax.legend(handles=legend_els, loc='lower left', fontsize=7.8,
              framealpha=1.0, edgecolor='#B0BEC5',
              bbox_to_anchor=(0.01, 0.01), title='State Machine Transition Legend', title_fontsize=8.5)

    out = OUT / 'fig2_feedback_loop.png'
    fig.savefig(out, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'[OK] fig2 updated with color & layout: {out}')


if __name__ == '__main__':
    print('Generating premium color-coded figures with fixed clashing layouts...\n')
    fig1_ieee()
    fig2_state()
    print('\nDone. Figures updated successfully.')
