# Microsoft Sentinel Built-in Analytics & Threat Detection
Source: https://learn.microsoft.com/en-us/azure/sentinel/detect-threats-built-in

Table of contents

Exit editor mode

Ask Learn

Ask Learn

Reading mode

Table of contents

Read in English

Add

Add to Plans

Edit

Copy Markdown

Print

Note

Access to this page requires authorization. You can try

signing in

or

changing directories

.

Access to this page requires authorization. You can try

changing directories

.

Threat detection in Microsoft Sentinel

Applies to: Microsoft Sentinel in the Microsoft Defender portal, Microsoft Sentinel in the Azure portal

Feedback

Summarize this article for me

Important

Custom detections

is now the best way to create new rules across Microsoft Sentinel SIEM Microsoft Defender XDR. With custom detections, you can reduce ingestion costs, get unlimited real-time detections, and benefit from seamless integration with Defender XDR data, functions, and remediation actions with automatic entity mapping. For more information, read

this blog

.

After

setting up Microsoft Sentinel to collect data from all over your organization

, you need to constantly dig through all that data to detect security threats to your environment. To accomplish this task, Microsoft Sentinel provides threat detection rules that run regularly, querying the collected data and analyzing it to discover threats. These rules come in a few different flavors and are collectively known as

analytics rules

.

These rules generate

alerts

when they find what theyâre looking for. Alerts contain information about the events detected, such as the

entities

(users, devices, addresses, and other items) involved. Alerts are aggregated and correlated into

incidents

âcase filesâthat you can

assign and investigate

to learn the full extent of the detected threat and respond accordingly. You can also build predetermined, automated responses into the rules' own configuration.

You can create these rules from scratch, using the

built-in analytics rule wizard

. However, Microsoft strongly encourages you to make use of the vast array of

analytics rule templates

available to you through the many

solutions for Microsoft Sentinel

provided in the content hub. These templates are pre-built rule prototypes, designed by teams of security experts and analysts based on their knowledge of known threats, common attack vectors, and suspicious activity escalation chains. You activate rules from these templates to automatically search across your environment for any activity that looks suspicious. Many of the templates can be customized to search for specific types of events, or filter them out, according to your needs.

This article helps you understand how Microsoft Sentinel detects threats, and what happens next.

Important

After

March 31, 2027

, Microsoft Sentinel will no longer be supported in the Azure portal and will be available only in the Microsoft Defender portal. All customers using Microsoft Sentinel in the Azure portal will be

redirected to the Defender portal and will use Microsoft Sentinel in the Defender portal only

.

If you're still using Microsoft Sentinel in the Azure portal, we recommend that you start planning your

transition to the Defender portal

to ensure a smooth transition and take full advantage of the

unified security operations experience offered by Microsoft Defender

.

Types of analytics rules

You can view the analytics rules and templates available for you to use on the

Analytics

page of the

Configuration

menu in Microsoft Sentinel. The currently

active rules

are visible in one tab, and

templates

to create new rules in another tab. A third tab displays

Anomalies

, a special rule type described later in this article.

To find more rule templates than are currently displayed, go to the

Content hub

in Microsoft Sentinel to install the related product solutions or standalone content. Analytics rule templates are available with nearly every product solution in the content hub.

The following types of analytics rules and rule templates are available in Microsoft Sentinel:

Scheduled rules

Near-real-time (NRT) rules

Anomaly rules

Microsoft security rules

Besides the preceding rule types, there are some other specialized template types that can each create one instance of a rule, with limited configuration options:

Threat intelligence

Advanced multistage attack detection ("Fusion")

Machine learning (ML) behavior analytics

Scheduled rules

By far the most common type of analytics rule,

Scheduled

rules are based on

Kusto queries

that are configured to run at regular intervals and examine raw data from a defined "lookback" period. If the number of results captured by the query passes the threshold configured in the rule, the rule produces an alert.

The queries in

scheduled rule templates

were written by security and data science experts, either from Microsoft or from the vendor of the solution providing the template. Queries can perform complex statistical operations on their target data, revealing baselines and outliers in groups of events.

The query logic is displayed in the rule configuration. You can use the query logic and the scheduling and lookback settings as defined in the template, or customize them to create new rules. Alternatively, you can create

entirely new rules from scratch

.

Learn more about

Scheduled analytics rules in Microsoft Sentinel

.

Near-real-time (NRT) rules

NRT rules are a limited subset of

scheduled rules

. They are designed to run once every minute, in order to supply you with information as up-to-the-minute as possible.

They function mostly like scheduled rules and are configured similarly, with some limitations.

Learn more about

Quick threat detection with near-real-time (NRT) analytics rules in Microsoft Sentinel

.

Anomaly rules

Anomaly rules use machine learning to observe specific types of behaviors over a period of time to determine a baseline. Each rule has its own unique parameters and thresholds, appropriate to the behavior being analyzed. After the observation period is completed, the baseline is set. When the rule observes behaviors that exceed the boundaries set in the baseline, it flags those occurrences as anomalous.

While the configurations of out-of-the-box rules can't be changed or fine-tuned, you can duplicate a rule, and then change and fine-tune the duplicate. In such cases, run the duplicate in

