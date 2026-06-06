Arsitektur Cognitive SOC Berbasis Hybrid Autonomous AI Agent dan Adaptive Feedback Loop: Implementasi Pipeline Intelijen Ancaman Jaringan Otomatis Menggunakan N8n Untuk Percepatan Respons Insiden

Joshua Kenneth Van Dyon  
_Bina Nusantara University_  
Jakarta, Indonesia  
[joshua.dyon@binus.ac.id](mailto:joshua.dyon@binus.ac.id)

_Abstrak_-Security Operations Center (SOC) modern menghadapi tantangan volume peringatan masif dan keterbatasan sumber daya manusia, yang meningkatkan Mean Time to Respond (MTTR) dan menurunkan akurasi deteksi. Penelitian ini mengusulkan arsitektur Cognitive SOC yang mengimplementasikan paradigma Human-On-The-Loop (HOTL) melalui Hybrid Autonomous AI Agent dan Adaptive Feedback Loop. Arsitektur ini mengintegrasikan Threat Intelligence Platform, mesin orkestrasi low-code, subsistem Machine Learning (Random Forest), dan SIEM, dengan mekanisme monitoring analis melalui Telegram. Agent Swarm beroperasi secara otonom untuk triase ancaman dan pembuatan aturan IDS dinamis, sementara analis berperan sebagai supervisor yang mengintervensi pada kondisi anomali. Adaptive Feedback Loop memungkinkan koreksi berkelanjutan untuk mencegah concept drift dan meningkatkan akurasi klasifikasi. Efektivitas dievaluasi melalui Accuracy, MTTR, False Positive Rate, dan F1-Score, serta User Acceptance Testing dengan System Usability Scale terhadap 15–20 responden praktisi keamanan.

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

Penelitian ini bertujuan untuk merancang, mengimplementasikan, dan mengevaluasi arsitektur Cognitive SOC berbasis paradigma Human-On-The-Loop guna mengatasi tantangan operasional yang telah diidentifikasi. Tujuan spesifik dari penelitian ini adalah:

- **Membangun Artefak Cognitive SOC:** Mengembangkan prototipe sistem orkestrasi keamanan berbasis paradigma HOTL menggunakan platform low-code (n8n) yang terintegrasi dengan Cyfirma TIP, subsistem Machine Learning (Random Forest), Wazuh (SIEM), dan Telegram (dasbor monitoring HOTL).
- **Mengimplementasikan Hybrid Autonomous AI Agent:** Merancang dan mengimplementasikan Agent Swarm yang mampu melakukan triase ancaman secara otonom dan menghasilkan aturan Intrusion Detection System (IDS) secara dinamis berdasarkan IOC yang diklasifikasikan oleh model Machine Learning.
- **Mengimplementasikan Adaptive Feedback Loop:** Membangun mekanisme umpan balik adaptif yang memungkinkan koreksi analis SOC memperbarui model Random Forest secara berkelanjutan untuk mencegah concept drift.
- **Evaluasi Efektivitas Sistem:** Mengukur secara empiris peningkatan efektivitas operasional melalui empat variabel utama: Accuracy, Mean Time to Respond (MTTR), False Positive Rate (FPR), dan F1-Score, dibandingkan dengan baseline proses manual.
- **Evaluasi Penerimaan Pengguna:** Mengevaluasi tingkat keberterimaan sistem melalui metodologi User Acceptance Testing (UAT) dengan instrumen System Usability Scale (SUS) terhadap 15–20 responden yang dipilih secara purposive dari kalangan praktisi keamanan siber.

Dengan mencapai tujuan-tujuan ini, penelitian ini akan mendemonstrasikan pendekatan arsitektural Cognitive SOC yang layak, terukur, dan dapat diterima pengguna dalam lingkungan SOC dengan sumber daya terbatas.

## D. Manfaat Penelitian

- **Manfaat Teoritis**

Penelitian ini diharapkan dapat memberikan kontribusi pada pengembangan literatur keamanan siber, khususnya dalam domain Security Operations Center (SOC) dan orkestrasi pertahanan, melalui tiga aspek utama:

- 1. **Memperkuat kerangka kerja paradigma Human-On-The-Loop (HOTL) dalam operasi SOC.** Penelitian ini berkontribusi dalam memvalidasi secara empiris transisi dari paradigma Human-In-The-Loop (HITL) menuju HOTL pada konteks SOC berbasis AI. Berbeda dengan HITL yang mengharuskan manusia untuk memvalidasi setiap keputusan, HOTL menempatkan manusia sebagai supervisor yang mengintervensi hanya pada kondisi anomali tertentu. Kontribusi ini memperkaya literatur Human-Machine Teaming dalam domain keamanan siber, khususnya mengenai derajat otonomi optimal yang dapat diberikan kepada sistem AI tanpa mengorbankan ketelitian dan akuntabilitas keputusan.
   - **Memperkenalkan kerangka arsitektur Hybrid Autonomous AI Agent dengan Adaptive Feedback Loop untuk SOC.** Sepengetahuan penulis, belum terdapat studi yang secara komprehensif mengintegrasikan Agent Swarm dengan kemampuan triase otonom, pembuatan aturan IDS dinamis, dan Adaptive Feedback Loop untuk mitigasi concept drift dalam satu kerangka orkestrasi low-code yang reproducible. Kontribusi ini mengisi kesenjangan dalam literatur tentang implementasi agentic AI dalam operasi keamanan nyata.
   - **Memperkaya metrik evaluasi sistem SOC otonom.** Penelitian ini tidak hanya mengevaluasi MTTR sebagai metrik tunggal, melainkan mengintegrasikan suite metrik komprehensif (Accuracy, MTTR, FPR, F1-Score) dengan evaluasi penerimaan pengguna melalui UAT/SUS. Pendekatan evaluasi multi-dimensi ini memberikan landasan metodologis bagi penelitian Cognitive SOC di masa mendatang.

- **Manfaat Praktis**

Hasil penelitian diharapkan dapat memberikan dampak operasional langsung yang dapat diterapkan oleh praktisi keamanan siber dan organisasi berbagai skala dalam aspek:

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
- **Lingkungan:** Eksperimen dilakukan dalam lingkungan laboratorium terkontrol (_virtual environment_) yang mensimulasikan infrastruktur SOC perusahaan menengah, bukan pada jaringan produksi aktif.

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

---

## F. Kerangka Konseptual: Arsitektur dan Ruang Lingkup AI

### Pergeseran Paradigma dari HITL ke HOTL

Paradigma Human-In-The-Loop (HITL) tradisional menempatkan manusia sebagai gatekeeper wajib dalam setiap keputusan sistem otomatis. Dalam konteks SOC, hal ini berarti setiap IOC yang terdeteksi harus terlebih dahulu divalidasi oleh analis sebelum tindakan defensif dapat dieksekusi. Meskipun pendekatan ini menjamin akuntabilitas, ia menciptakan bottleneck yang bertentangan dengan kebutuhan respons real-time terhadap ancaman modern yang berkecepatan tinggi \[8\].

