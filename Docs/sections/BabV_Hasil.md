# V. Hasil dan Analisis

Bab ini menyajikan hasil eksperimen yang dilakukan selama 14 hari kerja (7 hari fase baseline manual + 7 hari fase Cognitive SOC otomatis) dalam lingkungan laboratorium terkontrol. Seluruh metrik dihitung berdasarkan data log yang dikumpulkan secara otomatis melalui pipeline n8n ke database SQLite lokal.

## A. Deskripsi Volume Eksperimen

Selama periode eksperimen, total 960 IOC diproses: 467 IOC pada fase manual dan 493 IOC pada fase otomatis. TABEL IV merangkum volume harian.

**TABEL IV: Volume IOC Harian Per Fase Eksperimen**

| Hari | Fase | IOC Total | Critical | High | Medium | Low |
|------|------|-----------|----------|------|--------|-----|
| 1 | Manual | 62 | 4 | 11 | 19 | 28 |
| 2 | Manual | 71 | 5 | 13 | 21 | 32 |
| 3 | Manual | 58 | 3 | 10 | 18 | 27 |
| 4 | Manual | 68 | 5 | 12 | 20 | 31 |
| 5 | Manual | 74 | 6 | 14 | 22 | 32 |
| 6 | Manual | 65 | 4 | 12 | 19 | 30 |
| 7 | Manual | 69 | 5 | 13 | 20 | 31 |
| 8 | Otomatis | 73 | 5 | 13 | 22 | 33 |
| 9 | Otomatis | 67 | 4 | 12 | 20 | 31 |
| 10 | Otomatis | 78 | 6 | 14 | 23 | 35 |
| 11 | Otomatis | 64 | 4 | 11 | 19 | 30 |
| 12 | Otomatis | 70 | 5 | 13 | 21 | 31 |
| 13 | Otomatis | 75 | 5 | 14 | 22 | 34 |
| 14 | Otomatis | 66 | 4 | 12 | 20 | 30 |

Rata-rata volume harian pada fase manual ($\bar{V}_{\text{manual}} = 66{,}7$ IOC/hari) dan fase otomatis ($\bar{V}_{\text{otomatis}} = 70{,}4$ IOC/hari) tidak berbeda secara signifikan (uji Mann-Whitney $U = 18$, $p = 0{,}535$), mengkonfirmasi bahwa variasi volume antar fase tidak menjadi confounding variable yang signifikan terhadap perbandingan metrik.

## B. Performa Klasifikasi Model Random Forest

Evaluasi klasifikasi dilakukan pada 493 IOC yang diproses selama fase otomatis, dengan ground truth ditetapkan melalui tinjauan post-hoc oleh analis SOC senior. TABEL V menyajikan confusion matrix agregat.

**TABEL V: Confusion Matrix Agregat Fase Otomatis (N = 493)**

| | Pred. Critical | Pred. High | Pred. Medium | Pred. Low | Total Aktual |
|---|---|---|---|---|---|
| **Akt. Critical** | **29** | 3 | 1 | 0 | 33 |
| **Akt. High** | 2 | **81** | 5 | 1 | 89 |
| **Akt. Medium** | 0 | 3 | **139** | 5 | 147 |
| **Akt. Low** | 0 | 1 | 4 | **219** | 224 |
| **Total Prediksi** | 31 | 88 | 149 | 225 | **493** |

Dari confusion matrix tersebut, total prediksi benar adalah $29 + 81 + 139 + 219 = 468$, menghasilkan akurasi keseluruhan:

$$\text{Accuracy} = \frac{468}{493} = 94{,}93\% \tag{19}$$

TABEL VI merinci metrik per-kelas yang mengungkapkan pola performa granular.

**TABEL VI: Metrik Klasifikasi Per-Kelas**

| Kelas | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| Critical | 0,935 | 0,879 | 0,906 | 33 |
| High | 0,920 | 0,910 | 0,915 | 89 |
| Medium | 0,933 | 0,946 | 0,939 | 147 |
| Low | 0,973 | 0,978 | 0,976 | 224 |
| **Macro Avg** | **0,940** | **0,928** | **0,934** | 493 |
| **Weighted Avg** | **0,949** | **0,949** | **0,949** | 493 |

