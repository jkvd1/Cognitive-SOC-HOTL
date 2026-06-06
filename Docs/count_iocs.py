import json

fp = r'c:\Users\ACER\Downloads\Skripsi\IOC.json'
with open(fp, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total elements in IOC.json: {len(data)}")
if len(data) > 0:
    print("Example element structure:")
    print(json.dumps(data[0], indent=2))
