# 🏛️ Enterprise SecOps Master Guide: Microsoft Defender XDR & Microsoft Sentinel

Source: Enterprise Security Architecture & Operations Guide

This guide provides an end-to-end blueprint for architecting, deploying, and operating Microsoft Defender XDR and Microsoft Sentinel within an enterprise environment. It covers unified SecOps architecture, enterprise deployment across all pillars, advanced KQL correlation, SOAR automation, threat hunting, and cost governance.

---

## 1. Enterprise Architecture & Strategy

In a modern enterprise Security Operations Center (SOC), Microsoft Defender XDR handles localized, high-fidelity detection and response across domain workloads, while Microsoft Sentinel aggregates cross-platform telemetry, provides multi-cloud visibility, and drives top-level SIEM/SOAR orchestration.

### 🔑 Key Integration Principles
- **Single Pane of Glass (Unified SecOps):** Incident queue bi-directional synchronization ensures that closing an incident in Sentinel automatically resolves it in Defender XDR and vice-versa.
- **Separation of Duties:**
  - **Defender XDR:** Domain-specific context, process-tree execution analysis, file quarantine, memory injection analysis, device isolation.
  - **Microsoft Sentinel:** Cross-domain timeline construction, non-Microsoft log ingestion (Firewalls, Identity Providers, Cloud infrastructure), long-term compliance retention, and cross-system orchestration.

---

## 2. Microsoft Defender XDR Enterprise Deployment

### 2.1 Microsoft Defender for Endpoint (MDE)
- **Onboarding Strategy:** Deploy via Microsoft Intune (Configuration Profiles) for endpoints, and Group Policy (GPO) or Azure Arc for on-premises servers.
- **Attack Surface Reduction (ASR) Rules:** Deploy initial rules in Audit mode for 14 days, analyze telemetry in MDE, then convert to Block mode. Critical rules include:
  - Block executable content from email client and webmail
  - Block Office applications from creating child processes
  - Block credential stealing from the Windows Local Security Authority subsystem (lsass.exe)
  - Block Process creations originating from PSExec and WMI commands
- **EDR in Block Mode:** Enable to allow Defender Antivirus to remediate malicious artifacts even when a 3rd party EDR/AV is running as primary.

### 2.2 Microsoft Defender for Office 365 (MDO)
- **Safe Links & Safe Attachments:**
  - Configure Safe Links with Real-time URL scanning and `UrlClickEvents` logging.
  - Enable Safe Attachments using Dynamic Delivery mode (delivers email immediately while attachment undergoes sandbox detonation).
- **Automated Investigation & Response (AIR):** Set execution action level to Full Automation for endpoint and mailbox threats to enable auto-remediation of phishing campaigns.

### 2.3 Microsoft Defender for Identity (MDI)
- **Sensor Deployment:** Install MDI Sensors directly on all Active Directory Domain Controllers (DCs) and Active Directory Federation Services (AD FS) servers.
- **Honeytoken Strategy:** Create decoy AD accounts with weak passwords and attractive names (e.g., `svc-sql-admin`). Configure them as Honeytokens in Defender for Identity to trigger instant alerts upon kerberoasting or authentication attempts.
- **Lateral Movement Paths (LMP):** Monitor non-expiring privileged credentials logged on to non-sensitive endpoints.

### 2.4 Microsoft Defender for Cloud Apps (MDA) & Defender for Cloud (MDC)
- **Conditional Access App Control:** Route high-risk SaaS sessions (e.g., unmanaged device accessing SharePoint) through Defender for Cloud Apps proxy to prevent file downloads and clipboard pasting.
- **Defender for Cloud Posture Management:** Enforce Agentless vulnerability scanning for Azure, AWS, and GCP virtual machine instances to maintain real-time security posture (CSPM).

---

## 3. Microsoft Sentinel Enterprise Architecture & Configuration

### 3.1 Workspace Architecture Options
- **Recommended Pattern:** A Single Log Analytics Workspace (LAW) per region/compliance boundary is preferred for maximum detection efficacy and simplified KQL correlation. Use Azure Lighthouse for multi-tenant MSSP scenarios.
- **Data Tiers:**
  1. **Analytics Logs:** 30-90 Days Hot Data for Active KQL & Detections
  2. **Basic Logs:** High-Volume Verbose Logs (NetFlow, VPC Flow Logs)
  3. **Archive Tier:** Long-Term Compliance Storage up to 7 Years

### 3.2 Data Ingestion & Cost Optimization Strategy
- **Free Defender Alerts & Incidents Ingestion:** Ingesting alerts and incidents from Defender XDR into Sentinel is free of charge.
- **Data Collection Rules (DCRs) & Azure Monitor Agent (AMA):** Replace legacy Log Analytics Agent (MMA) with AMA. Use XPath queries in DCRs to filter out noisy Event IDs (e.g., ingest Security Event ID 4624 [Successful Logon] and 4625 [Failed Logon], but drop noisy 4688 [Process Creation] if process logs are already ingested via MDE `DeviceProcessEvents`).