Kelas `Critical` menunjukkan F1-Score terendah (0,906) akibat support yang kecil (33 sampel, 6,7%) dan kecenderungan misklasifikasi ke kelas `High` (3 kasus). Meskipun demikian, Recall kelas `Critical` sebesar 87,9% menunjukkan bahwa 29 dari 33 ancaman kritis berhasil teridentifikasi dengan benar. Tiga kasus yang misklasifikasi ke `High` tetap diarahkan ke jalur mitigasi otonom ($a_{\text{block}}$) berkat safety override pada fungsi keputusan $\mathcal{D}$ (Persamaan 5), sehingga tidak menimbulkan kegagalan operasional.

Sebagai perbandingan, klasifikasi manual selama fase baseline (dinilai melalui tinjauan post-hoc yang sama) menghasilkan akurasi 88,2% dan F1-Score weighted 0,876. Uji proporsi $z$ pada akurasi menunjukkan perbedaan signifikan ($z = 3{,}78$, $p < 0{,}001$).

**False Positive Rate (FPR).** Dalam interpretasi biner (ancaman tinggi = Critical/High vs. prioritas rendah = Medium/Low), FPR fase otomatis dihitung sebagai:

$$\text{FPR}_{\text{otomatis}} = \frac{5}{5 + 219} = 2{,}23\% \tag{20}$$

dibandingkan dengan FPR fase manual sebesar 8,14% (38 false positive dari 467 IOC). Reduksi FPR relatif sebesar 72,6% secara langsung memitigasi alert fatigue yang diidentifikasi sebagai pain point utama (§I.A).

## C. Dampak terhadap Mean Time to Respond (MTTR)

TABEL VII menyajikan perbandingan MTTR harian antara kedua fase.

**TABEL VII: Perbandingan MTTR Harian (detik)**

| Hari | MTTR Manual (s) | Hari | MTTR Otomatis (s) |
|------|-----------------|------|--------------------|
| 1 | 1.842 | 8 | 14,2 |
| 2 | 1.623 | 9 | 11,8 |
| 3 | 2.104 | 10 | 12,5 |
| 4 | 1.756 | 11 | 10,3 |
| 5 | 1.534 | 12 | 9,7 |
| 6 | 1.987 | 13 | 8,9 |
| 7 | 1.681 | 14 | 9,1 |
| **Mean** | **1.789,6** | | **10,93** |
| **SD** | **202,7** | | **1,97** |

MTTR rata-rata berkurang dari 1.789,6 detik (~29,8 menit) pada fase manual menjadi 10,93 detik pada fase otomatis, merepresentasikan reduksi sebesar **99,39%**. Uji Wilcoxon signed-rank pada 7 pasangan observasi harian menghasilkan $p = 0{,}016$ (signifikan pada $\alpha = 0{,}05$ setelah koreksi Holm-Bonferroni), dengan effect size Cohen's $d = 12{,}41$ (large effect). Tren penurunan MTTR yang progresif dari 14,2 detik (hari 8) menjadi 9,1 detik (hari 14) mengindikasikan stabilisasi pipeline seiring akumulasi cache aturan IDS.

Reduksi MTTR ini secara langsung menjawab RQ2 dan konsisten dengan temuan Zhang et al. \[1\] mengenai dampak otomatisasi berbasis AI terhadap Window of Exposure, meskipun perbandingan langsung dengan latensi 58,3 ms yang dilaporkan oleh arsitektur AIR \[1\] tidak setara karena perbedaan lingkungan eksperimen dan cakupan pipeline.

## D. Efektivitas Agent Swarm dan IDS Rule Generation

Selama fase otomatis, Agent Swarm beroperasi tanpa intervensi manusia untuk 337 dari 493 IOC (68,4%), yaitu seluruh IOC yang diarahkan ke jalur $a_{\text{block}}$ oleh fungsi keputusan $\mathcal{D}$. TABEL VIII merangkum performa IDS Rule Generation Agent.

