import zipfile
import xml.etree.ElementTree as ET

def extract_docx_text(filepath):
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with zipfile.ZipFile(filepath, 'r') as z:
        with z.open('word/document.xml') as f:
            tree = ET.parse(f)
    root = tree.getroot()
    paragraphs = []
    for para in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        texts = []
        for run in para.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
            if run.text:
                texts.append(run.text)
        paragraphs.append(''.join(texts))
    return '\n'.join(paragraphs)

if __name__ == '__main__':
    fp = r'c:\Users\ACER\Downloads\Skripsi\ProposalSkripsiV8c.docx'
    text = extract_docx_text(fp)
    out = r'c:\Users\ACER\Downloads\Skripsi\ProposalSkripsiV8c_extracted.txt'
    with open(out, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Extracted {len(text)} chars to {out}")
