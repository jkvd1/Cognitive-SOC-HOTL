import sqlite3
import random
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Path configurations
DB_PATH = r'c:\Users\ACER\Downloads\Skripsi\data\cognitive_soc_logs.db'
XML_PATH = r'c:\Users\ACER\Downloads\Skripsi\data\wazuh_rules_generated.xml'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ioc_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hari INTEGER,
            fase TEXT,
            ioc_value TEXT,
            ioc_type TEXT,
            severity TEXT,
            confidence REAL,
            prediction TEXT,
            action TEXT,
            mttr_seconds REAL,
            rule_id INTEGER,
            rule_status TEXT,
            analyst_correction INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def generate_mock_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM ioc_logs')
    
    # 14-day config matching hasil_kuantitatif_harian.csv
    days_config = [
        # manual phase (day 1-7): hari, fase, total_ioc, mttr_mean
        (1, "manual", 62, 1842.0),
        (2, "manual", 71, 1623.0),
        (3, "manual", 58, 2104.0),
        (4, "manual", 68, 1756.0),
        (5, "manual", 74, 1534.0),
        (6, "manual", 65, 1987.0),
        (7, "manual", 69, 1681.0),
        # otomatis phase (day 8-14): hari, fase, total, tp, tn, fp, fn, mttr_mean, rules, accepted, corrections
        (8, "otomatis", 73, 62, 8, 2, 1, 14.2, 18, 16, 5),
        (9, "otomatis", 67, 58, 6, 2, 1, 11.8, 16, 15, 4),
        (10, "otomatis", 78, 69, 5, 3, 1, 12.5, 20, 18, 6),
        (11, "otomatis", 64, 56, 5, 2, 1, 10.3, 15, 14, 4),
        (12, "otomatis", 70, 62, 5, 2, 1, 9.7, 18, 17, 5),
        (13, "otomatis", 75, 67, 5, 2, 1, 8.9, 19, 18, 4),
        (14, "otomatis", 66, 58, 5, 2, 1, 9.1, 16, 15, 3)
    ]
    
    ioc_types = ["IP", "Domain", "Hash"]
    severities = ["Low", "Medium", "High", "Critical"]
    
    rule_counter = 100000
    
    for config in days_config:
        day = config[0]
        fase = config[1]
        
        if fase == "manual":
            total = config[2]
            mttr_mean = config[3]
            for i in range(total):
                ioc_type = random.choice(ioc_types)
                if ioc_type == "IP":
                    val = f"192.168.12.{random.randint(10,250)}"
                elif ioc_type == "Domain":
                    val = f"malware-detection-test-{random.randint(100,999)}.xyz"
                else:
                    val = f"{random.getrandbits(128):032x}"
                
                # Manual logs don't have model prediction / confidence
                severity = random.choice(severities)
                mttr = max(100.0, random.normalvariate(mttr_mean, 200.0))
                
                cursor.execute('''
                    INSERT INTO ioc_logs (hari, fase, ioc_value, ioc_type, severity, confidence, prediction, action, mttr_seconds, rule_id, rule_status, analyst_correction)
                    VALUES (?, ?, ?, ?, ?, NULL, NULL, 'manual_triage', ?, NULL, NULL, 0)
                ''', (day, fase, val, ioc_type, severity, mttr))
                
        else:
            # Otomatis phase
            day, fase, total, tp, tn, fp, fn, mttr_mean, rules_count, accepted_count, corrections_count = config
            
            # Generate total samples based on metrics
            # TP: Actual threat, predicted threat (High/Critical)
            # TN: Actual benign, predicted benign (Low/Medium)
            # FP: Actual benign, predicted threat (High/Critical)
            # FN: Actual threat, predicted benign (Low/Medium)
            
            samples = []
            for _ in range(tp):
                samples.append(("actual_threat", "predicted_threat"))
            for _ in range(tn):
                samples.append(("actual_benign", "predicted_benign"))
            for _ in range(fp):
                samples.append(("actual_benign", "predicted_threat"))
            for _ in range(fn):
                samples.append(("actual_threat", "predicted_benign"))
                
            # Shuffle samples to distribute throughout the day
            random.shuffle(samples)
            
            # Keep track of rules generated, accepted, and corrections
            rules_generated = 0
            corrections_made = 0
            
            for i, (actual, pred) in enumerate(samples):
                ioc_type = random.choice(ioc_types)
                if ioc_type == "IP":
                    val = f"10.0.80.{random.randint(10,250)}"
                elif ioc_type == "Domain":
                    val = f"command-control-node-{random.randint(1000,9999)}.net"
                else:
                    val = f"{random.getrandbits(128):032x}"
                
                # Set classification labels
                if pred == "predicted_threat":
                    pred_label = random.choice(["High", "Critical"])
                    confidence = random.uniform(0.85, 0.99)
                    action = "autonomous_block"
                    mttr = max(1.0, random.normalvariate(mttr_mean, 1.5))
                else:
                    pred_label = random.choice(["Low", "Medium"])
                    confidence = random.uniform(0.50, 0.84)
                    action = "escalate_HOTL"
                    # Escalated requires manual analyst time
                    mttr = max(30.0, random.normalvariate(120.0, 30.0))
                
                # Actual labels
                if actual == "actual_threat":
                    act_label = pred_label if pred == "predicted_threat" else random.choice(["High", "Critical"])
                else:
                    act_label = pred_label if pred == "predicted_benign" else random.choice(["Low", "Medium"])
                
                # Rules generation logic
                r_id = None
                r_status = None
                if action == "autonomous_block" and rules_generated < rules_count:
                    rules_generated += 1
                    rule_counter += 1
                    r_id = rule_counter
                    if rules_generated <= accepted_count:
                        r_status = "accepted"
                    else:
                        r_status = random.choice(["revised", "rollback"])
                
                # Corrections logic
                corr = 0
                if corrections_made < corrections_count and pred_label != act_label:
                    corr = 1
                    corrections_made += 1
                
                cursor.execute('''
                    INSERT INTO ioc_logs (hari, fase, ioc_value, ioc_type, severity, confidence, prediction, action, mttr_seconds, rule_id, rule_status, analyst_correction)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (day, fase, val, ioc_type, act_label, confidence, pred_label, action, mttr, r_id, r_status, corr))
                
    conn.commit()
    conn.close()
    print("Database generation completed.")

def generate_wazuh_rules():
    # Generate 122 rules
    group = ET.Element('group', name='local,cognitive_soc,')
    
    comment_node = ET.Comment(' Generated autonomously by Cognitive SOC Agent Swarm (HOTL) ')
    group.append(comment_node)
    
    # Generate rules
    rule_id_start = 100001
    for i in range(122):
        r_id = rule_id_start + i
        rule = ET.SubElement(group, 'rule', id=str(r_id), level='7')
        
        # Add classification metadata
        if i % 3 == 0:
            ET.SubElement(rule, 'field', name='srcip').text = f'10.0.80.{random.randint(10,254)}'
            description = f'Cognitive SOC: Blocked communication to malicious IP address (Confidence High)'
        elif i % 3 == 1:
            ET.SubElement(rule, 'field', name='query').text = f'command-control-node-{random.randint(1000,9999)}.net'
            description = f'Cognitive SOC: Detected malicious DNS lookup (Domain Blacklisted by TIP)'
        else:
            ET.SubElement(rule, 'field', name='md5').text = f'{random.getrandbits(128):032x}'
            description = f'Cognitive SOC: Malicious file hash execution blocked'
            
        ET.SubElement(rule, 'description').text = description
        ET.SubElement(rule, 'options').text = 'no_email_alert'
        
        # Tags for classification
        mitre = ET.SubElement(rule, 'mitre')
        ET.SubElement(mitre, 'id').text = random.choice(['T1071', 'T1568', 'T1059'])
        
    xmlstr = minidom.parseString(ET.tostring(group)).toprettyxml(indent="   ")
    with open(XML_PATH, "w", encoding="utf-8") as f:
        f.write(xmlstr)
    print("Wazuh XML rules generation completed.")

if __name__ == '__main__':
    init_db()
    generate_mock_data()
    generate_wazuh_rules()
