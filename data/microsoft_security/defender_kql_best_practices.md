# Microsoft Defender Advanced Hunting KQL Performance & Best Practices

Source URL: https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-best-practices


Note

Access to this page requires authorization. You can try signing in or changing directories.

Access to this page requires authorization. You can try changing directories.

Advanced hunting query best practices

Get results faster and avoid timeouts while running complex queries by optimizing your queries. For guidance on improving query performance:

General optimization tips - in this article
Optimize the join operator - in this article
Optimize the summarize operator - in this article
Query scenarios - in this article
Kusto query best practices - includes several scenarios for making your query more efficient
Optimize log queries in Azure Monitor - contains additional guidance for query optimization
Optimizing KQL queries (video) - most common ways to improve your query

join

summarize

Understand CPU resource quotas

Depending on its size, each tenant has access to a set amount of CPU resources allocated for running advanced hunting queries. For detailed information about various usage parameters, read about advanced hunting quotas and usage parameters.

After running your query, you can see the execution time and its resource usage (Low, Medium, High). High indicates that the query took more resources to run and could be improved to return results more efficiently.

Customers who run multiple queries regularly should track consumption and apply the optimization guidance in this article to minimize disruption resulting from exceeding quotas or usage parameters.

General optimization tips

Size new queriesâIf you suspect that a query will return a large result set, assess it first using the count operator. Use limit or its synonym take to avoid large result sets.

Apply filters earlyâApply time filters and other filters to reduce the data set, especially before using transformation and parsing functions, such as substring(), replace(), trim(), toupper(), or parse_json(). In the example below, the parsing function extractjson() is used after filtering operators have reduced the number of records.
DeviceEvents
| where Timestamp > ago(1d)
| where ActionType == "UsbDriveMount"
| where DeviceName == "user-desktop.domain.com"
| extend DriveLetter = extractjson("$.DriveLetter", AdditionalFields)


Has beats containsâTo avoid searching substrings within words unnecessarily, use the has operator instead of contains. Learn about string operators

Scope your searchâAvoid running unscoped search or union queries, as they span all tables in the schema and could exceed query size limits in environments with many tables. Use search in to specify the tables you want to search. For example, instead of search "email", use search in (EmailEvents, EmailAttachmentInfo, IdentityInfo) "email".

Look in specific columnsâLook in a specific column rather than running full text searches. Don't use * to check all columns.

Case-sensitive for speedâCase-sensitive searches are more specific and generally more performant. Names of case-sensitive string operators, such as has_cs and contains_cs, generally end with _cs. You can also use the case-sensitive equals operator == instead of =~.

Parse, don't extractâWhenever possible, use the parse operator or a parsing function like parse_json(). Avoid the matches regex string operator or the extract() function, both of which use regular expression. Reserve the use of regular expression for more complex scenarios. Read more about parsing functions

Filter tables not expressionsâDon't filter on a calculated column if you can filter on a table column.

No three-character termsâAvoid comparing or filtering using terms with three characters or fewer. These terms are not indexed and matching them will require more resources.

Project selectivelyâMake your results easier to understand by projecting only the columns you need. Projecting specific columns prior to running join or similar operations also helps improve performance.

Size new queriesâIf you suspect that a query will return a large result set, assess it first using the count operator. Use limit or its synonym take to avoid large result sets.

take

Apply filters earlyâApply time filters and other filters to reduce the data set, especially before using transformation and parsing functions, such as substring(), replace(), trim(), toupper(), or parse_json(). In the example below, the parsing function extractjson() is used after filtering operators have reduced the number of records.

DeviceEvents
| where Timestamp > ago(1d)
| where ActionType == "UsbDriveMount"
| where DeviceName == "user-desktop.domain.com"
| extend DriveLetter = extractjson("$.DriveLetter", AdditionalFields)

DeviceEvents
| where Timestamp > ago(1d)
| where ActionType == "UsbDriveMount"
| where DeviceName == "user-desktop.domain.com"
| extend DriveLetter = extractjson("$.DriveLetter", AdditionalFields)

