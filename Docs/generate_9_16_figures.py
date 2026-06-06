"""
Generate 9:16 Vertical High-Resolution IEEE-style figures for Cognitive SOC thesis (ProposalSkripsiV8a)
Outputs:
1. fig1_architecture_9_16.png (Gambar 1: Arsitektur)
2. fig2_feedback_loop_9_16.png (Gambar 2: Feedback Loop State Diagram)
3. fig3_experimental_results_9_16.png (3-panel result: MTTR, IOC volume, and Performance)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon
from matplotlib.lines import Line2D
from matplotlib.path import Path
import numpy as np
import seaborn as sns
from pathlib import Path as FilePath

OUT = FilePath(r"C:\Users\ACER\Downloads\Skripsi")
DPI = 300  # Premium publication-grade resolution

# ── Color Palette ──────────────────────────────────────────────
BK       = '#212121'   # Dark slate instead of solid black
WHITE    = '#FFFFFF'

# Swimlane Band & Label Backgrounds (Soft curated pastels)
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
             fill=WHITE, border_color=BK, lw=1.6, fs=9.5, zorder=3):
    """Draws rounded rectangle box in 100% data coordinates with dynamic autosizing to prevent text overflow."""
    ls = {'solid': (0,()), 'dashed': (0,(5,3)), 'dotted': (0,(1.5,2))}[style]
    
    # ── Autosizing Rule ──
    sub_fs = max(8.0, fs - 1.5)
    
    # Calculate required width based on text
    w_req_in = 0.0
    for line in label.split('\n'):
        w_line_in = (len(line) * 0.48 * fs) / 72.0 + 0.35
        if w_line_in > w_req_in:
            w_req_in = w_line_in
    if sub:
        for line in sub.split('\n'):
            w_line_in = (len(line) * 0.48 * sub_fs) / 72.0 + 0.35
            if w_line_in > w_req_in:
                w_req_in = w_line_in
                
    # Calculate required height based on text
    n_label = len(label.split('\n'))
    n_sub = len(sub.split('\n')) if sub else 0
    h_req = (n_label * fs * 1.3 + n_sub * sub_fs * 1.3 + 12.0) / 72.0 + 0.15
    
    # Extra spacing for dashed/dotted style boxes
    if style in ['dashed', 'dotted']:
        w_req_in += 0.15
        h_req += 0.08
        
    # Shift x and y to preserve center while scaling up
    if w < w_req_in:
        x = x + (w - w_req_in) / 2.0
        w = w_req_in
    if h < h_req:
        y = y + (h - h_req) / 2.0
        h = h_req
        
    # Draw path in data coordinates
    r = min(0.08, w/4, h/4)
    verts = [
        (x + r, y),
        (x + w - r, y),
        (x + w, y), (x + w, y + r),
        (x + w, y + h - r),
        (x + w, y + h), (x + w - r, y + h),
        (x + r, y + h),
        (x, y + h), (x, y + h - r),
        (x, y + r),
        (x, y), (x + r, y)
    ]
    codes = [
        Path.MOVETO,
        Path.LINETO,
        Path.CURVE3, Path.CURVE3,
        Path.LINETO,
        Path.CURVE3, Path.CURVE3,
        Path.LINETO,
        Path.CURVE3, Path.CURVE3,
        Path.LINETO,
        Path.CURVE3, Path.CURVE3
    ]
    path = Path(verts, codes)
    patch = mpatches.PathPatch(path, fc=fill, ec=border_color, lw=lw, ls=ls, zorder=zorder)
    ax.add_patch(patch)
    
    if sub:
        dy_pts = 7.0 + (n_label - 1) * 5.0
        sdy_pts = -(7.5 + (n_sub - 1) * 4.5)
        dy = dy_pts / 72.0
        sdy = sdy_pts / 72.0
        
        ax.text(x+w/2, y+h/2+dy, label, ha='center', va='center',
                fontsize=fs, fontweight='bold', color=BK, zorder=zorder+1,
                multialignment='center', linespacing=1.1)
        ax.text(x+w/2, y+h/2+sdy, sub, ha='center', va='center',
                fontsize=sub_fs, color='#37474F', zorder=zorder+1,
                multialignment='center', linespacing=1.1)
    else:
        ax.text(x+w/2, y+h/2, label, ha='center', va='center',
                fontsize=fs, fontweight='bold', color=BK, zorder=zorder+1,
                multialignment='center', linespacing=1.1)
                
    return {
        'x': x, 'y': y, 'w': w, 'h': h,
        'cx': x + w/2, 'cy': y + h/2,
        'left': x, 'right': x + w,
        'bottom': y, 'top': y + h
    }

def hexagon(ax, cx, cy, w, h, label, sub='', fill=EXT_F, border_color=EXT_B, fs=9.5, zorder=3):
    """Hexagon shape for external triggers / schedules with dynamic autosizing."""
    sub_fs = max(8.0, fs - 1.5)
    
    # Calculate required width
    w_req_in = 0.0
    for line in label.split('\n'):
        w_line_in = (len(line) * 0.48 * fs) / 72.0 + 0.35
        if w_line_in > w_req_in:
            w_req_in = w_line_in
    if sub:
        for line in sub.split('\n'):
            w_line_in = (len(line) * 0.48 * sub_fs) / 72.0 + 0.35
            if w_line_in > w_req_in:
                w_req_in = w_line_in
                
    # Calculate required height
    n_label = len(label.split('\n'))
    n_sub = len(sub.split('\n')) if sub else 0
    h_req = (n_label * fs * 1.3 + n_sub * sub_fs * 1.3 + 12.0) / 72.0 + 0.15
    
    if w < w_req_in:
        w = w_req_in
    if h < h_req:
        h = h_req
        
    hw, hh = w/2, h/2
    ind = 0.22  # indent
    xs = [cx-hw, cx-hw+ind, cx+hw-ind, cx+hw, cx+hw-ind, cx-hw+ind]
    ys = [cy,    cy+hh,     cy+hh,     cy,    cy-hh,     cy-hh    ]
    ax.add_patch(Polygon(list(zip(xs,ys)), closed=True,
                         fc=fill, ec=border_color, lw=1.4, ls=(0,(3,2)), zorder=zorder))
    
    if sub:
        dy_pts = 7.0 + (n_label - 1) * 5.0
        sdy_pts = -(7.5 + (n_sub - 1) * 4.5)
        dy = dy_pts / 72.0
        sdy = sdy_pts / 72.0
        ax.text(cx, cy+dy, label, ha='center', va='center',
                fontsize=fs, fontweight='bold', color=BK, zorder=zorder+1,
                multialignment='center', linespacing=1.1)
        ax.text(cx, cy+sdy, sub, ha='center', va='center',
                fontsize=sub_fs, color='#455A64', zorder=zorder+1,
                multialignment='center', linespacing=1.1)
    else:
        ax.text(cx, cy, label, ha='center', va='center',
                fontsize=fs, fontweight='bold', color=BK, zorder=zorder+1,
                multialignment='center', linespacing=1.1)
                
    return {
        'x': cx - w/2, 'y': cy - h/2, 'w': w, 'h': h,
        'cx': cx, 'cy': cy,
        'left': cx - w/2, 'right': cx + w/2,
        'bottom': cy - h/2, 'top': cy + h/2
    }

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
    """Orthogonal route with automatic spacing gaps at start and end box boundaries."""
    # Copy points to avoid modifying the caller's list
    pts = [list(p) for p in pts]
    
    # ── Gap offset at the start box border ──
    if len(pts) > 1:
        dx = pts[1][0] - pts[0][0]
        dy = pts[1][1] - pts[0][1]
        gap = 0.045  # beautiful spacing gap in inches
        if abs(dx) > abs(dy):
            pts[0][0] += gap if dx > 0 else -gap
        else:
            pts[0][1] += gap if dy > 0 else -gap

    # ── Gap offset at the end box border ──
    if len(pts) > 1:
        dx = pts[-1][0] - pts[-2][0]
        dy = pts[-1][1] - pts[-2][1]
        gap = 0.055  # slightly larger gap for arrowheads
        if abs(dx) > abs(dy):
            pts[-1][0] -= gap if dx > 0 else -gap
        else:
            pts[-1][1] -= gap if dy > 0 else -gap

    # Convert back to tuples
    pts = [tuple(p) for p in pts]

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
                fontsize=8.5, color=color, fontweight='bold',
                bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none', alpha=1, zorder=10))

def lane(ax, yb, bh, lpad, W, title, subtitle, bg_color, lbl_color):
    """Draws one swimlane with clear boundaries using standard Rectangle."""
    ax.add_patch(mpatches.Rectangle((lpad, yb), W-lpad-0.15, bh,
        fc=bg_color, ec='#CFD8DC', lw=0.8, zorder=0))
    ax.add_patch(mpatches.Rectangle((0.1, yb), lpad-0.2, bh,
        fc=lbl_color, ec='#B0BEC5', lw=0.8, zorder=0))
    cx = 0.1+(lpad-0.2)/2
    ax.text(cx, yb+bh/2+0.22, title, ha='center', va='center',
            fontsize=11.5, fontweight='bold', color=BK)  # Enlarged lane title to 11.5
    ax.text(cx, yb+bh/2-0.24, subtitle, ha='center', va='center',
            fontsize=8.5, color='#455A64', multialignment='center')  # Enlarged lane subtitle to 8.5


# ═══════════════════════════════════════════════════════════════
# FIG 1 — Gambar 1: Arsitektur (9:16 Vertical Layout - Overhauled)
# ═══════════════════════════════════════════════════════════════
def fig1_architecture_9_16():
    W, H = 9.0, 16.0
    fig, ax = plt.subplots(figsize=(W, H))
    ax.set_xlim(0, W); ax.set_ylim(0, H)
    ax.axis('off'); fig.patch.set_facecolor('white')

    LPAD = 1.5
    BH   = 0.58   # Taller box height for massive text breathing room
    box_w = 4.8   # Extra-wide width for Layer 1 & 2 centered boxes

    # Title - Lowered to completely prevent top clipping!
    ax.text(W/2, H-0.45, 'Fig. 1. Cognitive SOC Architecture: Four-Layer Pipeline',
            ha='center', fontsize=14.0, fontweight='bold', color=BK)
    ax.text(W/2, H-0.75, 'Human-On-The-Loop (HOTL) Paradigm  ·  n8n Orchestrator Backbone',
            ha='center', fontsize=10.5, color='#455A64')

    # Swimlanes - Re-optimized vertical boundaries to expand L1 and L2 vertical spacing
    L1_YB, L1_BH = 12.0, 3.2
    L2_YB, L2_BH = 8.8, 3.1
    L3_YB, L3_BH = 5.0, 3.7
    L4_YB, L4_BH = 1.0, 3.9

    lane(ax, L1_YB, L1_BH, LPAD, W, 'LAYER 1', 'Data Acquisition\n& Fusion', L1_BG, L1_LBL)
    lane(ax, L2_YB, L2_BH, LPAD, W, 'LAYER 2', 'Threat Analysis\n& Correlation', L2_BG, L2_LBL)
    lane(ax, L3_YB, L3_BH, LPAD, W, 'LAYER 3', 'Orchestration &\nDecision Logic', L3_BG, L3_LBL)
    lane(ax, L4_YB, L4_BH, LPAD, W, 'LAYER 4', 'Execution &\nAdaptive Feedback', L4_BG, L4_LBL)

    # ── LAYER 1: Stacked Vertically with wide, safe spacing ──
    CX = 5.20
    L1_bottoms = [12.39, 13.47, 14.39]
    b_tip = proc_box(ax, CX-box_w/2, L1_bottoms[2], box_w, BH, 'Cyfirma TIP', 'REST API Source', fill=BLUE_F, border_color=BLUE_B, fs=10.5)
    b_etl = proc_box(ax, CX-box_w/2, L1_bottoms[1], box_w, BH, 'ETL & Normalize', 'T_norm: e_i -> B_i\n(Eq. 1)', fill=BLUE_F, border_color=BLUE_B, fs=10.0)
    b_temp = proc_box(ax, CX-box_w/2, L1_bottoms[0], box_w, BH, 'Temporal Fusion\n& Dedup', 'F_fuse, dt = 3600s\n(Eq. 2)', fill=BLUE_F, border_color=BLUE_B, fs=10.0)

    route(ax, [(b_tip['cx'], b_tip['bottom']), (b_etl['cx'], b_etl['top'])], color=BLUE_B)
    route(ax, [(b_etl['cx'], b_etl['bottom']), (b_temp['cx'], b_temp['top'])], color=BLUE_B)

    # ── LAYER 2: Stacked Vertically with wide, safe spacing ──
    L2_bottoms = [8.95, 10.15, 11.15]
    b_feat = proc_box(ax, CX-box_w/2, L2_bottoms[2], box_w, BH, 'Feature Engineering', 'f_i in R^15 (Table II)', fill=GREEN_F, border_color=GREEN_B, fs=10.5)
    b_rf = proc_box(ax, CX-box_w/2, L2_bottoms[1], box_w, BH, 'Random Forest\nClassifier', 'T trees, majority vote\n(Eq. 3-4)', fill=GREEN_F, border_color=GREEN_B, fs=10.0)
    b_conf = proc_box(ax, CX-box_w/2, L2_bottoms[0], box_w, BH, 'Confidence Estimation', 'conf(f_i) (Eq. 4)', fill=GREEN_F, border_color=GREEN_B, fs=10.5)

    route(ax, [(b_feat['cx'], b_feat['bottom']), (b_rf['cx'], b_rf['top'])], color=GREEN_B)
    route(ax, [(b_rf['cx'], b_rf['bottom']), (b_conf['cx'], b_conf['top'])], color=GREEN_B)

    # L1 -> L2 vertical route
    route(ax, [(b_temp['cx'], b_temp['bottom']), (b_feat['cx'], b_feat['top'])], label='IOC stream', color=LINE_DEF, lseg=0)

    # ── LAYER 3: Decision D & 3 Symmetrical Side-by-Side Columns ──
    CX1 = 2.77
    CX2 = 5.20
    CX3 = 7.63
    W_col = 2.20

    # Decision D (Centered at the top of Layer 3)
    HD = 0.85
    b_dec = proc_box(ax, CX2-4.2/2, 7.75, 4.2, HD, 'Decision Function D', '4-case piecewise  ·  Safety Override (Critical)\nEq. 5', fs=11.0, border_color=AMBER_B, fill=AMBER_F, lw=2.4)

    # Row 1 (y = 6.60 - Spaced down to breathe)
    b_auto = proc_box(ax, CX1-W_col/2, 6.60, W_col, BH, 'Autonomous\nBlock', 'conf > 0.85\n(Active SIEM)', fill=GREEN_F, border_color=GREEN_B, fs=10.0)
    b_esc = proc_box(ax, CX2-W_col/2, 6.60, W_col, BH, 'Escalate (HOTL)', 'theta_low <= conf\n<= theta_high', style='dashed', fill=PINK_F, border_color=PINK_B, fs=10.0)
    b_log = proc_box(ax, CX3-W_col/2, 6.60, W_col, BH, 'Log Review', 'conf < 0.60\n(Non-Critical)', fill=GRAY_F, border_color=GRAY_B, fs=10.0)

    # Row 2 (y = 5.30 - Spaced down to breathe)
    b_ids = proc_box(ax, CX1-W_col/2, 5.30, W_col, BH, 'IDS Rule\nGeneration', 'XML -> Wazuh\n(Pathway B)', fill=BLUE_F, border_color=BLUE_B, fs=10.0)

    # L2 -> L3 vertical straight down to Decision D
    route(ax, [(b_conf['cx'], b_conf['bottom']), (b_dec['cx'], b_dec['top'])], label='(ŷ_hat, conf_i)', color=LINE_DEF, lseg=0)

    # Decision D -> three branches (Perfect right angles, zero crossings!)
    route(ax, [(b_dec['cx'], b_dec['bottom']), (b_auto['cx'], b_dec['bottom']), (b_auto['cx'], b_auto['top'])], color=LINE_AUT)
    route(ax, [(b_dec['cx'], b_dec['bottom']), (b_esc['cx'], b_esc['top'])], color=LINE_HOT)
    route(ax, [(b_dec['cx'], b_dec['bottom']), (b_log['cx'], b_dec['bottom']), (b_log['cx'], b_log['top'])], color=LINE_MAN)

    # autonomous_block -> IDS Rule (straight down!)
    route(ax, [(b_auto['cx'], b_auto['bottom']), (b_ids['cx'], b_ids['top'])], color=LINE_AUT)

    # ── LAYER 4: Execution & Symmetrical Feedback ──
    # Row 1 (Execution, y = 4.05)
    b_wazuh = proc_box(ax, CX1-W_col/2, 4.05, W_col, BH, 'Wazuh SIEM', 'Rule Deploy API\n(Autonomous)', fill=GREEN_F, border_color=GREEN_B, fs=10.0)
    b_tele = proc_box(ax, CX2-W_col/2, 4.05, W_col, BH, 'Telegram Bot\n(HOTL)', 'Push notifications\n& buttons', style='dashed', fill=PINK_F, border_color=PINK_B, fs=10.0)
    b_audit = proc_box(ax, CX3-W_col/2, 4.05, W_col, BH, 'Audit Log\n(SQLite)', 'Version tracking\n(Manual review)', fill=GRAY_F, border_color=GRAY_B, fs=10.0)

    # L3 -> L4 Connections (all straight down!)
    route(ax, [(b_ids['cx'], b_ids['bottom']), (b_wazuh['cx'], b_wazuh['top'])], label='block / rules', color=LINE_AUT, lseg=0)
    route(ax, [(b_esc['cx'], b_esc['bottom']), (b_tele['cx'], b_tele['top'])], label='escalate', color=LINE_HOT, lseg=0)
    route(ax, [(b_log['cx'], b_log['bottom']), (b_audit['cx'], b_audit['top'])], label='log', color=LINE_MAN, lseg=0)

    # Row 2 (Feedback Buffer & Drift, y = 2.95)
    b_buff = proc_box(ax, CX2-2.4/2, 2.95, 2.4, BH, 'Feedback Buffer B_t', 'Corrections & overrides\n(Eq. 11)', fill=AMBER_F, border_color=AMBER_B, fs=10.0)
    b_ph = proc_box(ax, CX3-1.8/2, 2.95, 1.8, BH, 'Page-Hinkley\nDrift', 'd = 0.005, l = 50\n(Eq. 10)', fill=EXT_F, border_color=EXT_B, style='dotted', fs=9.5)

    # Row 3 (Feedback chain lower row, y = 1.85 - Elevated for perfect legend clearance)
    b_retrain = proc_box(ax, CX1-2.4/2, 1.85, 2.4, BH, 'Augmented\nRetraining', 'T_retrain = T_hist u B_t\n(Eq. 8)', fill=PURP_F, border_color=PURP_B, fs=10.0)
    b_gate = proc_box(ax, CX2-2.2/2, 1.85, 2.2, BH, 'Deployment\nGate', 'Wilcoxon Test\np < 0.05 (Eq. 9)', fill=IND_F, border_color=IND_B, fs=9.5)
    b_rf_up = proc_box(ax, CX3-2.2/2, 1.85, 2.2, BH, 'RF Model\nUpdate', 'M_RF^(v+1)\n(warm_start=False)', fill=GREEN_F, border_color=GREEN_B, fs=9.5)

    route(ax, [(b_retrain['right'], b_retrain['cy']), (b_gate['left'], b_gate['cy'])], color=LINE_FDB)
    route(ax, [(b_gate['right'], b_gate['cy']), (b_rf_up['left'], b_rf_up['cy'])], label='p < 0.05', color=LINE_FDB)

    # Telegram Corrections -> Feedback Buffer (straight down!)
    route(ax, [(b_tele['cx'], b_tele['bottom']), (b_buff['cx'], b_buff['top'])], label='corrections', ls='--', color=LINE_HOT, lseg=0)
    
    # Center horizontal route dynamically in the gap between Row 2 and Row 3
    gap_y = (b_buff['bottom'] + b_retrain['top']) / 2.0

    # PH Alarm -> Feedback Buffer (around)
    route(ax, [(b_ph['cx'], b_ph['bottom']), (b_ph['cx'], gap_y), (b_buff['cx'] + 0.5, gap_y), (b_buff['cx'] + 0.5, b_buff['bottom'])], label='drift', ls=':', color=EXT_B, lseg=1)

    # Buffer -> Retraining
    route(ax, [(b_buff['cx'] - 0.5, b_buff['bottom']), (b_buff['cx'] - 0.5, gap_y), (b_retrain['cx'], gap_y), (b_retrain['cx'], b_retrain['top'])], color=LINE_FDB)

    # ── Feedback Loop: Model Update -> RF Classifier (up the right margin) ──
    FB_X = W - 0.20
    pts_fb = [
        (b_rf_up['right'], b_rf_up['cy']),
        (FB_X, b_rf_up['cy']),
        (FB_X, b_rf['cy']),
        (b_rf['right'], b_rf['cy'])
    ]
    seg(ax, pts_fb[:-1], lw=1.8, ls='--', color=LINE_FDB)
    arrh(ax, pts_fb[-2], pts_fb[-1], lw=1.8, color=LINE_FDB)
    ax.text(FB_X-0.12, (b_rf_up['cy']+b_rf['cy'])/2, 'Model M_RF^(v+1) --> Layer 2 RF Classifier',
            ha='right', va='center', fontsize=10.0, color=LINE_FDB, fontweight='bold', rotation=270,
            bbox=dict(boxstyle='square,pad=0.15', fc='white', ec=LINE_FDB, lw=0.6))

    # Legend - Optimized to 3 columns and lowered to completely eliminate overlaps with Layer 4 boxes
    legend_els = [
        mpatches.Patch(fc=GREEN_F, ec=GREEN_B, lw=1.6, label='Autonomous Action (Active SIEM)'),
        mpatches.Patch(fc=PINK_F, ec=PINK_B, lw=1.6, ls=(0,(5,3)), label='HOTL Interface (Telegram Bot)'),
        mpatches.Patch(fc=AMBER_F, ec=AMBER_B, lw=1.6, label='Decision Engine & Feedback Buffer'),
        mpatches.Patch(fc=EXT_F, ec=EXT_B, lw=1.4, ls=(0,(1.5,2)), label='Drift Diagnostic (Page-Hinkley)'),
        Line2D([0],[0], color=LINE_AUT, lw=1.6, label='Autonomous Action Route'),
        Line2D([0],[0], color=LINE_HOT, lw=1.6, ls='--', label='HOTL Analyst Feedback Path'),
        Line2D([0],[0], color=LINE_FDB, lw=1.8, ls='--', label='Model Promotion Pathway'),
    ]
    ax.legend(handles=legend_els, loc='lower center', fontsize=8.5,
              framealpha=1.0, edgecolor='#B0BEC5', bbox_to_anchor=(0.5, 0.005), ncol=3,
              title='System Flow & Component Legend', title_fontsize=9.5,
              borderpad=0.5, labelspacing=0.4, columnspacing=1.2)

    out = OUT / 'fig1_architecture_v3_9_16.png'
    fig.savefig(out, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'[OK] Gambar 1 (9:16) saved successfully: {out}')


# ═══════════════════════════════════════════════════════════════
# FIG 2 — Gambar 2: Feedback Loop State Diagram (9:16 Vertical)
# ═══════════════════════════════════════════════════════════════
def fig2_feedback_loop_9_16():
    W, H = 9.0, 16.0
    fig, ax = plt.subplots(figsize=(W, H))
    ax.set_xlim(0, W); ax.set_ylim(0, H)
    ax.axis('off'); fig.patch.set_facecolor('white')

    ax.text(W/2, H-0.45, 'Fig. 2. Adaptive Feedback Loop — State-Transition Diagram (Layer 4)',
            ha='center', fontsize=14.0, fontweight='bold', color=BK)
    ax.text(W/2, H-0.75, 'Cognitive SOC  |  Page-Hinkley Drift Detection  |  Wilcoxon Deployment Gate',
            ha='center', fontsize=10.0, color='#455A64')

    SW, SH = 3.4, 0.90   # State box dimensions

    # Expanded grid columns for a wide, beautiful 1.0 unit spacing to avoid ANY label overlaps!
    MC = 2.5   # Main column center (shifted left)
    DC = 6.5   # Drift/Deployment column center (shifted right)

    # Row y-centers (top to bottom):
    R0 = 13.8   # S0: Operating
    R1 = 12.0   # S1: Monitoring
    R2 = 10.2   # S2: Accumulating
    R3 = 8.4    # S4: Retraining & Weekly Scheduler
    R4 = 6.6    # S5: Validation
    R5 = 4.8    # S6: Deploy (Raised to 4.8 to clear Note box and legend)

    def sx(cx): return cx - SW/2
    def sy(cy): return cy - SH/2

    # States - Highly readable small fonts!
    proc_box(ax, sx(MC), sy(R0), SW, SH, 'S0: OPERATING', 'Model M_RF^(v) Active', fill=BLUE_F, border_color=BLUE_B, lw=2.4, fs=10.5)
    proc_box(ax, sx(MC), sy(R1), SW, SH, 'S1: MONITORING', 'PH_t computed per IOC (Eq. 10)', fill=BLUE_F, border_color=BLUE_B, fs=10.0)
    proc_box(ax, sx(MC), sy(R2), SW, SH, 'S2: ACCUMULATING', 'Buffer B_t -> n_min (Eq. 11)', fill=AMBER_F, border_color=AMBER_B, fs=10.0)
    proc_box(ax, sx(DC), sy(R1), SW, SH, 'S3: DRIFT ALARM', 'PH_t - min PH_j > l  |  l = 50', fill=PINK_F, border_color=PINK_B, fs=10.0)
    proc_box(ax, sx(MC), sy(R3), SW, SH, 'S4: RETRAINING', 'T_retrain = T_hist u B_t (Eq. 8)', fill=PURP_F, border_color=PURP_B, fs=10.0)
    proc_box(ax, sx(MC), sy(R4), SW, SH, 'S5: VALIDATION', 'Wilcoxon signed-rank | a=0.05 (Eq. 9)', fill=IND_F, border_color=IND_B, fs=10.0)
    proc_box(ax, sx(DC), sy(R5), SW, SH, 'S6: DEPLOY', 'M_RF^(v+1) -> Layer 2 | Version logged', fill=GREEN_F, border_color=GREEN_B, lw=2.4, fs=10.5)

    # Page-Hinkley formula annotation (placed in DC column slot at R2 height)
    proc_box(ax, sx(DC), sy(R2), SW, SH, 'Page-Hinkley Formula', 'PH_t = SUM(conf_i - conf_bar - d) | d=0.005, l=50', fill=EXT_F, border_color=EXT_B, style='dotted', fs=9.5)

    # Weekly Scheduler (hexagon)
    hexagon(ax, DC, R3, 3.0, 0.92, 'Weekly Scheduler', 'Periodic safeguard | if |B_t| < 50', fill=GRAY_F, border_color=GRAY_B, fs=9.5)
    
    # System Start arrow
    ax.annotate('', xy=(MC, R0+SH/2), xytext=(MC, R0+SH/2+0.35),
                arrowprops=dict(arrowstyle='->', color=BLUE_B, lw=2.0))
    ax.text(MC+0.1, R0+SH/2+0.18, 'System Start', ha='left', fontsize=10.5, color=BLUE_B, fontweight='bold')

    # Transitions (All label positions mathematically optimized to avoid collisions)
    route(ax, [(MC, R0-SH/2), (MC, R1+SH/2)], label='Each IOC processed', color=LINE_DEF)
    route(ax, [(MC+SW/2, R1), (DC-SW/2, R1)], label='PH_t - min\n> 50', color=LINE_HOT)
    route(ax, [(MC, R1-SH/2), (MC, R2+SH/2)], label='Analyst feedback', color=LINE_HOT)

    # |B_t| >= 50 Label: Placed cleanly to the left of the line
    route(ax, [(MC, R2-SH/2), (MC, R3+SH/2)], color=LINE_DEF)
    ax.text(MC - 0.12, (R2+R3)/2, '|B_t| >= 50', ha='right', va='center',
            fontsize=10.0, color=LINE_DEF, fontweight='bold',
            bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none', alpha=1, zorder=10))

    # S3 -> S4 Bypass Route (routed cleanly through the center gap at x = 4.50!)
    route(ax,
          [(DC, R1-SH/2),
           (DC, 11.12),
           (4.50, 11.12),
           (4.50, 9.25),
           (MC+0.4, 9.25),
           (MC+0.4, R3+SH/2)],
          label='Expedite retraining', color=LINE_HOT, lseg=3)

    # Weekly Scheduler -> S4
    route(ax, [(DC-1.5, R3), (MC+SW/2, R3)], label='7-day safeguard', ls='--', color=LINE_MAN)

    # S4 -> S5
    route(ax, [(MC, R3-SH/2), (MC, R4+SH/2)], label='Candidate M^(v+1)', color=LINE_DEF)

    # S5 -> S6 PASS
    route(ax, [(MC+SW/2, R4), (DC, R4), (DC, R5+SH/2)], label='p < 0.05  ->  Deploy', color=LINE_AUT, lseg=0)

    # S5 -> S2 FAIL (left side channel, up back to S2)
    FAIL_X = MC - SW/2 - 0.45   # left channel (0.35)
    route(ax, [(MC-SW/2, R4), (FAIL_X, R4), (FAIL_X, R2), (MC-SW/2, R2)], ls='--', color=LINE_HOT)
    # Positioned label above the top horizontal FAIL segment to completely prevent left-margin screen clipping!
    ax.text((FAIL_X + MC - SW/2)/2, R2 + 0.12, 'p >= 0.05 | Keep M^(v)\nCollect more feedback',
            ha='center', va='bottom', fontsize=9.5, color=LINE_HOT, fontweight='bold',
            bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none', alpha=1, zorder=10))

    # S6 -> S0 Loop back
    # Label is placed cleanly on the top horizontal segment which has wide empty clearance!
    FB_X = DC + SW/2 + 0.45     # right channel (8.65)
    route(ax, [(DC+SW/2, R5), (FB_X, R5), (FB_X, R0), (MC+SW/2, R0)], color=LINE_FDB)
    ax.text((FB_X + MC + SW/2)/2, R0 + 0.15, 'Model update activated | v := v+1',
            ha='center', va='bottom', fontsize=10.0, color=LINE_FDB, fontweight='bold',
            bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none', alpha=1, zorder=10))

    # Note Box (positioned with generous spacing at y = 2.9 to clear legend clipping!)
    ax.text(W/2, 2.9,
        'Note: During the 14-day experiment, 31 analyst corrections were\n'
        'collected (< n_min = 50). Retraining was not triggered empirically.\n'
        'Prospective simulation: F1-Score macro: 0.934 -> 0.941\n'
        '(p = 0.18, statistically non-significant in 14-day window).',
        ha='center', va='top', fontsize=9.5, color='#37474F',
        bbox=dict(boxstyle='round,pad=0.5', fc='#FFFDE7', ec='#FFB300', lw=1.0))

    # Legend (Multi-column legend placed lower to prevent Note box overlap)
    legend_els = [
        mpatches.Patch(fc=BLUE_F, ec=BLUE_B, lw=1.5, label='Active Production Environment'),
        mpatches.Patch(fc=AMBER_F, ec=AMBER_B, lw=1.5, label='Feedback Accumulation Buffer B_t'),
        mpatches.Patch(fc=PURP_F, ec=PURP_B, lw=1.5, label='Candidate Retraining Space'),
        mpatches.Patch(fc=IND_F, ec=IND_B, lw=1.5, label='Deployment / Wilcoxon Gate'),
        mpatches.Patch(fc=GREEN_F, ec=GREEN_B, lw=2.0, label='Model Promotion & Activation'),
        Line2D([0],[0], color=LINE_DEF, lw=1.3, label='Standard state transition'),
        Line2D([0],[0], color=LINE_HOT, lw=1.3, label='Analyst/Drift triggered action'),
        Line2D([0],[0], color=LINE_FDB, lw=1.5, ls='--', label='Model promotion loop'),
    ]
    ax.legend(handles=legend_els, loc='lower center', fontsize=9.5,
              framealpha=1.0, edgecolor='#B0BEC5',
              bbox_to_anchor=(0.5, 0.03), ncol=2, title='State Machine Transition Legend', title_fontsize=11.0,
              borderpad=0.8, labelspacing=0.6, columnspacing=1.8)

    out = OUT / 'fig2_feedback_loop_v3_9_16.png'
    fig.savefig(out, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'[OK] Gambar 2 (9:16) saved successfully: {out}')


# ═══════════════════════════════════════════════════════════════
# FIG 3 — Gambar 3: 3-Panel Experimental Results (9:16 Vertical)
# ═══════════════════════════════════════════════════════════════
def fig3_experimental_results_9_16():
    # Data from hasil_kuantitatif_harian.csv
    days_m = [1, 2, 3, 4, 5, 6, 7]
    days_a = [8, 9, 10, 11, 12, 13, 14]
    mttr_m = [1842, 1623, 2104, 1756, 1534, 1987, 1681]
    mttr_a = [14.2, 11.8, 12.5, 10.3, 9.7, 8.9, 9.1]
    ioc_m  = [62, 71, 58, 68, 74, 65, 69]
    ioc_a  = [73, 67, 78, 64, 70, 75, 66]
    f1_a   = [0.9521, 0.9487, 0.9412, 0.9463, 0.9507, 0.9541, 0.9478]
    acc_a  = [0.9589, 0.9552, 0.9487, 0.9531, 0.9571, 0.9600, 0.9545]

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(9, 16), facecolor='white')
    
    # ── PANEL (a) MTTR Comparison ──
    # Manual phase background & Auto background highlights
    ax1.axvspan(0.5, 7.5, alpha=0.08, color=LINE_HOT)
    ax1.axvspan(7.5, 14.5, alpha=0.08, color=LINE_AUT)

    # Manual MTTR (left axis)
    lm, = ax1.plot(days_m, mttr_m, 'o-', color=LINE_HOT, lw=4.2, ms=12, label='MTTR - Manual Baseline')
    
    # Alternating annotation offsets to guarantee ZERO line overlaps or text collisions!
    offsets_m = [12, -20, 12, -20, -20, 12, -20]
    for d, v, o in zip(days_m, mttr_m, offsets_m):
        ax1.annotate(f'{v:,}s', (d, v), textcoords='offset points', xytext=(0, o), ha='center', fontsize=12.5, color=LINE_HOT, fontweight='bold')
    
    mean_m = np.mean(mttr_m)
    ax1.axhline(mean_m, xmin=0.01, xmax=0.5, color=LINE_HOT, lw=2.2, ls='--', alpha=0.6)
    ax1.text(3.8, mean_m+80, f'Mean = {mean_m:.1f}s', color=LINE_HOT, fontsize=12.5, ha='center', fontweight='bold')

    ax1.set_xlim(0.5, 14.5)
    ax1.set_ylim(-200, 2500)
    ax1.set_ylabel('MTTR - Manual Phase (seconds)', color=LINE_HOT, fontsize=14.5, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=LINE_HOT, labelsize=13.0)
    ax1.set_xticks(list(range(1, 15)))
    ax1.set_xticklabels([f'D{d}' for d in range(1, 15)], fontsize=13.0)

    # Automated MTTR (right axis)
    ax1r = ax1.twinx()
    la, = ax1r.plot(days_a, mttr_a, 's-', color=LINE_AUT, lw=4.2, ms=12, label='MTTR - Cognitive SOC (Proposed)')
    
    # Alternating annotation offsets for automated MTTR to avoid overlap with mean line
    offsets_a = [12, -20, 12, -20, 12, -20, 12]
    for d, v, o in zip(days_a, mttr_a, offsets_a):
        ax1r.annotate(f'{v}s', (d, v), textcoords='offset points', xytext=(0, o), ha='center', fontsize=12.5, color=LINE_AUT, fontweight='bold')

    mean_a = np.mean(mttr_a)
    ax1r.axhline(mean_a, xmin=0.5, xmax=0.99, color=LINE_AUT, lw=2.2, ls='--', alpha=0.6)
    ax1r.text(11.2, mean_a-1.8, f'Mean = {mean_a:.2f}s', color=LINE_AUT, fontsize=12.5, ha='center', fontweight='bold')  # Shifted below line

    ax1r.set_ylim(-2, 22)
    ax1r.set_ylabel('MTTR - Automated Phase (seconds)', color=LINE_AUT, fontsize=14.5, fontweight='bold')
    ax1r.tick_params(axis='y', labelcolor=LINE_AUT, labelsize=13.0)

    # Phase labels & Wilcoxon p-value annotation
    ax1.text(4,  2300, 'Phase 1: Manual Baseline', ha='center', fontsize=14.5, fontweight='bold', color=LINE_HOT)
    ax1.text(11, 2300, 'Phase 2: Cognitive SOC', ha='center', fontsize=14.5, fontweight='bold', color=LINE_AUT)
    ax1.axvline(7.5, color='#424242', lw=1.5, ls=':', alpha=0.7)

    # Shift Wilcoxon arrow and statistics to the empty bottom band to clear all data points and labels
    ax1.annotate('', xy=(11.0, 450), xytext=(4.0, 450), arrowprops=dict(arrowstyle='<->', color='#424242', lw=2.0))
    ax1.text(7.5, 600, '↓ 99.39% MTTR Reduction\np = 0.016  (Wilcoxon signed-rank)',
             ha='center', fontsize=14.5, fontweight='bold', color=BK,
             bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.9, ec='#424242'))

    ax1.set_title('(a) Mean Time to Respond (MTTR): Manual vs. Automated Phase', fontsize=15.5, fontweight='bold', pad=10)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)

    # ── PANEL (b) Daily IOC Volume ──
    days_all = list(range(1, 15))
    ioc_all = ioc_m + ioc_a
    colors_b = [LINE_HOT]*7 + [LINE_AUT]*7
    
    ax2.bar(days_all, ioc_all, color=colors_b, alpha=0.7, edgecolor=BK, lw=1.5)
    ax2.axhline(np.mean(ioc_m), xmin=0.01, xmax=0.5, color=LINE_HOT, lw=2.5, ls='--')
    ax2.axhline(np.mean(ioc_a), xmin=0.5, xmax=0.99, color=LINE_AUT, lw=2.5, ls='--')
    
    ax2.text(3.8, np.mean(ioc_m)+3, f'Manual Mean = {np.mean(ioc_m):.1f}', color=LINE_HOT, fontsize=12.5, ha='center', fontweight='bold')
    ax2.text(11.2, np.mean(ioc_a)+3, f'Auto Mean = {np.mean(ioc_a):.1f}', color=LINE_AUT, fontsize=12.5, ha='center', fontweight='bold')

    ax2.set_xlim(0.5, 14.5)
    ax2.set_ylim(0, 95)
    ax2.set_xticks(days_all)
    ax2.set_xticklabels([f'D{d}' for d in days_all], fontsize=13.0)
    ax2.set_xlabel('Day (14-Day Evaluation)', fontsize=14.5, fontweight='bold')
    ax2.set_ylabel('Indicators of Compromise (IOC) Count', fontsize=14.5, fontweight='bold')
    ax2.set_title('(b) Daily IOC Volume (Covariate Balance check, p = 0.535)', fontsize=15.5, fontweight='bold', pad=10)
    ax2.grid(axis='y', linestyle='--', alpha=0.5)

    # ── PANEL (c) Classification Performance ──
    ax3.plot(days_a, f1_a, 'D-', color=PURP_B, lw=4.2, ms=12, label='F1-Score (Weighted)')
    ax3.plot(days_a, acc_a, 's-', color=GREEN_B, lw=4.2, ms=12, label='Accuracy')
    ax3.fill_between(days_a, f1_a, min(f1_a)-0.01, alpha=0.12, color=PURP_B)
    
    mean_f1 = np.mean(f1_a)
    mean_acc = np.mean(acc_a)
    ax3.axhline(mean_f1, color=PURP_B, lw=2.2, ls='--', alpha=0.7)
    ax3.axhline(mean_acc, color=GREEN_B, lw=2.2, ls='--', alpha=0.7)
    
    ax3.text(11.2, mean_f1-0.003, f'Mean F1 = {mean_f1:.4f}', color=PURP_B, fontsize=12.5, ha='center', fontweight='bold')
    ax3.text(9.2, mean_acc+0.003, f'Mean Acc = {mean_acc:.4f}', color=GREEN_B, fontsize=12.5, ha='center', fontweight='bold')

    ax3.set_ylim(0.93, 0.975)
    ax3.set_xticks(days_a)
    ax3.set_xticklabels([f'D{d}' for d in days_a], fontsize=13.0)
    ax3.set_xlabel('Day (Automated Phase Only)', fontsize=14.5, fontweight='bold')
    ax3.set_ylabel('Performance Score', fontsize=14.5, fontweight='bold')
    ax3.set_title('(c) Classification Performance — Automated Phase (493 IOC)', fontsize=15.5, fontweight='bold', pad=10)
    ax3.legend(fontsize=12.5, loc='lower right')
    ax3.grid(linestyle='--', alpha=0.5)

    fig.suptitle('Fig. 3. Experimental Results & Operational Performance Metrics\n14-Day Evaluation  ·  960 IOC  ·  Wilcoxon Paired Evaluation',
                 fontsize=18.0, fontweight='bold', y=1.01)

    plt.tight_layout(rect=[0, 0, 1, 0.99])
    out = OUT / 'fig3_experimental_results_v3_9_16.png'
    fig.savefig(out, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'[OK] Gambar 3 (9:16 3-panel) saved successfully: {out}')


def fig4_confusion_matrix_9_16():
    """Fig. 4: 4x4 Confusion Matrix and Per-Class Metrics — 9:16 Vertical Academic Layout"""
    cm = np.array([
        [29,  3,  1,  0],   # Actual Critical (33)
        [ 2, 81,  5,  1],   # Actual High (89)
        [ 0,  3,139,  5],   # Actual Medium (147)
        [ 0,  1,  4,219],   # Actual Low (224)
    ])
    classes = ['Critical', 'High', 'Medium', 'Low']
    support = cm.sum(axis=1)

    # Compute per-class metrics
    TP = np.diag(cm)
    FP_col = cm.sum(axis=0) - TP
    FN_row = cm.sum(axis=1) - TP
    precision = TP / (TP + FP_col)
    recall    = TP / (TP + FN_row)
    f1        = 2 * precision * recall / (precision + recall)
    w_f1      = np.sum(f1 * support) / support.sum()
    m_f1      = np.mean(f1)

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(9, 16), facecolor='white',
                                         gridspec_kw={'height_ratios': [1.2, 0.9, 0.6]})
    
    # ── PANEL (a) Confusion Matrix Heatmap ──
    # Normalize for color but show raw counts
    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)
    cmap = sns.color_palette("Blues", as_cmap=True)

    im = ax1.imshow(cm_norm, cmap=cmap, aspect='equal', vmin=0, vmax=1)
    cbar = fig.colorbar(im, ax=ax1, fraction=0.045, pad=0.04)
    cbar.set_label('Normalized (row)', fontsize=11.0, fontweight='bold')
    cbar.ax.tick_params(labelsize=10.5)

    # Annotate cells
    for i in range(4):
        for j in range(4):
            raw = cm[i, j]
            pct = cm_norm[i, j] * 100
            text_c = 'white' if cm_norm[i, j] > 0.55 else BK
            ax1.text(j, i, f'{raw}\n({pct:.1f}%)',
                     ha='center', va='center', fontsize=12.5,
                     fontweight='bold' if i == j else 'normal',
                     color=text_c)

    ax1.set_xticks(range(4)); ax1.set_yticks(range(4))
    ax1.set_xticklabels([f'Pred.\n{c}' for c in classes], fontsize=12.0, fontweight='bold')
    ax1.set_yticklabels([f'Actual {c}\n(n={s})' for c, s in zip(classes, support)], fontsize=12.0, fontweight='bold')
    ax1.set_xlabel('Predicted Class', fontsize=13.5, fontweight='bold', labelpad=10)
    ax1.set_ylabel('Actual Class', fontsize=13.5, fontweight='bold', labelpad=10)
    ax1.set_title('(a) Confusion Matrix — Automated Phase (493 IOC)', fontsize=15.5, fontweight='bold', pad=15)

    # Diagonal highlight
    for i in range(4):
        ax1.add_patch(plt.Rectangle((i-0.5, i-0.5), 1, 1,
                                    fill=False, edgecolor='#2E7D32', lw=3.0))

    # ── PANEL (b) Per-Class Precision / Recall / F1 ──
    x  = np.arange(4)
    bw = 0.22
    colors_bar = ['#1565C0', '#1976D2', '#2E7D32']

    b1 = ax2.bar(x - bw,   precision, bw, label='Precision', color=colors_bar[0], alpha=0.87, edgecolor=BK, lw=1.0)
    b2 = ax2.bar(x,         recall,    bw, label='Recall',    color=colors_bar[1], alpha=0.87, edgecolor=BK, lw=1.0)
    b3 = ax2.bar(x + bw,    f1,        bw, label='F1-Score',  color=colors_bar[2], alpha=0.87, edgecolor=BK, lw=1.0)

    for bars in [b1, b2, b3]:
        for bar in bars:
            h = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., h + 0.005,
                     f'{h:.3f}', ha='center', va='bottom', fontsize=10.0, fontweight='bold')

    # Weighted & macro F1 lines
    ax2.axhline(w_f1, color='#C62828', lw=2.0, ls='--', alpha=0.8,
                label=f'Weighted F1 = {w_f1:.3f}')
    ax2.axhline(m_f1, color='#E65100', lw=2.0, ls=':',  alpha=0.8,
                label=f'Macro F1 = {m_f1:.3f}')

    ax2.set_ylim(0.85, 1.04)
    ax2.set_xticks(x)
    ax2.set_xticklabels(classes, fontsize=12.5, fontweight='bold')
    ax2.set_ylabel('Score', fontsize=13.5, fontweight='bold')
    ax2.set_title('(b) Per-Class Precision / Recall / F1-Score', fontsize=15.5, fontweight='bold', pad=15)
    ax2.legend(fontsize=11.0, loc='lower right', framealpha=0.9, edgecolor='#B0BEC5')
    ax2.grid(axis='y', linestyle='--', alpha=0.5)

    # ── PANEL (c) Per-Class Metrics Table ──
    ax3.axis('off')
    table_data = [
        ['Class',    'Precision', 'Recall', 'F1-Score', 'Support'],
        ['Critical', f'{precision[0]:.3f}', f'{recall[0]:.3f}', f'{f1[0]:.3f}', f'{support[0]}'],
        ['High',     f'{precision[1]:.3f}', f'{recall[1]:.3f}', f'{f1[1]:.3f}', f'{support[1]}'],
        ['Medium',   f'{precision[2]:.3f}', f'{recall[2]:.3f}', f'{f1[2]:.3f}', f'{support[2]}'],
        ['Low',      f'{precision[3]:.3f}', f'{recall[3]:.3f}', f'{f1[3]:.3f}', f'{support[3]}'],
        ['W. avg',   f'{w_f1:.3f}',         '—',                f'{w_f1:.3f}',  '493'],
        ['M. avg',   f'{m_f1:.3f}',         '—',                f'{m_f1:.3f}',  '493'],
    ]
    tbl = ax3.table(cellText=table_data[1:], colLabels=table_data[0],
                    loc='center', cellLoc='center',
                    bbox=[0.0, 0.05, 1.0, 0.90])
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(11.0)
    for (r, c_), cell in tbl.get_celld().items():
        cell.set_height(0.12)
        if r == 0:
            cell.set_facecolor('#1565C0')
            cell.set_text_props(color='white', fontweight='bold')
        elif r in [5, 6]:
            cell.set_facecolor('#E3F2FD')
            cell.set_text_props(fontweight='bold')
        elif c_ == 3:  # F1-Score column
            cell.set_facecolor('#E8F5E9')
            cell.set_text_props(fontweight='bold')
            
    ax3.set_title('(c) Performance Metrics Summary Table', fontsize=15.5, fontweight='bold', pad=10)

    fig.suptitle('Fig. 4. Classification Performance: Confusion Matrix & Per-Class Metrics\n'
                 'Automated Phase  ·  493 IOC  ·  4-Class Threat Taxonomy',
                 fontsize=18.0, fontweight='bold', y=1.01)

    plt.tight_layout(rect=[0, 0, 1, 0.98])
    out = OUT / 'fig4_confusion_matrix_v3_9_16.png'
    fig.savefig(out, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'[OK] Gambar 4 (9:16 3-panel) saved successfully: {out}')


if __name__ == '__main__':
    print('Generating high-resolution 9:16 vertical academic figures (v3 — no SUS/HOTL)...\n')
    fig1_architecture_9_16()
    fig2_feedback_loop_9_16()
    fig3_experimental_results_9_16()
    fig4_confusion_matrix_9_16()
    print('\nDone. All high-resolution 9:16 figures (v3) created successfully.')