---

## 4. Advanced KQL Threat Correlation & Hunting

### 4.1 Scenario A: Detecting Pass-the-Hash / LSASS Credential Dumping to Lateral Movement
```kql
// Detects LSASS process access on Endpoint followed by SMB/RDP logon to another machine within 15 minutes
let DumpEvents = 
    DeviceEvents
    | where ActionType == "LsassHexDump" or (ActionType == "OpenProcessApiCall" and AdditionalFields.DesiredAccess == "0x1410")
    | project DumpTime = Timestamp, DumpDevice = DeviceName, AccountName = InitiatingProcessAccountName, ReportId;
let LateralLogons = 
    IdentityLogonEvents
    | where LogonType in ("Network", "RemoteInteractive") and Protocol in ("NTLM", "Kerberos", "RDP")
    | project LogonTime = Timestamp, TargetDevice = DeviceName, AccountName, IPAddress;
DumpEvents
| join kind=inner (LateralLogons) on AccountName
| where LogonTime between (DumpTime .. (DumpTime + 15m)) and DumpDevice != TargetDevice
| project DumpTime, LogonTime, AccountName, SourceDevice = DumpDevice, TargetDevice, IPAddress
```

### 4.2 Scenario B: Phishing Email Link Click Leading to Malicious PowerShell Execution
```kql
// Correlates Defender for Office 365 URL clicks with Defender for Endpoint process creation
let ClickedURLs = 
    UrlClickEvents
    | where Workload == "Email" and ActionType == "ClickAllowed"
    | project ClickTime = Timestamp, AccountUpn = UserEmail, ClickedUrl = Url;
let SuspiciousPowerShell = 
    DeviceProcessEvents
    | where ProcessCommandLine has_any ("-enc", "-encodedcommand", "downloadstring", "iex", "bypass")
    | project ProcessTime = Timestamp, DeviceName, AccountUpn = AccountUserPrincipalName, FileName, ProcessCommandLine;
ClickedURLs
| join kind=inner (SuspiciousPowerShell) on AccountUpn
| where ProcessTime between (ClickTime .. (ClickTime + 10m))
| project ClickTime, ProcessTime, AccountUpn, DeviceName, ClickedUrl, ProcessCommandLine
```

---

## 5. SOAR & Automated Incident Response (Playbooks)

### 5.1 Sentinel Automation Rules vs. Logic Apps
- **Automation Rules:** High-level triage, tagging, assignment, suppressor logic (e.g., Assign high-severity incidents to Tier 2 Analyst; change status to In Progress).
- **Logic App Playbooks:** Complex workflows requiring external API calls & orchestration (e.g., Isolate device via MDE API, disable user in Entra ID, open ticket in ServiceNow).
- **Implementation Tip:** Always use Managed Identities (System-Assigned) for Logic App authentication to Azure Graph API and Defender APIs instead of hardcoded secrets or service principal passwords.

---

## 6. Enterprise Operations & Cost Governance

### 6.1 Tiered SOC Operating Model
- **Tier 1 (Triage & Automation):** Automated Playbook Validation, True Positive / False Positive triage, Standard SOP Execution.
- **Tier 2 (Incident Response):** Root Cause Analysis, Live Response PowerShell execution, Complex Remediation Tuning.
- **Tier 3 (Threat Hunting):** Proactive KQL Hunting, Custom Detection Engineering, Deep Forensic Detonation.

### 6.2 Key Operational Metrics (KPIs)
- **Mean Time to Detect (MTTD):** Target < 15 minutes via automated XDR correlation rules.
- **Mean Time to Acknowledge (MTTA):** Target < 10 minutes for Tier 1 triage.
- **Mean Time to Remediate (MTTR):** Target < 30 minutes for automated workflows; < 2 hours for manual Tier 2 containment.

### 6.3 Cost Optimization Best Practices
- **Enable Commitment Tiers:** If log ingestion exceeds 100 GB/day in Log Analytics, switch from Pay-As-You-Go to Commitment Tiers (saves up to 30-50%).
- **Table Level Transformation Rules:** Use KQL transformations in Data Collection Rules (DCRs) to filter out unnecessary columns prior to ingestion.
- **Move Compliance Logs to Archive:** Set active ingestion retention to 90 Days for Sentinel, and move long-term retention data to Log Analytics Archive (very low cost per GB/month).

---

## Summary
Integrating Defender XDR with Sentinel creates a complete enterprise defense loop. Defender provides local auto-healing and rich telemetry; Sentinel provides cross-cloud intelligence, custom KQL correlation, and enterprise-wide SOAR governance.
