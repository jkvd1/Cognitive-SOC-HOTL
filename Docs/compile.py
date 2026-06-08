import re

def compile_paper():
    with open(r'c:\Users\ACER\Downloads\Skripsi\ProposalSkripsiV7.md', 'r', encoding='utf-8') as f:
        text = f.read()

    with open(r'c:\Users\ACER\Downloads\Skripsi\sections\BabV_Hasil.md', 'r', encoding='utf-8') as f:
        hasil = f.read()

    # 1. Update Abstract
    abstract_old = "_Abstrak_-Security Operations Center (SOC) modern menghadapi tantangan volume peringatan masif dan keterbatasan sumber daya manusia, yang meningkatkan Mean Time to Respond (MTTR) dan menurunkan akurasi deteksi. Penelitian ini mengusulkan arsitektur Cognitive SOC yang mengimplementasikan paradigma Human-On-The-Loop (HOTL) melalui Hybrid Autonomous AI Agent dan Adaptive Feedback Loop. Arsitektur ini mengintegrasikan Threat Intelligence Platform, mesin orkestrasi low-code, subsistem Machine Learning (Random Forest), dan SIEM, dengan mekanisme monitoring analis melalui Telegram. Agent Swarm beroperasi secara otonom untuk triase ancaman dan pembuatan aturan IDS dinamis, sementara analis berperan sebagai supervisor yang mengintervensi pada kondisi anomali. Adaptive Feedback Loop memungkinkan koreksi berkelanjutan untuk mencegah concept drift dan meningkatkan akurasi klasifikasi. Efektivitas dievaluasi melalui Accuracy, MTTR, False Positive Rate, dan F1-Score, serta User Acceptance Testing dengan System Usability Scale terhadap 15–20 responden praktisi keamanan."

    abstract_new = "_Abstrak_-Security Operations Center (SOC) modern menghadapi tantangan volume peringatan masif dan keterbatasan sumber daya manusia, yang meningkatkan Mean Time to Respond (MTTR) dan menurunkan akurasi deteksi. Penelitian ini telah merancang, mengimplementasikan, dan mengevaluasi arsitektur Cognitive SOC yang mengimplementasikan paradigma Human-On-The-Loop (HOTL) melalui Hybrid Autonomous AI Agent dan Adaptive Feedback Loop. Arsitektur ini mengintegrasikan Threat Intelligence Platform (TIP), mesin orkestrasi low-code (n8n), subsistem Machine Learning (Random Forest), dan SIEM (Wazuh), dengan mekanisme monitoring analis melalui Telegram. Agent Swarm beroperasi secara otonom untuk triase ancaman dan pembuatan aturan IDS dinamis, sementara analis berperan sebagai supervisor yang mengintervensi pada kondisi anomali. Adaptive Feedback Loop memungkinkan koreksi berkelanjutan untuk mencegah concept drift dan meningkatkan akurasi klasifikasi. Evaluasi empiris melalui eksperimen sekuensial 14 hari pada 960 IOC menunjukkan peningkatan signifikan: akurasi klasifikasi mencapai 94,93%, reduksi MTTR sebesar 99,39% (dari 1.789,6 detik menjadi 10,93 detik), penurunan False Positive Rate dari 8,14% menjadi 2,23%, dan F1-Score sebesar 0,949. Agent Swarm berhasil menghasilkan 122 aturan IDS dinamis dengan tingkat penerimaan 92,6%. Pengujian penerimaan pengguna (UAT) terhadap 17 praktisi keamanan menghasilkan skor System Usability Scale (SUS) rata-rata 75,9 (\"Good\"), melampaui threshold benchmark industri."

    text = text.replace(abstract_old, abstract_new)

    # 2. Update Tenses
    text = text.replace("Penelitian ini mengusulkan", "Penelitian ini telah mengusulkan dan mengimplementasikan")
    text = text.replace("Penelitian ini bertujuan untuk merancang", "Penelitian ini telah merancang")
    text = text.replace("penelitian ini akan mendemonstrasikan", "penelitian ini telah mendemonstrasikan")
    text = text.replace("Penelitian ini diharapkan dapat memberikan", "Penelitian ini memberikan")
    text = text.replace("Hasil penelitian diharapkan dapat memberikan", "Hasil penelitian memberikan")
    text = text.replace("akan dilaporkan untuk", "dilaporkan untuk")
    text = text.replace("Evaluasi efektivitas sistem dilakukan", "Evaluasi efektivitas sistem telah dilakukan")
    text = text.replace("Eksperimen dilakukan", "Eksperimen telah dilakukan")
    text = text.replace("evaluasi akan melaporkan:", "evaluasi melaporkan:")
    text = text.replace("Target: **15–20 responden**", "Tercapai: **17 responden**")
    text = text.replace("akan dilaporkan.", "telah dilaporkan.")

    # 3. Insert Bab V (Hasil) and transform old Bab V to Bab VI
    parts = text.split("# V. Kesimpulan dan Pekerjaan Mendatang")

    if len(parts) == 2:
        bab6_title = "# VI. Kesimpulan dan Pekerjaan Mendatang\n\n## A. Kesimpulan\n\nPenelitian ini telah berhasil merancang, mengimplementasikan, dan mengevaluasi arsitektur Cognitive SOC berbasis paradigma Human-On-The-Loop (HOTL) menggunakan Hybrid Autonomous AI Agent dan Adaptive Feedback Loop. Hasil eksperimen empiris selama 14 hari mengkonfirmasi bahwa integrasi orkestrasi low-code (n8n) dengan klasifikasi Random Forest mampu memberikan dampak operasional yang substansial. Secara kuantitatif, arsitektur ini mencapai akurasi 94,93% dan mereduksi Mean Time to Respond (MTTR) sebesar 99,39% (dari ~29,8 menit menjadi 10,93 detik). Tingkat False Positive juga berhasil diturunkan sebesar 72,6%, secara signifikan memitigasi isu alert fatigue pada analis SOC. Agent Swarm terbukti efektif dengan kapabilitas menghasilkan 122 aturan IDS dinamis, di mana 92,6% di antaranya diterima tanpa modifikasi. Selain itu, evaluasi UAT mengkonfirmasi penerimaan praktisi dengan skor SUS 75,9 (\"Good\"). Secara keseluruhan, arsitektur Cognitive SOC ini terbukti andal, terukur, dan mampu mengatasi kesenjangan temporal dalam respons insiden siber secara proaktif.\n\n## B. Keterbatasan dan Pekerjaan Mendatang\n"
        
        bab6_content = parts[1]
        
        new_text = parts[0] + "\n" + hasil + "\n\n" + bab6_title + bab6_content
    else:
        print("Could not find '# V. Keterbatasan dan Pekerjaan Mendatang'")
        new_text = text

    with open(r'c:\Users\ACER\Downloads\Skripsi\ProposalSkripsi_Final.md', 'w', encoding='utf-8') as f:
        f.write(new_text)

    print("Done writing ProposalSkripsi_Final.md")

if __name__ == "__main__":
    compile_paper()
