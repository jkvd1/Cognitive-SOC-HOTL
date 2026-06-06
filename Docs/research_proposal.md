# Implementation of an Automated Network Threat Intelligence Pipeline using n8n for Accelerated Incident Response

**Research Proposal for Scientific Paper (Non-Thesis Track)**

**Author:** Joshua Kenneth Van Dyon
**Role:** Final-year Cybersecurity Student and CTI Analyst  
**Institution:** Bina Nusantara  
**Date:** January 10, 2026

---

## Abstract

Modern Security Operations Centers (SOCs) face an escalating volume of cyber threats that exceed human analyst capacity, creating critical bottlenecks in incident response workflows. The manual transfer of Indicators of Compromise (IOCs)—such as malicious IP addresses and command-and-control domains—from Threat Intelligence Platforms (TIPs) to operational security teams introduces significant latency, increasing the Mean Time to Respond (MTTR) and expanding the Window of Exposure during active attacks. This research proposes the design and implementation of an automated network threat intelligence pipeline using n8n, a low-code workflow automation platform, to orchestrate real-time IOC distribution from the Cyfirma TIP via REST API. The system architecture comprises three core components: API-based data ingestion from Cyfirma, automated data normalization and false-positive filtering within n8n workflows, and real-time alert dissemination through Telegram Bot API with human-in-the-loop validation gates. By eliminating manual data entry and accelerating threat intelligence propagation, this automation pipeline aims to reduce processing time from minutes to seconds, minimize human error, and enhance overall network security posture through proactive defense mechanisms. The proposed system addresses a critical operational gap in contemporary SOC workflows and demonstrates practical application of Security Orchestration, Automation, and Response (SOAR) principles in resource-constrained environments.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Literature Review](#2-literature-review)
3. [Methodology](#3-methodology)
4. [Expected Results](#4-expected-results)
5. [Conclusion](#5-conclusion)
6. [References](#references)

---

## 1. Introduction

### 1.1 Background

The contemporary cyber threat landscape is characterized by an exponential increase in attack volume, sophistication, and velocity. Security Operations Centers worldwide process thousands of security alerts daily, with documented cases reporting over 22,000 weekly alerts in enterprise environments [1]. This overwhelming volume of threat data far exceeds the processing capacity of human security analysts, creating a fundamental asymmetry between defensive capabilities and adversarial activity. The speed of threat detection and remediation has become a critical determinant of organizational resilience, as adversaries exploit the temporal gap between initial compromise and defensive response—commonly referred to as the "Window of Exposure." In network defense operations, even marginal reductions in response latency can prevent lateral movement, data exfiltration, and system compromise. Cyber Threat Intelligence (CTI) serves as a foundational element of proactive defense, providing actionable information about adversary tactics, techniques, procedures, and infrastructure. However, the operational value of CTI is directly contingent upon the speed and accuracy with which intelligence is translated into defensive action.

### 1.2 Problem Statement

Despite significant investments in Threat Intelligence Platforms and security tooling, many organizations continue to rely on manual processes for operationalizing threat intelligence. In the current operational environment at [Organization Name], IOCs retrieved from the Cyfirma TIP—including malicious IP addresses, domain names, file hashes, and other technical indicators—are manually extracted, validated, and disseminated to security teams for remediation. This manual workflow introduces multiple failure points: human transcription errors compromise data integrity, processing delays extend the Window of Exposure, and analyst fatigue from repetitive tasks reduces overall SOC effectiveness. The latency inherent in manual data transfer creates a critical bottleneck between threat detection and remediation, directly impacting MTTR and organizational risk posture. Furthermore, the lack of standardized data formats and automated validation mechanisms increases the likelihood of false positives reaching production security controls, potentially disrupting legitimate business operations. These operational inefficiencies underscore the urgent need for automated orchestration mechanisms that can bridge the gap between threat intelligence acquisition and operational response.

### 1.3 Research Objectives

This research aims to design, implement, and evaluate an automated network threat intelligence pipeline that addresses the operational challenges identified above. The primary objectives are:

1. **Design a real-time API-based orchestration system** that automatically retrieves IOC data from the Cyfirma TIP using REST API calls, eliminating manual data extraction processes.

2. **Implement automated data processing workflows** within the n8n platform to normalize IOC formats, filter false positives, and enrich threat intelligence with contextual metadata.

3. **Establish a real-time alerting mechanism** using Telegram Bot API to disseminate validated IOCs to security analysts with minimal latency, enabling rapid decision-making.

4. **Integrate human-in-the-loop validation gates** to maintain analyst oversight and prevent erroneous automated actions while preserving the throughput benefits of automation.

5. **Evaluate the system's impact** on key operational metrics including processing time, data accuracy, and overall network security posture.

By achieving these objectives, this research will demonstrate a practical, cost-effective approach to implementing SOAR principles in resource-constrained SOC environments, contributing to the broader body of knowledge on threat intelligence automation and incident response optimization.

---

## 2. Literature Review

### 2.1 Cyber Threat Intelligence and Security Operations

Cyber Threat Intelligence has emerged as a critical capability for modern security operations, enabling organizations to transition from reactive incident response to proactive threat hunting and defense. The operational integration of CTI within Security Operations Centers represents a fundamental shift in defensive strategy, as documented in recent design science research [2]. Abdulrazaq and Kulugh demonstrate that systematic CTI integration reduces analyst workload and accelerates incident workflows, establishing a theoretical foundation for linking automation to improved incident outcomes [2]. This operational imperative is further reinforced by empirical studies correlating SOC maturity levels with incident response performance. Sohal's comprehensive analysis reveals that investments in SOAR-driven automation correlate with substantial reductions in Mean Time to Respond, though exact MTTR values vary by organizational maturity and operational context [3]. These findings underscore the strategic importance of CTI automation as a force multiplier for resource-constrained security teams.

### 2.2 Security Orchestration, Automation, and Response (SOAR)

The SOAR paradigm represents a systematic approach to addressing analyst burnout and operational inefficiency through intelligent automation of repetitive security tasks. Recent advances in AI-driven automated incident response systems have demonstrated remarkable performance improvements. Zhang et al. report that an AI-based Automated Incident Response (AIR) architecture achieved a 93% mean F1-score across multiple attack scenarios, with a 42% reduction in false negatives for command-and-control tunneling detection and a 39% reduction in false positives [1]. Critically, this system demonstrated an end-to-end processing latency of only 58.3 ms, providing empirical evidence that automated CTI ingestion and decisioning can operate at near-real-time speeds compared to manual enrichment workflows [1]. These quantitative results establish a compelling case for automation in high-velocity threat environments. The theoretical foundations of SOAR extend beyond simple task automation to encompass sophisticated orchestration patterns. Contemporary research emphasizes hyper-automation approaches using agentic artificial intelligence to enable adaptive, auditable automated responses while maintaining human oversight [4]. This evolution toward intelligent orchestration addresses earlier concerns about the complexity and potential latency introduced by naive multi-API aggregation patterns [5].

### 2.3 Impact of Automation on Incident Response Time

The relationship between automation and incident response performance has been extensively documented in recent literature, with consistent evidence of substantial operational improvements. The reduction of MTTR through automated threat intelligence processing represents a critical operational advantage in contemporary network defense. Zhang et al.'s AIR system not only achieved high detection accuracy but also demonstrated that automated pipelines can process threat intelligence with minimal latency—58.3 ms end-to-end—enabling security teams to respond to threats in near-real-time [1]. This dramatic reduction in processing time directly addresses the Window of Exposure problem, limiting adversary dwell time and reducing the potential impact of security incidents. Beyond latency improvements, automation significantly enhances data quality and operational consistency. The documented 39% reduction in false positives and 42% reduction in false negatives demonstrates that well-engineered automated systems can outperform manual processes in both speed and accuracy [1]. However, the literature also provides important caveats regarding automation implementation. Pigg notes that SOAR-enabled automation can introduce complexity and additional API-mediated aggregation steps, potentially increasing orchestration latency or error surfaces if not architected carefully [5]. This finding emphasizes the importance of thoughtful system design and validation mechanisms in automated threat intelligence pipelines.

### 2.4 API-Driven Orchestration and Real-Time Alerting

Modern threat intelligence architectures increasingly rely on API-driven orchestration patterns to enable real-time data exchange between disparate security tools. The adoption of standardized exchange formats, particularly STIX (Structured Threat Information eXpression) and TAXII (Trusted Automated eXchange of Intelligence Information), has facilitated unified data ingestion and automated action chains that materially lower processing latency [1]. These standards provide a common language for describing threat intelligence, enabling different security products to interoperate without custom parsing logic. Practical implementations of API-driven orchestration demonstrate the feasibility of integrating commercial TIPs with open-source automation platforms. Research on open-source SOAR platforms and threat intelligence orchestrators shows that connector-based architectures can successfully aggregate multiple threat feeds while maintaining acceptable performance characteristics [6]. However, operational analyses emphasize the need for robust API management, rate-limiting, and aggregation logic to avoid introducing additional latency or inconsistent alerting when composing multiple TIP sources [7]. The architectural recommendation emerging from this literature is clear: prefer standardized exchange formats, implement parallel API calls where possible, utilize local caching for high-frequency indicators, and design asynchronous playbooks to minimize the temporal gap between detection and actionable alerting [1].

### 2.5 Human-in-the-Loop Validation

While automation offers substantial operational benefits, the literature consistently emphasizes the critical role of human oversight in maintaining trust, auditability, and decision quality in security operations. Multiple recent studies argue that human-in-the-loop (HITL) validation mechanisms are essential to retain analyst expertise, improve explainability, and prevent unbounded automated actions in adversarial contexts [4], [8]. Mareedu's research on autonomous SOCs demonstrates that hybrid architectures combining automated triage with human approval gates achieve strong operational equilibria while preserving audit trails and explainability for analyst review [8]. The design patterns emerging from this research include confidence-based routing (where high-confidence, low-risk cases are auto-handled while lower-confidence cases are escalated to analysts), explicit human approval gates for high-impact remediation actions, and explainability outputs that provide concise model rationales or indicator provenance to accelerate analyst validation [4]. Empirical evidence suggests that HITL approaches reduce the risk of erroneous automated actions and help maintain SOC trust in automation while still achieving significant throughput gains when tasks are appropriately tiered by automation confidence [4]. This balanced approach addresses the dual imperatives of operational speed and analytical rigor in contemporary threat intelligence operations.

---

## 3. Methodology

### 3.1 System Architecture Overview

The proposed automated threat intelligence pipeline implements a three-stage architecture: **Ingestion → Normalization → Dissemination**. This design follows established SOAR orchestration patterns documented in recent literature [1], [6], adapted for deployment in a resource-constrained SOC environment. The system leverages n8n, an open-source low-code workflow automation platform, as the central orchestration engine. While the academic literature does not provide empirical validation of n8n specifically in cybersecurity contexts, the platform's REST API capabilities, JSON processing functions, and extensible connector architecture align with documented best practices for API-driven threat intelligence orchestration [1], [6].

### 3.2 Data Source: Cyfirma Threat Intelligence Platform

The primary data source for this pipeline is the Cyfirma TIP, a commercial threat intelligence platform that aggregates IOCs from multiple global threat feeds. The system retrieves threat intelligence data via Cyfirma's REST API, which provides structured JSON responses containing IOC metadata including:

- **Malicious IP addresses** (IPv4 and IPv6)
- **Command-and-control (C2) domain names**
- **File hashes** (MD5, SHA-1, SHA-256)
- **Threat actor attribution** and campaign context
- **Confidence scores** and temporal validity indicators

API authentication is implemented using token-based credentials with automatic refresh mechanisms to ensure continuous operation. The ingestion workflow executes on a configurable schedule (default: every 15 minutes) to balance real-time responsiveness with API rate-limit constraints. This polling interval aligns with industry practices for threat intelligence refresh cycles while avoiding excessive API load.

### 3.3 Processing Engine: n8n Workflow Automation

The n8n platform serves as the core processing engine, implementing the following automated workflows:

#### 3.3.1 Data Ingestion Workflow

1. **API Request Node**: Executes authenticated HTTP GET requests to Cyfirma API endpoints
2. **JSON Parser Node**: Extracts IOC data from API responses and validates schema compliance
3. **Error Handling**: Implements retry logic and fallback mechanisms for API failures

#### 3.3.2 Data Normalization and Filtering

1. **Format Standardization**: Converts IOC data to consistent internal schema (aligned with STIX 2.1 object models where applicable)
2. **Deduplication**: Compares incoming IOCs against historical database to eliminate redundant alerts
3. **False Positive Filtering**: Applies configurable whitelists to exclude known-good infrastructure (e.g., legitimate CDN IPs, corporate domains)
4. **Confidence Thresholding**: Filters IOCs based on Cyfirma confidence scores (default threshold: ≥70%) to reduce noise
5. **Enrichment**: Appends contextual metadata including threat type classification, geographic origin, and recommended remediation actions

#### 3.3.3 Data Quality Validation

To address concerns about automation introducing errors [5], the system implements multiple validation checkpoints:

- **Schema validation** against predefined IOC structure
- **Format verification** (e.g., IP address syntax, domain name validity)
- **Temporal validity checks** to exclude expired indicators
- **Cross-reference validation** against multiple threat intelligence sources (where available)

### 3.4 Output Interface: Telegram Bot API

Real-time alert dissemination is implemented via Telegram Bot API, chosen for its low latency, mobile accessibility, and ease of integration. The alerting workflow operates as follows:

#### 3.4.1 Alert Generation

1. **Message Formatting**: Constructs structured alert messages containing:
   - IOC type and value (e.g., "Malicious IP: 192.0.2.1")
   - Threat classification and severity level
   - Confidence score and source attribution
   - Recommended remediation actions
   - Timestamp and unique alert identifier

2. **Priority Routing**: Implements severity-based routing to different Telegram channels:
   - **Critical alerts** (high-confidence C2 infrastructure): Immediate notification to on-call analysts
   - **Medium alerts** (suspicious but lower confidence): Routed to general SOC channel for review
   - **Low alerts** (informational IOCs): Logged for historical analysis

#### 3.4.2 Interactive Response Mechanisms

The Telegram bot implements interactive buttons enabling analysts to:

- **Approve** IOC for immediate blocking at firewall/IPS layer
- **Reject** IOC as false positive (with feedback loop to improve filtering)
- **Request additional context** (triggers automated enrichment query)
- **Escalate** to senior analyst or incident response team

### 3.5 Human-in-the-Loop Validation

Consistent with literature recommendations on HITL approaches [4], [8], the system implements a mandatory validation gate before any automated remediation action. This design preserves analyst oversight while maintaining throughput benefits:

1. **Validation Requirement**: No IOC is automatically blocked without explicit analyst approval via Telegram interface
2. **Confidence-Based Routing**: High-confidence IOCs (≥90%) are flagged for expedited review, while lower-confidence indicators undergo enhanced scrutiny
3. **Audit Trail**: All analyst decisions (approve/reject/escalate) are logged with timestamps and analyst identifiers for compliance and retrospective analysis
4. **Feedback Loop**: Analyst rejections are fed back into the filtering logic to continuously improve false positive reduction

This HITL design addresses the dual imperatives of operational speed and analytical rigor, ensuring that automation enhances rather than replaces human expertise [4], [8].

### 3.6 Integration with Security Infrastructure

Upon analyst approval, validated IOCs are automatically propagated to downstream security controls:

1. **Firewall Rules**: Automated API calls to firewall management interfaces to block malicious IPs
2. **DNS Filtering**: Updates to DNS blacklists to prevent resolution of malicious domains
3. **SIEM Integration**: IOC data forwarded to Security Information and Event Management (SIEM) system for correlation with internal security events
4. **Threat Intelligence Database**: Validated IOCs stored in internal threat intelligence repository for historical analysis and threat hunting

### 3.7 Performance Monitoring and Metrics

The system implements comprehensive logging and metrics collection to evaluate operational impact:

- **Processing Time**: Measures end-to-end latency from API ingestion to analyst notification
- **Accuracy Metrics**: Tracks false positive and false negative rates based on analyst feedback
- **Throughput**: Monitors number of IOCs processed per time period
- **Analyst Response Time**: Measures time from alert notification to analyst decision
- **System Availability**: Tracks uptime and API failure rates

These metrics enable continuous optimization and provide quantitative evidence of the system's impact on SOC operations, following the measurement frameworks established in recent SOAR research [1], [3].

---

## 4. Expected Results

### 4.1 Reduction in Processing Time

The primary expected outcome is a dramatic reduction in IOC processing time. Based on empirical evidence from similar automated incident response systems [1], the proposed pipeline is expected to reduce processing time from the current manual baseline (estimated 5-15 minutes per IOC batch) to near-real-time performance (under 60 seconds from API ingestion to analyst notification). This improvement directly addresses the Window of Exposure problem by accelerating the transition from threat detection to defensive action. The automated workflow eliminates multiple manual steps including: logging into the Cyfirma portal, manually copying IOC data, formatting for internal systems, and distributing via email or ticketing systems. By replacing these manual processes with API-driven automation, the system is expected to achieve processing latencies comparable to the 58.3 ms end-to-end performance reported in advanced AIR systems [1], though actual performance will depend on API response times and network latency in the deployment environment.

### 4.2 Elimination of Manual Data Entry Errors

Automated data extraction and normalization are expected to eliminate human transcription errors that currently compromise IOC data integrity. Manual data entry introduces multiple error vectors including typographical mistakes (e.g., incorrect IP octets), format inconsistencies (e.g., mixed date formats), and incomplete data transfer (e.g., missing confidence scores or context). The proposed system's schema validation and format verification mechanisms ensure that only syntactically correct, complete IOC records are propagated to downstream security controls. This improvement in data quality is expected to reduce false negatives caused by malformed IOCs and decrease analyst time spent troubleshooting data integrity issues. The literature documents that well-engineered automated systems can achieve substantial reductions in false positives (39%) and false negatives (42%) compared to manual processes [1], providing a benchmark for expected data quality improvements.

### 4.3 Improvement in Network Security Posture

The combined effects of reduced processing time and improved data quality are expected to yield measurable improvements in overall network security posture:

1. **Reduced Mean Time to Respond (MTTR)**: Faster IOC propagation enables more rapid blocking of malicious infrastructure, limiting adversary operational windows. Based on SOC maturity research [3], organizations implementing SOAR automation report substantial MTTR reductions, though exact values vary by operational context.

2. **Enhanced Threat Coverage**: Automated processing enables the SOC to operationalize a higher volume of threat intelligence than manual workflows permit, expanding defensive coverage against emerging threats.

3. **Improved Analyst Efficiency**: By automating repetitive data transfer tasks, the system frees analyst time for higher-value activities including threat hunting, incident investigation, and strategic threat analysis. This addresses the analyst burnout problem documented in SOAR literature [2], [4].

4. **Proactive Defense Posture**: Real-time IOC distribution enables preemptive blocking of known-malicious infrastructure before it is observed in internal network traffic, shifting from reactive to proactive defense [9].

5. **Operational Consistency**: Automated workflows ensure consistent application of threat intelligence across all security controls, eliminating gaps caused by manual oversight or inconsistent procedures.

### 4.4 Quantitative Success Metrics

The system's effectiveness will be evaluated against the following quantitative metrics:

- **Processing Time Reduction**: Target ≥80% reduction in average time from IOC availability to analyst notification
- **Data Accuracy**: Target ≥95% IOC format correctness (validated via automated schema checks)
- **False Positive Rate**: Target ≤10% false positive rate based on analyst feedback
- **Analyst Satisfaction**: Qualitative assessment via post-deployment surveys
- **System Reliability**: Target ≥99% uptime for automated workflows

These metrics align with performance benchmarks established in recent SOAR and automated incident response research [1], [3], [4], providing a rigorous framework for evaluating the system's operational impact.

---

## 5. Conclusion

This research proposal presents a practical, cost-effective approach to implementing automated threat intelligence distribution in resource-constrained SOC environments. By leveraging API-driven orchestration, low-code automation platforms, and human-in-the-loop validation mechanisms, the proposed system addresses critical operational bottlenecks in contemporary network defense operations. The literature review establishes a strong theoretical foundation for this work, demonstrating that SOAR-driven automation can achieve substantial improvements in detection accuracy, processing latency, and overall incident response effectiveness [1], [3], [4]. The proposed methodology adapts these academic findings to a practical implementation context, balancing the operational benefits of automation with the need for analyst oversight and data quality assurance [4], [8].

The expected results—dramatic reductions in processing time, elimination of manual errors, and improved network security posture—directly address the research objectives and provide measurable value to the organization. By minimizing the Window of Exposure and reducing MTTR, this system contributes to a more resilient defensive posture against contemporary cyber threats. Furthermore, this research demonstrates the feasibility of implementing SOAR principles using accessible, low-code platforms, potentially lowering the barrier to entry for organizations lacking resources for enterprise SOAR solutions.

Future work will focus on system implementation, empirical evaluation of operational metrics, and iterative refinement based on analyst feedback. Additional research directions include integration of machine learning models for automated false positive filtering, expansion to additional threat intelligence sources beyond Cyfirma, and investigation of fully autonomous remediation workflows for high-confidence, low-risk IOCs. This research contributes to the growing body of knowledge on practical threat intelligence automation and operational security optimization, with potential applications across diverse organizational contexts.

---

## References

[1] J. Zhang, S. Li, W. Huang, H. Jing, and Q. Zhang, "Design and Computational Modeling of an AI-Based Automated Cybersecurity Incident Response System," *IEEE Access*, 2025. DOI: [10.1109/access.2025.3603975](https://doi.org/10.1109/access.2025.3603975)

[2] U. F. Abdulrazaq and V. E. Kulugh, "Operational Integration of Cyber Threat Intelligence in Modern Security Operations Centers: A Design Science Approach," 2024.

[3] S. Sohal, "Correlating SOC Maturity Levels with Incident Response Outcomes: An Empirical Study," 2024.

[4] Ismail, R. Kurnia, Z. A. Brata, G. A. Nelistiani, and S. Heo, "Toward Robust Security Orchestration and Automated Response in Security Operations Centers with a Hyper-Automation Approach Using Agentic Artificial Intelligence," 2024.

[5] H. Pigg, "Threat Intelligence Automation and Optimization Through SOAR Integration," 2024.

[6] V. G. Bilali, D. Kosyvas, and T. Theodoropoulos, "Iris Advanced Threat Intelligence Orchestrator—A Way to Manage Cybersecurity Challenges of IoT Ecosystems in Smart Cities," 2024.

[7] M. Mennuni, "An Analysis of SOC Monitoring Systems," 2024.

[8] A. Mareedu, "Autonomous Security Operations Centers (SOC): AI Agents for Threat Triage, Response, and Orchestration," 2025. DOI: [10.63282/3050-922x.ijeret-v6i2p108](https://doi.org/10.63282/3050-922x.ijeret-v6i2p108)

[9] S. M. I. Mahadi, S. K. Mallik, N. R. Shatu, and M. Rahman, "From Reactive to Proactive: Engineering a Next-Generation Cyber Threat Response Emergency Operations Center (EOC) for Financial Institutions," *American Journal of Geospatial Technology*, 2025. DOI: [10.54536/ajgt.v4i1.5355](https://doi.org/10.54536/ajgt.v4i1.5355)

---

**End of Research Proposal**
