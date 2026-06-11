# Cognitive SOC: Human-On-The-Loop (HOTL) Threat Intelligence Pipeline

An automated Cognitive Security Operations Center (SOC) architecture implementing the **Human-On-The-Loop (HOTL)** paradigm for IOC triage, threat classification, and IDS rule deployment.

The machine learning classifier is a **Random Forest** model trained on 16 structural and contextual features derived from raw IOC attributes — **no TIP-scored fields are used as features** (i.e., `confidence`, `verdict`, `exposure_score` are reserved for label derivation only to prevent data leakage). It classifies Indicators of Compromise (IOC) into a four-class threat taxonomy (`Low`, `Medium`, `High`, `Critical`) and routes decisions via confidence-based thresholds.

---

## 📁 Repository Structure

```
Skripsi/
├── Data/
│   ├── IOC.json                          # 4,200 real-world TIP IOCs (STIX format)
│   ├── ioc_rf_model.pkl                  # Trained Random Forest classifier
│   ├── label_encoder.pkl                 # Label encoder (4 severity classes)
│   ├── confusion_matrix_latest.png       # Latest confusion matrix & classification report
│   ├── feature_importance.png            # RF feature importance plot
│   ├── cognitive_soc_logs.db             # SQLite operational log database
│   ├── wazuh_rules_generated.xml         # 122 autonomously synthesized Wazuh detection rules
│   ├── n8n_workflows_cognitive_soc.json  # SOAR orchestrator workflow definitions
│   ├── n8n_etl_node.js                   # ETL node script for n8n
│   ├── filter_and_export_research_data.py/.js  # Data export utilities
│   └── local_telegram_bot_handler.py     # HOTL Telegram notification handler
├── RandomForest.ipynb                    # Full ML pipeline: preprocessing → training → evaluation
└── README.md
```

---

## 🛠️ Technologies

| Layer | Component |
|---|---|
| Orchestration | [n8n](https://n8n.io/) (self-hosted, Docker) |
| SIEM / IDS | Wazuh Manager (Windows 11 host) |
| ML | Python 3.7, scikit-learn, pandas, NumPy |
| Visualization | matplotlib, seaborn |
| HOTL Interface | Telegram Bot API |
| Data Format | STIX 2.1, JSON, XML |

---

## 🧠 Model Architecture

| Property | Value |
|---|---|
| **Model** | Random Forest Classifier |
| **Estimators** | 200 |
| **Max Depth** | 12 |
| **Min Samples Leaf** | 5 |
| **Class Weight** | balanced |
| **Feature Vector** | 16-dimensional (see below) |
| **Training Set** | N = 2,400 (80% of stratified 3,000 sample) |
| **Validation Set** | N = 600 (20% of stratified 3,000 sample) |

### Feature Set (16 features — zero leakage)

| # | Feature | Type | Source |
|---|---|---|---|
| 1–3 | `indicator_type_*` | one-hot (3) | STIX pattern field |
| 4–8 | `threat_category_*` | one-hot (5) | NLP on description text |
| 9 | `active_days` | scalar | log1p(modified − created) |
| 10 | `first_seen` | scalar | active_days × 0.8 |
| 11 | `hour_created` | scalar | hour(created) / 23 |
| 12 | `geo_risk` | scalar | country_code heuristic |
| 13 | `asn_reputation` | scalar | asn_owner heuristic |
| 14 | `name_len` | scalar | log1p(len(name)) / 10 |
| 15 | `dot_count` | scalar | name.count('.') / 10 |
| 16 | `hyphen_count` | scalar | name.count('-') / 5 |

### Severity Label Mapping (from TIP `exposure_score` 1–10)

| Label | Rule |
|---|---|
| `Critical` | score = 10 |
| `High` | score ∈ {6, 7} |
| `Low` | score ≤ 3 OR verdict ∈ {Benign, Unknown} |
| `Medium` | otherwise |

---

## 📊 Results

### Classification Metrics (Validation Set, N = 600)

| Metric | Value |
|---|---|
| **Accuracy** | 96.67% |
| **Precision (Weighted)** | 0.967 |
| **Recall (Weighted)** | 0.967 |
| **F1-Score (Weighted)** | 0.967 |
| **Macro F1-Score** | 0.966 |
| **False Positive Rate** | 1.11% |

### Confusion Matrix

| | Pred. Critical | Pred. High | Pred. Low | Pred. Medium |
|---|---|---|---|---|
| **Act. Critical** (n=42) | **42** (100%) | 0 | 0 | 0 |
| **Act. High** (n=108) | 0 | **104** (96.3%) | 0 | 4 |
| **Act. Low** (n=270) | 0 | 0 | **267** (98.9%) | 3 |
| **Act. Medium** (n=180) | 3 | 1 | 9 | **167** (92.8%) |

### Operational Metrics (7-day Automated Phase, 493 IOCs)

| Metric | Value |
|---|---|
| **MTTR** | 10.93 seconds |
| **Autonomous Triage Rate** | 93.7% (462 / 493 IOCs) |
| **IDS Rules Synthesized** | 122 |
| **Rules Accepted w/o Modification** | 92.6% (113 / 122) |
| **Page-Hinkley Max Stat** | 12.7 (threshold: 50 — no drift detected) |

---

## 🚀 How to Run

1. **Install dependencies:**
   ```bash
   pip install pandas numpy scikit-learn matplotlib seaborn ipykernel
   ```

2. **Run the notebook:**
   Open [`RandomForest.ipynb`](RandomForest.ipynb) in VS Code or Jupyter and run all cells.
   The notebook will:
   - Load and preprocess `Data/IOC.json`
   - Sample and split the dataset (N=3,000 → train/val 80/20)
   - Train the Random Forest classifier
   - Print the classification report and accuracy metrics
   - Save `Data/ioc_rf_model.pkl`, `Data/label_encoder.pkl`
   - Save `Data/confusion_matrix.png` and `Data/feature_importance.png`

3. **Expected output:**
   ```
   Validation Accuracy: 96.67%
   ```

---

## 📜 Citation

```text
Kenneth Van Dyon, Joshua (2026). Adaptive Feedback Loop Based Multi-Agent
Automated Network Threat Intelligence Pipeline. Bina Nusantara University.
```