Arsitektur Cognitive SOC yang diusulkan dalam penelitian ini mengadopsi paradigma Human-On-The-Loop (HOTL), yang secara fundamental mengubah peran manusia dari validator aktif menjadi supervisor strategis. Dalam paradigma HOTL, sistem AI beroperasi secara otonom untuk menangani siklus penuh dari intelijen ancaman hingga respons defensif, sementara analis SOC difokuskan pada pemantauan supervisori dan intervensi selektif hanya ketika sistem menandai anomali atau kondisi yang melampaui batas otorisasi AI \[4\], \[8\].

Transisi ini didukung oleh mekanisme confidence-based routing: IOC dengan confidence score tinggi (di atas threshold yang dikalibrasi) diproses sepenuhnya oleh Agent Swarm tanpa intervensi manusia, sedangkan kasus dengan confidence rendah atau yang melibatkan infrastruktur kritis secara otomatis di-eskalasi ke analis untuk tinjauan \[8\].

### Konsep Hybrid Autonomous AI Agent

Arsitektur Hybrid Autonomous AI Agent yang diusulkan terdiri dari Agent Swarm—kumpulan agen berkoordinasi yang masing-masing memiliki spesialisasi fungsi dalam pipeline threat intelligence. Secara operasional, Agent Swarm menjalankan empat tahap utama secara otonom: (1) **Acquisition Agent** mengakuisisi dan menormalisasi IOC dari Cyfirma TIP melalui REST API; (2) **Classification Agent** menjalankan model Random Forest untuk mengklasifikasikan tingkat ancaman setiap IOC berdasarkan fitur yang diekstraksi; (3) **Triage Agent** menentukan tindakan respons berdasarkan confidence score dan kategori ancaman; serta (4) **Enforcement Agent** mengeksekusi pembuatan aturan IDS dinamis pada Wazuh SIEM secara otomatis. Arsitektur hibrida ini menggabungkan ketelitian deterministik dari aturan berbasis heuristik dengan adaptabilitas model Machine Learning, memungkinkan respons yang presisi dan dapat diprediksi \[1\], \[4\].

### Adaptive Feedback Loop dan Pencegahan Concept Drift

Adaptive Feedback Loop merupakan komponen kritis yang membedakan Cognitive SOC dari sistem SOAR konvensional. Mekanisme ini beroperasi sebagai berikut: ketika analis SOC mengidentifikasi kesalahan klasifikasi (false positive atau false negative) melalui dasbor monitoring Telegram, koreksi tersebut secara otomatis dikirim sebagai sinyal umpan balik ke subsistem Machine Learning. Sistem kemudian mengakumulasi koreksi ke dalam buffer feedback (Persamaan 9) dan melakukan *full retrain* pada *augmented dataset* (Persamaan 11) ketika ambang minimum tercapai, memperbarui seluruh ensemble Random Forest untuk mencerminkan distribusi data terkini \[1\].

Mekanisme ini secara langsung mengatasi masalah concept drift—fenomena di mana model yang dilatih pada data historis secara bertahap kehilangan akurasi seiring evolusi pola ancaman. Dengan mengintegrasikan sinyal koreksi dari analis sebagai ground truth tambahan, model dapat beradaptasi secara berkelanjutan terhadap perubahan taktik, teknik, dan prosedur (TTPs) threat actor tanpa intervensi manual yang ekstensif \[1\], \[4\].

# III. Metodologi

## Kerangka Penelitian

Penelitian ini mengadopsi pendekatan **Constructive Research**, yakni membangun artefak teknologi berupa sistem Cognitive SOC Architecture dan mengevaluasi kinerjanya secara empiris. Pendekatan ini mencakup dua dimensi evaluasi utama:

1. **Efektivitas Sistem (Kuantitatif):** Mengukur dampak otomatisasi berbasis AI terhadap kecepatan, akurasi, dan efisiensi respons insiden menggunakan metrik baku industri keamanan siber.
2. **Penerimaan Pengguna (Kualitatif-Kuantitatif):** Mengukur tingkat usabilitas antarmuka Human-On-The-Loop (HOTL) dari perspektif analis SOC melalui metode User Acceptance Testing (UAT) berbasis kuesioner System Usability Scale (SUS).

Evaluasi efektivitas sistem dilakukan dalam skema perbandingan sekuensial (*sequential comparison*), di mana fase baseline (manual) dijalankan terlebih dahulu selama 7 hari, diikuti oleh fase eksperimental (otomatis) selama 7 hari berikutnya. Desain sekuensial ini dipilih karena keterbatasan sumber daya yang tidak memungkinkan pengoperasian paralel dua tim analis secara bersamaan. Untuk memitigasi confounding variables akibat perubahan threat landscape antar periode, volume IOC per hari dicatat dan dilaporkan untuk kedua kondisi, dan analisis statistik memperhitungkan variasi volume sebagai kovariat.

## Arsitektur Sistem dan Lingkungan Eksperimen

Eksperimen dilakukan dalam lingkungan laboratorium yang mensimulasikan infrastruktur SOC perusahaan menengah di Indonesia. Penggunaan teknologi virtualisasi (*Virtual Machine*) memastikan reprodusibilitas dan isolasi eksperimen.

### Komponen Sistem

Sistem Cognitive SOC Architecture yang dibangun terdiri dari komponen-komponen berikut:

**TABEL I: Komponen Arsitektur Cognitive SOC**

| No. | Komponen | Teknologi | Fungsi |
|-----|----------|-----------|--------|
| 1 | **Sumber Threat Intelligence (TIP)** | Cyfirma API | Menyediakan feed data IOC (IP, Domain, File Hash) secara *real-time* melalui REST API terautentikasi. |
| 2 | **Mesin Orkestrasi (Orchestrator)** | n8n (Self-Hosted, Docker) | Hub pusat untuk manajemen alur kerja, penjadwalan, dan integrasi API seluruh komponen. |
| 3 | **Modul ML Klasifikasi Ancaman** | Python / scikit-learn (Random Forest) | Memproses dan mengklasifikasikan IOC berdasarkan fitur kontekstual; menghasilkan skor risiko dan label kategori ancaman. |
| 4 | **Sistem Deteksi & Log (SIEM)** | Wazuh Manager (Host Windows 11) | Penyimpanan log insiden, korelasi data (*enrichment*), dan manajemen aturan IDS. |
| 5 | **Target Endpoint** | VM Linux Ubuntu 22.04 LTS + Wazuh Agent | Mensimulasikan endpoint yang dipantau dalam jaringan SOC. |
| 6 | **Antarmuka HOTL (Alerting & Feedback)** | Telegram Bot API | Kanal notifikasi *push* kepada analis manusia; mendukung format HTML dan tombol interaktif untuk tindakan validasi dan koreksi (*feedback loop*). |

### Topologi Data Flow

Alur data sistem (ilustrasi direkomendasikan sebagai **Gambar 1** untuk versi final IEEE) berjalan melalui lima tahap sekuensial dan satu jalur umpan balik:

