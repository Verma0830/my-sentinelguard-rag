# Kusto Query Language (KQL) Operators & Functions Quick Reference

Source URL: https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/kql-quick-reference


Note

Access to this page requires authorization. You can try signing in or changing directories.

Access to this page requires authorization. You can try changing directories.

KQL quick reference

Switch services using the Version drop-down list. Learn more about navigation. 
Applies to: â Microsoft Fabric â Azure Data Explorer â Azure Monitor â Microsoft Sentinel

This article shows you a list of functions and their descriptions to help get you started using Kusto Query Language.

Operator/Function
Description
Syntax




Filter/Search/Condition
Find relevant data by filtering or searching



where
Filters on a specific predicate
T | where Predicate


where contains/has
Contains: Looks for any substring match  Has: Looks for a specific word (better performance)
T | where col1 contains/has "[search term]"


search
Searches all columns in the table for the value
[TabularSource |] search [kind=CaseSensitivity] [in (TableSources)] SearchPredicate


take
Returns the specified number of records. Use to test a queryNote: take and limit are synonyms.
T | take NumberOfRows


case
Adds a condition statement, similar to if/then/elseif in other systems.
case(predicate_1, then_1, predicate_2, then_2, predicate_3, then_3, else)


distinct
Produces a table with the distinct combination of the provided columns of the input table
distinct [ColumnName], [ColumnName]


Date/Time
Operations that use date and time functions



ago
Returns the time offset relative to the time the query executes. For example, ago(1h) is one hour before the current clock's reading.
ago(a_timespan)


format_datetime
Returns data in various date formats.
format_datetime(datetime , format)


bin
Rounds all values in a timeframe and groups them
bin(value,roundTo)


Create/Remove Columns
Add or remove columns in a table



print
Outputs a single row with one or more scalar expressions
print [ColumnName =] ScalarExpression [',' ...]


project
Selects the columns to include in the order specified
T | project ColumnName [= Expression] [, ...]  Or  T | project [ColumnName | (ColumnName[,]) =] Expression [, ...]


project-away
Selects the columns to exclude from the output
T | project-away ColumnNameOrPattern [, ...]


project-keep
Selects the columns to keep in the output
T | project-keep ColumnNameOrPattern [, ...]


project-rename
Renames columns in the result output
T | project-rename new_column_name = column_name


project-reorder
Reorders columns in the result output
T | project-reorder Col2, Col1, Col* asc


extend
Creates a calculated column and adds it to the result set
T | extend [ColumnName | (ColumnName[, ...]) =] Expression [, ...]


Sort and Aggregate Dataset
Restructure the data by sorting or grouping them in meaningful ways



sort operator
Sort the rows of the input table by one or more columns in ascending or descending order
T | sort by expression1 [asc|desc], expression2 [asc|desc], â¦


top
Returns the first N rows of the dataset when the dataset is sorted using by
T | top numberOfRows by expression [asc|desc] [nulls first|last]


summarize
Groups the rows according to the by group columns, and calculates aggregations over each group
T | summarize [[Column =] Aggregation [, ...]] [by [Column =] GroupExpression [, ...]]


count
Counts records in the input table (for example, T)This operator is shorthand for summarize count() 
T | count


join
Merges the rows of two tables to form a new table by matching values of the specified column(s) from each table. Supports a full range of join types: fullouter, inner, innerunique, leftanti, leftantisemi, leftouter, leftsemi, rightanti, rightantisemi, rightouter, rightsemi
LeftTable | join [JoinParameters] ( RightTable ) on Attributes


union
Takes two or more tables and returns all their rows
[T1] | union [T2], [T3], â¦


range
Generates a table with an arithmetic series of values
range columnName from start to stop step step


Format Data
Restructure the data to output in a useful way



lookup
Extends the columns of a fact table with values looked-up in a dimension table
T1 | lookup [kind = (leftouter|inner)] ( T2 ) on Attributes


mv-expand
Turns dynamic arrays into rows (multi-value expansion)
T | mv-expand Column


parse
Evaluates a string expression and parses its value into one or more calculated columns. Use for structuring unstructured data.
T | parse [kind=regex  [flags=regex_flags] |simple|relaxed] Expression with * (StringConstant ColumnName [: ColumnType]) *...


make-series
Creates series of specified aggregated values along a specified axis
T | make-series [MakeSeriesParamters] [Column =] Aggregation [default = DefaultValue] [, ...] on AxisColumn from start to end step step [by [Column =] GroupExpression [, ...]]


let
Binds a name to expressions that can refer to its bound value. Values can be lambda expressions to create query-defined functions as part of the query. Use let to create expressions over tables whose results look like a new table.
let Name = ScalarExpression | TabularExpression | FunctionDefinitionExpression


General
Miscellaneous operations and function



invoke
Runs the function on the table that it receives as input.
T | invoke function([param1, param2])


evaluate pluginName
Evaluates query language extensions (plugins)
[T |] evaluate [ evaluateParameters ] PluginName ( [PluginArg1 [, PluginArg2]... )


Visualization
Operations that display the data in a graphical format



render
Renders results as a graphical output
T | render Visualization [with (PropertyName = PropertyValue [, ...] )]

T | where Predicate

Contains

Has

T | where col1 contains/has "[search term]"

[TabularSource |] search [kind=CaseSensitivity] [in (TableSources)] SearchPredicate

take

limit

T | take NumberOfRows

case(predicate_1, then_1, predicate_2, then_2, predicate_3, then_3, else)

distinct [ColumnName], [ColumnName]

ago(1h)

ago(a_timespan)

format_datetime(datetime , format)

bin(value,roundTo)

print [ColumnName =] ScalarExpression [',' ...]

T | project ColumnName [= Expression] [, ...]

T | project [ColumnName | (ColumnName[,]) =] Expression [, ...]

T | project-away ColumnNameOrPattern [, ...]

T | project-keep ColumnNameOrPattern [, ...]

T | project-rename new_column_name = column_name

T | project-reorder Col2, Col1, Col* asc

T | extend [ColumnName | (ColumnName[, ...]) =] Expression [, ...]

T | sort by expression1 [asc|desc], expression2 [asc|desc], â¦

by

T | top numberOfRows by expression [asc|desc] [nulls first|last]

by

T | summarize [[Column =] Aggregation [, ...]] [by [Column =] GroupExpression [, ...]]

summarize count()

T | count

fullouter

inner

innerunique

leftanti

leftantisemi

leftouter

leftsemi

rightanti

rightantisemi

rightouter

rightsemi

LeftTable | join [JoinParameters] ( RightTable ) on Attributes

[T1] | union [T2], [T3], â¦

range columnName from start to stop step step

T1 | lookup [kind = (leftouter|inner)] ( T2 ) on Attributes

T | mv-expand Column

T | parse [kind=regex  [flags=regex_flags] |simple|relaxed] Expression with * (StringConstant ColumnName [: ColumnType]) *...

T | make-series [MakeSeriesParamters] [Column =] Aggregation [default = DefaultValue] [, ...] on AxisColumn from start to end step step [by [Column =] GroupExpression [, ...]]

let

let Name = ScalarExpression | TabularExpression | FunctionDefinitionExpression

T | invoke function([param1, param2])

[T |] evaluate [ evaluateParameters ] PluginName ( [PluginArg1 [, PluginArg2]... )

T | render Visualization [with (PropertyName = PropertyValue [, ...] )]

Related content

SQL cheat sheet
Splunk cheat sheet

Was this page helpful?

Need help with this topic?

Want to try using Ask Learn to clarify or guide you through this topic?

Additional resources