Has beats containsâTo avoid searching substrings within words unnecessarily, use the has operator instead of contains. Learn about string operators

has

contains

Scope your searchâAvoid running unscoped search or union queries, as they span all tables in the schema and could exceed query size limits in environments with many tables. Use search in to specify the tables you want to search. For example, instead of search "email", use search in (EmailEvents, EmailAttachmentInfo, IdentityInfo) "email".

search

union

search in

search "email"

search in (EmailEvents, EmailAttachmentInfo, IdentityInfo) "email"

Look in specific columnsâLook in a specific column rather than running full text searches. Don't use * to check all columns.

*

Case-sensitive for speedâCase-sensitive searches are more specific and generally more performant. Names of case-sensitive string operators, such as has_cs and contains_cs, generally end with _cs. You can also use the case-sensitive equals operator == instead of =~.

has_cs

contains_cs

_cs

==

=~

Parse, don't extractâWhenever possible, use the parse operator or a parsing function like parse_json(). Avoid the matches regex string operator or the extract() function, both of which use regular expression. Reserve the use of regular expression for more complex scenarios. Read more about parsing functions

matches regex

Filter tables not expressionsâDon't filter on a calculated column if you can filter on a table column.

No three-character termsâAvoid comparing or filtering using terms with three characters or fewer. These terms are not indexed and matching them will require more resources.

Project selectivelyâMake your results easier to understand by projecting only the columns you need. Projecting specific columns prior to running join or similar operations also helps improve performance.

Optimize the join operator

join

The join operator merges rows from two tables by matching values in specified columns. Apply these tips to optimize queries that use this operator.

Smaller table to your leftâThe join operator matches records in the table on the left side of your join statement to records on the right. By having the smaller table on the left, fewer records will need to be matched, thus speeding up the query.
In the table below, we reduce the left table DeviceLogonEvents to cover only three specific devices before joining it with IdentityLogonEvents by account SIDs.
DeviceLogonEvents
| where DeviceName in ("device-1.domain.com", "device-2.domain.com", "device-3.domain.com")
| where ActionType == "LogonFailed"
| join
    (IdentityLogonEvents
    | where ActionType == "LogonFailed"
    | where Protocol == "Kerberos")
on AccountSid


Use the inner-join flavorâThe default join flavor or the innerunique-join deduplicates rows in the left table by the join key before returning a row for each match to the right table. If the left table has multiple rows with the same value for the join key, those rows will be deduplicated to leave a single random row for each unique value.
This default behavior can leave out important information from the left table that can provide useful insight. For example, the query below will only show one email containing a particular attachment, even if that same attachment was sent using multiple emails messages:
EmailAttachmentInfo
| where Timestamp > ago(1h)
| where Subject == "Document Attachment" and FileName == "Document.pdf"
| join (DeviceFileEvents | where Timestamp > ago(1h)) on SHA256

To address this limitation, we apply the inner-join flavor by specifying kind=inner to show all rows in the left table with matching values in the right:
EmailAttachmentInfo
| where Timestamp > ago(1h)
| where Subject == "Document Attachment" and FileName == "Document.pdf"
| join kind=inner (DeviceFileEvents | where Timestamp > ago(1h)) on SHA256


Join records from a time windowâWhen investigating security events, analysts look for related events that occur around the same time period. Applying the same approach when using join also benefits performance by reducing the number of records to check.
The query below checks for logon events within 30 minutes of receiving a malicious file:
EmailEvents
| where Timestamp > ago(7d)
| where ThreatTypes has "Malware"
| project EmailReceivedTime = Timestamp, Subject, SenderFromAddress, AccountName = tostring(split(RecipientEmailAddress, "@")[0])
| join (
DeviceLogonEvents
| where Timestamp > ago(7d)
| project LogonTime = Timestamp, AccountName, DeviceName
) on AccountName
| where (LogonTime - EmailReceivedTime) between (0min .. 30min)


