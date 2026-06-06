import json
import collections

fp = r'c:\Users\ACER\Downloads\Skripsi\IOC.json'
with open(fp, 'r', encoding='utf-8') as f:
    data = json.load(f)

verdicts = []
for item in data:
    ext_def = "extension-definition--8e1c4b7d-9a2f-4d63-b5e0-3c7a1f9d2b44"
    if "extensions" in item and ext_def in item["extensions"]:
        props = item["extensions"][ext_def].get("properties", {})
        verdict = props.get("verdict", "Missing")
        verdicts.append(verdict)

print("Verdict distribution:")
print(collections.Counter(verdicts))
