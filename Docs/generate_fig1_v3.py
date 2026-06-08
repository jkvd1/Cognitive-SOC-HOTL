"""
Fig. 1 — IEEE-Compliant Architecture (v3, layout fixes)
- Wider canvas, fixed L3 routing box overlap
- Fixed L4 legend position
- Feedback channel stays within bounds
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.lines import Line2D
import numpy as np
from pathlib import Path

OUT = Path(r"C:\Users\ACER\Downloads\Skripsi")
DPI = 220
BK       = '#111111'
BAND_BG  = '#F3F3F3'
BAND_LBL = '#E0E0E0'
GRAY_SRC = '#DADADA'
WHITE    = '#FFFFFF'
GRAY_EXT = '#EBEBEB'


def proc_box(ax, x, y, w, h, label, sub='', style='solid',
             fill=WHITE, lw=1.5, fs=8.5, zorder=3):
    ls = {'solid': (0,()), 'dashed': (0,(5,3)), 'dotted': (0,(1.5,2))}[style]
    ax.add_patch(FancyBboxPatch((x, y), w, h,
        boxstyle="round,pad=0.07,rounding_size=0.07",
        fc=fill, ec=BK, lw=lw, ls=ls, zorder=zorder))
    dy = 0.13 if sub else 0
    ax.text(x+w/2, y+h/2+dy, label, ha='center', va='center',
            fontsize=fs, fontweight='bold', color=BK, zorder=zorder+1,
            multialignment='center')
    if sub:
        ax.text(x+w/2, y+h/2-0.2, sub, ha='center', va='center',
                fontsize=max(5.5, fs-2), color='#444444', zorder=zorder+1,
                multialignment='center')

def seg(ax, pts, lw=1.2, color=BK, ls='-'):
    for i in range(len(pts)-1):
        ax.plot([pts[i][0],pts[i+1][0]], [pts[i][1],pts[i+1][1]],
                color=color, lw=lw, ls=ls, zorder=6, solid_capstyle='butt')

def arrh(ax, p1, p2, lw=1.2, color=BK):
    ax.annotate('', xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle='->', color=color, lw=lw,
                                connectionstyle='arc3,rad=0'))

def route(ax, pts, label='', ls='-', lw=1.2, color=BK, lseg=0):
    seg(ax, pts[:-1], lw=lw, color=color, ls=ls)
    arrh(ax, pts[-2], pts[-1], lw=lw, color=color)
    if label:
        i = min(lseg, len(pts)-2)
        lx = (pts[i][0]+pts[i+1][0])/2
        ly = (pts[i][1]+pts[i+1][1])/2
        horiz = abs(pts[i+1][0]-pts[i][0]) >= abs(pts[i+1][1]-pts[i][1])
        ox, oy = (0, 0.09) if horiz else (0.09, 0)
        ax.text(lx+ox, ly+oy, label,
                ha='center' if horiz else 'left',
                va='bottom' if horiz else 'center',
                fontsize=6.2, color=BK,
                bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none', alpha=1))

def lane(ax, yb, bh, lpad, W, title, subtitle):
    ax.add_patch(FancyBboxPatch((lpad, yb), W-lpad-0.3, bh,
        boxstyle="square,pad=0", fc=BAND_BG, ec='#BBBBBB', lw=0.7, zorder=0))
    ax.add_patch(FancyBboxPatch((0.1, yb), lpad-0.2, bh,
        boxstyle="square,pad=0", fc=BAND_LBL, ec='#BBBBBB', lw=0.7, zorder=0))
    cx = 0.1+(lpad-0.2)/2
    ax.text(cx, yb+bh/2+0.18, title,
            ha='center', va='center', fontsize=8, fontweight='bold', color=BK)
    ax.text(cx, yb+bh/2-0.22, subtitle,
            ha='center', va='center', fontsize=6, color='#555555', multialignment='center')


def fig1_v3():
    # ── Canvas: wider to prevent right-channel clipping ─────────
    W, H = 20.0, 12.0
    fig, ax = plt.subplots(figsize=(W, H))
    ax.set_xlim(0, W); ax.set_ylim(0, H)
    ax.axis('off'); fig.patch.set_facecolor('white')

    LPAD = 2.1
    BH   = 0.82   # standard box height
    BHS  = 0.72   # routing node height (L3)

    # ── Title ──────────────────────────────────────────────────
    ax.text(W/2, H-0.32,
        'Fig. 1.  Cognitive SOC Architecture: Four-Layer Pipeline (Human-On-The-Loop Paradigm, n8n Orchestration)',
        ha='center', fontsize=11.5, fontweight='bold', color=BK)

    # ── Swimlane bands ──────────────────────────────────────────
    L1_YB, L1_BH = 9.5,  1.7   # Layer 1
    L2_YB, L2_BH = 7.2,  1.9   # Layer 2
    L3_YB, L3_BH = 4.0,  2.8   # Layer 3  (3 routing rows)
    L4_YB, L4_BH = 0.5,  3.1   # Layer 4

    lane(ax, L1_YB, L1_BH, LPAD, W, 'LAYER 1', 'Data Acquisition\n& Fusion')
    lane(ax, L2_YB, L2_BH, LPAD, W, 'LAYER 2', 'Threat Analysis\n& Correlation')
    lane(ax, L3_YB, L3_BH, LPAD, W, 'LAYER 3', 'Orchestration &\nDecision Logic')
    lane(ax, L4_YB, L4_BH, LPAD, W, 'LAYER 4', 'Execution &\nAdaptive Feedback')

    # ── LAYER 1 ─────────────────────────────────────────────────
    L1_YC = L1_YB + L1_BH/2
    L1_BB = L1_YC - BH/2

    X1=LPAD+0.25; W1=2.0    # TIP
    X2=X1+W1+0.35; W2=2.35  # ETL
    X3=X2+W2+0.35; W3=2.65  # Temporal Fusion

    proc_box(ax, X1, L1_BB, W1, BH, 'TIP TIP', 'REST API Source', fill=GRAY_SRC)
    proc_box(ax, X2, L1_BB, W2, BH, 'ETL & Normalize', 'T_norm: e_i -> B_i  (Eq. 1)')
    proc_box(ax, X3, L1_BB, W3, BH, 'Temporal Fusion\n& Dedup', 'F_fuse,  dt=3600s  (Eq. 2)', fs=8.2)

    route(ax, [(X1+W1, L1_YC), (X2, L1_YC)], label='JSON feed')
    route(ax, [(X2+W2, L1_YC), (X3, L1_YC)], label='B_i bundles')

    # ── LAYER 2 ─────────────────────────────────────────────────
    L2_YC = L2_YB + L2_BH/2
    L2_BB = L2_YC - BH/2

    XA=LPAD+0.25; WA=2.2    # Feature Eng
    XB=XA+WA+0.35; WB=2.75  # Random Forest
    XC=XB+WB+0.35; WC=2.4   # Confidence

    proc_box(ax, XA, L2_BB, WA, BH, 'Feature Engineering', 'f_i in R^15  (TABEL II)')
    proc_box(ax, XB, L2_BB, WB, BH, 'Random Forest Classifier', 'Eq. 3-4  |  T trees, majority vote', fs=8.2)
    proc_box(ax, XC, L2_BB, WC, BH, 'Confidence\nEstimation', 'conf(f_i)  (Eq. 4)')

    route(ax, [(XA+WA, L2_YC), (XB, L2_YC)])
    route(ax, [(XB+WB, L2_YC), (XC, L2_YC)])

    # L1 -> L2 inter-layer (route bottom-of-Fusion -> gap -> Feature Eng top)
    GAP12 = (L1_YB + L2_YB+L2_BH) / 2   # center of gap: (9.5 + 9.1)/2 = 9.3
    FUS_CX = X3 + W3/2
    FEA_CX = XA + WA/2
    route(ax,
          [(FUS_CX, L1_BB),
           (FUS_CX, GAP12),
           (FEA_CX, GAP12),
           (FEA_CX, L2_BB+BH)],
          label='IOC stream', lseg=1)

    # ── LAYER 3 — Decision D + 3 routing rows + IDS Rule ────────
    # Three rows:
    L3_ROW_T = L3_YB + L3_BH - 0.6 - BHS/2   # top    ~5.84
    L3_ROW_M = L3_YB + L3_BH/2                # middle ~5.40
    L3_ROW_B = L3_YB + 0.6 + BHS/2            # bottom ~4.96

    # Decision D box (spans full band height, left side)
    XD=LPAD+0.25; WD=2.2
    proc_box(ax, XD, L3_YB+0.18, WD, L3_BH-0.36,
             'Decision\nFunction  D',
             'Eq. 5  |  4-case piecewise\n+ Safety Override (Critical)', fs=8.5, lw=2.0)

    # Routing nodes — short labels, fixed width, clear separation from IDS
    XR=XD+WD+0.55; WR=2.0      # routing column (3 stacked rows)
    XI=XR+WR+0.9; WI=2.6       # IDS Rule Gen (clear gap from routing column)

    proc_box(ax, XR, L3_ROW_T-BHS/2, WR, BHS, 'autonomous_block',
             'conf > 0.85', fill=GRAY_SRC, fs=8.0)
    proc_box(ax, XR, L3_ROW_M-BHS/2, WR, BHS, 'escalate_HOTL',
             'theta_low <= conf <= theta_high', style='dashed', fs=8.0)
    proc_box(ax, XR, L3_ROW_B-BHS/2, WR, BHS, 'log_review',
             'conf < 0.60', fs=8.0)
    proc_box(ax, XI, L3_ROW_T-BHS/2, WI, BHS, 'IDS Rule Generation',
             'XML -> Wazuh  (Jalur B)', fill=GRAY_SRC)

    # Decision D -> three routing rows
    DEC_R = XD+WD
    MID_GAP = (DEC_R + XR) / 2

    route(ax, [(DEC_R, L3_ROW_T), (XR, L3_ROW_T)], label='block')
    route(ax, [(DEC_R, L3_ROW_M), (XR, L3_ROW_M)], label='escalate')
    route(ax, [(DEC_R, L3_ROW_B), (XR, L3_ROW_B)], label='log')
    route(ax, [(XR+WR, L3_ROW_T), (XI, L3_ROW_T)], label='High/Critical')

    # L2 -> L3 inter-layer (Confidence bottom -> Decision top)
    GAP23 = (L2_YB + L3_YB+L3_BH) / 2   # (7.2 + 6.8)/2 = 7.0
    DEC_CX = XD + WD/2
    CON_CX = XC + WC/2
    route(ax,
          [(CON_CX, L2_BB),
           (CON_CX, GAP23),
           (DEC_CX, GAP23),
           (DEC_CX, L3_YB+L3_BH-0.18)],
          label='(y_hat, conf_i)', lseg=1)

    # ── LAYER 4 — Execution (upper) + Feedback chain (lower) ────
    L4_UP_YC = L4_YB + L4_BH*0.72   # ~2.73
    L4_UP_BB = L4_UP_YC - BH/2
    L4_LO_YC = L4_YB + L4_BH*0.22   # ~1.18
    L4_LO_BB = L4_LO_YC - BH/2

    # Execution row
    XW=LPAD+0.25; WW=2.0    # Wazuh
    XT=XW+WW+0.3; WT=2.25   # Telegram (HOTL)
    XU=XT+WT+0.3; WU=2.0    # Audit

    proc_box(ax, XW, L4_UP_BB, WW, BH, 'Wazuh SIEM', 'Rule Deploy\nRESTful API')
    proc_box(ax, XT, L4_UP_BB, WT, BH, 'Telegram Bot\n(HOTL Interface)', 'Push notify\nInteractive btns', style='dashed')
    proc_box(ax, XU, L4_UP_BB, WU, BH, 'Audit Log\n(SQLite)', 'Version tracking')

    # Page-Hinkley — external trigger (dotted), right of Audit
    XPH=XU+WU+0.35; WPH=2.2
    proc_box(ax, XPH, L4_UP_BB, WPH, BH, 'Page-Hinkley\nDrift Detect',
             'Eq. 10  |  d=0.005,  l=50', fill=GRAY_EXT, style='dotted', fs=8.0)

    # Feedback chain row
    XF=LPAD+0.25; WF=2.4    # Feedback Buffer
    XRT=XF+WF+0.3; WRT=2.2  # Retraining
    XGT=XRT+WRT+0.3; WGT=2.25 # Deployment Gate
    XMD=XGT+WGT+0.3; WMD=2.35 # Model Update

    proc_box(ax, XF,  L4_LO_BB, WF,  BH, 'Feedback Buffer  B_t', 'Analyst corrections  (Eq. 11)')
    proc_box(ax, XRT, L4_LO_BB, WRT, BH, 'Augmented Retraining', 'T_retrain  (Eq. 8)')
    proc_box(ax, XGT, L4_LO_BB, WGT, BH, 'Deployment Gate', 'Wilcoxon  a=0.05  (Eq. 9)')
    proc_box(ax, XMD, L4_LO_BB, WMD, BH, 'RF Model Update', 'M_RF^(v+1)\nwarm_start = False')

    route(ax, [(XF+WF, L4_LO_YC), (XRT, L4_LO_YC)])
    route(ax, [(XRT+WRT, L4_LO_YC), (XGT, L4_LO_YC)])
    route(ax, [(XGT+WGT, L4_LO_YC), (XMD, L4_LO_YC)], label='p < 0.05')

    # ── L3 -> L4 inter-layer connections ────────────────────────
    GAP34 = (L4_YB+L4_BH + L3_YB) / 2   # (3.6 + 4.0)/2 = 3.8
    WAZ_CX = XW+WW/2
    TEL_CX = XT+WT/2
    AUD_CX = XU+WU/2

    # Block -> Wazuh
    BLK_CX = XR+WR/2
    route(ax, [(BLK_CX, L3_ROW_T-BHS/2),
               (BLK_CX, GAP34),
               (WAZ_CX, GAP34),
               (WAZ_CX, L4_UP_BB+BH)], label='block', lseg=2)

    # Escalate -> Telegram (route slightly offset in gap to avoid overlap)
    ESC_CX = XR+WR/2
    route(ax, [(ESC_CX, L3_ROW_M-BHS/2),
               (ESC_CX, GAP34+0.15),
               (TEL_CX, GAP34+0.15),
               (TEL_CX, L4_UP_BB+BH)], label='escalate', lseg=2)

    # Log -> Audit (offset)
    LOG_CX = XR+WR/2
    route(ax, [(LOG_CX, L3_ROW_B-BHS/2),
               (LOG_CX, GAP34+0.3),
               (AUD_CX, GAP34+0.3),
               (AUD_CX, L4_UP_BB+BH)], label='log', lseg=2)

    # IDS Rule -> Wazuh (right of IDS block, down, left)
    IDS_CX = XI+WI/2
    route(ax, [(IDS_CX, L3_ROW_T-BHS/2),
               (IDS_CX, GAP34-0.12),
               (WAZ_CX+0.55, GAP34-0.12),
               (WAZ_CX+0.55, L4_UP_BB+BH)], label='IDS rules', lseg=2)

    # Telegram -> Feedback Buffer (vertical mid-section)
    MID_L4 = (L4_UP_BB + L4_LO_BB+BH) / 2
    FBF_CX = XF+WF/2
    route(ax, [(TEL_CX, L4_UP_BB),
               (TEL_CX, MID_L4),
               (FBF_CX, MID_L4),
               (FBF_CX, L4_LO_BB+BH)],
          label='analyst corrections', ls='--', lseg=1)

    # Page-Hinkley -> Feedback Buffer (drift alarm, dotted)
    PH_CX = XPH+WPH/2
    route(ax, [(PH_CX, L4_UP_BB),
               (PH_CX, MID_L4-0.08),
               (XF+WF-0.55, MID_L4-0.08),
               (XF+WF-0.55, L4_LO_BB+BH)],
          label='drift alarm', ls=':', lseg=1)

    # ── Feedback Loop: Model Update -> RF Classifier ─────────────
    # Route via right channel (inside canvas)
    FB_X = XMD+WMD+0.5   # right channel x = stays well within W=18.5
    RF_CX = XB+WB/2

    pts_fb = [
        (XMD+WMD, L4_LO_YC),           # right of Model Update
        (FB_X,    L4_LO_YC),            # rightward to channel
        (FB_X,    L2_BB+BH+0.2),        # up to L2 level
        (RF_CX+0.6, L2_BB+BH+0.2),     # left to above RF
        (RF_CX+0.6, L2_BB+BH),         # down into RF top
    ]
    seg(ax, pts_fb[:-1], lw=1.7, ls='--')
    arrh(ax, pts_fb[-2], pts_fb[-1], lw=1.7)
    # Label inside the right channel
    ax.text(FB_X+0.1, (L4_LO_YC+L2_BB+BH)/2,
            'M_RF^(v+1)\n--> RF Layer 2',
            ha='left', va='center', fontsize=7, color=BK,
            bbox=dict(boxstyle='square,pad=0.12', fc='white', ec='none', alpha=1))

    # ── Legend (bottom-right, clear of all boxes) ───────────────
    legend_els = [
        mpatches.Patch(fc=WHITE, ec=BK, lw=1.5,
                       label='Automated Process  (solid border)'),
        mpatches.Patch(fc=WHITE, ec=BK, lw=1.2, ls=(0,(5,3)),
                       label='HOTL Interface / Analyst  (dashed border)'),
        mpatches.Patch(fc=WHITE, ec=BK, lw=1.2, ls=(0,(1.5,2)),
                       label='External Monitor / Trigger  (dotted border)'),
        mpatches.Patch(fc=GRAY_SRC, ec=BK, lw=1.5,
                       label='Data Source / Output Artifact  (gray fill)'),
        Line2D([0],[0], color=BK, lw=1.5, ls='--',
               label='Analyst Feedback / Conditional Flow'),
    ]
    ax.legend(handles=legend_els, fontsize=8,
              framealpha=1.0, edgecolor='#AAAAAA', loc='lower right',
              bbox_to_anchor=(0.99, 0.005), ncol=1,
              title='Legend', title_fontsize=8)

    out = OUT / 'fig1_architecture.png'
    fig.savefig(out, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'[OK] fig1 saved: {out}')


if __name__ == '__main__':
    fig1_v3()
    print('Done.')