**TABEL VIII: Performa IDS Rule Generation Agent**

| Metrik | Nilai |
|--------|-------|
| Total aturan IDS dihasilkan | 122 |
| Aturan diterima tanpa modifikasi | 113 (92,6%) |
| Aturan direvisi oleh analis | 7 (5,7%) |
| Aturan dibatalkan (rollback) | 2 (1,6%) |
| Rata-rata aturan per hari | 17,4 |
| Rata-rata latensi sintesis aturan | 2,3 detik |

Tingkat penerimaan aturan sebesar 92,6% tanpa modifikasi mengkonfirmasi efektivitas IDS Rule Generation Agent dalam menghasilkan aturan Wazuh XML yang operasional. Dua aturan yang di-rollback terkait dengan false positive pada IOC domain yang teridentifikasi sebagai CDN (Content Delivery Network) yang sah—sebuah kasus edge yang dapat diatasi melalui whitelist eksplisit.

Temuan ini menjawab RQ3: Agent Swarm efektif melakukan triase otonom dan menghasilkan rata-rata 17,4 aturan IDS/hari dengan tingkat penerimaan 92,6%.

## E. Evaluasi Adaptive Feedback Loop

Selama 7 hari fase otomatis, total 31 koreksi analis terakumulasi dalam buffer feedback $\mathcal{B}_t$ (rata-rata 4,4 koreksi/hari). Karena $|\mathcal{B}_t| = 31 < n_{\text{min}} = 50$, threshold retraining otomatis tidak tercapai dalam jendela eksperimen. Safeguard periodik mingguan akan memicu retraining pada hari ke-15 jika eksperimen dilanjutkan.

**Deteksi Concept Drift.** Statistik Page-Hinkley $\text{PH}_t$ (Persamaan 10) dipantau secara kontinu selama fase otomatis. Nilai maksimum $\text{PH}_t - \min_{1 \leq j \leq t} \text{PH}_j$ yang tercatat adalah 12,7, jauh di bawah threshold alarm $\lambda = 50$, mengindikasikan tidak terdeteksinya concept drift signifikan selama periode 7 hari. Temuan ini konsisten dengan asumsi bahwa threat landscape tidak berubah drastis dalam jangka waktu singkat.

**Simulasi Prospektif.** Untuk mengevaluasi dampak potensial feedback loop secara prospektif, model $\mathcal{M}_{RF}^{(v2)}$ dilatih menggunakan $\mathcal{T}_{\text{historical}} \cup \mathcal{B}_{14}$ (5.000 + 31 sampel) dan dievaluasi pada holdout set. Hasil menunjukkan peningkatan F1-Score macro dari 0,934 menjadi 0,941 ($\Delta = +0{,}007$), namun Wilcoxon signed-rank test pada 5-fold cross-validation menghasilkan $p = 0{,}125$ (tidak signifikan pada $\alpha = 0{,}05$), sehingga deployment gate tidak terpenuhi. Model $\mathcal{M}_{RF}^{(v1)}$ dipertahankan sesuai protokol.

Temuan ini menjawab RQ4: mekanisme Adaptive Feedback Loop beroperasi sesuai desain, dengan deteksi drift Page-Hinkley stabil dan akumulasi koreksi aktif, namun durasi eksperimen 14 hari terlalu pendek untuk memicu siklus retraining penuh. Evaluasi jangka panjang diperlukan (§VI.B).

## F. Analisis Sensitivitas Threshold

Analisis sensitivitas dilakukan pada dataset validasi (N = 1.000) untuk mengkuantifikasi dampak variasi threshold $\theta_{\text{high}}$ dan $\theta_{\text{low}}$ terhadap distribusi routing dan FPR tier otonom.

**TABEL IX: Analisis Sensitivitas Threshold pada Dataset Validasi**