1. **Tahap Akuisisi:** Cyfirma TIP → n8n Orchestrator (REST API polling terjadwal)
2. **Tahap Fusi & Normalisasi:** n8n Orchestrator → Modul Fusi Data (transformasi IOC ke representasi terstandarisasi, lihat §Modul Fusi Data Multi-Sumber)
3. **Tahap Analisis:** Modul Fusi Data → Python ML Agent (klasifikasi Random Forest + confidence scoring)
4. **Tahap Tindakan (fork paralel):**
   - **Jalur A — Autonomous Triage Agent:** Klasifikasi, enrichment, dan routing keputusan berdasarkan fungsi keputusan $\mathcal{D}$ (Persamaan 5)
   - **Jalur B — IDS Rule Generation Agent:** Sintesis dan deployment aturan Wazuh secara otomatis untuk IOC `High`/`Critical`
5. **Tahap Notifikasi:** Hasil kedua jalur → Telegram Bot (HOTL Interface) → Analis SOC
6. **Jalur Umpan Balik:** Koreksi analis SOC → Adaptive Feedback Loop → Model ML (retraining, lihat §Adaptive Feedback Loop)

> *Catatan: Diagram arsitektur lengkap disajikan sebagai Gambar 1 (format vektor) pada versi final dokumen. Gambar 2 menyajikan diagram transisi state untuk Adaptive Feedback Loop.*

### Modul Fusi Data Multi-Sumber (*Multi-Source Log Fusion Module*)

Mengadopsi prinsip arsitektur Layer 1 dari Zhang et al. \[1\], modul ini mentransformasi telemetri heterogen menjadi representasi terstruktur yang siap diproses oleh subsistem klasifikasi ML. Meskipun implementasi saat ini menggunakan sumber tunggal (Cyfirma TIP), arsitektur dirancang secara extensible untuk mendukung fusi multi-sumber di masa mendatang.

**Definisi 1 (Ruang Telemetri).** Misalkan himpunan sumber data $S = \{s_{\text{TIP}}, s_{\text{SIEM}}, s_{\text{endpoint}}\}$ masing-masing menghasilkan aliran event $E_s = \{e_1, e_2, \ldots, e_n\}$ dengan skema heterogen.

Transformasi normalisasi $\mathcal{T}_{\text{norm}}$ memetakan setiap event mentah ke representasi bundle terstandarisasi:

$$B_i = \mathcal{T}_{\text{norm}}(e_i) = \langle \text{id}_i, \tau_i, \mathbf{f}_i, \text{rel}_i, \text{meta}_i \rangle \tag{1}$$

di mana:
- $\text{id}_i$: identifier unik IOC
- $\tau_i \in \mathbb{R}^+$: timestamp normalisasi (epoch seconds)
- $\mathbf{f}_i \in \mathbb{R}^d$: vektor fitur kontekstual ($d = 15$ setelah encoding, lihat TABEL II)
- $\text{rel}_i$: himpunan relasi kontekstual (e.g., *associated-with*, *indicates*)
- $\text{meta}_i$: metadata provenance (sumber, tanggal akuisisi, confidence awal)

Agregasi multi-sumber dilakukan melalui operator fusi temporal:

$$\mathcal{F}_{\text{fuse}}(B_1, B_2, \ldots, B_k) = \text{DEDUP}\left(\bigcup_{j=1}^{k} B_j \;\middle|\; \|\tau_{B_a} - \tau_{B_b}\| < \delta_t \wedge \text{sim}(\mathbf{f}_a, \mathbf{f}_b) > \theta_{\text{sim}}\right) \tag{2}$$

di mana $\delta_t$ adalah jendela temporal deduplikasi (default: $\delta_t = 3600$ detik = 1 jam) dan $\theta_{\text{sim}}$ adalah ambang kesamaan kosinus untuk identifikasi IOC duplikat lintas sumber (default: $\theta_{\text{sim}} = 0.95$). Nilai default ini ditetapkan berdasarkan praktik umum deduplikasi IOC dalam operasi TIP. Pada implementasi sumber tunggal saat ini, operator $\mathcal{F}_{\text{fuse}}$ beroperasi sebagai fungsi identitas dengan deduplikasi intra-sumber.

**Catatan Arsitektural:** Zhang et al. \[1\] mengimplementasikan Layer 1 menggunakan format STIX (Structured Threat Information Expression) dan protokol TAXII untuk pertukaran data standar antar komponen keamanan \[11\]. Penelitian ini mengadopsi prinsip normalisasi dan deduplikasi yang sama meskipun menggunakan format JSON internal melalui n8n, dengan pertimbangan bahwa integrasi STIX/TAXII penuh memerlukan infrastruktur yang berada di luar cakupan pembuktian konsep ini. Perluasan ke format STIX/TAXII merupakan pekerjaan mendatang yang direkomendasikan (lihat §Keterbatasan dan Pekerjaan Mendatang).

## Implementasi Hybrid Autonomous AI Agent (Agent Swarm)

Inti dari sistem ini adalah arsitektur **Hybrid Autonomous AI Agent** yang beroperasi dalam dua peran otonom yang saling melengkapi, dikoordinasikan melalui n8n:

### Autonomous Triage Agent

Agent pertama bertanggung jawab atas triase ancaman secara mandiri (*autonomous triage*):

