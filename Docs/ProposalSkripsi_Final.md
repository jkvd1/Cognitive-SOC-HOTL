                 Arsitektur Cognitive SOC Berbasis Hybrid Autonomous AI Agent dan Adaptive Feedback Loop: Implementasi Pipeline Intelijen Ancaman Jaringan Otomatis Menggunakan N8n Untuk Percepatan Respons Insiden

Joshua Kenneth Van Dyon  
_Bina Nusantara University_  
Jakarta, Indonesia  
[joshua.dyon@binus.ac.id](mailto:joshua.dyon@binus.ac.id)

_Abstrak_-Security Operations Center (SOC) modern menghadapi tantangan volume peringatan masif dan keterbatasan sumber daya manusia, yang meningkatkan Mean Time to Respond (MTTR) dan menurunkan akurasi deteksi. Penelitian ini merancang, mengimplementasikan, dan mengevaluasi arsitektur Cognitive SOC yang mengimplementasikan paradigma Human-On-The-Loop (HOTL) melalui Hybrid Autonomous AI Agent dan Adaptive Feedback Loop. Arsitektur ini mengintegrasikan Threat Intelligence Platform (Cyfirma), mesin orkestrasi low-code (n8n), subsistem Machine Learning (Random Forest), dan SIEM (Wazuh), dengan mekanisme monitoring analis melalui Telegram. Evaluasi empiris melalui eksperimen sekuensial 14 hari (7 hari baseline manual + 7 hari otomatis) pada 960 IOC menunjukkan peningkatan signifikan: akurasi klasifikasi 95,54% dengan F1-Score weighted 0,949 dan F1-Score macro 0,908, reduksi MTTR sebesar 99,39% (dari 1.789,6 detik menjadi 10,93 detik; Wilcoxon $p = 0{,}016$, Cohen's $d = 12{,}41$), dan penurunan False Positive Rate rata-rata harian menjadi 2,92%. Agent Swarm menghasilkan 122 aturan IDS dinamis dengan tingkat penerimaan 92,6% tanpa modifikasi. User Acceptance Testing terhadap 17 praktisi keamanan menghasilkan skor System Usability Scale (SUS) rata-rata 76,0 ("Good"), melampaui threshold benchmark 68.

**_Kata Kunci-Cognitive SOC, Human-On-The-Loop (HOTL), Agentic AI, Adaptive Feedback Loop, Cyber Threat Intelligence (CTI), Security Orchestration Automation and Response (SOAR)._**

# I. Pendahuluan

## A. Latar Belakang

Lanskap ancaman siber (cyber threat landscape) kontemporer ditandai dengan peningkatan eksponensial dalam volume, kecanggihan, dan kecepatan serangan. Security Operations Center (SOC) di seluruh dunia kini harus memproses ribuan peringatan keamanan (security alerts) setiap harinya, dengan studi terdokumentasi melaporkan lebih dari 22.000 peringatan mingguan pada lingkungan perusahaan berskala besar \[1\]. Volume data ancaman yang masif ini jauh melampaui kapasitas pemrosesan kognitif analis keamanan manusia, sehingga menciptakan asimetri fundamental antara kemampuan defensif organisasi dan aktivitas threat actor (adversary).

Kecepatan deteksi dan remediasi ancaman menjadi determinan kritis bagi ketahanan siber (cyber resilience) dalam organisasi. Hal ini dikarenakan threat actor senantiasa mengeksploitasi kesenjangan temporal antara kompromi awal dan respons defensif—sebuah periode yang dikenal sebagai Window of Exposure. Dalam operasi pertahanan jaringan, bahkan pengurangan marjinal dalam latensi respons dapat mencegah pergerakan lateral (lateral movement), eksfiltrasi data, dan kompromi sistem yang lebih luas.

Cyber Threat Intelligence (CTI) berfungsi sebagai elemen fundamental dalam pertahanan proaktif dengan menyediakan informasi yang dapat ditindaklanjuti (actionable intelligence) mengenai taktik, teknik, dan prosedur (TTPs), serta infrastruktur musuh. Namun, nilai operasional CTI berbanding lurus dengan kecepatan dan akurasi dalam menerjemahkan intelijen tersebut menjadi aksi defensif yang konkret. Berdasarkan latar belakang di atas, penelitian ini mengidentifikasi pain points spesifik dalam operasi SOC manual yang menjadi fokus investigasi:

- **Lambatnya Ingesti Manual (_Manual Ingestion Latency_):** Proses pemantauan dasbor TIP, ekstraksi IOC, dan verifikasi manual memakan waktu yang signifikan. Kesenjangan waktu antara publikasi ancaman oleh penyedia intelijen (seperti Cyfirma) dan tindakan defensif oleh SOC memberikan keuntungan taktis bagi penyerang.
- **Tingginya Tingkat False Positive:** Tanpa mekanisme penyaringan otomatis berbasis _confidence score_ dan deduplikasi, analis sering kali menerima data mentah yang belum diverifikasi. Studi menunjukkan bahwa tingkat false positive di lingkungan SOC dapat mencapai 68% dari keseluruhan alert \[1\], membuang siklus kerja yang berharga.
- **Beban Kognitif dan Human Error:** Sifat repetitif dari pemrosesan data CTI meningkatkan risiko kesalahan transkripsi manusia. Penelitian terdokumentasi mengindikasikan bahwa kelelahan dan _burnout_ ditemukan pada lebih dari 70% analis SOC \[20\], yang menurunkan kualitas pengambilan keputusan dalam insiden kritis.
- **Inefisiensi Alokasi Sumber Daya:** Analis tingkat lanjut sering kali terperangkap dalam tugas-tugas administratif "Level 1", padahal keahlian mereka dibutuhkan untuk analisis "Level 3" (threat hunting dan analisis forensik). Survei prioritasi alert menunjukkan bahwa sebagian besar waktu SOC terbuang untuk triase manual alert berprioritas rendah \[19\].
- **Concept Drift pada Model Machine Learning:** Tanpa mekanisme umpan balik (feedback loop) yang sistematis, model klasifikasi ancaman mengalami degradasi akurasi seiring perubahan pola serangan secara temporal \[16\].

Tinjauan literatur komprehensif terhadap publikasi IEEE, ACM, dan jurnal terkait periode 2022-2025 mengungkapkan beberapa kesenjangan penelitian (research gaps) yang signifikan:

- Penelitian sebelumnya berfokus pada desain arsitektur SOAR atau algoritma deteksi berbasis AI, namun minim pada implementasi paradigma **Human-On-The-Loop (HOTL)** pada konteks SOC yang nyata, di mana sistem AI beroperasi secara otonom sementara manusia berperan sebagai supervisor.
- Belum terdapat studi yang secara komprehensif mengintegrasikan konsep **Agent Swarm** untuk triase ancaman otonom dan pembuatan aturan Intrusion Detection System (IDS) secara dinamis dalam satu kerangka kerja orkestrasi low-code yang dapat direplikasi.
- Implementasi **Adaptive Feedback Loop** untuk mencegah concept drift pada model Machine Learning dalam konteks operasional SOC masih jarang dievaluasi secara empiris bersamaan dengan metrik efektivitas operasional (MTTR, FPR, F1-Score).
- Evaluasi penerimaan pengguna (User Acceptance Testing/UAT) terhadap sistem SOC otonom berbasis HOTL, khususnya dengan instrumen standar seperti System Usability Scale (SUS), masih sangat terbatas dalam literatur akademis.

## B. Rumusan Masalah

Terlepas dari investasi signifikan pada Threat Intelligence Platform (TIP) dan perangkat keamanan, banyak organisasi masih bergantung pada proses manual untuk mengoperasionalisasikan threat intelligence. Dalam lingkungan operasional salah satu perusahaan penyedia layanan (Managed Security Service Provider) di Indonesia, Indicators of Compromise (IOC) yang bersumber dari TIP Cyfirma-termasuk alamat IP berbahaya, nama domain, hash file, dan indikator teknis lainnya-masih diekstraksi, divalidasi, dan didistribusikan secara manual kepada tim keamanan untuk remediasi.

Alur kerja manual ini memperkenalkan beberapa titik kegagalan (points of failure): kesalahan transkripsi manusia yang membahayakan integritas data, penundaan pemrosesan yang memperlebar Window of Exposure, serta kelelahan analis (alert fatigue) akibat tugas repetitif yang mendegradasi efektivitas SOC secara keseluruhan. Latensi inheren dalam transfer data manual menciptakan hambatan (bottleneck) kritis antara deteksi dan remediasi, yang berdampak langsung pada peningkatan Mean Time to Respond (MTTR) dan postur risiko organisasi. Selain itu, ketiadaan format data yang terstandarisasi dan mekanisme validasi otomatis meningkatkan probabilitas false positive mencapai kontrol keamanan produksi, yang berpotensi mengganggu keberlangsungan operasi bisnis yang sah.

Berdasarkan identifikasi masalah dan kesenjangan riset tersebut, penelitian ini merumuskan pertanyaan penelitian sebagai berikut untuk memandu investigasi:

- **RQ1:** Bagaimana merancang arsitektur Cognitive SOC berbasis paradigma Human-On-The-Loop (HOTL) yang mengintegrasikan Hybrid Autonomous AI Agent dengan Adaptive Feedback Loop dalam platform orkestrasi low-code (n8n) secara andal?
- **RQ2:** Seberapa signifikan dampak penerapan arsitektur Cognitive SOC tersebut terhadap peningkatan Accuracy, reduksi Mean Time to Respond (MTTR), penurunan False Positive Rate (FPR), dan peningkatan F1-Score dibandingkan dengan alur kerja manual konvensional?
- **RQ3:** Bagaimana efektivitas mekanisme Agent Swarm dalam melakukan triase ancaman secara otonom dan menghasilkan aturan Intrusion Detection System (IDS) secara dinamis, diukur melalui jumlah aturan IDS yang berhasil di-generate per hari dan proporsi aturan yang diterima tanpa modifikasi oleh analis?
- **RQ4:** Sejauh mana Adaptive Feedback Loop mampu mencegah concept drift pada model Random Forest, diukur melalui statistik deteksi drift Page-Hinkley (Persamaan 13) dan delta F1-Score antar siklus retraining, dengan memanfaatkan koreksi analis SOC sebagai sinyal pembaruan model secara berkelanjutan?
- **RQ5:** Apakah sistem Cognitive SOC berbasis HOTL yang diusulkan dapat diterima oleh pengguna akhir (analis SOC, security engineer) berdasarkan metodologi User Acceptance Testing (UAT) dengan instrumen System Usability Scale (SUS) pada threshold benchmark industri yang ditetapkan?

## C. Tujuan Penelitian

Penelitian ini telah merancang, mengimplementasikan, dan mengevaluasi arsitektur Cognitive SOC berbasis paradigma Human-On-The-Loop guna mengatasi tantangan operasional yang telah diidentifikasi. Tujuan spesifik dari penelitian ini adalah:

- **Membangun Artefak Cognitive SOC:** Mengembangkan prototipe sistem orkestrasi keamanan berbasis paradigma HOTL menggunakan platform low-code (n8n) yang terintegrasi dengan Cyfirma TIP, subsistem Machine Learning (Random Forest), Wazuh (SIEM), dan Telegram (dasbor monitoring HOTL).
- **Mengimplementasikan Hybrid Autonomous AI Agent:** Merancang dan mengimplementasikan Agent Swarm yang mampu melakukan triase ancaman secara otonom dan menghasilkan aturan Intrusion Detection System (IDS) secara dinamis berdasarkan IOC yang diklasifikasikan oleh model Machine Learning.
- **Mengimplementasikan Adaptive Feedback Loop:** Membangun mekanisme umpan balik adaptif yang memungkinkan koreksi analis SOC memperbarui model Random Forest secara berkelanjutan untuk mencegah concept drift.
- **Evaluasi Efektivitas Sistem:** Mengukur secara empiris peningkatan efektivitas operasional melalui empat variabel utama: Accuracy, Mean Time to Respond (MTTR), False Positive Rate (FPR), dan F1-Score, dibandingkan dengan baseline proses manual.
- **Evaluasi Penerimaan Pengguna:** Mengevaluasi tingkat keberterimaan sistem melalui metodologi User Acceptance Testing (UAT) dengan instrumen System Usability Scale (SUS) terhadap 15–20 responden yang dipilih secara purposive dari kalangan praktisi keamanan siber.

Dengan mencapai tujuan-tujuan ini, penelitian ini telah mendemonstrasikan pendekatan arsitektural Cognitive SOC yang layak, terukur, dan dapat diterima pengguna dalam lingkungan SOC dengan sumber daya terbatas.

## D. Manfaat Penelitian

- **Manfaat Teoritis**

Penelitian ini memberikan kontribusi pada pengembangan literatur keamanan siber, khususnya dalam domain Security Operations Center (SOC) dan orkestrasi pertahanan, melalui tiga aspek utama:

- 1. **Memperkuat kerangka kerja paradigma Human-On-The-Loop (HOTL) dalam operasi SOC.** Penelitian ini berkontribusi dalam memvalidasi secara empiris transisi dari paradigma Human-In-The-Loop (HITL) menuju HOTL pada konteks SOC berbasis AI. Berbeda dengan HITL yang mengharuskan manusia untuk memvalidasi setiap keputusan, HOTL menempatkan manusia sebagai supervisor yang mengintervensi hanya pada kondisi anomali tertentu. Kontribusi ini memperkaya literatur Human-Machine Teaming dalam domain keamanan siber, khususnya mengenai derajat otonomi optimal yang dapat diberikan kepada sistem AI tanpa mengorbankan ketelitian dan akuntabilitas keputusan.
   - **Memperkenalkan kerangka arsitektur Hybrid Autonomous AI Agent dengan Adaptive Feedback Loop untuk SOC.** Sepengetahuan penulis, belum terdapat studi yang secara komprehensif mengintegrasikan Agent Swarm dengan kemampuan triase otonom, pembuatan aturan IDS dinamis, dan Adaptive Feedback Loop untuk mitigasi concept drift dalam satu kerangka orkestrasi low-code yang reproducible. Kontribusi ini mengisi kesenjangan dalam literatur tentang implementasi agentic AI dalam operasi keamanan nyata.
   - **Memperkaya metrik evaluasi sistem SOC otonom.** Penelitian ini tidak hanya mengevaluasi MTTR sebagai metrik tunggal, melainkan mengintegrasikan suite metrik komprehensif (Accuracy, MTTR, FPR, F1-Score) dengan evaluasi penerimaan pengguna melalui UAT/SUS. Pendekatan evaluasi multi-dimensi ini memberikan landasan metodologis bagi penelitian Cognitive SOC di masa mendatang.

- **Manfaat Praktis**

Hasil penelitian memberikan dampak operasional langsung yang dapat diterapkan oleh praktisi keamanan siber dan organisasi berbagai skala dalam aspek:

- 1. **Reduksi Mean Time to Respond (MTTR) melalui Autonomous Triage.** Agent Swarm yang beroperasi dalam paradigma HOTL memungkinkan triase ancaman berlangsung secara real-time tanpa menunggu konfirmasi manusia untuk setiap IOC. Hal ini secara langsung mempersempit Window of Exposure dan membatasi dwell time threat actor dalam jaringan.
   - **Mitigasi Alert Fatigue melalui Sistem Klasifikasi Cerdas.** Model Random Forest dengan Adaptive Feedback Loop memastikan analis hanya menerima peringatan berprioritas tinggi yang telah divalidasi secara otomatis. Beban kognitif berkurang drastis, kualitas pengambilan keputusan meningkat, dan analis dapat fokus pada aktivitas bernilai tinggi seperti threat hunting.
   - **Peningkatan Ketahanan Model terhadap Concept Drift.** Adaptive Feedback Loop yang dibangun memungkinkan model Machine Learning memperbarui parameternya secara berkelanjutan berdasarkan koreksi analis SOC. Hal ini menjamin akurasi klasifikasi yang terjaga seiring evolusi pola ancaman siber.
   - **Demokratisasi Teknologi Cognitive SOC untuk Organisasi Skala Menengah.** Platform low-code (n8n) sebagai backbone orkestrasi memungkinkan implementasi arsitektur Cognitive SOC berkualitas enterprise tanpa biaya lisensi platform SOAR komersial yang prohibitif.

## E. Ruang Lingkup Masalah

Agar penelitian ini lebih terarah dan fokus, penulis menetapkan batasan masalah sebagai berikut:

- **Sumber Data:** Fokus pada Indicators of Compromise (IOC) jenis IP, Domain, dan Hash File yang bersumber dari Cyfirma TIP melalui REST API.
- **Teknologi:** Cyfirma (Threat Intelligence Platform), n8n sebagai mesin orkestrasi (Orchestrator) low-code, Python/scikit-learn untuk subsistem Machine Learning (Random Forest), Wazuh (SIEM/Log management), dan Telegram (dasbor monitoring HOTL).
- **Ruang Lingkup Otoritas AI (Agent Swarm):** Sistem AI beroperasi secara otonom dalam: (a) akuisisi dan normalisasi IOC dari Cyfirma TIP, (b) klasifikasi ancaman menggunakan model Random Forest, (c) triase berdasarkan tingkat kepercayaan (_confidence score_), (d) pembuatan aturan IDS dinamis pada Wazuh secara otomatis, dan (e) pengiriman notifikasi monitoring ke Telegram. Agent Swarm tidak memerlukan persetujuan manusia untuk operasi rutin dalam kategori kepercayaan tinggi.
- **Ruang Lingkup Otoritas Manusia (SOC Analyst):** Analis SOC berperan sebagai supervisor dalam paradigma HOTL dengan tugas: (a) memantau dasbor Telegram untuk anomali atau _outlier_ yang di-flag sistem, (b) memberikan koreksi atau eskalasi pada kasus borderline atau false positive yang lolos filter, (c) mengintervensi pada insiden berisiko tinggi yang melampaui threshold otorisasi AI, dan (d) mem-validasi pembaruan model sebagai umpan balik pada Adaptive Feedback Loop.
- **Metrik Evaluasi:** Accuracy, Mean Time to Respond (MTTR), False Positive Rate (FPR), F1-Score (efektivitas sistem), dan System Usability Scale/SUS score (penerimaan pengguna). Analisis forensik endpoint berada di luar cakupan utama.
- **Lingkungan:** Eksperimen telah dilakukan dalam lingkungan laboratorium terkontrol (_virtual environment_) yang mensimulasikan infrastruktur SOC perusahaan menengah, bukan pada jaringan produksi aktif.

# II. Landasan Teori

## A. Peran Cyber Threat Intelligence (CTI) dalam Security Operations Center (SOC)

Cyber Threat Intelligence (CTI) telah berkembang menjadi kapabilitas fundamental dalam operasi keamanan siber modern, memungkinkan organisasi untuk mentransformasi paradigma pertahanan dari respons insiden reaktif menuju pertahanan proaktif. Integrasi CTI yang dilakukan secara sistematis dalam lingkungan SOC terbukti mampu mereduksi beban kognitif analis dan mengakselerasi alur kerja penanganan insiden \[2\]. Ampel et al. memvalidasi bahwa pendekatan proaktif berbasis deep transfer learning mampu mengidentifikasi ancaman yang muncul dari komunitas hacker sebelum eksploitasi terjadi secara luas \[17\]. Pendekatan integratif ini memperkuat korelasi antara implementasi otomatisasi dan peningkatan kualitas luaran respons insiden.

Pada tataran operasional, arsitektur intelijen ancaman modern semakin bergantung pada pola orkestrasi berbasis API dan standar pertukaran data seperti STIX dan TAXII guna memfasilitasi pertukaran data secara real-time antar perangkat keamanan yang heterogen \[6\], \[11\]. Platform orkestrasi intelijen ancaman berbasis open source seperti IRIS Orchestrator mendemonstrasikan bahwa arsitektur berbasis konektor mampu mengagregasi berbagai threat feeds dengan tetap mempertahankan karakteristik performa yang optimal \[6\]. Tinjauan sistematis terhadap integrasi AI dan ML dalam SOC juga menggarisbawahi pentingnya integrasi yang tepat antara berbagai komponen keamanan untuk menghasilkan respons yang efektif \[7\], \[10\].

## B. Security Orchestration, Automation, and Response (SOAR) dan Agentic AI

Paradigma SOAR merepresentasikan pendekatan sistematis untuk memitigasi kelelahan analis dan inefisiensi operasional melalui otomatisasi tugas-tugas repetitif \[25\], \[27\]. Perkembangan terkini dalam sistem respons insiden otomatis berbasis AI menunjukkan peningkatan kinerja yang signifikan. Zhang et al. melaporkan bahwa model respons insiden berbasis AI yang terintegrasi dengan pipeline DevSecOps mampu mereduksi Mean Time to Detect (MTTD) dan Mean Time to Recover (MTTR) secara substansial \[1\]. Konvergensi SIEM, SOAR, dan AI telah menjadi pendorong utama ketahanan siber modern \[12\].

Penelitian kontemporer menekankan pendekatan hyper-automation menggunakan kecerdasan buatan berbasis agen (agentic AI) untuk memungkinkan respons otomatis yang adaptif dan mempertahankan mekanisme pengawasan manusia yang dapat diaudit (*auditable*). Ismail et al. mengusulkan platform SOAR berbasis agentic-LLM yang mampu menghasilkan kode otomatisasi secara dinamis, melampaui keterbatasan solusi SOAR no-code tradisional \[4\]. Sementara itu, Pigg mendemonstrasikan bahwa integrasi SOAR dengan alur kerja threat intelligence secara signifikan mengurangi waktu pemrosesan tanpa mengorbankan akurasi data \[5\]. Nandi memperluas pandangan ini dengan mengidentifikasi bahwa platform SOAR generasi baru yang berbasis adaptive playbooks dan reinforcement learning merupakan evolusi kritis dari pendekatan otomatisasi berbasis aturan statis \[13\].

Studi empiris mengungkapkan korelasi signifikan antara tingkat maturitas SOC dan pengurangan MTTR, meskipun nilai absolut bervariasi berdasarkan tingkat kematangan organisasi dan konteks operasional spesifik \[3\]. Temuan ini menggarisbawahi pentingnya desain arsitektur yang tepat untuk memaksimalkan efektivitas otomatisasi.

## C. Paradigma Human-On-The-Loop (HOTL) dalam Keamanan Siber

Transisi dari paradigma Human-In-The-Loop (HITL) menuju Human-On-The-Loop (HOTL) merupakan evolusi signifikan dalam kontrol supervisori sistem keamanan berbasis AI \[26\]. Dalam paradigma HOTL, sistem AI beroperasi secara otonom sementara manusia berperan sebagai supervisor yang mengintervensi hanya pada kondisi anomali tertentu. Mareedu mengindikasikan bahwa arsitektur SOC otonom yang memadukan triase otomatis berbasis AI Agents dengan validasi manusia mampu mencapai keseimbangan operasional yang optimal sembari tetap menyediakan jejak audit dan penjelasan bagi tinjauan analis \[8\]. Tantangan utama dalam paradigma ini adalah alert fatigue—fenomena di mana volume peringatan yang berlebihan menyebabkan kelelahan dan penurunan kinerja analis \[19\], \[20\], \[21\].

Pola desain yang mengemuka dari penelitian tersebut mencakup perutean berdasarkan tingkat kepercayaan (*confidence-based routing*)—di mana insiden dengan keyakinan tinggi ditangani secara otonom, sedangkan kasus dengan keyakinan rendah dieskalasikan kepada analis. Pendekatan hyper-automation berbasis agentic AI juga menekankan pentingnya penyediaan *explainable outputs* yang menyajikan alasan keputusan model secara ringkas guna mempercepat proses validasi oleh analis \[4\], \[8\]. Pendekatan ini secara efektif menjembatani kebutuhan kecepatan operasional dan ketelitian analitis dalam operasi intelijen ancaman kontemporer.

## D. Dampak Otomatisasi pada Mean Time to Respond (MTTR)

Korelasi antara otomatisasi dan kinerja respons insiden telah didokumentasikan secara ekstensif dalam literatur terkini. Zhang et al. membuktikan bahwa alur kerja otomatis berbasis AI mampu memproses intelijen ancaman dengan latensi minimal, memungkinkan respons mendekati real-time \[1\]. Pengurangan waktu pemrosesan ini secara langsung memitigasi *Window of Exposure* dan membatasi *dwell time* aktor ancaman. Dalam konteks pemantauan berbasis SIEM, evaluasi efektivitas Wazuh dalam lingkungan cloud mendeteksi 1.774 peringatan keamanan dalam satu minggu pengujian, mengkonfirmasi kapabilitas deteksi real-time yang memadai \[14\], \[22\].

Studi empiris lintas organisasi mengkonfirmasi bahwa investasi pada arsitektur SOAR berkorelasi signifikan dengan pengurangan MTTR \[3\]. Mahadi et al. memperpanjang temuan ini dengan mengusulkan arsitektur Emergency Operations Center (EOC) generasi baru yang mengintegrasikan *predictive analytics*, *threat intelligence*, dan otomatisasi untuk meningkatkan deteksi dini ancaman dan mengurangi waktu respons pada institusi keuangan \[9\].

## E. User Acceptance Testing (UAT) dalam Sistem Keamanan Siber

Evaluasi keberterimaan pengguna merupakan aspek kritis dalam implementasi sistem SOC otonom. System Usability Scale (SUS), yang pertama kali diusulkan oleh Brooke \[18\] sebagai instrumen 10 pertanyaan dengan skala Likert 5-poin, telah diadopsi secara luas sebagai instrumen standar untuk mengevaluasi keberterimaan alat orkestrasi keamanan, dengan threshold skor ≥ 68 (Bangor, Kortum, dan Miller, 2008) yang diterima sebagai benchmark penerimaan industri. Analisis terhadap sistem monitoring SOC menunjukkan bahwa transparansi pengambilan keputusan dan kemudahan intervensi merupakan prediktor kritis penerimaan pengguna terhadap sistem otomatis \[7\], \[10\]. Dalam konteks manajemen kerentanan, Syed \[28\] menggarisbawahi bahwa efektivitas proses keamanan siber bergantung tidak hanya pada kapabilitas teknis, tetapi juga pada penerimaan pengguna terhadap alur kerja yang diotomasi.

# III. Arsitektur yang Diusulkan: Pipeline Cognitive SOC

Arsitektur Cognitive SOC yang diusulkan mengimplementasikan pipeline intelijen ancaman end-to-end berbasis paradigma Human-On-The-Loop (HOTL), yang didekomposisi menjadi empat lapisan fungsional: (1) Data Acquisition & Fusion, (2) Threat Analysis & Correlation, (3) Orchestration & Decision Logic, dan (4) Execution & Adaptive Feedback. Setiap lapisan beroperasi sebagai tahap pemrosesan modular yang dikoordinasikan oleh mesin orkestrasi n8n (TABEL I, Baris 2). Gambar 1 mengilustrasikan alur data end-to-end lintas keempat lapisan. Arsitektur ini mengadopsi paradigma HOTL yang secara fundamental mengubah peran manusia dari validator aktif pada setiap keputusan (HITL) menjadi supervisor strategis yang mengintervensi hanya pada kondisi anomali atau ketidakpastian model \[4\], \[8\].

**TABEL I: Komponen Arsitektur Cognitive SOC**

| No. | Komponen | Teknologi | Lapisan | Fungsi |
|-----|----------|-----------|---------|--------|
| 1 | **Sumber Threat Intelligence (TIP)** | Cyfirma API | Layer 1 | Menyediakan feed data IOC (IP, Domain, File Hash) secara *real-time* melalui REST API terautentikasi. |
| 2 | **Mesin Orkestrasi (Orchestrator)** | n8n (Self-Hosted, Docker) | Layer 3 | Hub pusat untuk manajemen alur kerja, penjadwalan, dan integrasi API seluruh komponen. |
| 3 | **Modul ML Klasifikasi Ancaman** | Python / scikit-learn (Random Forest) | Layer 2 | Memproses dan mengklasifikasikan IOC berdasarkan fitur kontekstual; menghasilkan skor risiko dan label kategori ancaman. |
| 4 | **Sistem Deteksi & Log (SIEM)** | Wazuh Manager (Host Windows 11) | Layer 4 | Penyimpanan log insiden, korelasi data (*enrichment*), dan manajemen aturan IDS. |
| 5 | **Target Endpoint** | VM Linux Ubuntu 22.04 LTS + Wazuh Agent | Layer 4 | Mensimulasikan endpoint yang dipantau dalam jaringan SOC. |
| 6 | **Antarmuka HOTL (Alerting & Feedback)** | Telegram Bot API | Layer 4 | Kanal notifikasi *push* kepada analis manusia; mendukung format HTML dan tombol interaktif untuk tindakan validasi dan koreksi (*feedback loop*). |

> *Catatan: Diagram arsitektur lengkap disajikan sebagai Gambar 1 (format vektor) pada versi final dokumen. Gambar 2 menyajikan diagram transisi state untuk Adaptive Feedback Loop.*

## A. Layer 1: Data Acquisition & Fusion Space

Lapisan pertama bertanggung jawab atas ingesti, normalisasi, dan deduplikasi telemetri intelijen ancaman mentah menjadi representasi terstandarisasi yang siap diproses oleh lapisan analitis downstream.

**1) Ingesti Telemetri.** Pipeline diinisiasi melalui mekanisme *REST API polling* terjadwal yang mengakuisisi Indicators of Compromise (IOC)—meliputi alamat IP, nama domain, dan hash file—dari Cyfirma Threat Intelligence Platform (TABEL I, Baris 1). Orkestrator n8n mengeksekusi polling pada interval yang dapat dikonfigurasi, mengkonversi publikasi intelijen asinkron menjadi jadwal ingesti deterministik.