Apply time filters on both sidesâEven if you're not investigating a specific time window, applying time filters on both the left and right tables can reduce the number of records to check and improve join performance. The query below applies Timestamp > ago(1h) to both tables so that it joins only records from the past hour:
EmailAttachmentInfo
| where Timestamp > ago(1h)
| where Subject == "Document Attachment" and FileName == "Document.pdf"
| join kind=inner (DeviceFileEvents | where Timestamp > ago(1h)) on SHA256


Use hints for performanceâUse hints with the join operator to instruct the backend to distribute load when running resource-intensive operations. Learn more about join hints.
For example, the shuffle hint helps improve query performance when joining tables using a key with high cardinalityâa key with many unique valuesâsuch as the AccountObjectId in the query below:
IdentityInfo
| where JobTitle == "CONSULTANT"
| join hint.shufflekey = AccountObjectId
(IdentityDirectoryEvents
    | where Application == "Active Directory"
    | where ActionType == "Private data retrieval")
on AccountObjectId

The broadcast hint helps when the left table is small (up to 100,000 records) and the right table is extremely large. For example, the query below is trying to join a few emails that have specific subjects with all messages containing links in the EmailUrlInfo table:
EmailEvents
| where Subject in ("Warning: Update your credentials now", "Action required: Update your credentials now")
| join hint.strategy = broadcast EmailUrlInfo on NetworkMessageId

Smaller table to your leftâThe join operator matches records in the table on the left side of your join statement to records on the right. By having the smaller table on the left, fewer records will need to be matched, thus speeding up the query.

join

In the table below, we reduce the left table DeviceLogonEvents to cover only three specific devices before joining it with IdentityLogonEvents by account SIDs.

DeviceLogonEvents

IdentityLogonEvents

DeviceLogonEvents
| where DeviceName in ("device-1.domain.com", "device-2.domain.com", "device-3.domain.com")
| where ActionType == "LogonFailed"
| join
    (IdentityLogonEvents
    | where ActionType == "LogonFailed"
    | where Protocol == "Kerberos")
on AccountSid

DeviceLogonEvents
| where DeviceName in ("device-1.domain.com", "device-2.domain.com", "device-3.domain.com")
| where ActionType == "LogonFailed"
| join
    (IdentityLogonEvents
    | where ActionType == "LogonFailed"
    | where Protocol == "Kerberos")
on AccountSid

Use the inner-join flavorâThe default join flavor or the innerunique-join deduplicates rows in the left table by the join key before returning a row for each match to the right table. If the left table has multiple rows with the same value for the join key, those rows will be deduplicated to leave a single random row for each unique value.

join

This default behavior can leave out important information from the left table that can provide useful insight. For example, the query below will only show one email containing a particular attachment, even if that same attachment was sent using multiple emails messages:

EmailAttachmentInfo
| where Timestamp > ago(1h)
| where Subject == "Document Attachment" and FileName == "Document.pdf"
| join (DeviceFileEvents | where Timestamp > ago(1h)) on SHA256

EmailAttachmentInfo
| where Timestamp > ago(1h)
| where Subject == "Document Attachment" and FileName == "Document.pdf"
| join (DeviceFileEvents | where Timestamp > ago(1h)) on SHA256

To address this limitation, we apply the inner-join flavor by specifying kind=inner to show all rows in the left table with matching values in the right:

kind=inner

EmailAttachmentInfo
| where Timestamp > ago(1h)
| where Subject == "Document Attachment" and FileName == "Document.pdf"
| join kind=inner (DeviceFileEvents | where Timestamp > ago(1h)) on SHA256

EmailAttachmentInfo
| where Timestamp > ago(1h)
| where Subject == "Document Attachment" and FileName == "Document.pdf"
| join kind=inner (DeviceFileEvents | where Timestamp > ago(1h)) on SHA256

Join records from a time windowâWhen investigating security events, analysts look for related events that occur around the same time period. Applying the same approach when using join also benefits performance by reducing the number of records to check.

join

The query below checks for logon events within 30 minutes of receiving a malicious file:

