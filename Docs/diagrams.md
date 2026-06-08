# Diagram Source Files for Cognitive SOC Manuscript

## Gambar 1: Arsitektur Pipeline Cognitive SOC (4-Layer)

Render this using Mermaid Live Editor (https://mermaid.live) or any Mermaid-compatible tool. Export as SVG or high-resolution PNG for the final manuscript.

```mermaid
flowchart TB
    subgraph L1["<b>LAYER 1: Data Acquisition & Fusion Space</b>"]
        direction LR
        TIP["🔒 TIP TIP API<br/><i>REST Polling</i>"]
        ETL["⚙️ ETL & Normalisasi<br/><i>T_norm (Pers. 1)</i>"]
        DEDUP["🔄 Fusi Temporal &<br/>Deduplikasi<br/><i>F_fuse (Pers. 2)</i>"]
        TIP --> ETL --> DEDUP
    end

    subgraph L2["<b>LAYER 2: Threat Analysis & Correlation Space</b>"]
        direction LR
        FE["📊 Feature Engineering<br/><i>9 atribut → 15 dimensi</i><br/>(TABEL II)"]
        RF["🌲 Random Forest<br/>Classifier<br/><i>M_RF (Pers. 3)</i>"]
        CONF["📈 Estimasi Confidence<br/><i>conf(f_i) (Pers. 4)</i>"]
        FE --> RF --> CONF
    end

    subgraph L3["<b>LAYER 3: Orchestration & Decision Logic Space</b>"]
        direction TB
        DEC["⚡ Fungsi Keputusan D<br/><i>(Pers. 5)</i>"]
        
        subgraph ROUTES["Routing Otomatis"]
            direction LR
            AUTO["✅ autonomous_block<br/><i>conf > θ_high (0.85)</i>"]
            HOTL_ESC["⚠️ escalate_HOTL<br/><i>θ_low ≤ conf ≤ θ_high</i>"]
            LOG["📋 log_review<br/><i>conf < θ_low (0.60)</i>"]
        end
        
        subgraph FORK["Fork Eksekusi Paralel"]
            direction LR
            TRIAGE["🔍 Autonomous<br/>Triage Agent"]
            IDS_GEN["🛡️ IDS Rule<br/>Generation Agent"]
        end
        
        DEC --> ROUTES
        AUTO --> FORK
    end

    subgraph L4["<b>LAYER 4: Execution & Adaptive Feedback Space</b>"]
        direction LR
        WAZUH["🖥️ Wazuh Manager<br/><i>Rule Deployment API</i>"]
        TELE["📱 Telegram HOTL<br/><i>Notifikasi & Validasi</i>"]
        
        subgraph AFL["Adaptive Feedback Loop"]
            direction TB
            BUF["📦 Buffer Feedback B_t<br/><i>(Pers. 9)</i>"]
            RETRAIN["🔄 Augmented Retraining<br/><i>T_retrain (Pers. 11)</i>"]
            GATE["🚪 Deployment Gate<br/><i>Wilcoxon (Pers. 12)</i>"]
            PH["📉 Page-Hinkley<br/>Drift Detection<br/><i>PH_t (Pers. 13)</i>"]
            BUF -->|"|B_t| ≥ 50"| RETRAIN
            RETRAIN --> GATE
            PH -->|"Alarm"| RETRAIN
        end
    end

    ANALYST["👤 SOC Analyst<br/><i>Human-On-The-Loop</i>"]

    DEDUP -->|"Bundle IOC {B_1...B_m}"| FE
    CONF -->|"Tuple (f_i, ŷ_i, conf_i)"| DEC
    FORK --> WAZUH
    HOTL_ESC --> TELE
    TELE <-->|"Validasi / Koreksi"| ANALYST
    ANALYST -->|"Koreksi Label"| BUF
    GATE -->|"M_RF^(v+1)"| RF
    PH -.->|"Monitor conf stream"| CONF

    style L1 fill:#E3F2FD,stroke:#1565C0,stroke-width:2px
    style L2 fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px
    style L3 fill:#FFF3E0,stroke:#E65100,stroke-width:2px
    style L4 fill:#F3E5F5,stroke:#6A1B9A,stroke-width:2px
    style ANALYST fill:#FFEBEE,stroke:#C62828,stroke-width:2px
    style AFL fill:#FCE4EC,stroke:#AD1457,stroke-width:1px
```

---

## Gambar 2: Diagram Transisi State — Adaptive Feedback Loop

```mermaid
stateDiagram-v2
    [*] --> MONITORING

    MONITORING: 🟢 MONITORING
    MONITORING: Model M_RF^(v) aktif
    MONITORING: Memantau aliran conf_i

    ACCUMULATING: 🟡 ACCUMULATING
    ACCUMULATING: Buffer B_t mengumpulkan
    ACCUMULATING: koreksi analis (Pers. 9)

    DRIFT_DETECTED: 🟠 DRIFT DETECTED
    DRIFT_DETECTED: PH_t - min > λ (Pers. 13)
    DRIFT_DETECTED: δ = 0.005, λ = 50

    RETRAINING: 🔵 RETRAINING
    RETRAINING: T_retrain = T_hist ∪ B_t (Pers. 11)
    RETRAINING: warm_start=False

    VALIDATION: 🟣 VALIDATION
    VALIDATION: K-fold CV + Wilcoxon
    VALIDATION: signed-rank test (Pers. 12)

    DEPLOYED: 🟢 DEPLOYED
    DEPLOYED: Model M_RF^(v+1) aktif
    DEPLOYED: Versi dicatat

    MONITORING --> ACCUMULATING: Koreksi analis diterima
    MONITORING --> DRIFT_DETECTED: PH alarm trigger
    ACCUMULATING --> RETRAINING: |B_t| ≥ n_min = 50 (Pers. 10)
    ACCUMULATING --> MONITORING: Safeguard mingguan\n(jika |B_t| < n_min)
    DRIFT_DETECTED --> RETRAINING: Retraining dipercepat
    RETRAINING --> VALIDATION: K-fold CV selesai
    VALIDATION --> DEPLOYED: H₀ ditolak (α=0.05)
    VALIDATION --> MONITORING: H₀ tidak ditolak\n(rollback ke M_RF^(v))
    DEPLOYED --> MONITORING: Versi di-log,\nresume monitoring
```

---

## Rendering Instructions

### Option A: Mermaid Live Editor (Recommended)
1. Go to [https://mermaid.live](https://mermaid.live)
2. Paste the Mermaid code block content
3. Export as **SVG** (vector, best for IEEE papers) or **PNG** (high-DPI)

### Option B: VS Code Extension
1. Install "Markdown Preview Mermaid Support" extension
2. Open this file in VS Code
3. Preview renders diagrams inline

### Option C: Command Line
```bash
npm install -g @mermaid-js/mermaid-cli
mmdc -i diagrams.md -o gambar1.svg -t neutral
```

### IEEE Formatting Notes
- Export at **minimum 300 DPI** for PNG
- SVG is preferred for vector quality in LaTeX/Word
- Use single-column width (~3.5 inches) or double-column width (~7 inches) depending on layout
- Caption format: "Gbr. 1. Arsitektur pipeline Cognitive SOC empat-lapisan."