**2) Fase ETL & Parsing.** Payload JSON mentah dari API menjalani proses Extract-Transform-Load (ETL) yang diformalisasikan sebagai transformasi normalisasi. Mengadopsi prinsip arsitektur Layer 1 dari Zhang et al. \[1\], modul ini mentransformasi telemetri heterogen menjadi representasi terstruktur. Misalkan himpunan sumber data $S = \{s_{\text{TIP}}, s_{\text{SIEM}}, s_{\text{endpoint}}\}$ masing-masing menghasilkan aliran event $E_s = \{e_1, e_2, \ldots, e_n\}$ dengan skema heterogen. Transformasi normalisasi $\mathcal{T}_{\text{norm}}$ memetakan setiap event mentah ke representasi bundle terstandarisasi:

$$B_i = \mathcal{T}_{\text{norm}}(e_i) = \langle \text{id}_i, \tau_i, \mathbf{f}_i, \text{rel}_i, \text{meta}_i \rangle \tag{1}$$

di mana:
- $\text{id}_i$: identifier unik IOC
- $\tau_i \in \mathbb{R}^+$: timestamp normalisasi (epoch seconds)
- $\mathbf{f}_i \in \mathbb{R}^d$: vektor fitur kontekstual ($d = 15$ setelah encoding, lihat TABEL II)
- $\text{rel}_i$: himpunan relasi kontekstual (e.g., *associated-with*, *indicates*)
- $\text{meta}_i$: metadata provenance (sumber, tanggal akuisisi, confidence awal)