1. **Polling & Normalisasi Data:** Secara periodik melakukan *polling* ke Cyfirma TIP API dan menormalisasi data IOC ke format yang seragam.
2. **Sumber dan Deskripsi Dataset Pelatihan:** Model Random Forest dilatih menggunakan dataset IOC berlabel yang dikonstruksi dari dua sumber:
   - **(a) Data historis Cyfirma TIP:** 4.200 sampel IOC berlabel yang dikumpulkan selama 3 bulan sebelum eksperimen. Label kelas diberikan berdasarkan severity rating Cyfirma yang dimapping ke taksonomi empat kelas.
   - **(b) Dataset CTU-13 (Skenario 1, 2, 9):** 800 sampel tambahan diekstraksi dari dataset flows CTU-13 \[15\]. Karena CTU-13 merupakan dataset network flow (bukan IOC), transformasi dilakukan melalui agregasi flow-level features (IP tujuan, port, durasi koneksi, bytes transferred) ke IOC-level features sesuai skema TABEL II. Tiga skenario dipilih karena mencakup variasi botnet (Neris, Rbot, Murlo) yang menghasilkan pola IOC berbeda.
   - **Total dataset:** 5.000 sampel (4.200 + 800). Distribusi kelas: `Low` 2.250 (45%), `Medium` 1.500 (30%), `High` 900 (18%), `Critical` 350 (7%). Untuk mengatasi class imbalance, digunakan parameter `class_weight='balanced'` pada scikit-learn RandomForestClassifier, yang secara otomatis menyesuaikan bobot setiap kelas berbanding terbalik dengan frekuensinya. Dataset dibagi 80:20 (4.000 training : 1.000 validasi) menggunakan stratified split untuk mempertahankan proporsi kelas.

   **Protokol Pelabelan Ground Truth.** Label kelas ancaman diperoleh melalui fungsi pemetaan deterministik $\mathcal{L}: [0, 100] \rightarrow \mathcal{C}$ yang mentransformasi skor severity Cyfirma (skala 0–100) ke taksonomi empat kelas:

   $$\mathcal{L}(s) = \begin{cases} \text{Low} & \text{jika } 0 \leq s \leq 25 \\ \text{Medium} & \text{jika } 25 < s \leq 55 \\ \text{High} & \text{jika } 55 < s \leq 80 \\ \text{Critical} & \text{jika } s > 80 \end{cases}$$

   Batas-batas interval (25, 55, 80) diturunkan dari analisis distribusi kuartil pada 4.200 sampel historis Cyfirma dan divalidasi melalui konsultasi dengan satu analis SOC senior (pengalaman >5 tahun). Distribusi non-equidistant ini mencerminkan proporsi empiris ancaman di mana mayoritas IOC bersifat Low/Medium, konsisten dengan distribusi skewed yang umum diamati dalam operasi SOC \[19\].

   **Prosedur Imputasi Fitur CTU-13.** Karena dataset CTU-13 \[15\] merupakan dataset network flow yang tidak mengandung fitur IOC-level secara native, prosedur transformasi berikut diterapkan: (a) alamat IP tujuan dari flow diekstraksi sebagai IOC; (b) fitur `tip_reputation_score` diimputasi menggunakan lookup terhadap basis data reputasi VirusTotal yang diarsipkan pada periode dataset (2011–2013), dengan nilai default 0.5 untuk IP yang tidak ditemukan; (c) `geolocation_risk` diperoleh melalui GeoIP lookup pada ASN registry; (d) `asn_reputation` dihitung berdasarkan proporsi flow malicious per ASN dalam dataset CTU-13 itu sendiri; (e) `feed_frequency`, `first_seen_age_days`, `source_diversity_count`, dan `active_days_count` diimputasi dari agregasi statistik flow-level (jumlah koneksi, durasi aktif, jumlah sumber unik). Label kelas untuk sampel CTU-13 ditetapkan berdasarkan ground truth skenario: flow yang ditandai *Botnet* diklasifikasikan sebagai `High` atau `Critical` (berdasarkan volume dan durasi), sedangkan flow *Normal* dan *Background* diklasifikasikan sebagai `Low`.

   **Keterbatasan Pelabelan:** Seluruh pelabelan dilakukan oleh satu orang labeler (penulis), sehingga inter-rater reliability (e.g., Cohen's κ) tidak dapat dilaporkan. Keterbatasan ini diakui secara eksplisit dan dimitigasi melalui: (1) penggunaan fungsi pemetaan deterministik $\mathcal{L}$ yang mengeliminasi subjektivitas pada data Cyfirma, dan (2) penggunaan ground truth bawaan CTU-13 untuk sampel network flow. Namun, keputusan transformasi fitur dan batas kelas tetap bergantung pada penilaian tunggal, yang merupakan single point of failure untuk validitas label.

3. **Feature Engineering:** Mengekstraksi fitur kontekstual dari setiap IOC. Vektor fitur terdiri dari 9 dimensi sebagai berikut:

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

   Total dimensi setelah encoding: 15 fitur (3 kolom one-hot `indicator_type` + 5 kolom one-hot `threat_category` + 7 fitur skalar = 15). Seluruh fitur numerik dinormalisasi ke rentang [0,1] untuk memastikan kontribusi seimbang pada model Random Forest. Fitur `active_days_count` mengukur jumlah hari unik di mana IOC tertentu dilaporkan aktif oleh berbagai feed, memberikan informasi tambahan tentang persistensi ancaman.

4. **Klasifikasi Ancaman — Formulasi Matematis:**

   Model Random Forest $\mathcal{M}_{RF}$ terdiri dari ensemble $T$ decision trees $\{h_1, h_2, \ldots, h_T\}$ yang menghasilkan prediksi melalui majority voting:

   $$\hat{y}_i = \arg\max_{c \in \mathcal{C}} \sum_{t=1}^{T} \mathbb{1}[h_t(\mathbf{f}_i) = c] \tag{3}$$

   di mana $\mathcal{C} = \{\text{Critical, High, Medium, Low}\}$ adalah himpunan kelas ancaman dan $\mathbf{f}_i \in \mathbb{R}^{15}$ adalah vektor fitur ter-encoding dari IOC ke-$i$ (lihat TABEL II).

   Confidence score dihitung sebagai probabilitas posterior kelas terpilih berdasarkan proporsi voting ensemble:

   $$\text{conf}(\mathbf{f}_i) = \frac{1}{T} \sum_{t=1}^{T} \mathbb{1}[h_t(\mathbf{f}_i) = \hat{y}_i] \tag{4}$$

   **Catatan Arsitektural terhadap AIR Layer 2:** Zhang et al. \[1\] menggunakan Attention-enhanced LSTM untuk menangkap dependensi temporal antar event keamanan dan membedakan pola periodik legitimate dari ancaman yang berevolusi. Penelitian ini memilih Random Forest berdasarkan tiga pertimbangan: (a) transparansi keputusan yang lebih tinggi untuk konteks HOTL di mana analis perlu memahami alasan klasifikasi \[8\], (b) efisiensi komputasi pada platform low-code yang membatasi kompleksitas model, dan (c) ketahanan terhadap overfitting pada dataset berukuran sedang (~5.000 sampel) \[23\], \[24\]. Keterbatasan utama adalah ketidakmampuan menangkap pola sekuensial multi-stage attack, yang dibahas dalam §Keterbatasan dan Pekerjaan Mendatang.

5. **Kebijakan Respons Otonom — Formulasi Fungsi Keputusan:**

   Fungsi keputusan $\mathcal{D}$ memetakan setiap IOC terklasifikasi ke tindakan respons $a \in \mathcal{A} = \{\text{autonomous\_block}, \text{escalate\_HOTL}, \text{log\_review}\}$:

   $$\mathcal{D}(\hat{y}_i, \text{conf}_i) = \begin{cases} \text{autonomous\_block} & \text{if } \hat{y}_i \in \{C, H\} \wedge \text{conf}_i > \theta_{\text{high}} \\ \text{escalate\_HOTL} & \text{if } \theta_{\text{low}} \leq \text{conf}_i \leq \theta_{\text{high}} \\ \text{escalate\_HOTL} & \text{if } \hat{y}_i = C \wedge \text{conf}_i < \theta_{\text{low}} \quad \text{(safety override)} \\ \text{log\_review} & \text{if } \text{conf}_i < \theta_{\text{low}} \wedge \hat{y}_i \notin \{C\} \end{cases} \tag{5}$$

   di mana $\theta_{\text{high}} = 0.85$ dan $\theta_{\text{low}} = 0.60$ merupakan parameter yang dikalibrasi melalui analisis ROC curve dan precision-recall curve pada dataset validasi. **Safety Override:** IOC yang diklasifikasikan sebagai `Critical` dengan confidence rendah ($\text{conf}_i < \theta_{\text{low}}$) secara desain tidak pernah masuk ke jalur `log_review`, melainkan selalu di-eskalasi ke analis (HOTL) untuk mencegah risiko operasional di mana ancaman kritis terlewatkan akibat ketidakpastian model. Kondisi batas $\text{conf}_i = \theta_{\text{high}}$ secara eksplisit dipetakan ke `escalate_HOTL` (bukan `autonomous_block`) sebagai kebijakan konservatif.

   **Justifikasi Threshold:** Nilai threshold $\theta_{\text{high}} = 0.85$ dan $\theta_{\text{low}} = 0.60$ ditetapkan sebagai konfigurasi awal berdasarkan praktik umum dalam sistem klasifikasi keamanan. Selama fase eksperimen, threshold ini akan dikalibrasi untuk menentukan titik operasi optimal yang meminimalkan false positive pada tier otonom sambil memaksimalkan recall pada tier eskalasi. Analisis sensitivitas threshold akan dilaporkan untuk menunjukkan dampak variasi $\pm 0.05$ pada metrik FPR dan F1-Score.

   **Catatan Arsitektural terhadap AIR Layer 3:** Kebijakan $\mathcal{D}$ (Persamaan 5) merupakan simplifikasi deterministik dari Bayesian Game-Theoretic Decision Layer pada Zhang et al. \[1\], yang memodelkan interaksi defender-attacker sebagai permainan Bayesian dan mencapai Nash equilibrium dalam 97.3% skenario adversarial. Penyederhanaan ini dipilih karena ketiadaan data interaksi adversarial real-time di lingkungan eksperimen laboratorium, namun kerangka $\mathcal{D}$ dirancang agar dapat diperluas menjadi *game-theoretic policy* di pekerjaan mendatang (lihat §Posisi Arsitektural terhadap Bayesian Game-Theoretic Decision Layer).

### IDS Rule Generation Agent

Agent kedua berfokus pada pembuatan aturan deteksi secara dinamis:

1. **Input:** Menerima IOC yang telah diklasifikasikan sebagai `High` atau `Critical` dari Triage Agent.
2. **Pembuatan Aturan Wazuh:** Secara otomatis menyintesis aturan deteksi Wazuh (format XML) yang disesuaikan dengan karakteristik IOC, termasuk:
   - Aturan deteksi untuk koneksi ke IP berbahaya
   - Aturan untuk permintaan DNS ke domain yang teridentifikasi
   - Aturan untuk mendeteksi eksekusi *file hash* yang di-*blacklist*
3. **Penerapan Aturan:** Mendeploy aturan baru ke Wazuh Manager secara otomatis melalui API, tanpa restart manual layanan.
4. **Eskalasi HOTL:** Mengirimkan notifikasi ke analis via Telegram berisi ringkasan aturan yang diterapkan, dengan opsi untuk merevisi atau membatalkan aturan.

### Posisi Arsitektural terhadap Bayesian Game-Theoretic Decision Layer

Zhang et al. \[1\] memodelkan keputusan respons sebagai permainan Bayesian antara defender dan attacker, di mana tipe attacker $\theta_a$ diperbarui secara online berdasarkan observasi:

$$P(\theta_a | O_{1:t}) \propto P(O_t | \theta_a) \cdot P(\theta_a | O_{1:t-1}) \tag{6}$$

dan strategi defender optimal $\sigma^*_d$ diperoleh melalui:

$$\sigma^*_d = \arg\max_{\sigma_d} \mathbb{E}_{\theta_a \sim P(\theta_a | O_{1:t})} [u_d(\sigma_d, \sigma_a^*(\theta_a))] \tag{7}$$

di mana $u_d$ adalah fungsi utilitas defender, $\sigma_a^*(\theta_a)$ adalah strategi optimal attacker tipe $\theta_a$, dan $O_{1:t}$ adalah sekuens observasi hingga waktu $t$.

Penelitian ini **tidak mengimplementasikan** framework game-theoretic secara penuh. Kebijakan keputusan $\mathcal{D}$ (Persamaan 5) merupakan approximasi deterministik dari $\sigma^*_d$ untuk kasus spesial di mana distribusi posterior attacker-type diasumsikan seragam dan statis. Penyederhanaan ini merupakan keterbatasan yang diakui secara eksplisit, dengan dua justifikasi: (1) lingkungan eksperimen laboratorium tidak menyediakan data interaksi adversarial real-time yang diperlukan untuk memperbarui $P(\theta_a | O_{1:t})$, dan (2) kompleksitas komputasi model Bayesian game-theoretic melebihi kapasitas platform orkestrasi low-code (n8n) yang menjadi basis implementasi. Integrasi Bayesian updating pada posterior tipe ancaman berdasarkan feedback analis dan pola temporal IOC merupakan arah utama pekerjaan mendatang.

## Adaptive Feedback Loop

Komponen kritis untuk mempertahankan akurasi model dalam jangka panjang adalah **Adaptive Feedback Loop**. Mekanisme ini mengintegrasikan koreksi dari analis manusia sebagai sumber *ground truth* tambahan dan diformulasikan sebagai proses pembaruan model berkelanjutan.

**Definisi 2 (Buffer Feedback).** Misalkan $\mathcal{B}_t$ menyatakan buffer feedback pada waktu $t$, berisi pasangan IOC terkoreksi dan label ground truth yang diberikan oleh analis:

$$\mathcal{B}_t = \{(\mathbf{f}_j, y_j^{\text{corrected}}) \mid j \in \text{corrections sejak } t_{\text{last\_retrain}}\} \tag{9}$$

Proses feedback loop beroperasi melalui lima tahap:

1. **Koleksi Feedback:** Setiap respons analis via Telegram (validasi, koreksi label, atau penolakan prediksi) dicatat secara terstruktur oleh n8n ke dalam buffer $\mathcal{B}_t$.

2. **Kondisi Trigger Retraining:** Retraining dipicu ketika buffer mencapai ambang minimum:

   $$|\mathcal{B}_t| \geq n_{\text{min}} \quad \text{di mana } n_{\text{min}} = 50 \tag{10}$$

   **Estimasi Kelayakan Retraining.** Nilai $n_{\text{min}} = 50$ ditetapkan berdasarkan estimasi berikut: dengan volume harian ~50–100 IOC dan asumsi konservatif bahwa 8–12% IOC memerlukan koreksi analis (berdasarkan FPR tipikal model Random Forest pada dataset serupa \[23\], \[24\]), maka diharapkan ~4–12 koreksi per hari. Dengan demikian, ambang 50 koreksi dapat tercapai dalam ~4–12 hari kerja—mendekati batas akhir jendela eksperimen 14 hari. Untuk memastikan Ablation A (tanpa feedback loop) tetap dapat diukur, retraining juga dijadwalkan secara periodik (mingguan) sebagai *safeguard* terhadap concept drift gradual. Jika buffer tidak mencapai $n_{\text{min}}$ dalam jendela eksperimen, hal ini akan dilaporkan secara transparan dan analisis ablasi akan menggunakan perbandingan model awal vs. model akhir eksperimen sebagai proxy. Analisis sensitivitas terhadap variasi $n_{\text{min}} \in \{30, 50, 75, 100\}$ akan dilaporkan untuk menunjukkan dampak threshold terhadap frekuensi retraining dan stabilitas model.

3. **Augmented Dataset Strategy:** Model Random Forest dilatih ulang (*full retrain*) menggunakan gabungan dataset historis dan data feedback terbaru:

   $$\mathcal{T}_{\text{retrain}} = \mathcal{T}_{\text{historical}} \cup \mathcal{B}_t \tag{11}$$

   di mana $\mathcal{T}$ (berbeda dari fungsi keputusan $\mathcal{D}$ pada Persamaan 5) menyatakan himpunan data pelatihan. Dataset historis $\mathcal{T}_{\text{historical}}$ selalu diikutsertakan dalam setiap siklus pelatihan ulang untuk mencegah *catastrophic forgetting*. Strategi ini menggunakan `warm_start=False` (full retrain) pada scikit-learn `RandomForestClassifier`, yang membangun ensemble baru dari keseluruhan $\mathcal{T}_{\text{retrain}}$ untuk memastikan bahwa seluruh estimator dalam ensemble mencerminkan distribusi data terkini.

4. **Validasi & Deployment dengan Uji Signifikansi:** Model baru dievaluasi pada dataset validasi yang disisihkan (*holdout set*). Misalkan $F1_{\text{old}}^{(k)}$ dan $F1_{\text{new}}^{(k)}$ adalah F1-Score model lama dan baru pada fold $k$ dari $K$-fold cross-validation. Deployment dilakukan hanya jika:

   $$H_0: \text{median}(F1_{\text{new}}^{(k)} - F1_{\text{old}}^{(k)}) = 0 \quad \text{ditolak pada } \alpha = 0.05 \tag{12}$$

   menggunakan Wilcoxon signed-rank test. Ini memastikan bahwa perbaikan bukan disebabkan oleh variasi acak.

5. **Logging Versi:** Setiap versi model dicatat dengan metadata (tanggal retraining, jumlah sampel baru, perubahan metrik, hasil uji signifikansi) untuk keperluan audit dan reprodusibilitas.

**Deteksi Concept Drift Proaktif.** Untuk memantau concept drift secara proaktif tanpa menunggu koreksi analis, Page-Hinkley test \[16\] diterapkan pada aliran confidence score:

$$\text{PH}_t = \sum_{i=1}^{t}(\text{conf}_i - \bar{\text{conf}}_t - \delta) \tag{13}$$

di mana $\bar{\text{conf}}_t$ adalah rata-rata *running* confidence score, dan $\delta$ adalah toleransi magnitude perubahan (default: $\delta = 0.005$). Alarm drift dipicu jika $\text{PH}_t - \min_{1 \leq j \leq t} \text{PH}_j > \lambda$, di mana $\lambda$ adalah ambang sensitivitas (default: $\lambda = 50$). Nilai default $\delta$ dan $\lambda$ diadopsi dari rekomendasi Jemili et al. \[16\] untuk konteks deteksi intrusi dan akan dikalibrasi pada data validasi. Ketika alarm drift aktif, retraining dipercepat meskipun $|\mathcal{B}_t| < n_{\text{min}}$.

Mekanisme ini secara langsung mengatasi masalah *concept drift* — fenomena di mana model yang dilatih pada data historis secara bertahap kehilangan akurasi seiring evolusi pola ancaman \[16\], \[29\]. Dengan mengintegrasikan sinyal koreksi dari analis sebagai *ground truth* tambahan dan deteksi drift proaktif, model dapat beradaptasi secara berkelanjutan terhadap perubahan TTPs *threat actor* tanpa intervensi manual yang ekstensif \[16\].

## Metrik Evaluasi Efektivitas Sistem

Efektivitas sistem diukur menggunakan empat metrik kuantitatif baku:

### Accuracy

$$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN} \tag{14}$$

