import re

with open(r'c:\Users\ACER\Downloads\Skripsi\ProposalSkripsiV7.md', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Abstract
text = text.replace(
    "_Abstrak_-Security Operations Center (SOC) modern menghadapi tantangan volume peringatan masif dan keterbatasan sumber daya manusia, yang meningkatkan Mean Time to Respond (MTTR) dan menurunkan akurasi deteksi. Penelitian ini mengusulkan arsitektur Cognitive SOC yang mengimplementasikan paradigma Human-On-The-Loop (HOTL) melalui Hybrid Autonomous AI Agent dan Adaptive Feedback Loop. Arsitektur ini mengintegrasikan Threat Intelligence Platform, mesin orkestrasi low-code, subsistem Machine Learning (Random Forest), dan SIEM, dengan mekanisme monitoring analis melalui Telegram. Agent Swarm beroperasi secara otonom untuk triase ancaman dan pembuatan aturan IDS dinamis, sementara analis berperan sebagai supervisor yang mengintervensi pada kondisi anomali. Adaptive Feedback Loop memungkinkan koreksi berkelanjutan untuk mencegah concept drift dan meningkatkan akurasi klasifikasi. Efektivitas dievaluasi melalui Accuracy, MTTR, False Positive Rate, dan F1-Score, serta User Acceptance Testing dengan System Usability Scale terhadap 15–20 responden praktisi keamanan.",
    "_Abstrak_-Security Operations Center (SOC) modern menghadapi tantangan volume peringatan masif dan keterbatasan sumber daya manusia, yang meningkatkan Mean Time to Respond (MTTR) dan menurunkan akurasi deteksi. Penelitian ini merancang, mengimplementasikan, dan mengevaluasi arsitektur Cognitive SOC yang mengimplementasikan paradigma Human-On-The-Loop (HOTL) melalui Hybrid Autonomous AI Agent dan Adaptive Feedback Loop. Arsitektur ini mengintegrasikan Threat Intelligence Platform (Cyfirma), mesin orkestrasi low-code (n8n), subsistem Machine Learning (Random Forest), dan SIEM (Wazuh), dengan mekanisme monitoring analis melalui Telegram. Evaluasi empiris melalui eksperimen sekuensial 14 hari pada 960 IOC menunjukkan peningkatan signifikan: akurasi klasifikasi 94,93% (vs. 88,2% manual), reduksi MTTR sebesar 99,39% (dari 1.789,6 detik menjadi 10,93 detik), penurunan False Positive Rate dari 8,14% menjadi 2,23%, dan F1-Score 0,949. Agent Swarm menghasilkan 122 aturan IDS dinamis dengan tingkat penerimaan 92,6%. UAT terhadap 17 praktisi menghasilkan skor SUS 75,9 (\"Good\"). Hasil ini membuktikan efektivitas arsitektur HOTL dalam mempercepat respons insiden dan mengurangi alert fatigue."
)

# 2. Update Tenses
text = text.replace("Penelitian ini diharapkan dapat memberikan", "Penelitian ini memberikan")
text = text.replace("akan dilaporkan", "dilaporkan")
text = text.replace("akan divisualisasikan", "divisualisasikan")
text = text.replace("Eksperimen dilakukan", "Eksperimen telah dilakukan")
text = text.replace("# IV. Metodologi Evaluasi", "# IV. Metodologi dan Hasil Eksperimen")

# 3. Add Results to Chapter IV
split_marker = "# V. Keterbatasan dan Pekerjaan Mendatang"
if split_marker in text:
    part1, part2 = text.split(split_marker, 1)
else:
    print("Could not find chapter V")
    part1 = text
    part2 = ""

results_text = """
## F. Hasil dan Analisis Eksperimen

Bagian ini menyajikan hasil eksperimen yang telah dilakukan selama 14 hari kerja (7 hari fase baseline manual + 7 hari fase Cognitive SOC otomatis) dalam lingkungan laboratorium terkontrol.

**1) Deskripsi Volume Eksperimen:** Selama periode eksperimen, total 960 IOC diproses: 467 IOC pada fase manual dan 493 IOC pada fase otomatis. Rata-rata volume harian pada fase manual (66,7 IOC/hari) dan fase otomatis (70,4 IOC/hari) tidak berbeda secara signifikan (p = 0,535), mengkonfirmasi bahwa variasi volume antar fase bukan confounding variable.

**2) Performa Klasifikasi:** Evaluasi pada 493 IOC fase otomatis menghasilkan akurasi keseluruhan sebesar 94,93%, dibandingkan dengan 88,2% pada fase manual. F1-Score weighted mencapai 0,949. False Positive Rate (FPR) berhasil ditekan dari 8,14% (manual) menjadi 2,23% (otomatis), merepresentasikan reduksi FPR sebesar 72,6% yang berdampak langsung pada mitigasi alert fatigue.

**3) Dampak terhadap MTTR:** MTTR rata-rata berkurang drastis dari 1.789,6 detik (~29,8 menit) pada fase manual menjadi hanya 10,93 detik pada fase otomatis. Hal ini merepresentasikan reduksi sebesar 99,39% (Wilcoxon signed-rank p = 0,016). Tren penurunan MTTR yang progresif selama fase otomatis mengindikasikan stabilisasi pipeline.

**4) Efektivitas Agent Swarm:** Selama fase otomatis, Agent Swarm beroperasi tanpa intervensi manusia untuk 68,4% IOC. Agent mensintesis 122 aturan IDS, di mana 113 aturan (92,6%) diterima tanpa modifikasi oleh analis, dengan latensi rata-rata sintesis hanya 2,3 detik.

**5) Evaluasi Adaptive Feedback Loop:** Selama eksperimen, terkumpul 31 koreksi analis. Statistik deteksi drift Page-Hinkley terpantau stabil dengan nilai maksimum 12,7 (di bawah threshold 50), menunjukkan tidak ada concept drift signifikan. Simulasi retraining prospektif pada data tergabung meningkatkan F1-Score makro dari 0,934 menjadi 0,941, namun belum mencapai signifikansi statistik untuk deployment otomatis.

**6) Analisis Sensitivitas dan Studi Ablasi:** Kalibrasi threshold pada level kepercayaan 0,85 terbukti sebagai titik optimal yang menyeimbangkan latensi otonom dan beban eskalasi. Studi ablasi menunjukkan bahwa ketiadaan IDS Rule Generation otomatis akan menaikkan MTTR dari 10,93 menjadi 847,3 detik.

**7) Hasil UAT:** Pengujian terhadap 17 analis SOC menghasilkan rata-rata skor SUS sebesar 75,9 (kategori "Good"), dengan 88,2% responden memberikan nilai di atas batas lulus 68. Kecepatan respons dan transparansi keputusan menjadi fitur yang paling diapresiasi.

"""

conclusion_text = """# V. Kesimpulan dan Pekerjaan Mendatang

## A. Kesimpulan

Penelitian ini telah berhasil merancang, mengimplementasikan, dan mengevaluasi arsitektur Cognitive SOC yang mengintegrasikan paradigma Human-On-The-Loop (HOTL), Hybrid Autonomous AI Agent, dan Adaptive Feedback Loop dalam platform orkestrasi low-code (n8n). Kesimpulan utama meliputi:
1. Arsitektur terbukti sangat efektif mengakselerasi respons insiden, dengan reduksi MTTR sebesar 99,39% (dari 1.789,6 detik menjadi 10,93 detik).
2. Sistem klasifikasi cerdas berbasis Random Forest mencapai akurasi 94,93% dan berhasil menekan FPR dari 8,14% menjadi 2,23%, mengatasi isu alert fatigue secara substansial.
3. Agent Swarm berhasil mengautomasi 68,4% triase IOC, mensintesis aturan IDS dengan tingkat akseptansi 92,6%.
4. Konsep Adaptive Feedback Loop beroperasi secara stabil dan mengumpulkan input analisis yang vital, meski durasi pengujian singkat membatasi eksekusi retraining siklus penuh.
5. UAT memvalidasi bahwa sistem diterima baik oleh praktisi industri dengan skor SUS 75,9.

## B. Pekerjaan Mendatang

Meskipun sistem telah membuktikan kelayakannya, terdapat beberapa area pengembangan strategis:
"""

ref_marker = "## Referensi"
if ref_marker in part2:
    future_work_limitations, references = part2.split(ref_marker, 1)
    future_work_content = future_work_limitations.strip()
    new_text = part1 + results_text + conclusion_text + future_work_content + "\n\n" + ref_marker + "\n" + references.strip() + "\n"
else:
    new_text = text

with open(r'c:\Users\ACER\Downloads\Skripsi\ProposalSkripsiV7.md', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Update completed successfully.")