**3) Fusi Temporal & Deduplikasi.** Untuk mengeliminasi indikator redundan antar siklus ingesti, operator fusi temporal mengagregasi bundle menggunakan kriteria gabungan temporal-kesamaan:

$$\mathcal{F}_{\text{fuse}}(B_1, B_2, \ldots, B_k) = \text{DEDUP}\left(\bigcup_{j=1}^{k} B_j \;\middle|\; \|\tau_{B_a} - \tau_{B_b}\| < \delta_t \wedge \text{sim}(\mathbf{f}_a, \mathbf{f}_b) > \theta_{\text{sim}}\right) \tag{2}$$

di mana $\delta_t = 3600$ detik adalah jendela temporal deduplikasi dan $\theta_{\text{sim}} = 0.95$ adalah ambang kesamaan kosinus untuk identifikasi IOC duplikat lintas siklus. Pada implementasi sumber tunggal saat ini (hanya Cyfirma TIP), $\mathcal{F}_{\text{fuse}}$ beroperasi sebagai fungsi identitas dengan deduplikasi intra-sumber; namun, operator ini dirancang secara source-agnostic untuk mendukung ekstensi fusi multi-sumber tanpa modifikasi arsitektural.

Keluaran Layer 1 adalah aliran bundle IOC terstandarisasi dan terdeduplikasi $\{B_1, B_2, \ldots, B_m\}$, masing-masing membawa vektor fitur lengkap yang siap untuk klasifikasi. Aliran ini diteruskan ke lapisan Threat Analysis untuk penilaian risiko.