Flighting

mode and the original concurrently in

Production

mode. Then compare results, and switch the duplicate to

Production

if and when its fine-tuning is to your liking.

Anomalies don't necessarily indicate malicious or even suspicious behavior by themselves. Therefore, anomaly rules don't generate their own alerts. Rather, they record the results of their analysisâthe detected anomaliesâin the

Anomalies

table. You can query this table to provide context that improves your detections, investigations, and threat hunting.

For more information, see

Use customizable anomalies to detect threats in Microsoft Sentinel

and

Work with anomaly detection analytics rules in Microsoft Sentinel

.

Microsoft security rules

While scheduled and NRT rules automatically create incidents for the alerts they generate, alerts generated in external services and ingested to Microsoft Sentinel don't create their own incidents. Microsoft security rules automatically create Microsoft Sentinel incidents from the alerts generated in other Microsoft security solutions, in real time. You can use Microsoft security templates to create new rules with similar logic.

Important

Microsoft security rules are

not available

if you have:

Enabled

Microsoft Defender XDR incident integration

, or

Onboarded Microsoft Sentinel to the

Defender portal

.

In these scenarios, Microsoft Defender XDR creates the incidents instead.

Any such rules you had defined beforehand are automatically disabled.

For more information about

Microsoft security

incident creation rules, see

Automatically create incidents from Microsoft security alerts

.

Threat intelligence

Take advantage of threat intelligence produced by Microsoft to generate high fidelity alerts and incidents with the

Microsoft Threat Intelligence Analytics

rule. This unique rule isn't customizable, but when enabled, automatically matches Common Event Format (CEF) logs, Syslog data or Windows DNS events with domain, IP and URL threat indicators from Microsoft Threat Intelligence. Certain indicators contain more context information through MDTI (

Microsoft Defender Threat Intelligence

).

For more information on how to enable this rule, see

Use matching analytics to detect threats

.

For more information on MDTI, see

What is Microsoft Defender Threat Intelligence

.

Advanced multistage attack detection (Fusion)

Microsoft Sentinel uses the

Fusion correlation engine

, with its scalable machine learning algorithms, to detect advanced multistage attacks by correlating many low-fidelity alerts and events across multiple products into high-fidelity and actionable incidents. The

Advanced multistage attack detection

rule is enabled by default. Because the logic is hidden and therefore not customizable, there can be only one rule with this template.

The Fusion engine can also correlate alerts produced by

scheduled analytics rules

with alerts from other systems, producing high-fidelity incidents as a result.

Important

The

Advanced multistage attack detection

rule type is

not available

if you have:

Enabled

Microsoft Defender XDR incident integration

, or

Onboarded Microsoft Sentinel to the

Defender portal

.

In these scenarios, Microsoft Defender XDR creates the incidents instead.

Also, some of the

Fusion

detection templates are currently in

PREVIEW

(see

Advanced multistage attack detection in Microsoft Sentinel

to see which ones). See the

Supplemental Terms of Use for Microsoft Azure Previews

for additional legal terms that apply to Azure features that are in beta, preview, or otherwise not yet released into general availability.

Machine learning (ML) behavior analytics

Take advantage of Microsoft's proprietary machine learning algorithms to generate high fidelity alerts and incidents with the

ML Behavior Analytics

rules. These unique rules (currently in

Preview

) aren't customizable, but when enabled, detect specific anomalous SSH and RDP login behaviors based on IP and geolocation and user history information.

Access permissions for analytics rules

When you create an analytics rule, an access permissions token is applied to the rule and saved along with it. This token ensures that the rule can access the workspace that contains the data queried by the rule, and that this access is maintained even if the rule's creator loses access to that workspace.

There is one exception to this access, however: when a rule is created to access workspaces in other subscriptions or tenants, such as what happens in the case of an MSSP, Microsoft Sentinel takes extra security measures to prevent unauthorized access to customer data. For these kinds of rules, the credentials of the user that created the rule are applied to the rule instead of an independent access token, so that when the user no longer has access to the other subscription or tenant, the rule stops working.

If you operate Microsoft Sentinel in a cross-subscription or cross-tenant scenario, when one of your analysts or engineers loses access to a particular workspace, any rules created by that user stops working. In this situation, you get a health monitoring message regarding "insufficient access to resource", and the rule is

auto-disabled

after having failed a certain number of times.

Export rules to an ARM template

You can easily

export your rule to an Azure Resource Manager (ARM) template

if you want to manage and deploy your rules as code. You can also import rules from template files in order to view and edit them in the user interface.

Next steps

Learn more about

Scheduled analytics rules in Microsoft Sentinel

and

Quick threat detection with near-real-time (NRT) analytics rules in Microsoft Sentinel

.

To find more rule templates, see

Discover and manage Microsoft Sentinel out-of-the-box content

.

Feedback

Was this page helpful?

Yes

No

No

Need help with this topic?

Want to try using Ask Learn to clarify or guide you through this topic?

Ask Learn

Ask Learn

Suggest a fix?

Additional resources

Last updated on

2026-05-14