# IEEE Transactions — Peer Review Report (V8a)

**Manuscript Title:** *Implementasi Pipeline Intelijen Ancaman Jaringan Otomatis Menggunakan N8n Untuk Percepatan Respons Insiden*

**Author:** Joshua Kenneth Van Dyon, Bina Nusantara University

**Reference Architecture:** IEEE Document 11145017 — Zhang et al. (2025), "Design and Computational Modeling of an AI-Based Automated Cybersecurity Incident Response System," *IEEE Access* (DOI: 10.1109/ACCESS.2025.3603975). Hereafter: **AIR/GameDefense**.

**Review Date:** 2026-05-19

**Prior Review:** V3 (2026-04-06) — Major Revision recommended.

---

## 1. Summary

This manuscript presents a Cognitive SOC architecture implementing a Human-On-The-Loop (HOTL) paradigm through a four-layer pipeline: (1) Data Acquisition & Fusion, (2) Threat Analysis & Correlation via Random Forest, (3) Orchestration & Decision Logic with confidence-based routing, and (4) Execution & Adaptive Feedback with Page-Hinkley drift detection. The system ingests IOC from TIP TIP, classifies them, autonomously generates Wazuh IDS rules, and provides analyst oversight via Telegram.

**Progress since V3 review:** The manuscript has improved *substantially*:
- Four-layer architecture now explicitly maps to AIR [1] Layers 1–4 with a dedicated comparison table (TABEL III)
- Mathematical formalization added (Eqs. 1–18+ covering fusion, classification, decision function, feedback loop, drift detection, evaluation metrics)
- `warm_start` contradiction resolved (now `warm_start=False`)
- Ablation study designed and executed
- Per-class metrics reporting planned (F1 macro/weighted, confusion matrix)
- Statistical rigor added: power analysis, Holm-Bonferroni correction, per-IOC sensitivity analysis
- **Experimental results section added** with actual data from 14-day experiment (960 IOC)
- **UAT results** from 17 respondents (SUS mean 75.9)

**Current mapping to AIR architecture:**

| AIR Layer | V8a Implementation | Status vs. V3 |
|---|---|---|
| Layer 1: STIX/TAXII Fusion | JSON-internal via n8n (Eqs. 1–2), format-agnostic design | ✅ Formalized, limitation acknowledged |
| Layer 2: Attention-LSTM | Random Forest (Eqs. 3–4) with 3-point justification | ✅ Positioned with rationale |
| Layer 3: Bayesian Game Theory | Deterministic threshold routing $\mathcal{D}$ (Eq. 5) + safety override | ✅ Positioned with Eqs. 6–7 |
| Layer 4: DRL Optimization | Adaptive Feedback Loop + Page-Hinkley (Eqs. 9–13) | ✅ Positioned with Eq. 8 in Future Work |

---

## 2. Strengths

**S1 — Mature Architectural Framing.** The four-layer decomposition with explicit AIR correspondence table (TABEL III) is a significant improvement. Each architectural simplification is transparently rationalized with specific justifications (HOTL transparency, low-code constraints, dataset size). This honest positioning transforms what were critical weaknesses in V3 into deliberate, justified design decisions.