EmailEvents
| where Timestamp > ago(7d)
| where ThreatTypes has "Malware"
| project EmailReceivedTime = Timestamp, Subject, SenderFromAddress, AccountName = tostring(split(RecipientEmailAddress, "@")[0])
| join (
DeviceLogonEvents
| where Timestamp > ago(7d)
| project LogonTime = Timestamp, AccountName, DeviceName
) on AccountName
| where (LogonTime - EmailReceivedTime) between (0min .. 30min)

EmailEvents
| where Timestamp > ago(7d)
| where ThreatTypes has "Malware"
| project EmailReceivedTime = Timestamp, Subject, SenderFromAddress, AccountName = tostring(split(RecipientEmailAddress, "@")[0])
| join (
DeviceLogonEvents
| where Timestamp > ago(7d)
| project LogonTime = Timestamp, AccountName, DeviceName
) on AccountName
| where (LogonTime - EmailReceivedTime) between (0min .. 30min)

Apply time filters on both sidesâEven if you're not investigating a specific time window, applying time filters on both the left and right tables can reduce the number of records to check and improve join performance. The query below applies Timestamp > ago(1h) to both tables so that it joins only records from the past hour:

join

Timestamp > ago(1h)

EmailAttachmentInfo
| where Timestamp > ago(1h)
| where Subject == "Document Attachment" and FileName == "Document.pdf"
| join kind=inner (DeviceFileEvents | where Timestamp > ago(1h)) on SHA256

EmailAttachmentInfo
| where Timestamp > ago(1h)
| where Subject == "Document Attachment" and FileName == "Document.pdf"
| join kind=inner (DeviceFileEvents | where Timestamp > ago(1h)) on SHA256

Use hints for performanceâUse hints with the join operator to instruct the backend to distribute load when running resource-intensive operations. Learn more about join hints.

join

For example, the shuffle hint helps improve query performance when joining tables using a key with high cardinalityâa key with many unique valuesâsuch as the AccountObjectId in the query below:

AccountObjectId

IdentityInfo
| where JobTitle == "CONSULTANT"
| join hint.shufflekey = AccountObjectId
(IdentityDirectoryEvents
    | where Application == "Active Directory"
    | where ActionType == "Private data retrieval")
on AccountObjectId

IdentityInfo
| where JobTitle == "CONSULTANT"
| join hint.shufflekey = AccountObjectId
(IdentityDirectoryEvents
    | where Application == "Active Directory"
    | where ActionType == "Private data retrieval")
on AccountObjectId

The broadcast hint helps when the left table is small (up to 100,000 records) and the right table is extremely large. For example, the query below is trying to join a few emails that have specific subjects with all messages containing links in the EmailUrlInfo table:

EmailUrlInfo

EmailEvents
| where Subject in ("Warning: Update your credentials now", "Action required: Update your credentials now")
| join hint.strategy = broadcast EmailUrlInfo on NetworkMessageId

EmailEvents
| where Subject in ("Warning: Update your credentials now", "Action required: Update your credentials now")
| join hint.strategy = broadcast EmailUrlInfo on NetworkMessageId

Optimize the summarize operator

summarize

The summarize operator aggregates the contents of a table. Apply these tips to optimize queries that use this operator.

Find distinct valuesâIn general, use summarize to find distinct values that can be repetitive. It can be unnecessary to use it to aggregate columns that don't have repetitive values.
While a single email can be part of multiple events, the example below is not an efficient use of summarize because a network message ID for an individual email always comes with a unique sender address.
EmailEvents
| where Timestamp > ago(1h)
| summarize by NetworkMessageId, SenderFromAddress

The summarize operator can be easily replaced with project, yielding potentially the same results while consuming fewer resources:
EmailEvents
| where Timestamp > ago(1h)
| project NetworkMessageId, SenderFromAddress

The following example is a more efficient use of summarize because there can be multiple distinct instances of a sender address sending email to the same recipient address. Such combinations are less distinct and are likely to have duplicates.
EmailEvents
| where Timestamp > ago(1h)
| summarize by SenderFromAddress, RecipientEmailAddress