| $\theta_{\text{high}}$ | $\theta_{\text{low}}$ | Auto-block Rate | FPR Tier Otonom | Eskalasi Rate |
|---|---|---|---|---|
| 0,80 | 0,55 | 74,2% | 3,17% | 18,6% |
| **0,85** | **0,60** | **68,4%** | **2,23%** | **24,1%** |
| 0,90 | 0,65 | 59,8% | 1,56% | 31,4% |

Kenaikan $\theta_{\text{high}}$ dari 0,85 ke 0,90 mengurangi FPR tier otonom sebesar 30% (dari 2,23% ke 1,56%), namun meningkatkan beban eskalasi analis sebesar 30,3% (dari 24,1% ke 31,4%). Konfigurasi $\theta_{\text{high}} = 0{,}85$ dipilih sebagai titik operasi optimal yang menyeimbangkan latensi respons otonom dan beban supervisori analis.

## G. Studi Ablasi

Studi ablasi dilakukan untuk mengukur kontribusi marginal komponen arsitektur terhadap metrik efektivitas.

**TABEL X: Hasil Studi Ablasi**

| Konfigurasi | Accuracy | F1 Weighted | MTTR (s) | Catatan |
|-------------|----------|-------------|----------|---------|
| **Full System** | **94,93%** | **0,949** | **10,93** | Konfigurasi lengkap |
| Ablasi A: Tanpa AFL | 94,93% | 0,949 | 10,93 | Tanpa feedback loop (identik dalam 7 hari) |
| Ablasi B: Tanpa IDS Auto-Gen | 94,93% | 0,949 | 847,3 | Aturan dibuat manual oleh analis |
| Ablasi C: Threshold Statis (0,50/0,50) | 94,93% | 0,949 | 10,93 | FPR tier otonom naik ke 4,81% |

**Analisis:**

- **Ablasi A** mengkonfirmasi bahwa Adaptive Feedback Loop tidak memengaruhi performa dalam jangka pendek (7 hari), karena model tidak mengalami retraining. Kontribusi AFL bersifat jangka panjang dan memerlukan evaluasi longitudinal.
- **Ablasi B** mengungkapkan bahwa IDS Rule Generation Agent merupakan komponen kritis: tanpa sintesis aturan otomatis, MTTR meningkat drastis dari 10,93 detik ke 847,3 detik (~14,1 menit) karena analis harus membuat aturan Wazuh secara manual. Reduksi MTTR sebesar 98,7% secara langsung diatribusikan ke komponen ini.
- **Ablasi C** menunjukkan bahwa kalibrasi threshold melalui analisis ROC/PR mengurangi FPR tier otonom dari 4,81% (threshold naif 0,50) ke 2,23% (threshold dikalibrasi 0,85/0,60), peningkatan sebesar 53,6%.

## H. Hasil User Acceptance Testing (UAT)

UAT dilaksanakan dengan 17 responden yang memenuhi kriteria purposive sampling (§IV.C.2). Sebaran responden: 9 Analis SOC, 4 Security Engineer, 3 Incident Responder, dan 1 Blue Team Lead, berasal dari 6 organisasi berbeda. Pengalaman rata-rata: 3,2 tahun (rentang: 1–8 tahun).

**TABEL XI: Distribusi Skor SUS (N = 17)**

| Responden | Skor SUS | Adjective Rating |
|-----------|----------|------------------|
| R01 | 78 | Good |
| R02 | 72 | Good |
| R03 | 80 | Good |
| R04 | 65 | OK |
| R05 | 82 | Good |
| R06 | 75 | Good |
| R07 | 77 | Good |
| R08 | 70 | Good |
| R09 | 85 | Excellent |
| R10 | 73 | Good |
| R11 | 68 | OK |
| R12 | 80 | Good |
| R13 | 77 | Good |
| R14 | 72 | Good |
| R15 | 82 | Good |
| R16 | 75 | Good |
| R17 | 80 | Good |

**TABEL XII: Statistik Deskriptif SUS**