**S2 — Rigorous Statistical Design.** The addition of *a priori* power analysis (G*Power, Cohen's d ≥ 1.4 for N=7), Holm-Bonferroni correction for multiple comparisons, and per-IOC sensitivity analysis (N ≈ 350–700) demonstrates statistical maturity well above the typical undergraduate level. The explicit acknowledgment that the design is powered only for large effects is commendable.

**S3 — Empirical Results with Strong Effect Sizes.** The reported results show genuinely large effects: 99.39% MTTR reduction (p = 0.016), 72.6% FPR reduction, and 92.6% IDS rule acceptance rate. These effect sizes far exceed the d ≥ 1.4 threshold, making the statistical results credible even with N = 7 paired observations.

**S4 — Dataset Construction Transparency.** The explicit documentation of the CTU-13→IOC transformation pipeline (IP extraction, VirusTotal lookup, GeoIP imputation), the deterministic labeling function $\mathcal{L}$ with quartile-derived boundaries, and the labeling limitation disclosure (single labeler, no Cohen's κ) are best practices for reproducibility.

**S5 — UAT with Bias Mitigation.** The single-blind design, anonymous questionnaire, and organizational diversity reporting for UAT are methodological improvements absent from V3. The SUS threshold is correctly cited from Bangor, Kortum & Miller (2008) rather than just Brooke (1996).

---

## 3. Weaknesses & Technical Flaws

### W1 — Duplicate Feature Table Rows (Critical Data Error)

TABEL II in the docx contains **duplicate entries**: rows for `asn_reputation`, `feed_frequency`, and `threat_category` appear twice (lines 150–173 in extracted text). This results in 11 listed features instead of 9, while the text claims 15 dimensions after one-hot encoding. The V7 markdown version has 9 correct features including `active_days_count`, but V8a's table is corrupted.

**Impact:** A reviewer will immediately flag this as a data integrity issue. The feature count (15) is only correct with the 9-unique-feature version.

### W2 — Missing Per-Class Metrics in Results

Section §IV.B.5 promises per-class Precision/Recall/F1, confusion matrix, and macro/weighted F1. The results section (§IV.F.2) reports only aggregate accuracy (94.93%) and weighted F1 (0.949). The raw data (`hasil_kuantitatif_harian.csv`) contains both `f1_score_weighted` and `f1_score_macro` columns, but:
- **No per-class breakdown** is reported in the manuscript
- **No confusion matrix** is presented
- The macro F1 values (0.896–0.917 range) are notably lower than weighted F1 (0.941–0.954), suggesting weaker performance on minority classes — exactly the pattern the per-class reporting was designed to surface

**Impact:** This is an unfulfilled methodological promise. Per-class metrics for `Critical` (7% of data) are operationally the most important and must be reported.

### W3 — Manual-Phase Baseline Ground Truth

The `hasil_kuantitatif_harian.csv` shows that TP, TN, FP, FN, accuracy, F1, and FPR are **blank for all 7 manual-phase days** (days 1–7). Only MTTR is recorded for the manual phase. This means:
- The claimed "88.2% manual accuracy" and "8.14% manual FPR" have **no per-day raw data** backing them in the CSV
- The Wilcoxon signed-rank test for MTTR (p = 0.016) can be verified from the CSV data, but accuracy/FPR/F1 comparisons cannot

**Impact:** Either (a) the manual-phase classification metrics were computed separately and should be documented, or (b) they are aggregate estimates that lack the daily granularity needed for paired statistical testing. This must be clarified — it affects the validity of the Wilcoxon tests for all non-MTTR metrics.

### W4 — Abstract Mismatch with Final Title

The title in V8a is shortened to "Implementasi Pipeline Intelijen Ancaman Jaringan Otomatis Menggunakan N8n Untuk Percepatan Respons Insiden" — dropping the original subtitle about Cognitive SOC and HOTL. However, the abstract and body extensively discuss Cognitive SOC, HOTL, and Adaptive Feedback Loop. The title undersells the contribution.

The V7 markdown retains the full title: "Arsitektur Cognitive SOC Berbasis Hybrid Autonomous AI Agent dan Adaptive Feedback Loop: ..." This is more accurate.

### W5 — Equation Numbering Inconsistency

The V8a docx has lost equation numbers in many places — the extracted text shows formulas referenced as "Pers. 1–2", "Pers. 3–4", etc. in TABEL III, but the actual equations in the body text are rendered without visible `\tag{}` numbering (only as inline math fragments). The V7 markdown had consistent `\tag{1}` through `\tag{18}` numbering.

**Impact:** IEEE requires sequential equation numbering. The docx conversion appears to have stripped tags from many equations.

### W6 — Ablation Results Underspecified

The ablation study reports only one condition in detail: "Ablation B shows MTTR would rise to 847.3 seconds without IDS Rule Generation." Missing:
- **Ablation A results** (impact of removing Feedback Loop on accuracy over time)
- **Ablation C results** (static vs. calibrated thresholds — specific FPR and F1 delta)
- No table summarizing all ablation conditions side-by-side

### W7 — 31 Corrections vs. n_min = 50 Trigger

The feedback loop collected 31 corrections over 7 days, which is below the retraining trigger threshold $n_{\text{min}} = 50$. This means the Adaptive Feedback Loop **never triggered an actual retraining cycle** during the experiment. The manuscript honestly reports a "prospective simulation" showing F1 improvement from 0.934→0.941 (not statistically significant), but this should be discussed more prominently as it means the feedback loop's core mechanism was **never empirically validated** in production.

### W8 — No Figure Included

Both V8a and V7 reference "Gambar 1" (system architecture) and "Gambar 2" (feedback loop state diagram), but neither document contains the actual figures. For IEEE submission, these are **mandatory**.

---

## 4. Novelty & Contribution Assessment

### Position Relative to V3 Review

The manuscript has significantly improved its positioning against AIR [1]. The critical gaps identified in V3 have been addressed through:
- Transparent architectural positioning (TABEL III) rather than attempting to rival AIR
- Mathematical formalization of all pipeline components
- Actual empirical results demonstrating the system works

### Contribution Classification

| Contribution | Type | Assessment |
|---|---|---|
| HOTL implementation via Telegram | Applied/Implementation | ✅ Novel — no prior empirical HOTL SOC study with low-code |
| Four-layer pipeline with n8n orchestration | System Design | ✅ Reproducible design, democratization angle valid |
| Adaptive Feedback Loop with Page-Hinkley | Methodological | ⚠️ Designed but not fully validated (31 < 50 trigger) |
| 99.39% MTTR reduction | Empirical | ✅ Strong result, large effect size |
| SUS evaluation of SOC automation | Evaluation | ✅ Novel — absent from AIR [1] |
| Per-class reporting + confusion matrix | Methodological promise | ❌ Not delivered in results |

**Verdict:** The work makes a **solid applied contribution** as a practical, reproducible instantiation of AIR principles in a resource-constrained, low-code SOC context. The MTTR reduction and IDS rule synthesis results are compelling. The contribution is **incremental but well-framed** — the manuscript does not overclaim, and the limitations section is thorough.

---

## 5. Detailed Comments

### 5.1 — Data Integrity Issues

#### 5.1.1 — Duplicate Feature Table (CRITICAL)

**Location:** Lines 134–173 in extracted text (TABEL II)

Features `asn_reputation`, `feed_frequency`, and `threat_category` each appear twice. The correct table should have 9 unique features (as in V7.md, including `active_days_count`):

```diff
 | 4 | asn_reputation | Numerik (0–1) | ... |
 | 5 | feed_frequency | Numerik | ... |
 | 6 | threat_category | Kategorikal | ... |
-| 7 | asn_reputation | Numerik (0–1) | ... |   ← DUPLICATE
-| 8 | feed_frequency | Numerik | ... |          ← DUPLICATE
-| 9 | threat_category | Kategorikal | ... |      ← DUPLICATE
+| 7 | first_seen_age_days | Numerik | Min-max normalisasi | 0.15 |
+| 8 | source_diversity_count | Numerik | Min-max normalisasi | 0.73 |
+| 9 | active_days_count | Numerik | Log-transform, lalu min-max normalisasi | 0.38 |
```

#### 5.1.2 — Cross-Validation of Results Against Raw Data

I cross-checked the reported results against `hasil_kuantitatif_harian.csv`:

| Metric | Reported in V8a | Computed from CSV | Match? |
|---|---|---|---|
| Total IOC (manual) | 467 | 62+71+58+68+74+65+69 = **467** | ✅ |
| Total IOC (auto) | 493 | 73+67+78+64+70+75+66 = **493** | ✅ |
| Total IOC | 960 | 467+493 = **960** | ✅ |
| Mean daily volume (manual) | 66.7 | 467/7 = **66.71** | ✅ |
| Mean daily volume (auto) | 70.4 | 493/7 = **70.43** | ✅ |
| Mean MTTR (manual) | 1789.6 sec | (1842+1623+2104+1756+1534+1987+1681)/7 = **1789.57** | ✅ |
| Mean MTTR (auto) | 10.93 sec | (14.2+11.8+12.5+10.3+9.7+8.9+9.1)/7 = **10.93** | ✅ |
| IDS rules generated | 122 | 18+16+20+15+18+19+16 = **122** | ✅ |
| IDS rules accepted | 113 | 16+15+18+14+17+18+15 = **113** | ✅ |
| Rule acceptance rate | 92.6% | 113/122 = **92.62%** | ✅ |
| Total corrections | 31 | 5+4+6+4+5+4+3 = **31** | ✅ |
| Mean accuracy (auto) | 94.93% | mean of daily accuracies = **(95.39+95.52+94.87+95.31+95.71+96.00+95.45)/7 = 95.46%** | ⚠️ Discrepancy |

> [!WARNING]
> **Accuracy discrepancy:** The daily accuracies in the CSV average to **95.46%**, not the reported **94.93%**. Two possibilities:
> 1. The reported 94.93% was computed as aggregate TP+TN over total IOC (i.e., sum(TP+TN)/sum(all) = (432+34)/493), which gives a different result from the mean of daily accuracies
> 2. There's a rounding or computation error
> 
> **Action required:** Clarify whether accuracy is reported as the mean of daily accuracies or as the aggregate over all 493 IOC. Use the same aggregation method consistently across all metrics and state it explicitly.

#### 5.1.3 — UAT Data Cross-Validation

From `hasil_kualitatif_sus.csv`:

| Metric | Reported | Computed from CSV | Match? |
|---|---|---|---|
| Respondent count | 17 | 17 rows (R01–R17) | ✅ |
| Mean SUS | 75.9 | mean(77.5, 72.5, 80.0, 65.0, 82.5, 75.0, 77.5, 70.0, 85.0, 72.5, 67.5, 80.0, 77.5, 72.5, 82.5, 75.0, 80.0) = **76.0** | ⚠️ Minor discrepancy (75.9 vs 76.0) |
| % above 68 | 88.2% | 15/17 = **88.24%** | ✅ |
| Adjective: "Excellent" | not reported | 1 respondent (R09: 85.0) | — |
| Adjective: "OK" | not reported | 2 respondents (R04: 65.0, R11: 67.5) | — |

SUS mean discrepancy is trivial (rounding). The data is consistent.

### 5.2 — Statistical Analysis Gaps

#### 5.2.1 — Missing Paired Tests for Non-MTTR Metrics

The manuscript reports Wilcoxon p = 0.016 for MTTR only. For accuracy, FPR, and F1-Score, **no p-values are reported**. Given that the manual phase CSV lacks daily TP/TN/FP/FN data, paired statistical tests for these metrics may not be feasible. If they were computed differently (e.g., on a per-IOC basis), this must be stated.

#### 5.2.2 — Effect Size Not Reported

Cohen's d is mentioned in the methodology but **not reported in the results section** for any metric. For MTTR: d = (1789.6 - 10.93) / pooled_SD. This should be computed and reported.

#### 5.2.3 — Holm-Bonferroni Not Applied

The methodology specifies Holm-Bonferroni correction for four simultaneous tests, but only one p-value (MTTR) is reported in the results. If only one metric was tested, correction is unnecessary — but this should be stated explicitly.

### 5.3 — IEEE Formatting Compliance

| Item | IEEE Standard | V8a Status | Action |
|---|---|---|---|
| Title | ≤15 words, centered, informative | ⚠️ Title undersells contribution — restore Cognitive SOC/HOTL subtitle | Restore full title from V7 |
| Abstract | 150–250 words, results-oriented | ✅ Includes results (V7 abstract already updated) — but V8a abstract is **still the old proposal version** without results | ❗ Update V8a abstract to match V7 |
| Section numbering | Roman numerals (I, II, III...) | ⚠️ Mixed — some sections use "Pendahuluan" without numbering, others reference "§III.D" | Standardize |
| Figures | Required for IEEE | ❌ No figures present | Must add Fig. 1 (architecture), Fig. 2 (feedback loop), Fig. 3 (MTTR trend), Fig. 4 (confusion matrix) |
| Tables | Numbered, captioned, referenced | ⚠️ TABEL I has structure issues in docx (column alignment); TABEL II has duplicates | Fix |
| Equations | Sequentially numbered | ⚠️ Many equations lost numbering in docx conversion | Renumber all equations 1–N |
| Two-column layout | Required for IEEE | ❌ Single column | Convert using IEEEtran template |
| References | [N] format, 29 refs | ✅ Mostly compliant; [29] added (Lu et al. concept drift) | Minor fixes needed |

### 5.4 — Content-Specific Comments

#### Abstract (Line 7)
The V8a abstract is **still the old proposal-style abstract** without experimental results. The V7 markdown has the updated abstract with "reduksi MTTR sebesar 99,39%..." etc. The V8a docx must be updated to match.

#### "Memperkuat Memperkuat" (Line 45)
Typographic error: "Memperkuat" is repeated twice.

#### Safety Override in Decision Function
The safety override (`Critical` never routed to `log_review`) is an excellent addition absent from V3. However, Eq. 5 in V8a (extracted text) shows the full four-case piecewise function but the docx appears to have lost the LaTeX formatting. Verify rendering.

#### Sensitivity Analysis for n_min (Line 235)
The manuscript promises sensitivity analysis for $n_{\text{min}} \in \{30, 50, 75, 100\}$ but the results section does not report it. Either conduct and report, or remove the promise.

#### Labeling Function Thresholds (Lines 179–182)
The thresholds (25, 55, 80) are "validated through consultation with one senior SOC analyst (>5 years experience)." This is methodologically weak for an IEEE paper. Strengthen by:
- Reporting the analyst's inter-rater agreement on a held-out sample
- Or running sensitivity analysis on threshold boundaries ±5

### 5.5 — Reference Assessment

**Total References:** 29 (including [29] Lu et al. 2019 — new addition for concept drift)

**Recency:** ~83% from 2022–2025. ✅ Acceptable.

**New issues:**
- **[6] Bilali et al.** — URL `https://zenodo.org/record/iris-orchestrator` may be invalid. Verify link.
- **[15] Ullah & Mahmoud** — Now correctly annotated with the primary CTU-13 reference (García et al. 2014). ✅ Good practice.
- **[18] Brooke (1996)** — The SUS threshold is now correctly attributed to Bangor, Kortum & Miller (2008) in the body text, but this secondary reference is not in the reference list. Add it as [30].

---

## 6. Final Recommendation

### **MINOR REVISION**

**Justification:**

The manuscript has undergone a **transformative improvement** since the V3 Major Revision. The critical deficiencies identified in the prior review — lack of mathematical formalism, absent AIR positioning, `warm_start` contradiction, no ablation design, no experimental results — have all been addressed substantively. The work now reads as a **complete empirical study** with actual results, proper statistical design, and transparent limitations.

The remaining issues are correctable without architectural or methodological redesign:

| Priority | Issue | Effort |
|---|---|---|
| **P0** | Fix duplicate feature table rows (TABEL II) | 5 min |
| **P0** | Update V8a abstract to include results (match V7) | 10 min |
| **P0** | Clarify accuracy computation method (mean-of-daily vs. aggregate) | 15 min |
| **P0** | Add per-class metrics (Precision/Recall/F1 per class + confusion matrix) — data exists in CSV | 30 min |
| **P1** | Report missing effect sizes (Cohen's d) | 15 min |
| **P1** | Report/remove Holm-Bonferroni (only 1 p-value reported) | 10 min |
| **P1** | Add ablation A and C results or explain why only B is reported | 20 min |
| **P1** | Create and include Figures 1–4 | 2–3 hours |
| **P1** | Fix equation numbering in docx | 30 min |
| **P2** | Restore full title with Cognitive SOC/HOTL subtitle | 2 min |
| **P2** | Fix "Memperkuat Memperkuat" typo | 1 min |
| **P2** | Add Bangor, Kortum & Miller (2008) to references | 5 min |
| **P2** | Address n_min sensitivity promise or remove | 10 min |
| **P2** | Discuss feedback loop non-triggering more prominently | 10 min |

**Overall Assessment:**

The manuscript demonstrates a well-designed, empirically validated Cognitive SOC system that achieves its stated objectives. The MTTR reduction (99.39%), FPR reduction (72.6%), and IDS rule acceptance rate (92.6%) are compelling results. The honest framing against AIR [1] — as a practical, low-code instantiation rather than a competitor — is the correct positioning. With the minor corrections above, this manuscript is ready for submission to an IEEE conference or a journal like IEEE Access.

---

*Reviewer: Senior Peer Review (IEEE Transactions Standard)*
*Confidence: High — Familiar with the AIR reference architecture and the manuscript's evolution from V3 through V8a.*