Shuffle the queryâWhile summarize is best used in columns with repetitive values, the same columns can also have high cardinality or large numbers of unique values. Like the join operator, you can also apply the shuffle hint with summarize to distribute processing load and potentially improve performance when operating on columns with high cardinality.
The query below uses summarize to count distinct recipient email address, which can run in the hundreds of thousands in large organizations. To improve performance, it incorporates hint.shufflekey:
EmailEvents
| where Timestamp > ago(1h)
| summarize hint.shufflekey = RecipientEmailAddress count() by Subject, RecipientEmailAddress

Find distinct valuesâIn general, use summarize to find distinct values that can be repetitive. It can be unnecessary to use it to aggregate columns that don't have repetitive values.

summarize

While a single email can be part of multiple events, the example below is not an efficient use of summarize because a network message ID for an individual email always comes with a unique sender address.

summarize

EmailEvents
| where Timestamp > ago(1h)
| summarize by NetworkMessageId, SenderFromAddress

EmailEvents
| where Timestamp > ago(1h)
| summarize by NetworkMessageId, SenderFromAddress

The summarize operator can be easily replaced with project, yielding potentially the same results while consuming fewer resources:

summarize

project

EmailEvents
| where Timestamp > ago(1h)
| project NetworkMessageId, SenderFromAddress

EmailEvents
| where Timestamp > ago(1h)
| project NetworkMessageId, SenderFromAddress

The following example is a more efficient use of summarize because there can be multiple distinct instances of a sender address sending email to the same recipient address. Such combinations are less distinct and are likely to have duplicates.

summarize

EmailEvents
| where Timestamp > ago(1h)
| summarize by SenderFromAddress, RecipientEmailAddress

EmailEvents
| where Timestamp > ago(1h)
| summarize by SenderFromAddress, RecipientEmailAddress

Shuffle the queryâWhile summarize is best used in columns with repetitive values, the same columns can also have high cardinality or large numbers of unique values. Like the join operator, you can also apply the shuffle hint with summarize to distribute processing load and potentially improve performance when operating on columns with high cardinality.

summarize

join

summarize

The query below uses summarize to count distinct recipient email address, which can run in the hundreds of thousands in large organizations. To improve performance, it incorporates hint.shufflekey:

summarize

hint.shufflekey

EmailEvents
| where Timestamp > ago(1h)
| summarize hint.shufflekey = RecipientEmailAddress count() by Subject, RecipientEmailAddress

EmailEvents
| where Timestamp > ago(1h)
| summarize hint.shufflekey = RecipientEmailAddress count() by Subject, RecipientEmailAddress

Query scenarios

Identify unique processes with process IDs

Process IDs (PIDs) are recycled in Windows and reused for new processes. On their own, they can't serve as unique identifiers for specific processes.

Typically, the only way to uniquely identify a process on a specific device was by combining its process ID with its process creation time, along with the device identifier (either DeviceId or DeviceName). For instance, the following example query finds processes that access more than 10 IP addresses over port 445 (SMB), possibly scanning for file shares.

DeviceId

DeviceName

DeviceNetworkEvents
| where RemotePort == 445 and Timestamp > ago(12h) and InitiatingProcessId !in (0, 4)
| summarize RemoteIPCount=dcount(RemoteIP) by DeviceName, InitiatingProcessId, InitiatingProcessCreationTime, InitiatingProcessFileName
| where RemoteIPCount > 10

DeviceNetworkEvents
| where RemotePort == 445 and Timestamp > ago(12h) and InitiatingProcessId !in (0, 4)
| summarize RemoteIPCount=dcount(RemoteIP) by DeviceName, InitiatingProcessId, InitiatingProcessCreationTime, InitiatingProcessFileName
| where RemoteIPCount > 10

The above query summarizes by both InitiatingProcessId and InitiatingProcessCreationTime so that it looks at a single process, without mixing multiple processes with the same process ID.

InitiatingProcessId

InitiatingProcessCreationTime

This approach is still valid, especially for non-Windows systems. However, in Windows, thereâs a more direct method using the ProcessUniqueId field. While both the previous method and the one discussed below yield unique process instances, as a best practice we recommend using ProcessUniqueId when available, as it simplifies queries and eliminates the need to handle PID reuse scenarios.