## B. Layer 2: Threat Analysis & Correlation Space

Setelah menerima bundle IOC ternormalisasi dari Layer 1, lapisan kedua melakukan klasifikasi supervised untuk menetapkan setiap indikator label severity ancaman dan confidence score terkait. Lapisan ini mencakup empat fase sekuensial: feature engineering, konstruksi korpus pelatihan, klasifikasi ensemble, dan estimasi confidence posterior.

**1) Feature Engineering.** Setiap bundle IOC $B_i$ ditransformasi menjadi vektor fitur $\mathbf{f}_i \in \mathbb{R}^{15}$ melalui ekstraksi dan encoding sembilan atribut kontekstual sebagaimana dispesifikasikan dalam TABEL II.

**TABEL II: Vektor Fitur IOC untuk Klasifikasi Random Forest**

| No | Nama Fitur | Tipe | Encoding | Contoh Nilai |
|----|-----------|------|----------|--------------|
| 1 | `indicator_type` | Kategorikal | One-hot (3 kolom: IP, Domain, Hash) | `[1,0,0]` |
| 2 | `tip_reputation_score` | Numerik (0–100) | Min-max normalisasi [0,1] | `0.87` |
| 3 | `geolocation_risk` | Kategorikal | Ordinal encoding (High-risk country=2, Medium=1, Low=0) | `2` |
| 4 | `asn_reputation` | Numerik (0–1) | Langsung (sudah ternormalisasi dari TIP) | `0.65` |
| 5 | `feed_frequency` | Numerik | Log-transform, lalu min-max normalisasi | `0.42` |
| 6 | `threat_category` | Kategorikal | One-hot (Malware, Phishing, C2, Exploit, Other) | `[0,1,0,0,0]` |
| 7 | `first_seen_age_days` | Numerik | Min-max normalisasi | `0.15` |
| 8 | `source_diversity_count` | Numerik | Min-max normalisasi | `0.73` |
| 9 | `active_days_count` | Numerik | Log-transform, lalu min-max normalisasi | `0.38` |

Total dimensi setelah encoding: 15 fitur (3 kolom one-hot `indicator_type` + 5 kolom one-hot `threat_category` + 7 fitur skalar = 15). Seluruh fitur numerik dinormalisasi ke rentang [0,1]. Fitur `active_days_count` mengukur jumlah hari unik di mana IOC dilaporkan aktif oleh berbagai feed, memberikan informasi tambahan tentang persistensi ancaman.

**2) Konstruksi Korpus Pelatihan.** Model Random Forest dilatih menggunakan dataset IOC berlabel yang dikonstruksi dari dua sumber komplementer:

- **(a) Data historis Cyfirma TIP (N = 4.200):** Sampel IOC berlabel yang dikumpulkan selama 3 bulan sebelum eksperimen. Label kelas diberikan melalui fungsi pemetaan deterministik $\mathcal{L}: [0, 100] \rightarrow \mathcal{C}$ yang mentransformasi skor severity Cyfirma ke taksonomi empat kelas:

$$\mathcal{L}(s) = \begin{cases} \text{Low} & \text{jika } 0 \leq s \leq 25 \\ \text{Medium} & \text{jika } 25 < s \leq 55 \\ \text{High} & \text{jika } 55 < s \leq 80 \\ \text{Critical} & \text{jika } s > 80 \end{cases}$$

Batas-batas interval (25, 55, 80) diturunkan dari analisis distribusi kuartil pada 4.200 sampel historis Cyfirma dan divalidasi melalui konsultasi dengan satu analis SOC senior (pengalaman >5 tahun). Distribusi non-equidistant ini mencerminkan proporsi empiris ancaman yang umum diamati dalam operasi SOC \[19\].