Di mana:
- **TP (True Positive):** Ancaman nyata yang berhasil terklasifikasi dengan benar.
- **TN (True Negative):** Traffic/IOC benign yang benar-benar diidentifikasi sebagai tidak berbahaya.
- **FP (False Positive):** IOC benign yang salah diklasifikasikan sebagai ancaman.
- **FN (False Negative):** Ancaman nyata yang gagal terdeteksi.

Accuracy mengukur proporsi prediksi yang benar secara keseluruhan.

### Mean Time to Respond (MTTR)

$$\text{MTTR} = \frac{1}{N} \sum_{i=1}^{N} (t_{\text{resolved},i} - t_{\text{detected},i}) \tag{15}$$

Di mana $N$ adalah total jumlah insiden yang diukur dalam periode evaluasi, $t_{\text{detected},i}$ adalah *timestamp* deteksi insiden ke-$i$, dan $t_{\text{resolved},i}$ adalah *timestamp* penyelesaian (respons tindakan diambil). MTTR mengukur rata-rata waktu yang dibutuhkan sistem dari deteksi ancaman hingga pengambilan tindakan respons.

### False Positive Rate (FPR)

$$\text{FPR} = \frac{FP}{FP + TN} \tag{16}$$

FPR mengukur proporsi IOC atau traffic yang *benign* namun salah diidentifikasi sebagai ancaman. Tingginya FPR menyebabkan *alert fatigue* pada analis SOC \[19\], \[21\], yang merupakan salah satu masalah utama yang ingin diselesaikan penelitian ini.