ProcessUniqueId

ProcessUniqueId

This query demonstrates how to use the ProcessUniqueId and InitiatingProcessUniqueId fields to link a specific parent process to its child processes. By matching each childâs InitiatingProcessUniqueId to the parentâs ProcessUniqueId, it isolates only those child processes launched by that exact parent instance, even if process IDs get reused over time.

ProcessUniqueId

InitiatingProcessUniqueId

InitiatingProcessUniqueId

ProcessUniqueId

Example query:

// Step 1: Select a specific parent process instance (for instance, powershell.exe). 
let parentProcess = 
    DeviceProcessEvents
    | where FileName =~ "powershell.exe" // For your specific use case, consider modifying the FileName and adding more identifying properties to specify your query.
    | where isnotempty(ProcessUniqueId)
    | top 1 by Timestamp asc 
    | project DeviceId, DeviceName, ParentProcessUniqueId = ProcessUniqueId, ParentFileName = FileName;
// Step 2: Find all child processes started by this unique parent.
DeviceProcessEvents
| where isnotempty(InitiatingProcessUniqueId)
| join kind=inner (
    parentProcess
) on DeviceId
| where InitiatingProcessUniqueId == ParentProcessUniqueId
| project 
    DeviceName,
    ParentProcessUniqueId,
    ParentFileName,
    ChildProcessName = FileName,
    ChildProcessId = ProcessId,
    ChildProcessUniqueId = ProcessUniqueId,
    Timestamp

// Step 1: Select a specific parent process instance (for instance, powershell.exe). 
let parentProcess = 
    DeviceProcessEvents
    | where FileName =~ "powershell.exe" // For your specific use case, consider modifying the FileName and adding more identifying properties to specify your query.
    | where isnotempty(ProcessUniqueId)
    | top 1 by Timestamp asc 
    | project DeviceId, DeviceName, ParentProcessUniqueId = ProcessUniqueId, ParentFileName = FileName;
// Step 2: Find all child processes started by this unique parent.
DeviceProcessEvents
| where isnotempty(InitiatingProcessUniqueId)
| join kind=inner (
    parentProcess
) on DeviceId
| where InitiatingProcessUniqueId == ParentProcessUniqueId
| project 
    DeviceName,
    ParentProcessUniqueId,
    ParentFileName,
    ChildProcessName = FileName,
    ChildProcessId = ProcessId,
    ChildProcessUniqueId = ProcessUniqueId,
    Timestamp

Likewise, the query summarizes by both InitiatingProcessId and InitiatingProcessCreationTime so that it looks at a single process, without mixing multiple processes with the same process ID.

InitiatingProcessId

InitiatingProcessCreationTime

Query command lines

There are numerous ways to construct a command line to accomplish a task. For example, an attacker could reference an image file without a path, without a file extension, using environment variables, or with quotes. The attacker could also change the order of parameters or add multiple quotes and spaces.

To create more durable queries around command lines, apply the following practices:

Identify the known processes (such as net.exe or psexec.exe) by matching on the file name fields, instead of filtering on the command-line itself.
Parse command-line sections using the parse_command_line() function
When querying for command-line arguments, don't look for an exact match on multiple unrelated arguments in a certain order. Instead, use regular expressions or use multiple separate contains operators.
Use case insensitive matches. For example, use =~, in~, and contains instead of ==, in, and contains_cs.
To mitigate command-line obfuscation techniques, consider removing quotes, replacing commas with spaces, and replacing multiple consecutive spaces with a single space. There are more complex obfuscation techniques that require other approaches, but these tweaks can help address common ones.

=~

in~

contains

==

in

contains_cs

The following examples show various ways to construct a query that looks for the file net.exe to stop the firewall service "MpsSvc":

// Non-durable query - do not use
DeviceProcessEvents
| where ProcessCommandLine == "net stop MpsSvc"
| limit 10

