# Cognitive SOC: Human-On-The-Loop (HOTL) Threat Intelligence Pipeline

An automated Cognitive Security Operations Center (SOC) architecture designed to implement the Human-On-The-Loop (HOTL) paradigm for threat triage and IDS rule deployment.

The machine learning classifier is a **Random Forest** model trained using contextual threat intelligence features from real-world indicators (Cyfirma). It classifies Indicators of Compromise (IOC) into a four-class threat taxonomy (Low, Medium, High, Critical) and performs confidence-based routing to escalate or autonomously block threats.

This repository contains the complete dataset, configurations, and Jupyter Notebook to train and evaluate the model.

---

## 📁 Repository Structure
* `Data/`
  * `IOC.json` - 4,200 real Cyfirma IOCs (STIX format).
  * `hasil_kuantitatif_harian.csv` - Daily quantitative metrics from the 14-day experiment.
  * `research_filtered_iocs.json` - Complete dataset of 960 indicators processed.
  * `wazuh_rules_generated.xml` - 122 autonomously synthesized Wazuh rules.
* `Docs/` - Academic proposal documents, peer review reports, and results.
* `src/` - Orchestration source code, local agents, and figure plot generators.
* `RandomForest.ipynb` - Entire machine learning pipeline (preprocessing, training, evaluation, plotting).
* `README.md` - Project documentation.

---

## 🛠️ Technologies
- **Python 3.8+**
- **scikit-learn** for machine learning and evaluation metrics
- **pandas** and **NumPy** for data processing
- **matplotlib** and **seaborn** for visualization and plotting
- **sqlite3** for log management
- **n8n** for low-code security orchestration automation and response (SOAR)
- **Wazuh Manager** for threat logging and XML rule execution

---

## 🧠 Model Architecture
- **Model Type:** Random Forest Classifier (100 estimators, `class_weight='balanced'`)
- **Inputs:** 15-dimensional encoded feature vector (3 one-hot indicator type columns, 5 one-hot threat category columns, and 7 scalar features).
- **Outputs:** Softmax probability outputs corresponding to the 4 threat classes: `Low`, `Medium`, `High`, `Critical`.

---

## 📊 Results
The classifier and architecture achieved the following results during validation and the 14-day experiment:
- **Accuracy:** 100.00% (Cyfirma-only validation set)
- **Weighted F1-Score:** 1.000
- **Macro F1-Score:** 1.000
- **MTTR Reduction:** 99.39% reduction (from 1,789.6s manual response to 10.93s automated response)
- **IDS Rule Acceptance Rate:** 92.62% accepted without modification (113/122 rules)

---

## 🚀 How to Run
1. Install dependencies:
   ```bash
   pip install pandas numpy scikit-learn matplotlib seaborn jinja2 ipykernel
   ```
2. Open the notebook:
   Run the [RandomForest.ipynb](RandomForest.ipynb) notebook in VS Code or Jupyter Notebook to run the pipeline, train the model, save the outputs, and plot the inline metrics.
3. (Optional) Deployed n8n workflows and Wazuh scripts are located under the `src/` directory.

---

## 📜 Citation
If you use this work or codebase in your academic research, please cite:
```text
Kenneth Van Dyon, Joshua (2026). Adaptive Feedback Loop Based Cognitive SOC: Automated Network Threat Intelligence Pipeline. Bina Nusantara University.
```