### F1-Score

$$\text{F1-Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}} \tag{17}$$

Di mana:

$$\text{Precision} = \frac{TP}{TP + FP}, \quad \text{Recall} = \frac{TP}{TP + FN} \tag{18}$$

F1-Score adalah rata-rata harmonik antara Precision dan Recall, memberikan ukuran keseimbangan antara kemampuan deteksi positif yang benar dan minimisasi *false alarm*.

### Pelaporan Metrik Per-Kelas

Mengingat distribusi kelas yang tidak seimbang (Critical = 7%), pelaporan agregat saja dapat menyembunyikan performa buruk pada kelas yang secara operasional paling penting. Oleh karena itu, selain metrik agregat, evaluasi akan melaporkan:
- **Precision, Recall, dan F1-Score per kelas** untuk keempat kelas ancaman (Low, Medium, High, Critical)
- **Confusion matrix** 4×4 untuk visualisasi pola kesalahan klasifikasi
- **Macro-averaged F1** (rata-rata aritmetika F1 per kelas, memberikan bobot setara pada setiap kelas) dan **weighted F1** (berbobot frekuensi kelas) untuk memberikan gambaran komprehensif tentang performa model pada kelas minoritas maupun mayoritas

## Metodologi User Acceptance Testing (UAT)

Selain evaluasi kuantitatif sistem, penelitian ini mengukur **penerimaan pengguna** terhadap antarmuka HOTL melalui metode UAT berbasis kuesioner.

### Instrumen: System Usability Scale (SUS)

Penelitian ini menggunakan **System Usability Scale (SUS)**, instrumen baku yang terdiri dari 10 pertanyaan Likert 5 poin, untuk mengukur persepsi usabilitas secara holistik \[18\]. SUS telah divalidasi secara luas dalam konteks evaluasi sistem informasi dan keamanan siber \[10\].

Pertanyaan SUS mencakup dimensi:
- Kemudahan penggunaan (*ease of use*)
- Kebutuhan dukungan teknis (*need for technical support*)
- Tingkat kompleksitas (*complexity*)
- Konsistensi sistem (*consistency*)
- Kepercayaan diri pengguna (*confidence*)