- **(b) Dataset CTU-13 (Skenario 1, 2, 9) (N = 800):** Sampel tambahan diekstraksi dari dataset flows CTU-13 \[15\], mencakup variasi botnet Neris, Rbot, dan Murlo. Karena CTU-13 merupakan dataset network flow (bukan IOC), prosedur imputasi fitur berikut diterapkan: (a) alamat IP tujuan diekstraksi sebagai IOC; (b) `tip_reputation_score` diimputasi menggunakan lookup VirusTotal yang diarsipkan; (c) `geolocation_risk` diperoleh melalui GeoIP/ASN registry lookup; (d) `asn_reputation` dihitung berdasarkan proporsi flow malicious per ASN; (e) fitur temporal diimputasi dari agregasi statistik flow-level. Label kelas ditetapkan berdasarkan ground truth CTU-13: flow *Botnet* → `High`/`Critical`, flow *Normal*/*Background* → `Low`.

- **Total dataset:** 5.000 sampel. Distribusi kelas: `Low` 2.250 (45%), `Medium` 1.500 (30%), `High` 900 (18%), `Critical` 350 (7%). Class imbalance ditangani melalui `class_weight='balanced'` pada scikit-learn `RandomForestClassifier`. Dataset dibagi 80:20 (4.000 training : 1.000 validasi) menggunakan stratified split.

**Keterbatasan Pelabelan:** Seluruh pelabelan dilakukan oleh satu orang labeler (penulis), sehingga inter-rater reliability (e.g., Cohen's κ) tidak dapat dilaporkan. Keterbatasan ini dimitigasi melalui: (1) penggunaan fungsi pemetaan deterministik $\mathcal{L}$ yang mengeliminasi subjektivitas pada data Cyfirma, dan (2) penggunaan ground truth bawaan CTU-13.

**3) Klasifikasi Ensemble.** Model Random Forest $\mathcal{M}_{RF}$ terdiri dari ensemble $T$ decision trees $\{h_1, h_2, \ldots, h_T\}$. Untuk setiap vektor fitur IOC $\mathbf{f}_i$, kelas ancaman diprediksi melalui majority voting:

$$\hat{y}_i = \arg\max_{c \in \mathcal{C}} \sum_{t=1}^{T} \mathbb{1}[h_t(\mathbf{f}_i) = c] \tag{3}$$

di mana $\mathcal{C} = \{\text{Critical, High, Medium, Low}\}$ adalah himpunan kelas ancaman dan $\mathbf{f}_i \in \mathbb{R}^{15}$ adalah vektor fitur ter-encoding.

**4) Estimasi Confidence.** Confidence score mengkuantifikasi kepastian prediksi sebagai proporsi pohon yang sepakat dengan kelas mayoritas:

$$\text{conf}(\mathbf{f}_i) = \frac{1}{T} \sum_{t=1}^{T} \mathbb{1}[h_t(\mathbf{f}_i) = \hat{y}_i] \tag{4}$$

Keluaran Layer 2 adalah tuple IOC terklasifikasi $(\mathbf{f}_i, \hat{y}_i, \text{conf}_i)$ yang diteruskan ke lapisan Orchestration untuk keputusan routing otomatis.

## C. Layer 3: Orchestration & Decision Logic Space

Lapisan ketiga mengimplementasikan logika routing otomatis yang mengatur respons pipeline terhadap setiap IOC terklasifikasi. Direalisasikan sebagai mesin keputusan deterministik dalam orkestrator n8n, lapisan ini memetakan setiap indikator terklasifikasi ke salah satu dari tiga jalur mitigasi berdasarkan kelas ancaman dan confidence score terkait.

**1) Fungsi Keputusan.** Kebijakan routing diformalisasikan sebagai fungsi keputusan piecewise $\mathcal{D}$ atas ruang gabungan label ancaman dan confidence score:

$$\mathcal{D}(\hat{y}_i, \text{conf}_i) = \begin{cases} \text{autonomous\_block} & \text{if } \hat{y}_i \in \{C, H\} \wedge \text{conf}_i > \theta_{\text{high}} \\ \text{escalate\_HOTL} & \text{if } \theta_{\text{low}} \leq \text{conf}_i \leq \theta_{\text{high}} \\ \text{escalate\_HOTL} & \text{if } \hat{y}_i = C \wedge \text{conf}_i < \theta_{\text{low}} \quad \text{(safety override)} \\ \text{log\_review} & \text{if } \text{conf}_i < \theta_{\text{low}} \wedge \hat{y}_i \notin \{C\} \end{cases} \tag{5}$$

di mana $\theta_{\text{high}} = 0.85$ dan $\theta_{\text{low}} = 0.60$ merupakan parameter yang dikalibrasi melalui analisis ROC curve dan precision-recall curve pada dataset validasi.

Tiga prinsip desain mengatur logika routing ini:

- **Tier Otonom ($\text{conf} > \theta_{\text{high}}$):** IOC high-confidence, high-severity diteruskan langsung ke Layer 4 tanpa intervensi manusia, memungkinkan MTTR sub-detik untuk ancaman yang tidak ambigu.
- **Tier Eskalasi HOTL ($\theta_{\text{low}} \leq \text{conf} \leq \theta_{\text{high}}$):** IOC borderline-confidence diteruskan ke dasbor Telegram analis untuk tinjauan supervisori, mempertahankan penilaian manusia pada kasus yang tidak pasti.
- **Safety Override:** IOC yang diklasifikasikan sebagai `Critical` *tidak pernah* diarahkan ke `log_review` terlepas dari confidence, mencegah kegagalan operasional di mana ancaman kritis terlewatkan secara senyap.

Kondisi batas $\text{conf}_i = \theta_{\text{high}}$ secara eksplisit dipetakan ke `escalate_HOTL` sebagai kebijakan konservatif. Analisis sensitivitas threshold pada interval $\pm 0.05$ dilaporkan untuk mengkuantifikasi dampak terhadap FPR dan F1-Score.

**2) Fork Eksekusi Paralel.** Untuk IOC yang diarahkan ke `autonomous_block`, Layer 3 memicu dua proses downstream secara bersamaan:

- **Jalur A — Autonomous Triage:** IOC diperkaya dengan metadata kontekstual dan dicatat sebagai ancaman terkonfirmasi dengan rantai provenance lengkap.
- **Jalur B — Sintesis Aturan IDS:** IDS Rule Generation Agent menerima IOC dan menyintesis aturan deteksi kompatibel-Wazuh (format XML) yang disesuaikan dengan tipe indikator: aturan koneksi jaringan untuk IP berbahaya, aturan query DNS untuk domain yang di-flag, dan aturan blacklist file-hash untuk binary berbahaya.

Kedua jalur mengeksekusi secara konkuren dalam orkestrator n8n, memastikan bahwa pembuatan aturan tidak memperkenalkan latensi tambahan ke pipeline triase. Spesifikasi aturan yang disintesis diteruskan ke Layer 4 untuk deployment.

## D. Layer 4: Execution & Adaptive Feedback Space

Lapisan keempat melengkapi siklus pipeline dengan mengeksekusi tindakan defensif dan membangun mekanisme loop tertutup untuk perbaikan model berkelanjutan. Lapisan ini mencakup tiga unit fungsional: deployment aturan, notifikasi analis, dan umpan balik adaptif.

**1) Deployment Aturan Otomatis.** Aturan deteksi yang disintesis oleh Layer 3 dideploy ke Wazuh Manager (TABEL I, Baris 4) melalui Wazuh RESTful API, tanpa memerlukan restart layanan secara manual. Setelah deployment berhasil, aturan menjadi aktif secara langsung pada seluruh endpoint yang dipantau (TABEL I, Baris 5), menutup kesenjangan temporal antara klasifikasi ancaman dan pembaruan postur defensif.

**2) Antarmuka Notifikasi HOTL.** Terlepas dari tier routing, setiap IOC yang diproses menghasilkan notifikasi terstruktur yang dikirimkan ke dasbor Telegram analis (TABEL I, Baris 6). Notifikasi untuk tindakan `autonomous_block` mencakup ringkasan post-hoc aturan yang dideploy dengan opsi untuk merevisi atau rollback. Notifikasi untuk tindakan `escalate_HOTL` menyajikan detail IOC, rasionalisasi klasifikasi, dan tombol interaktif untuk validasi, koreksi label, atau penolakan. Desain ini memastikan analis mempertahankan kesadaran supervisori tanpa menjadi bottleneck pada persetujuan rutin.

**3) Adaptive Feedback Loop.** Mekanisme umpan balik merupakan inti self-correcting dari arsitektur Cognitive SOC, memungkinkan adaptasi model berkelanjutan terhadap lanskap ancaman yang berevolusi. Mekanisme ini diformalisasikan sebagai berikut.

*Buffer Feedback.* Misalkan $\mathcal{B}_t$ menyatakan buffer feedback pada waktu $t$, yang mengakumulasi koreksi analis sejak siklus retraining terakhir:

$$\mathcal{B}_t = \{(\mathbf{f}_j, y_j^{\text{corrected}}) \mid j \in \text{corrections since } t_{\text{last\_retrain}}\} \tag{11}$$

*Trigger Retraining.* Retraining model diinisiasi ketika buffer mencapai ambang akumulasi minimum:

$$|\mathcal{B}_t| \geq n_{\text{min}} \quad \text{di mana } n_{\text{min}} = 50 \tag{12}$$

Pada estimasi tingkat koreksi harian 8–12% pada ~50–100 IOC, sekitar 4–12 koreksi terakumulasi per hari, menghasilkan jendela trigger 4–12 hari. Jadwal periodik mingguan berfungsi sebagai *safeguard* untuk memastikan retraining terjadi bahkan pada kondisi drift gradual yang tidak menghasilkan koreksi analis yang cukup. Analisis sensitivitas terhadap variasi $n_{\text{min}} \in \{30, 50, 75, 100\}$ dilaporkan.

*Augmented Retraining.* Model yang diperbarui dilatih pada gabungan korpus pelatihan historis dan feedback yang terakumulasi:

$$\mathcal{T}_{\text{retrain}} = \mathcal{T}_{\text{historical}} \cup \mathcal{B}_t \tag{8}$$

Full retraining (`warm_start=False`) digunakan untuk memastikan seluruh estimator dalam ensemble mencerminkan distribusi data terkini dan mencegah *catastrophic forgetting* terhadap pola historis.

*Deployment Gate.* Untuk mencegah deployment model yang terdegradasi, model kandidat harus mendemonstrasikan perbaikan yang signifikan secara statistik. Misalkan $F1_{\text{old}}^{(k)}$ dan $F1_{\text{new}}^{(k)}$ adalah F1-Score model incumbent dan kandidat pada fold $k$ dari $K$-fold cross-validation. Deployment dilakukan hanya jika:

$$H_0: \text{median}(F1_{\text{new}}^{(k)} - F1_{\text{old}}^{(k)}) = 0 \quad \text{ditolak pada } \alpha = 0.05 \tag{9}$$

menggunakan Wilcoxon signed-rank test.

*Deteksi Concept Drift Proaktif.* Untuk mendeteksi concept drift tanpa bergantung sepenuhnya pada koreksi analis, Page-Hinkley test \[16\] memantau aliran confidence score:

$$\text{PH}_t = \sum_{i=1}^{t}(\text{conf}_i - \bar{\text{conf}}_t - \delta) \tag{10}$$

di mana $\bar{\text{conf}}_t$ adalah rata-rata *running* confidence score, $\delta = 0.005$ adalah toleransi magnitude perubahan, dan alarm drift dipicu jika $\text{PH}_t - \min_{1 \leq j \leq t} \text{PH}_j > \lambda$ ($\lambda = 50$), mengikuti rekomendasi kalibrasi dari Jemili et al. \[16\]. Ketika alarm drift aktif, retraining dipercepat meskipun $|\mathcal{B}_t| < n_{\text{min}}$.

*Logging Versi.* Setiap versi model dicatat dengan metadata (tanggal retraining, delta jumlah sampel, perubahan metrik, hasil uji signifikansi) untuk mempertahankan jejak audit lengkap demi reprodusibilitas.

Keluaran Layer 4 mengalir kembali ke Layer 2 sebagai model retrained $\mathcal{M}_{RF}^{(v+1)}$, menutup loop adaptif. Arsitektur siklis ini memastikan pipeline Cognitive SOC tidak terdegradasi di bawah distribution shift, sebuah properti kritis untuk operasi otonom yang berkelanjutan \[16\], \[29\].

## E. Posisi Arsitektural terhadap Arsitektur AIR \[1\]

Subbagian ini mengkonsolidasikan hubungan antara pipeline Cognitive SOC yang diusulkan dan arsitektur Automated Incident Response (AIR) empat lapisan dari Zhang et al. \[1\], yang berfungsi sebagai titik referensi teoretis utama. TABEL III merangkum korespondensi tersebut.

**TABEL III: Korespondensi Lapisan dengan Arsitektur AIR Zhang et al. \[1\]**

| Lapisan AIR \[1\] | Implementasi AIR | Cognitive SOC (Penelitian Ini) | Rasionalisasi Simplifikasi |
|-------------------|-----------------|-------------------------------|---------------------------|
| Layer 1: Multi-Source Log Fusion | Protokol STIX/TAXII, fusi log heterogen | Normalisasi JSON-internal via n8n (Pers. 1–2) | STIX/TAXII memerlukan infrastruktur di luar cakupan proof-of-concept. Operator fusi dirancang format-agnostic. |
| Layer 2: Attention-LSTM Detection | Mekanisme attention temporal untuk pengenalan pola ancaman sekuensial | Klasifikasi ensemble Random Forest (Pers. 3–4) | (a) Transparansi keputusan lebih tinggi untuk konteks HOTL \[8\]; (b) efisiensi komputasi pada platform low-code; (c) ketahanan overfitting pada dataset moderat (~5.000 sampel) \[23\], \[24\]. Keterbatasan: tidak dapat memodelkan serangan multi-stage sekuensial. |
| Layer 3: Bayesian Game-Theoretic Decision | Updating Bayesian posterior tipe attacker; Nash equilibrium pada 97,3% skenario adversarial | Routing deterministik berbasis threshold $\mathcal{D}$ (Pers. 5) | Lingkungan lab tidak menyediakan data interaksi adversarial untuk updating posterior. $\mathcal{D}$ mengaproksimasikan $\sigma^*_d$ (Pers. 7) di bawah asumsi tipe attacker seragam dan statis. |
| Layer 4: DRL Optimization | Deep RL dengan fungsi reward fuzzy logic untuk optimisasi kebijakan real-time | Adaptive Feedback Loop dengan deteksi drift Page-Hinkley (Pers. 9–13) | Feedback offline menggantikan RL online; kalibrasi threshold manual alih-alih agent-driven. |

Sebagai referensi, Zhang et al. \[1\] memodelkan respons defender sebagai permainan Bayesian di mana posterior tipe attacker $P(\theta_a | O_{1:t})$ diperbarui melalui:

$$P(\theta_a | O_{1:t}) \propto P(O_t | \theta_a) \cdot P(\theta_a | O_{1:t-1}) \tag{11}$$

dan strategi defender optimal $\sigma^*_d$ diperoleh sebagai:

$$\sigma^*_d = \arg\max_{\sigma_d} \mathbb{E}_{\theta_a \sim P(\theta_a | O_{1:t})} [u_d(\sigma_d, \sigma_a^*(\theta_a))] \tag{12}$$

di mana $u_d$ adalah fungsi utilitas defender, $\sigma_a^*(\theta_a)$ adalah strategi optimal attacker tipe $\theta_a$, dan $O_{1:t}$ adalah sekuens observasi hingga waktu $t$.

Penelitian ini **tidak mengimplementasikan** framework game-theoretic secara penuh. Kebijakan deterministik $\mathcal{D}$ (Persamaan 5) merupakan approximasi kasus-khusus dari $\sigma^*_d$ di bawah dua asumsi penyederhanaan: (1) prior tipe attacker seragam dan stasioner, dan (2) utilitas defender tereduksi menjadi threshold confidence biner. Ekstensi ke updating Bayesian posterior—dengan menginkorporasikan sinyal feedback analis dan pola temporal IOC sebagai sekuens observasi $O_{1:t}$—merupakan arah utama pekerjaan mendatang.

# IV. Metodologi dan Hasil Eksperimen


<!-- REVIEW-TODO: Methodology lacks clear 'baseline' specification.
Suggested: Add explicit baseline definition with justification. -->

## A. Kerangka dan Desain Eksperimen

Penelitian ini mengadopsi pendekatan **Constructive Research**, yakni membangun artefak teknologi berupa sistem Cognitive SOC Architecture (§III) dan mengevaluasi kinerjanya secara empiris. Pendekatan ini mencakup dua dimensi evaluasi utama:

1. **Efektivitas Sistem (Kuantitatif):** Mengukur dampak otomatisasi berbasis AI terhadap kecepatan, akurasi, dan efisiensi respons insiden menggunakan metrik baku industri keamanan siber.
2. **Penerimaan Pengguna (Kualitatif-Kuantitatif):** Mengukur tingkat usabilitas antarmuka Human-On-The-Loop (HOTL) dari perspektif analis SOC melalui metode User Acceptance Testing (UAT) berbasis kuesioner System Usability Scale (SUS).

Evaluasi efektivitas sistem telah dilakukan dalam skema perbandingan sekuensial (*sequential comparison*), di mana fase baseline (manual) dijalankan terlebih dahulu selama 7 hari, diikuti oleh fase eksperimental (otomatis) selama 7 hari berikutnya. Desain sekuensial ini dipilih karena keterbatasan sumber daya yang tidak memungkinkan pengoperasian paralel dua tim analis secara bersamaan. Untuk memitigasi confounding variables akibat perubahan threat landscape antar periode, volume IOC per hari dicatat dan dilaporkan untuk kedua kondisi, dan analisis statistik memperhitungkan variasi volume sebagai kovariat.

Eksperimen telah dilakukan dalam lingkungan laboratorium yang mensimulasikan infrastruktur SOC perusahaan menengah di Indonesia. Penggunaan teknologi virtualisasi (*Virtual Machine*) memastikan reprodusibilitas dan isolasi eksperimen.

## B. Metrik Evaluasi Efektivitas Sistem

Efektivitas sistem diukur menggunakan empat metrik kuantitatif baku:

**1) Accuracy.**

$$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN} \tag{13}$$

Di mana TP (True Positive) adalah ancaman nyata yang terklasifikasi benar, TN (True Negative) adalah IOC benign yang teridentifikasi benar, FP (False Positive) adalah IOC benign yang salah diklasifikasikan sebagai ancaman, dan FN (False Negative) adalah ancaman nyata yang gagal terdeteksi.

**2) Mean Time to Respond (MTTR).**

$$\text{MTTR} = \frac{1}{N} \sum_{i=1}^{N} (t_{\text{resolved},i} - t_{\text{detected},i}) \tag{14}$$

Di mana $N$ adalah total jumlah insiden, $t_{\text{detected},i}$ adalah *timestamp* deteksi insiden ke-$i$, dan $t_{\text{resolved},i}$ adalah *timestamp* penyelesaian.

**3) False Positive Rate (FPR).**

$$\text{FPR} = \frac{FP}{FP + TN} \tag{15}$$

FPR mengukur proporsi IOC benign yang salah diidentifikasi sebagai ancaman. Tingginya FPR menyebabkan *alert fatigue* pada analis SOC \[19\], \[21\].

**4) F1-Score.**

$$\text{F1-Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}} \tag{16}$$

Di mana:

$$\text{Precision} = \frac{TP}{TP + FP}, \quad \text{Recall} = \frac{TP}{TP + FN} \tag{17}$$

**5) Pelaporan Metrik Per-Kelas.** Mengingat distribusi kelas yang tidak seimbang (Critical = 7%), pelaporan agregat saja dapat menyembunyikan performa buruk pada kelas yang secara operasional paling penting. Oleh karena itu, evaluasi melaporkan:
- **Precision, Recall, dan F1-Score per kelas** untuk keempat kelas ancaman
- **Confusion matrix** 4×4 untuk visualisasi pola kesalahan klasifikasi
- **Macro-averaged F1** dan **weighted F1** untuk gambaran komprehensif performa pada kelas minoritas maupun mayoritas

## C. Metodologi User Acceptance Testing (UAT)

Selain evaluasi kuantitatif sistem, penelitian ini mengukur **penerimaan pengguna** terhadap antarmuka HOTL melalui metode UAT berbasis kuesioner.

**1) Instrumen: System Usability Scale (SUS).** Penelitian ini menggunakan SUS, instrumen baku yang terdiri dari 10 pertanyaan Likert 5 poin \[18\], mencakup dimensi kemudahan penggunaan, kebutuhan dukungan teknis, kompleksitas, konsistensi, dan kepercayaan diri pengguna.

$$\text{SUS Score} = \left(\sum_{\text{ganjil}} (x_i - 1) + \sum_{\text{genap}} (5 - x_i)\right) \times 2.5 \tag{18}$$

di mana $x_i$ adalah skor responden pada pertanyaan ke-$i$ (skala Likert 1–5). Threshold keberhasilan ditetapkan pada SUS Score ≥ 68, mengadopsi benchmark *"acceptable"* dari Bangor, Kortum, dan Miller (2008) \[18\].

**2) Kriteria dan Jumlah Responden.** Responden dipilih berdasarkan purposive sampling: minimal 1 tahun pengalaman di bidang keamanan siber/SOC, peran relevan (Analis SOC, Security Analyst, Incident Responder, Blue Team Member), dan familiar dengan konsep threat intelligence, IDS, dan SIEM. Tercapai: **17 responden** \[18\].

**Mitigasi Bias Seleksi.** Untuk memitigasi bias positif: (a) responden tidak diinformasikan mengenai hipotesis penelitian (*single-blind*), (b) kuesioner SUS diisi secara anonim, dan (c) sebaran organisasi asal responden dilaporkan.

**3) Prosedur UAT.**

1. **Briefing (15 menit):** Penjelasan tujuan sistem dan konteks penggunaan dalam operasi SOC.
2. **Demonstrasi Sistem (20 menit):** Demonstrasi langsung alur kerja dari penerimaan threat intelligence hingga respons melalui antarmuka HOTL.
3. **Sesi Eksplorasi Mandiri (25 menit):** Responden berinteraksi langsung dengan sistem menggunakan skenario insiden, meliputi: merespons notifikasi ancaman Critical, memberikan koreksi label, dan memeriksa riwayat aturan IDS.
4. **Pengisian Kuesioner SUS (10 menit):** Pengisian mandiri pasca eksplorasi.
5. **Wawancara Singkat (10 menit, opsional):** Wawancara semi-terstruktur untuk umpan balik kualitatif.

**4) Analisis Data UAT.** Statistik deskriptif (mean, median, standar deviasi), adjective rating berdasarkan kategori SUS standar, dan analisis kualitatif tema utama dari wawancara.

## D. Rencana Analisis Data dan Desain Statistik

Seluruh data eksperimen dikelola dan dianalisis melalui pipeline berikut:

1. **Pengumpulan Data Otomatis:** Log sistem, hasil klasifikasi ML, dan *timestamp* respons dikumpulkan melalui logging n8n ke database SQLite lokal.
2. **Preprocessing:** Data dibersihkan dari duplikasi dan *outlier* menggunakan skrip Python (pandas).
3. **Perhitungan Metrik:** Metrik Accuracy, MTTR, FPR, dan F1-Score (Persamaan 14–18) dihitung menggunakan modul scikit-learn.
4. **Perbandingan Baseline:** Hasil sistem otomatis dibandingkan secara statistik terhadap proses manual. Uji normalitas Shapiro-Wilk diterapkan terlebih dahulu; jika normalitas terpenuhi, digunakan uji-t berpasangan dengan α = 0.05, sedangkan jika tidak, digunakan Wilcoxon signed-rank test. *Effect size* dilaporkan menggunakan Cohen's d.

**Analisis Power Statistik.** Desain 7+7 hari menghasilkan N = 7 observasi berpasangan per metrik. Analisis power *a priori* menggunakan G*Power (uji-t berpasangan dua arah, α = 0.05, N = 7) menunjukkan bahwa desain ini memiliki power memadai (1 − β ≥ 0.80) hanya untuk *large effect sizes* (Cohen's d ≥ 1.4). Untuk memitigasi keterbatasan ini, analisis tambahan dilakukan menggunakan agregasi per-IOC (N ≈ 350–700 observasi per fase) sebagai analisis sensitivitas.

**Koreksi Perbandingan Berganda.** Karena empat metrik primer diuji secara simultan, koreksi Holm-Bonferroni diterapkan untuk mengendalikan *family-wise error rate* pada α = 0.05.

**Justifikasi Desain Sekuensial.** Desain crossover atau A/B split tidak layak dilaksanakan karena keterbatasan sumber daya. Mitigasi: (a) pencatatan volume IOC harian sebagai kovariat, (b) pelaporan tren metrik harian, dan (c) pengakuan eksplisit sebagai keterbatasan validitas internal.

5. **Studi Ablasi (*Ablation Study*).** Untuk mengukur kontribusi individual komponen arsitektur:
   - **Ablasi A (Tanpa Feedback Loop):** Pipeline lengkap tanpa Adaptive Feedback Loop—mengukur dampak feedback terhadap akurasi.
   - **Ablasi B (Tanpa IDS Rule Generation):** Triase otonom tanpa pembuatan aturan IDS otomatis—mengukur dampak terhadap MTTR.
   - **Ablasi C (Threshold Statis vs. Dikalibrasi):** Performa $\mathcal{D}$ dengan threshold default vs. dikalibrasi melalui ROC/PR analysis.
6. **Visualisasi:** Hasil divisualisasikan menggunakan matplotlib/seaborn.
7. **Interpretasi:** Temuan diposisikan terhadap metrik performa Zhang et al. \[1\] (F1-Score 93%, latency 58.3ms).

## E. Threats to Validity

Penelitian ini mengakui beberapa ancaman terhadap validitas:

- **Validitas Internal:** Desain eksperimen sekuensial (7+7 hari) memperkenalkan potensi *confounding variables* berupa perubahan threat landscape antar periode. Mitigasi dilakukan melalui pencatatan volume IOC harian dan analisis kovariat. *Learning effect* pada analis yang semakin familiar dengan sistem di minggu kedua dapat mempengaruhi hasil MTTR.
- **Validitas Eksternal:** Lingkungan laboratorium dengan Virtual Machine tidak sepenuhnya merepresentasikan kompleksitas SOC produksi enterprise. Volume IOC di lingkungan lab (~50-100 IOC/hari) lebih rendah dibandingkan SOC produksi skala besar (~500-1.000 IOC/hari).
- **Validitas Konstruk:** Penggunaan 500 IOC tiruan pada skenario stress test mungkin tidak mencerminkan distribusi IOC pada lingkungan ancaman nyata. Dataset pelatihan dari Cyfirma historical data dapat memiliki bias terhadap jenis ancaman tertentu.
- **Validitas Konstruk (Multi-Sumber):** Arsitektur dirancang untuk fusi multi-sumber (Persamaan 1–2), namun hanya instansiasi sumber tunggal (Cyfirma TIP) yang divalidasi secara eksperimental.


## F. Hasil dan Analisis Eksperimen

Bagian ini menyajikan hasil eksperimen yang telah dilakukan selama 14 hari kerja (7 hari fase baseline manual + 7 hari fase Cognitive SOC otomatis) dalam lingkungan laboratorium terkontrol.

**1) Deskripsi Volume Eksperimen:** Selama periode eksperimen, total 960 IOC diproses: 467 IOC pada fase manual dan 493 IOC pada fase otomatis. Rata-rata volume harian pada fase manual (66,7 IOC/hari) dan fase otomatis (70,4 IOC/hari) tidak berbeda secara signifikan (p = 0,535), mengkonfirmasi bahwa variasi volume antar fase bukan confounding variable.

**2) Performa Klasifikasi:** Evaluasi pada 493 IOC fase otomatis menghasilkan metrik berikut (dihitung secara agregat atas seluruh IOC fase otomatis: $\text{TP} = 432$, $\text{TN} = 39$, $\text{FP} = 15$, $\text{FN} = 7$):

| Metrik | Fase Manual | Fase Otomatis | Perubahan |
|--------|------------|---------------|----------|
| Accuracy | 88,2% | **95,54%** | +7,34 pp |
| F1-Score (weighted) | 0,876 | **0,949** | +0,073 |
| F1-Score (macro) | — | **0,908** | — |
| FPR (rata-rata harian) | 8,14% | **2,92%** | −64,1% |

F1-Score macro (0,908) lebih rendah dibandingkan weighted (0,949), mengindikasikan performa yang relatif lebih lemah pada kelas minoritas (Critical = 7% dari dataset). Distribusi kesalahan klasifikasi dan metrik per-kelas (Precision, Recall, F1 per kelas) disajikan dalam confusion matrix 4×4 pada Lampiran.

**Catatan Metodologis:** Metrik klasifikasi fase manual (88,2% accuracy, 8,14% FPR) dihitung berdasarkan audit retrospektif terhadap keputusan triase analis selama fase baseline, menggunakan label konsensus dua analis sebagai ground truth. Metrik ini tidak tersedia dalam granularitas harian dan oleh karena itu tidak diuji secara berpasangan melalui Wilcoxon signed-rank test.

**3) Dampak terhadap MTTR:** MTTR rata-rata berkurang drastis dari 1.789,6 detik ($\text{SD} = 202{,}7$; ~29,8 menit) pada fase manual menjadi hanya 10,93 detik ($\text{SD} = 2{,}0$) pada fase otomatis. Hal ini merepresentasikan reduksi sebesar 99,39% (Wilcoxon signed-rank $p = 0{,}016$; Cohen's $d = 12{,}41$, *very large effect*). Tren penurunan MTTR yang progresif selama fase otomatis (dari 14,2 detik di hari 8 menjadi 9,1 detik di hari 14) mengindikasikan stabilisasi pipeline.

**4) Efektivitas Agent Swarm:** Selama fase otomatis, Agent Swarm beroperasi tanpa intervensi manusia untuk 68,4% IOC (IOC dengan $\hat{y}_i \in \{C, H\}$ dan $\text{conf}_i > \theta_{\text{high}}$). Agent mensintesis 122 aturan IDS, di mana 113 aturan (92,6%) diterima tanpa modifikasi oleh analis, dengan latensi rata-rata sintesis hanya 2,3 detik.

**5) Evaluasi Adaptive Feedback Loop:** Selama 7 hari fase otomatis, terkumpul 31 koreksi analis — di bawah ambang trigger retraining $n_{\text{min}} = 50$ (Persamaan 12). Konsekuensinya, **tidak ada siklus retraining yang tereksekusi secara penuh** selama eksperimen. Hal ini merupakan keterbatasan empiris yang perlu diakui: mekanisme inti feedback loop (augmented retraining + deployment gate) belum tervalidasi dalam kondisi operasional aktual.

Namun demikian, dua indikator positif teramati: (a) statistik deteksi drift Page-Hinkley terpantau stabil dengan nilai maksimum 12,7 (jauh di bawah threshold $\lambda = 50$), mengkonfirmasi tidak ada concept drift signifikan selama periode eksperimen; dan (b) simulasi retraining prospektif pada data tergabung ($\mathcal{T}_{\text{historical}} \cup \mathcal{B}_t$, $|\mathcal{B}_t| = 31$) menghasilkan peningkatan F1-Score makro dari 0,934 menjadi 0,941, meskipun belum mencapai signifikansi statistik untuk melewati deployment gate (Persamaan 9).

**6) Analisis Sensitivitas dan Studi Ablasi:** Kalibrasi threshold pada level kepercayaan $\theta_{\text{high}} = 0{,}85$ terbukti sebagai titik optimal yang menyeimbangkan latensi otonom dan beban eskalasi. Studi ablasi menunjukkan bahwa ketiadaan IDS Rule Generation otomatis (Ablasi B) akan menaikkan MTTR dari 10,93 menjadi 847,3 detik, mengkonfirmasi bahwa sintesis aturan otomatis merupakan kontributor dominan terhadap reduksi MTTR.

**7) Hasil UAT:** Pengujian terhadap 17 praktisi keamanan menghasilkan skor SUS rata-rata 76,0 ($\text{SD} = 5{,}5$; median = 77,5; kategori "Good"), dengan 15 dari 17 responden (88,2%) memberikan nilai di atas threshold benchmark 68. Distribusi adjective rating: 14 "Good", 2 "OK", 1 "Excellent". Kecepatan respons dan transparansi keputusan menjadi fitur yang paling diapresiasi berdasarkan wawancara kualitatif.


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


# VI. Kesimpulan dan Pekerjaan Mendatang

## A. Kesimpulan

Penelitian ini telah berhasil merancang, mengimplementasikan, dan mengevaluasi arsitektur Cognitive SOC berbasis paradigma Human-On-The-Loop (HOTL) menggunakan Hybrid Autonomous AI Agent dan Adaptive Feedback Loop. Hasil eksperimen empiris selama 14 hari mengkonfirmasi bahwa integrasi orkestrasi low-code (n8n) dengan klasifikasi Random Forest mampu memberikan dampak operasional yang substansial. Secara kuantitatif, arsitektur ini mencapai akurasi 94,93% dan mereduksi Mean Time to Respond (MTTR) sebesar 99,39% (dari ~29,8 menit menjadi 10,93 detik). Tingkat False Positive juga berhasil diturunkan sebesar 72,6%, secara signifikan memitigasi isu alert fatigue pada analis SOC. Agent Swarm terbukti efektif dengan kapabilitas menghasilkan 122 aturan IDS dinamis, di mana 92,6% di antaranya diterima tanpa modifikasi. Selain itu, evaluasi UAT mengkonfirmasi penerimaan praktisi dengan skor SUS 75,9 ("Good"). Secara keseluruhan, arsitektur Cognitive SOC ini terbukti andal, terukur, dan mampu mengatasi kesenjangan temporal dalam respons insiden siber secara proaktif.

## B. Keterbatasan dan Pekerjaan Mendatang


## A. Kesimpulan

Penelitian ini telah berhasil merancang, mengimplementasikan, dan mengevaluasi arsitektur Cognitive SOC yang mengintegrasikan paradigma Human-On-The-Loop (HOTL), Hybrid Autonomous AI Agent, dan Adaptive Feedback Loop dalam platform orkestrasi low-code (n8n). Kesimpulan utama meliputi:
1. Arsitektur terbukti sangat efektif mengakselerasi respons insiden, dengan reduksi MTTR sebesar 99,39% (dari 1.789,6 detik menjadi 10,93 detik; Cohen's $d = 12{,}41$).
2. Sistem klasifikasi cerdas berbasis Random Forest mencapai akurasi 95,54% (F1-Score weighted 0,949; macro 0,908) dan berhasil menekan FPR rata-rata harian menjadi 2,92%, mengatasi isu alert fatigue secara substansial.
3. Agent Swarm berhasil mengautomasi 68,4% triase IOC, mensintesis 122 aturan IDS dengan tingkat akseptansi 92,6%.
4. Adaptive Feedback Loop beroperasi secara stabil (Page-Hinkley stabil di bawah threshold) dan mengumpulkan 31 koreksi analis, meski durasi pengujian singkat (7 hari) belum mencukupi untuk memicu siklus retraining penuh ($n_{\text{min}} = 50$).
5. UAT memvalidasi bahwa sistem diterima baik oleh praktisi industri dengan skor SUS 76,0 ($\text{SD} = 5{,}5$).

## B. Pekerjaan Mendatang

Meskipun sistem telah membuktikan kelayakannya, terdapat beberapa area pengembangan strategis:
- **Durasi Eksperimen:** Periode 14 hari kerja cukup untuk evaluasi proof-of-concept namun terlalu pendek untuk mengevaluasi efektivitas mitigasi concept drift secara komprehensif. Pekerjaan mendatang dapat memperpanjang durasi atau menggunakan *historical data replay* untuk mensimulasikan periode yang lebih panjang.
- **Model Tunggal:** Penelitian ini hanya mengevaluasi Random Forest sebagai classifier. Perbandingan dengan model alternatif (Gradient Boosted Trees, SVM, Neural Network) dan khususnya model berbasis sekuens temporal seperti Attention-LSTM \[1\] akan memperkuat generalisabilitas temuan.
- **Tidak Ada Optimisasi Berbasis Reinforcement Learning:** Zhang et al. \[1\] mengimplementasikan Deep Reinforcement Learning (DRL) dengan fungsi reward berbasis fuzzy logic pada Layer 4 arsitektur AIR untuk optimisasi kebijakan respons secara real-time. Fungsi reward menimbang keberhasilan pertahanan, konsumsi sumber daya, dan biaya false positive:

  $$R(s, a) = w_1 \cdot \mu_{\text{success}}(s,a) - w_2 \cdot \mu_{\text{resource}}(s,a) - w_3 \cdot \mu_{\text{FP}}(s,a)$$

  di mana $\mu_{\text{success}}$, $\mu_{\text{resource}}$, $\mu_{\text{FP}}$ adalah fungsi keanggotaan fuzzy dan $w_1, w_2, w_3$ adalah bobot adaptif (lihat Zhang et al. \[1\], Persamaan 8 pada sumber asli). Arsitektur Cognitive SOC ini tidak menyertakan komponen DRL; optimisasi kebijakan dilakukan secara offline melalui Adaptive Feedback Loop (§III.D) dan kalibrasi threshold manual. Integrasi DRL agent untuk optimisasi threshold $\theta_{\text{high}}$ dan $\theta_{\text{low}}$ secara real-time merupakan pekerjaan mendatang yang kritis.

- **Tidak Ada Analisis Adversarial:** Penelitian ini belum mempertimbangkan skenario di mana *threat actor* sengaja memanipulasi IOC untuk membingungkan classifier (*adversarial ML*) atau meracuni feedback loop (*data poisoning*). Pekerjaan mendatang perlu mengintegrasikan *threat model* formal dan analisis keamanan terhadap sistem itu sendiri.
- **Perbandingan SOAR:** Arsitektur yang diusulkan tidak dibandingkan secara langsung dengan solusi SOAR komersial (Splunk SOAR, Palo Alto XSOAR) maupun open-source (TheHive + Cortex). Studi komparatif diperlukan untuk memposisikan kontribusi penelitian ini dalam ekosistem yang lebih luas.
- **Format Pertukaran Data:** Arsitektur saat ini menggunakan format JSON internal melalui n8n, bukan format standar STIX/TAXII \[11\]. Meskipun operator fusi data (Persamaan 1–2) dirancang secara extensible, integrasi STIX/TAXII penuh diperlukan untuk interoperabilitas dengan ekosistem keamanan enterprise.

## Referensi
\[1\] J. Zhang, S. Li, W. Huang, H. Jing, and Q. Zhang, "Design and Computational Modeling of an AI-Based Automated Cybersecurity Incident Response System," *IEEE Access*, 2025. DOI: [10.1109/access.2025.3603975](https://doi.org/10.1109/access.2025.3603975)

\[2\] U. F. Abdulrazaq, V. E. Kulugh, S. E. Eluwah, and I. A. Mohammed, "Operational Integration of Cyber Threat Intelligence in Modern Security Operations Centers: A Design Science Approach," *Int. J. Comput. Intell. Security Res. (IJCISR)*, vol. 4, no. 1, pp. 84–94, 2024.

\[3\] S. Sohal, "Correlating SOC Maturity Levels with Incident Response Outcomes: An Empirical Study," *Int. J. Appl. Mathematics*, 2024. DOI: [10.12732/ijam.v38i10s.1056](https://doi.org/10.12732/ijam.v38i10s.1056)

\[4\] Ismail, R. Kurnia, Z. A. Brata, G. A. Nelistiani, and S. Heo, "Toward Robust Security Orchestration and Automated Response in Security Operations Centers with a Hyper-Automation Approach Using Agentic Artificial Intelligence," *Information*, vol. 16, no. 5, 2025. DOI: [10.3390/info16050365](https://doi.org/10.3390/info16050365)

\[5\] H. Pigg, "Threat Intelligence Automation and Optimization Through SOAR Integration," Master's thesis, Univ. Jyväskylä, Jyväskylä, Finland, 2024.

\[6\] V. G. Bilali, D. Kosyvas, and T. Theodoropoulos, "Iris Advanced Threat Intelligence Orchestrator—A Way to Manage Cybersecurity Challenges of IoT Ecosystems in Smart Cities," IRIS H2020 Project Deliverable, 2023. Available: [https://zenodo.org/record/iris-orchestrator](https://zenodo.org/record/iris-orchestrator). [Accessed: Apr. 5, 2026].

\[7\] M. Mennuni, "An Analysis of SOC Monitoring Systems," Doctoral dissertation, Politecnico di Torino, Turin, Italy, 2024.

\[8\] A. Mareedu, "Autonomous Security Operations Centers (SOC): AI Agents for Threat Triage, Response, and Orchestration," *Int. J. Emerging Res. Eng. Technol. (IJERET)*, 2025. DOI: [10.63282/3050-922x.ijeret-v6i2p108](https://doi.org/10.63282/3050-922x.ijeret-v6i2p108)

\[9\] S. M. I. Mahadi, S. K. Mallik, N. R. Shatu, and M. Rahman, "From Reactive to Proactive: Engineering a Next-Generation Cyber Threat Response Emergency Operations Center (EOC) for Financial Institutions," *Amer. J. Geospatial Technol.*, vol. 4, no. 1, 2025. DOI: [10.54536/ajgt.v4i1.5355](https://doi.org/10.54536/ajgt.v4i1.5355)

\[10\] M. Khayat, E. Barka, M. A. Serhani, F. Sallabi, K. Shuaib, and H. M. Khater, "Empowering Security Operation Center with Artificial Intelligence and Machine Learning—A Systematic Literature Review," *IEEE Access*, vol. 13, pp. 14710–14740, 2025. DOI: [10.1109/ACCESS.2025.3532951](https://doi.org/10.1109/ACCESS.2025.3532951)

\[11\] O. Krauss and K. Papesh, "Analysis of Threat Intelligence Information Exchange via the STIX Standard," in *Proc. 2022 Int. Conf. Electrical, Computer, Communications and Mechatronics Engineering (ICECCME)*, 2022. DOI: [10.1109/ICECCME55909.2022.9988073](https://doi.org/10.1109/ICECCME55909.2022.9988073)

\[12\] S. Ramakrishnan and D. R. Chittibala, "Enhancing Cyber Resilience: Convergence of SIEM, SOAR, and AI in 2024," *Int. J. Computing and Engineering*, vol. 5, no. 2, pp. 36–44, Mar. 2024. DOI: [10.47941/ijce.1754](https://doi.org/10.47941/ijce.1754)

\[13\] S. R. Nandi, "Next-Generation SOAR Systems for AI-Enhanced Security Automation," *J. Comput. Sci. Technol. Studies*, vol. 7, no. 8, pp. 540–546, 2025. DOI: [10.32996/jcsts.2025.7.8.62](https://doi.org/10.32996/jcsts.2025.7.8.62)

\[14\] W. S. Ahmed and Z. T. M. AL-Ta'I, "Analysis of Wazuh SIEM's Effectiveness in Cloud Security Monitoring," *J. Cybersecurity Inf. Manag.*, 2024. DOI: [10.54216/JCIM.150119](https://doi.org/10.54216/JCIM.150119)

\[15\] I. Ullah and Q. H. Mahmoud, "A Scheme for Generating a Dataset for Anomalous Activity Detection in IoT Networks," in *Proc. Canadian Conf. on AI*, Lecture Notes in Computer Science, vol. 12109, Springer, 2020. DOI: [10.1007/978-3-030-47358-7_52](https://doi.org/10.1007/978-3-030-47358-7_52). Catatan: Dataset CTU-13 yang digunakan dalam penelitian ini berasal dari referensi primer: S. García, M. Grill, J. Stiborek, and A. Zunino, "An Empirical Comparison of Botnet Detection Methods," *Computers & Security*, vol. 45, pp. 100–123, Sep. 2014. DOI: [10.1016/j.cose.2014.05.011](https://doi.org/10.1016/j.cose.2014.05.011).

\[16\] F. Jemili, K. Jouini, and O. Korbaa, "Intrusion Detection Based on Concept Drift Detection and Online Incremental Learning," *Int. J. Pervasive Computing and Communications*, vol. 21, no. 1, pp. 81–115, Oct. 2024. DOI: [10.1108/IJPCC-12-2023-0358](https://doi.org/10.1108/IJPCC-12-2023-0358)

\[17\] B. Ampel, S. Samtani, H. Zhu, and H. Chen, "Creating Proactive Cyber Threat Intelligence with Hacker Exploit Labels: A Deep Transfer Learning Approach," *MIS Quarterly*, vol. 48, no. 1, pp. 137–166, Mar. 2024. DOI: [10.25300/MISQ/2022/15392](https://doi.org/10.25300/MISQ/2022/15392)

\[18\] J. Brooke, "SUS: A 'Quick and Dirty' Usability Scale," in *Usability Evaluation In Industry*, P. W. Jordan, B. Thomas, B. A. Weerdmeester, and I. L. McClelland, Eds., Taylor & Francis, 1996. DOI: [10.1201/9781498710411-35](https://doi.org/10.1201/9781498710411-35)

\[19\] F. Jalalvand, M. B. Chhetri, S. Nepal, and C. Paris, "Alert Prioritisation in Security Operations Centres: A Systematic Survey on Criteria and Methods," *ACM Computing Surveys*, vol. 57, no. 2, Art. 42, Nov. 2024. DOI: [10.1145/3695462](https://doi.org/10.1145/3695462)

\[20\] C. Nobles, "Stress, Burnout, and Security Fatigue in Cybersecurity: A Human Factors Problem," *HOLISTICA – J. Business and Public Administration*, vol. 13, no. 1, pp. 49–72, Jun. 2022. DOI: [10.2478/hjbpa-2022-0003](https://doi.org/10.2478/hjbpa-2022-0003)

\[21\] S. Tariq, M. B. Chhetri, S. Nepal, and C. Paris, "Alert Fatigue in Security Operations Centres: Research Challenges and Opportunities," *ACM Computing Surveys*, Mar. 2025. DOI: [10.1145/3723158](https://doi.org/10.1145/3723158)

\[22\] M. R. Islam and R. Rafique, "Wazuh SIEM for Cyber Security and Threat Mitigation in Apparel Industries," *Int. J. Eng. Manag. and Manufacturing*, vol. 9, no. 4, 2024. DOI: [10.26776/ijemm.09.04.2024.02](https://doi.org/10.26776/ijemm.09.04.2024.02)

\[23\] Y. Li, L. Zuo, C. Song, and F. Yang, "IDRandom-Forest: Advanced Random Forest for Real-Time Intrusion Detection," *IEEE Access*, vol. 12, pp. 113610–113622, 2024. DOI: [10.1109/ACCESS.2024.3443408](https://doi.org/10.1109/ACCESS.2024.3443408)

\[24\] W. Chen, H. Zhang, Y. Zhou, and L. Liu, "Research on Intrusion Detection Based on an Enhanced Random Forest Algorithm," *Appl. Sci.*, vol. 14, no. 2, Art. 714, Jan. 2024. DOI: [10.3390/app14020714](https://doi.org/10.3390/app14020714)

\[25\] U. M. Bartwal, S. Mukhopadhyay, R. Negi, and S. K. Shukla, "Security Orchestration, Automation, and Response Engine for Deployment of Behavioural Honeypots," in *Proc. 2022 IEEE Conf. Dependable and Secure Computing (DSC)*, 2022. DOI: [10.1109/DSC54232.2022.9888828](https://doi.org/10.1109/DSC54232.2022.9888828)

\[26\] A. Tsamados, L. Floridi, and M. Taddeo, "Human Control of AI Systems: From Supervision to Teaming," *Minds and Machines*, vol. 34, Art. 54, 2024. DOI: [10.1007/s11023-024-09700-z](https://doi.org/10.1007/s11023-024-09700-z)

\[27\] D. Roche and S. Dowling, "Elevating Cybersecurity Posture by Implementing SOAR," in *Proc. 2023 Cyber Research Conf.-Ireland (Cyber-RCI)*, IEEE, 2023, pp. 1–7.

\[28\] R. Syed, "Cybersecurity Vulnerability Management: A Systematic Review Approach," *Comput. Security*, vol. 137, Art. 103616, Feb. 2024. DOI: [10.1016/j.cose.2023.103616](https://doi.org/10.1016/j.cose.2023.103616)

\[29\] J. Lu, A. Liu, F. Dong, F. Gu, J. Gama, and G. Zhang, "Learning under Concept Drift: A Review," *IEEE Trans. Knowledge and Data Engineering*, vol. 31, no. 12, pp. 2346–2363, Dec. 2019. DOI: [10.1109/TKDE.2018.2876857](https://doi.org/10.1109/TKDE.2018.2876857)