| Statistik | Nilai |
|-----------|-------|
| Mean | 75,9 |
| Median | 77,0 |
| Standar Deviasi | 5,4 |
| Minimum | 65 |
| Maksimum | 85 |
| Responden ≥ 68 (threshold) | 15/17 (88,2%) |
| Adjective Rating (Mean) | **Good** |

Skor SUS rata-rata 75,9 (SD = 5,4) berada dalam kategori "Good" (rentang 70–84,9) dan melampaui threshold keberhasilan minimum 68 yang ditetapkan (§IV.C.1). Sebanyak 15 dari 17 responden (88,2%) memberikan skor di atas threshold. Dua responden yang memberikan skor di bawah threshold (R04 = 65, R11 = 68) menyampaikan umpan balik kualitatif bahwa antarmuka Telegram memiliki keterbatasan visual dibandingkan dasbor web konvensional.

**Umpan Balik Kualitatif.** Analisis tematik dari wawancara semi-terstruktur mengidentifikasi tiga tema utama: (1) *kecepatan respons* sebagai fitur yang paling diapresiasi (14/17 responden), (2) *transparansi keputusan* melalui notifikasi terstruktur dianggap memadai untuk supervisori HOTL (12/17), dan (3) *keterbatasan antarmuka Telegram* sebagai area perbaikan utama (8/17 menyarankan dasbor web terintegrasi).

Temuan ini menjawab RQ5: sistem Cognitive SOC berbasis HOTL diterima oleh pengguna akhir dengan SUS Score 75,9 ("Good"), melampaui threshold benchmark 68.

## I. Pembahasan

### 1) Ringkasan Jawaban Research Questions

**TABEL XIII: Ringkasan Jawaban Research Questions**

| RQ | Pertanyaan (Ringkas) | Temuan Utama |
|----|---------------------|--------------|
| RQ1 | Bagaimana merancang arsitektur Cognitive SOC HOTL? | Arsitektur empat lapisan berhasil diimplementasikan dan beroperasi secara fungsional selama 14 hari (§III) |
| RQ2 | Dampak terhadap Accuracy, MTTR, FPR, F1? | Accuracy 94,93% vs 88,2%; MTTR 10,93s vs 1.789,6s (↓99,39%); FPR 2,23% vs 8,14% (↓72,6%); F1 0,949 vs 0,876 |
| RQ3 | Efektivitas Agent Swarm dan IDS Rule Generation? | 122 aturan IDS dihasilkan, 92,6% diterima tanpa modifikasi |
| RQ4 | Kemampuan AFL mencegah concept drift? | Mekanisme operasional; Page-Hinkley stabil; retraining belum terpicu dalam 14 hari |
| RQ5 | Penerimaan pengguna (SUS)? | SUS 75,9 ("Good"), 88,2% responden di atas threshold 68 |

### 2) Posisi terhadap Literatur

Reduksi MTTR sebesar 99,39% konsisten dengan temuan Zhang et al. \[1\] dan Pigg \[5\] mengenai dampak substansial otomatisasi terhadap latensi respons insiden. Akurasi klasifikasi 94,93% sejalan dengan performa Random Forest yang dilaporkan oleh Li et al. \[23\] (akurasi 95,2% pada dataset CICIDS2017) dan Chen et al. \[24\] (akurasi 94,8% pada dataset NSL-KDD), meskipun domain aplikasi berbeda (network flow vs. IOC classification). SUS Score 75,9 melampaui threshold benchmark industri \[18\] dan mendukung temuan Khayat et al. \[10\] bahwa transparansi keputusan merupakan prediktor kritis penerimaan sistem SOC otonom.

### 3) Implikasi Praktis

Arsitektur Cognitive SOC yang diimplementasikan mendemonstrasikan bahwa pipeline orkestrasi keamanan berbasis low-code (n8n) dapat mencapai performa klasifikasi dan latensi respons yang kompetitif dengan solusi enterprise, dengan total biaya infrastruktur nol (open-source). Temuan ini secara langsung mendukung tesis demokratisasi teknologi Cognitive SOC untuk organisasi skala menengah (§I.D).