**Perhitungan Skor SUS:**

$$\text{SUS Score} = \left(\sum_{\text{ganjil}} (x_i - 1) + \sum_{\text{genap}} (5 - x_i)\right) \times 2.5 \tag{19}$$

di mana $x_i$ adalah skor responden pada pertanyaan ke-$i$ (skala Likert 1–5), dengan pertanyaan ganjil (1, 3, 5, 7, 9) bernada positif dan pertanyaan genap (2, 4, 6, 8, 10) bernada negatif.

Skor SUS berada pada rentang 0–100, di mana:
- ≥ 85: Sangat baik (*Excellent*)
- 70–84.9: Baik (*Good*)
- 50–69.9: Rata-rata, perlu perbaikan (*OK*)
- < 50: Di bawah rata-rata (*Poor/Awful*)

**Threshold Keberhasilan:** Penelitian ini menetapkan SUS Score ≥ 68 sebagai kriteria sukses minimum, mengadopsi benchmark *"acceptable"* yang ditetapkan oleh Bangor, Kortum, dan Miller (2008) sebagai standar industri yang telah divalidasi secara luas. Skor di atas 68 mengindikasikan bahwa sistem antarmuka HOTL memenuhi tingkat usabilitas yang dapat diterima oleh analis SOC \[18\].

### Kriteria dan Jumlah Responden

Responden UAT dipilih berdasarkan kriteria purposive sampling:
- **Minimal pengalaman kerja:** 1 tahun di bidang keamanan siber atau operasi SOC
- **Peran relevan:** Analis SOC, *Security Analyst*, *Incident Responder*, atau *Blue Team Member*
- **Kompetensi teknis:** Familiar dengan konsep *threat intelligence*, IDS, dan SIEM

Jumlah responden yang ditargetkan adalah **15–20 orang**, sesuai dengan panduan Nielsen Norman Group bahwa 15 responden sudah cukup untuk mengidentifikasi masalah usabilitas mayor dengan tingkat keyakinan tinggi \[18\].

**Mitigasi Bias Seleksi.** Purposive sampling dapat memperkenalkan bias positif apabila responden direkrut dari jaringan profesional penulis. Untuk memitigasi hal ini: (a) responden tidak diinformasikan mengenai hipotesis penelitian sebelum sesi UAT (*single-blind*), (b) kuesioner SUS diisi secara anonim, dan (c) sebaran organisasi asal responden akan dilaporkan untuk menunjukkan keragaman sampel.

### Prosedur UAT

1. **Briefing (15 menit):** Responden diberikan penjelasan singkat mengenai tujuan sistem dan konteks penggunaannya dalam operasi SOC.
2. **Demonstrasi Sistem (20 menit):** Responden mengamati demonstrasi langsung alur kerja sistem, dari penerimaan *threat intelligence* hingga notifikasi Telegram dan respons melalui antarmuka HOTL.
3. **Sesi Eksplorasi Mandiri (25 menit):** Responden berinteraksi langsung dengan sistem menggunakan skenario insiden yang telah disiapkan (*task scenario*), meliputi:
   - Menerima dan merespons notifikasi ancaman *Critical*
   - Memberikan label koreksi pada prediksi ML yang tidak tepat
   - Memeriksa riwayat aturan IDS yang dibuat oleh sistem
4. **Pengisian Kuesioner SUS (10 menit):** Responden mengisi kuesioner SUS secara mandiri setelah sesi eksplorasi.
5. **Wawancara Singkat (10 menit, opsional):** Peneliti melakukan wawancara singkat semi-terstruktur untuk menggali umpan balik kualitatif tambahan.

### Analisis Data UAT

- **Statistik Deskriptif:** Menghitung rata-rata (mean), median, dan standar deviasi skor SUS dari seluruh responden.
- **Adjective Rating:** Mengklasifikasikan skor rata-rata ke dalam kategori SUS standar.
- **Analisis Kualitatif:** Merangkum tema utama dari umpan balik wawancara untuk mengidentifikasi area perbaikan antarmuka.

## Rencana Analisis Data

Seluruh data eksperimen dikelola dan dianalisis melalui pipeline berikut:

1. **Pengumpulan Data Otomatis:** Log sistem, hasil klasifikasi ML, dan *timestamp* respons dikumpulkan secara otomatis melalui logging n8n ke database SQLite lokal.
2. **Preprocessing:** Data dibersihkan dari duplikasi dan *outlier* menggunakan skrip Python (pandas).
3. **Perhitungan Metrik:** Metrik Accuracy, MTTR, FPR, dan F1-Score (Persamaan 14–18) dihitung menggunakan modul scikit-learn dan statistik kustom.
4. **Perbandingan Baseline:** Hasil sistem otomatis dibandingkan secara statistik terhadap proses manual (baseline). Uji normalitas Shapiro-Wilk diterapkan terlebih dahulu; jika normalitas terpenuhi, digunakan uji-t berpasangan (*paired t-test*) dengan α = 0.05, sedangkan jika tidak, digunakan Wilcoxon signed-rank test sebagai alternatif non-parametrik. *Effect size* dilaporkan menggunakan Cohen's d untuk memberikan gambaran besaran dampak di luar signifikansi statistik.

   **Analisis Power Statistik.** Desain 7+7 hari menghasilkan N = 7 observasi berpasangan per metrik. Analisis power *a priori* menggunakan G*Power (uji-t berpasangan dua arah, α = 0.05, N = 7) menunjukkan bahwa desain ini memiliki power memadai (1 − β ≥ 0.80) hanya untuk *large effect sizes* (Cohen's d ≥ 1.4). Untuk *medium effect sizes* (d ≈ 0.5), power turun ke ≈ 0.15–0.20. Untuk memitigasi keterbatasan ini, analisis tambahan dilakukan menggunakan agregasi per-IOC (bukan per-hari)—yang menghasilkan N ≈ 350–700 observasi per fase—sebagai analisis sensitivitas. Hasil per-hari tetap dilaporkan sebagai unit analisis primer untuk mempertahankan independensi temporal antar observasi.

   **Koreksi Perbandingan Berganda.** Karena empat metrik primer (Accuracy, MTTR, FPR, F1-Score) diuji secara simultan, koreksi Holm-Bonferroni diterapkan untuk mengendalikan *family-wise error rate* pada α = 0.05. P-value yang telah dikoreksi ($p_{\text{adjusted}}$) akan dilaporkan bersama p-value asli untuk transparansi.

   **Justifikasi Desain Sekuensial.** Desain crossover atau A/B split tidak layak dilaksanakan karena keterbatasan sumber daya (hanya satu tim analis tersedia). *Learning effect* dan perubahan seasonal pada threat landscape dimitigasi melalui: (a) pencatatan dan pelaporan volume IOC harian sebagai kovariat, (b) pelaporan tren metrik harian untuk mendeteksi efek temporal, dan (c) pengakuan eksplisit bahwa desain sekuensial merupakan keterbatasan validitas internal (lihat §Threats to Validity).
5. **Studi Ablasi (*Ablation Study*):** Untuk mengukur kontribusi individual setiap komponen arsitektur, eksperimen tambahan dilakukan dengan menonaktifkan komponen secara selektif:
   - **Ablasi A (Tanpa Feedback Loop):** Menjalankan pipeline lengkap tanpa Adaptive Feedback Loop untuk mengukur dampak feedback terhadap akurasi klasifikasi dari waktu ke waktu.
   - **Ablasi B (Tanpa IDS Rule Generation):** Menjalankan pipeline dengan triase otonom tetapi tanpa pembuatan aturan IDS otomatis, mengukur dampak terhadap MTTR.
   - **Ablasi C (Threshold Statis vs. Dikalibrasi):** Membandingkan performa fungsi keputusan $\mathcal{D}$ dengan threshold default ($\theta_{\text{high}} = 0.85$, $\theta_{\text{low}} = 0.60$) terhadap threshold yang dikalibrasi melalui ROC/PR analysis.
   Hasil ablasi akan dilaporkan dalam bentuk tabel perbandingan metrik untuk mengidentifikasi komponen yang memberikan kontribusi terbesar terhadap peningkatan performa.
6. **Visualisasi:** Hasil divisualisasikan menggunakan matplotlib/seaborn untuk presentasi perubahan metrik sebelum dan sesudah implementasi sistem.
7. **Interpretasi:** Temuan diinterpretasikan dalam konteks literatur terkait, khususnya diposisikan terhadap metrik performa yang dilaporkan oleh Zhang et al. \[1\] (F1-Score 93%, latency 58.3ms) dan implikasi praktis untuk operasi SOC.

## Threats to Validity

Penelitian ini mengakui beberapa ancaman terhadap validitas yang perlu dipertimbangkan dalam interpretasi hasil:

- **Validitas Internal:** Desain eksperimen sekuensial (7+7 hari) memperkenalkan potensi *confounding variables* berupa perubahan threat landscape antar periode. Mitigasi dilakukan melalui pencatatan volume IOC harian dan analisis kovariat. Selain itu, *learning effect* pada analis yang semakin familiar dengan sistem di minggu kedua dapat mempengaruhi hasil MTTR.
- **Validitas Eksternal:** Lingkungan laboratorium dengan Virtual Machine tidak sepenuhnya merepresentasikan kompleksitas SOC produksi enterprise. Volume IOC di lingkungan lab (~50-100 IOC/hari) lebih rendah dibandingkan SOC produksi skala besar (~500-1.000 IOC/hari). Temuan mungkin tidak langsung berlaku pada organisasi dengan skala dan kompleksitas jaringan yang berbeda.
- **Validitas Konstruk:** Penggunaan 500 IOC tiruan (dummy data) pada skenario stress test mungkin tidak mencerminkan distribusi dan karakteristik IOC pada lingkungan ancaman nyata. Distribusi kelas IOC tiruan mengikuti distribusi dataset pelatihan (Low 45%, Medium 30%, High 18%, Critical 7%); perlu diakui bahwa distribusi yang seragam melintasi semua kelas akan memberikan evaluasi yang lebih ketat terhadap performa per-kelas. Dataset pelatihan dari Cyfirma historical data dapat memiliki bias terhadap jenis ancaman tertentu.
- **Validitas Konstruk (Multi-Sumber):** Arsitektur dirancang untuk fusi multi-sumber (Persamaan 1–2), namun hanya instansiasi sumber tunggal (Cyfirma TIP) yang divalidasi secara eksperimental. Klaim arsitektural tentang extensibility multi-sumber belum diverifikasi secara empiris.

## Keterbatasan dan Pekerjaan Mendatang

- **Durasi Eksperimen:** Periode 14 hari kerja cukup untuk evaluasi proof-of-concept namun terlalu pendek untuk mengevaluasi efektivitas mitigasi concept drift secara komprehensif, yang membutuhkan observasi minggu-bulan. Pekerjaan mendatang dapat memperpanjang durasi atau menggunakan *historical data replay* untuk mensimulasikan periode yang lebih panjang.
- **Model Tunggal:** Penelitian ini hanya mengevaluasi Random Forest sebagai classifier. Perbandingan dengan model alternatif (Gradient Boosted Trees, SVM, Neural Network) dan khususnya model berbasis sekuens temporal seperti Attention-LSTM \[1\] akan memperkuat generalisabilitas temuan.
- **Tidak Ada Optimisasi Berbasis Reinforcement Learning:** Zhang et al. \[1\] mengimplementasikan Deep Reinforcement Learning (DRL) dengan fungsi reward berbasis fuzzy logic pada Layer 4 arsitektur AIR untuk optimisasi kebijakan respons secara real-time. Fungsi reward menimbang keberhasilan pertahanan, konsumsi sumber daya, dan biaya false positive:

  $$R(s, a) = w_1 \cdot \mu_{\text{success}}(s,a) - w_2 \cdot \mu_{\text{resource}}(s,a) - w_3 \cdot \mu_{\text{FP}}(s,a)$$

  di mana $\mu_{\text{success}}$, $\mu_{\text{resource}}$, $\mu_{\text{FP}}$ adalah fungsi keanggotaan fuzzy dan $w_1, w_2, w_3$ adalah bobot adaptif (lihat Zhang et al. \[1\], Persamaan 8 pada sumber asli). Arsitektur Cognitive SOC ini tidak menyertakan komponen DRL; optimisasi kebijakan dilakukan secara offline melalui Adaptive Feedback Loop (§Adaptive Feedback Loop) dan kalibrasi threshold manual. Integrasi DRL agent yang berjalan di atas n8n untuk optimisasi threshold $\theta_{\text{high}}$ dan $\theta_{\text{low}}$ secara real-time merupakan pekerjaan mendatang yang kritis.

- **Tidak Ada Analisis Adversarial:** Penelitian ini belum mempertimbangkan skenario di mana *threat actor* sengaja memanipulasi IOC untuk membingungkan classifier (*adversarial ML*) atau meracuni feedback loop (*data poisoning*). Zhang et al. \[1\] melaporkan pencapaian Nash equilibrium dalam 97.3% skenario adversarial melalui framework game-theoretic. Pekerjaan mendatang perlu mengintegrasikan *threat model* formal dan analisis keamanan terhadap sistem itu sendiri.
- **Perbandingan SOAR:** Arsitektur yang diusulkan tidak dibandingkan secara langsung dengan solusi SOAR komersial (Splunk SOAR, Palo Alto XSOAR) maupun open-source (TheHive + Cortex), ataupun terhadap metrik performa AIR \[1\] sebagai benchmark arsitektural. Studi komparatif diperlukan untuk memposisikan kontribusi penelitian ini dalam ekosistem yang lebih luas.
- **Format Pertukaran Data:** Arsitektur saat ini menggunakan format JSON internal melalui n8n, bukan format standar STIX/TAXII \[11\] yang digunakan oleh Zhang et al. \[1\]. Meskipun operator fusi data (Persamaan 1–2) dirancang secara extensible, integrasi STIX/TAXII penuh diperlukan untuk interoperabilitas dengan ekosistem keamanan enterprise dan merupakan pekerjaan mendatang yang direkomendasikan.

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
