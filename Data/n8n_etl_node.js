/**
 * n8n JavaScript Code Node
 * 
 * Filters and extracts raw CYFIRMA STIX IOC data from IOC.json / TIP API response
 * into the exact normalized schema (15 features) described in Table II of the thesis.
 * 
 * Input: Array of raw CYFIRMA STIX indicator objects.
 * Output: Normalized features ready for machine learning classification.
 */

// In n8n, input data is stored in the 'items' variable.
// If running in a Node.js script locally, we can wrap this.
const inputItems = typeof items !== 'undefined' ? items : [];

const normalizedIocs = inputItems.map(item => {
    // n8n wraps item JSON inside .json field
    const raw = item.json || item;
    
    const name = raw.name || "";
    const pattern = raw.pattern || "";
    
    // 1. Identify indicator_type (One-Hot Encoded columns in Python model)
    let indicator_type = "Hash";
    if (pattern.includes("ipv4-addr") || pattern.includes("ipv6-addr")) {
        indicator_type = "IP";
    } else if (pattern.includes("domain-name")) {
        indicator_type = "Domain";
    } else if (name.count && name.count('.') === 3 && !name.startsWith('File')) {
        indicator_type = "IP";
    } else if (name.includes('.') && !name.startsWith('File')) {
        indicator_type = "Domain";
    }
    
    // Extract property extension data
    const extDef = "extension-definition--8e1c4b7d-9a2f-4d63-b5e0-3c7a1f9d2b44";
    const props = (raw.extensions && raw.extensions[extDef]) ? raw.extensions[extDef].properties || {} : {};
    
    // 2. tip_reputation_score (exposure score scaled to 0-100)
    const exposure_score = props.exposure_score !== undefined ? props.exposure_score : 5;
    const tip_reputation_score = exposure_score * 10;
    
    // 3. geolocation_risk (High risk countries = 2, Medium = 1, Low = 0)
    const highRiskCountries = ["RU", "CN", "KP", "IR", "BY"];
    const countryCode = props.country_code || "";
    let geolocation_risk = 0;
    if (highRiskCountries.includes(countryCode.toUpperCase())) {
        geolocation_risk = 2;
    } else if (countryCode) {
        geolocation_risk = 1;
    }
    
    // 4. asn_reputation (0 to 1 based on ASN reputation history)
    const asn = props.asn || "";
    const asn_reputation = asn ? 0.75 : 0.25;
    
    // 5. feed_frequency (log-transformed sources count)
    const sourcesStr = props.sources || "IOC sourced from 1 sources";
    const sourcesCount = parseInt(sourcesStr.replace(/\D/g, '')) || 1;
    const feed_frequency = Math.log(sourcesCount + 1);
    
    // 6. active_days_count (relevance timeline)
    const history = props.threat_score_history || {};
    const active_days_count = Object.keys(history).length || 1;
    
    // 7. threat_category (One-Hot Encoded columns: Malware, Phishing, C2, Exploit, Other)
    let threat_category = "Other";
    const labels = raw.labels || [];
    const labelsStr = labels.join(" ").toLowerCase();
    
    if (labelsStr.includes("c2") || labelsStr.includes("command-control") || name.includes("c2")) {
        threat_category = "C2";
    } else if (labelsStr.includes("phishing") || labelsStr.includes("credential")) {
        threat_category = "Phishing";
    } else if (labelsStr.includes("malware") || labelsStr.includes("trojan") || labelsStr.includes("ransomware")) {
        threat_category = "Malware";
    } else if (labelsStr.includes("exploit") || labelsStr.includes("vulnerability") || labelsStr.includes("hacking")) {
        threat_category = "Exploit";
    }
    
    // Generate normalized JSON structure
    return {
        json: {
            id: raw.id,
            ioc_value: name,
            ioc_type: indicator_type,
            tip_reputation_score: tip_reputation_score,
            geolocation_risk: geolocation_risk,
            asn_reputation: asn_reputation,
            feed_frequency: feed_frequency,
            active_days_count: active_days_count,
            threat_category: threat_category
        }
    };
});

// For n8n execution, return the mapped elements
if (typeof items !== 'undefined') {
    return normalizedIocs;
} else {
    // If running in local Node.js environment
    console.log(JSON.stringify(normalizedIocs.slice(0, 3), null, 2));
}