// Better query - filters on file name, does case-insensitive matches
DeviceProcessEvents
| where Timestamp > ago(7d) and FileName in~ ("net.exe", "net1.exe") and ProcessCommandLine contains "stop" and ProcessCommandLine contains "MpsSvc"

// Best query also ignores quotes
DeviceProcessEvents
| where Timestamp > ago(7d) and FileName in~ ("net.exe", "net1.exe")
| extend CanonicalCommandLine=replace("\"", "", ProcessCommandLine)
| where CanonicalCommandLine contains "stop" and CanonicalCommandLine contains "MpsSvc"

// Non-durable query - do not use
DeviceProcessEvents
| where ProcessCommandLine == "net stop MpsSvc"
| limit 10

// Better query - filters on file name, does case-insensitive matches
DeviceProcessEvents
| where Timestamp > ago(7d) and FileName in~ ("net.exe", "net1.exe") and ProcessCommandLine contains "stop" and ProcessCommandLine contains "MpsSvc"

// Best query also ignores quotes
DeviceProcessEvents
| where Timestamp > ago(7d) and FileName in~ ("net.exe", "net1.exe")
| extend CanonicalCommandLine=replace("\"", "", ProcessCommandLine)
| where CanonicalCommandLine contains "stop" and CanonicalCommandLine contains "MpsSvc"

Ingest data from external sources

To incorporate long lists or large tables into your query, use the externaldata operator to ingest data from a specified URI. You can get data from files in TXT, CSV, JSON, or other formats. The example below shows how you can utilize the extensive list of malware SHA-256  hashes provided by MalwareBazaar (abuse.ch) to check attachments on emails:

let abuse_sha256 = (externaldata(sha256_hash: string)
[@"https://bazaar.abuse.ch/export/txt/sha256/recent/"]
with (format="txt"))
| where sha256_hash !startswith "#"
| project sha256_hash;
abuse_sha256
| join (EmailAttachmentInfo
| where Timestamp > ago(1d)
) on $left.sha256_hash == $right.SHA256
| project Timestamp,SenderFromAddress,RecipientEmailAddress,FileName,FileType,
SHA256,ThreatTypes,DetectionMethods

let abuse_sha256 = (externaldata(sha256_hash: string)
[@"https://bazaar.abuse.ch/export/txt/sha256/recent/"]
with (format="txt"))
| where sha256_hash !startswith "#"
| project sha256_hash;
abuse_sha256
| join (EmailAttachmentInfo
| where Timestamp > ago(1d)
) on $left.sha256_hash == $right.SHA256
| project Timestamp,SenderFromAddress,RecipientEmailAddress,FileName,FileType,
SHA256,ThreatTypes,DetectionMethods

Parse strings

There are various functions you can use to efficiently handle strings that need parsing or conversion.

String
Function
Usage example




Command-lines
parse_command_line()
Extract the command and all arguments.


Paths
parse_path()
Extract the sections of a file or folder path.


Version numbers
parse_version()
Deconstruct a version number with up to four sections and up to eight characters per section. Use the parsed data to compare version age.


IPv4 addresses
parse_ipv4()
Convert an IPv4 address to a long integer. To compare IPv4 addresses without converting them, use ipv4_compare().


IPv6 addresses
parse_ipv6()
Convert an IPv4 or IPv6 address to the canonical IPv6 notation. To compare IPv6 addresses, use ipv6_compare().

To learn about all supported parsing functions, read about Kusto string functions.

Note

Some tables in this article might not be available in Microsoft Defender for Endpoint. Turn on Microsoft Defender to hunt for threats using more data sources. You can move your advanced hunting workflows from Microsoft Defender for Endpoint to Microsoft Defender by following the steps in Migrate advanced hunting queries from Microsoft Defender for Endpoint.

Related topics

Kusto query language documentation
Quotas and usage parameters
Handle advanced hunting errors
Advanced hunting overview
Learn the query language

Tip

Do you want to learn more? Engage with the Microsoft Security community in our Tech Community:  Microsoft Defender XDR Tech Community.

Was this page helpful?

Need help with this topic?

Want to try using Ask Learn to clarify or guide you through this topic?

Additional resources