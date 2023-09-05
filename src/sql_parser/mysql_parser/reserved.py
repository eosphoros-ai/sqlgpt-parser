# coding=utf-8
"""

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""

sql92_reserved = (
    'SELECT',
    'FROM',
    'ADD',
    'AS',
    'ALL',
    'SOME',
    'ANY',
    'DISTINCT',
    'WHERE',
    'GROUP',
    'BY',
    'ORDER',
    'HAVING',
    'AT',
    'XOR',
    'OR',
    'AND',
    'IN',
    'NOT',
    'NO',
    'EXISTS',
    'BETWEEN',
    'LIKE',
    'IS',
    'NULL',
    'TRUE',
    'FALSE',
    'FIRST',
    'LAST',
    'ESCAPE',
    'ASC',
    'DESC',
    'SUBSTRING',
    'STR_TO_DATE',
    'POSITION',
    'FOR',
    'DATE',
    'TIME',
    'INTERVAL',
    'YEAR',
    'MONTH',
    'DAY',
    'HOUR',
    'MINUTE',
    'SECOND',
    'ZONE',
    'CURRENT_DATE',
    'CURRENT_TIME',
    'CURRENT_TIMESTAMP',
    'EXTRACT',
    'CASE',
    'WHEN',
    'THEN',
    'ELSE',
    'END',
    'JOIN',
    'CROSS',
    'OUTER',
    'INNER',
    'LEFT',
    'RIGHT',
    'FULL',
    'NATURAL',
    'USING',
    'ON',
    'ROWS',
    'CURRENT',
    'WITH',
    'VALUES',
    'CREATE',
    'TABLE',
    'VIEW',
    'INSERT',
    'DELETE',
    'INTO',
    'CONSTRAINT',
    'DESCRIBE',
    'GRANT',
    'PRIVILEGES',
    'PUBLIC',
    'OPTION',
    'CAST',
    'COLUMN',
    'DROP',
    'UNION',
    'EXCEPT',
    'INTERSECT',
    'TO',
    'ALTER',
    'SET',
    'SESSION',
    'TRANSACTION',
    'COMMIT',
    'ROLLBACK',
    'WORK',
    'ISOLATION',
    'LEVEL',
    'READ',
    'WRITE',
    'ONLY',
)

sql92_conditions = (
    'CONDITION_NUMBER',
    'RETURNED_SQLSTATE',
    'CLASS_ORIGIN',
    'SUBCLASS_ORIGIN',
    'SERVER_NAME',
    'CONNECTION_NAME',
    'CONSTRATIN_CATALOG',
    'CONSTRAINT_SCHEMA',
    'CONSTRAINT_NAME',
    'CATALOG_NAME',
    'SCHEMA_NAME',
    'TABLE_NAME',
    'COLUMN_NAME',
    'CURSOR_NAME',
    'MESSAGE_TEXT',
    'MESSAGE_LENGTH',
    'MESSAGE_OCTET_LENGTH',
)

sql92_languages = ('ADA', 'C', 'COBOL', 'FORTRAN', 'MUMPS', 'PASCAL', 'PLI')

sql92_descriptors = (
    'TYPE',
    'LENGTH',
    'OCTET_LENGTH',
    'RETURNED_LENGTH',
    'RETURNED_OCTET_LENGTH',
    'PRECISION',
    'SCALE',
    'DATETIME_INTERVAL_CODE',
    'DATETIME_INTERVAL_PRECISION',
    'NULLABLE',
    'INDICATOR',
    'DATA',
    'NAME',
    'UNNAMED',
    'COLLATION_CATALOG',
    'COLLATION_SCHEMA',
    'COLLATION_NAME',
    'CHARACTER_SET_CATALOG',
    'CHARACTER_SET_SCHEMA',
    'CHARACTER_SET_NAME',
)

sql92_transaction = ('COMMITTED', 'REPEATABLE', 'SERIALIZABLE', 'UNCOMMITTED')

sql92_statement_info = (
    'COMMAND_FUNCTION',
    'DYNAMIC_FUNCTION',
    'MORE',
    'NUMBER',
    'ROW_COUNT',
)

sql92_nonreserved = (
    ('CONSTRAINT_CATALOG',)
    + sql92_conditions
    + sql92_transaction
    + sql92_languages
    + sql92_descriptors
    + sql92_statement_info
)

sql99_reserved = (
    'ABSOLUTE',
    'ACTION',
    'ADD',
    'AFTER',
    'ALL',
    'ALLOCATE',
    'ALTER',
    'AND',
    'ANY',
    'ARE',
    'ARRAY',
    'AS',
    'ASC',
    'ASSERTION',
    'AT',
    'AUTHORIZATION',
    'BEFORE',
    'BEGIN',
    'BETWEEN',
    'BINARY',
    'BIT',
    'BLOB',
    'BOOLEAN',
    'BOTH',
    'BREADTH',
    'BY',
    'CALL',
    'CASCADE',
    'CASCADED',
    'CASE',
    'CAST',
    'CATALOG',
    'CHAR',
    'CHARACTER',
    'CHECK',
    'CLOB',
    'CLOSE',
    'COLLATE',
    'COLLATION',
    'COLUMN',
    'COMMIT',
    'CONDITION',
    'CONNECT',
    'CONNECTION',
    'CONSTRAINT',
    'CONSTRAINTS',
    'CONSTRUCTOR',
    'CONTINUE',
    'CORRESPONDING',
    'CREATE',
    'CROSS',
    'CUBE',
    'CURRENT',
    'CURRENT_DATE',
    'CURRENT_DEFAULT_TRANSFORM_GROUP',
    'CURRENT_TRANSFORM_GROUP_FOR_TYPE',
    'CURRENT_PATH',
    'CURRENT_ROLE',
    'CURRENT_TIME',
    'CURRENT_TIMESTAMP',
    'CURRENT_USER',
    'CURSOR',
    'CYCLE',
    'DATA',
    'DATE',
    'DAY',
    'DEALLOCATE',
    'DEC',
    'DECIMAL',
    'DECLARE',
    'DEFAULT',
    'DEFERRABLE',
    'DEFERRED',
    'DELETE',
    'DEPTH',
    'DEREF',
    'DESC',
    'DESCRIBE',
    'DESCRIPTOR',
    'DETERMINISTIC',
    'DIAGNOSTICS',
    'DISCONNECT',
    'DISTINCT',
    'DO',
    'DOMAIN',
    'DOUBLE',
    'DROP',
    'DYNAMIC',
    'EACH',
    'ELSE',
    'ELSEIF',
    'END',
    'END-EXEC',
    'EQUALS',
    'ESCAPE',
    'EXCEPT',
    'EXCEPTION',
    'EXEC',
    'EXECUTE',
    'EXISTS',
    'EXIT',
    'EXTERNAL',
    'FALSE',
    'FETCH',
    'FIRST',
    'FLOAT',
    'FOR',
    'FOREIGN',
    'FOUND',
    'FROM',
    'FREE',
    'FULL',
    'FUNCTION',
    'GENERAL',
    'GET',
    'GLOBAL',
    'GO',
    'GOTO',
    'GRANT',
    'GROUP',
    'GROUPING',
    'HANDLE',
    'HAVING',
    'HOLD',
    'HOUR',
    'IDENTITY',
    'IF',
    'IMMEDIATE',
    'IN',
    'INDICATOR',
    'INITIALLY',
    'INNER',
    'INOUT',
    'INPUT',
    'INSERT',
    'INT',
    'INTEGER',
    'INTERSECT',
    'INTERVAL',
    'INTO',
    'IS',
    'ISOLATION',
    'JOIN',
    'KEY',
    'LANGUAGE',
    'LARGE',
    'LAST',
    'LATERAL',
    'LEADING',
    'LEAVE',
    'LEFT',
    'LEVEL',
    'LIKE',
    'LOCAL',
    'LOCALTIME',
    'LOCALTIMESTAMP',
    'LOCATOR',
    'LOOP',
    'MAP',
    'MATCH',
    'METHOD',
    'MINUTE',
    'MODIFIES',
    'MODULE',
    'MONTH',
    'NAMES',
    'NATIONAL',
    'NATURAL',
    'NCHAR',
    'NCLOB',
    'NESTING',
    'NEW',
    'NEXT',
    'NO',
    'NONE',
    'NOT',
    'NOWAIT',
    'NULL',
    'NUMERIC',
    'OBJECT',
    'OF',
    'OLD',
    'ON',
    'ONLY',
    'OPEN',
    'OPTION',
    'OR',
    'ORDER',
    'ORDINALITY',
    'OUT',
    'OUTER',
    'OUTPUT',
    'OVERLAPS',
    'PAD',
    'PARAMETER',
    'PARTIAL',
    'PATH',
    'PRECISION',
    'PREPARE',
    'PRESERVE',
    'PRIMARY',
    'PRIOR',
    'PRIVILEGES',
    'PROCEDURE',
    'PUBLIC',
    'READ',
    'READS',
    'REAL',
    'RECURSIVE',
    'REDO',
    'REF',
    'REFERENCES',
    'REFERENCING',
    'RELATIVE',
    'RELEASE',
    'REPEAT',
    'RESIGNAL',
    'RESTRICT',
    'RESULT',
    'RETURN',
    'RETURNS',
    'REVOKE',
    'RIGHT',
    'ROLE',
    'ROLLBACK',
    'ROLLUP',
    'ROUTINE',
    'ROW',
    'ROWS',
    'SAVEPOINT',
    'SCHEMA',
    'SCROLL',
    'SEARCH',
    'SECOND',
    'SECTION',
    'SELECT',
    'SESSION',
    'SESSION_USER',
    'SET',
    'SETS',
    'SIGNAL',
    'SIMILAR',
    'SIZE',
    'SMALLINT',
    'SOME',
    'SPACE',
    'SPECIFIC',
    'SPECIFICTYPE',
    'SQL',
    'SQLEXCEPTION',
    'SQLSTATE',
    'SQLWARNING',
    'START',
    'STATE',
    'STATIC',
    'SYSTEM_USER',
    'TABLE',
    'TEMPORARY',
    'THEN',
    'TIME',
    'TIMEZONE_HOUR',
    'TIMEZONE_MINUTE',
    'TO',
    'TRAILING',
    'TRANSACTION',
    'TRANSLATION',
    'TREAT',
    'TRIGGER',
    'TRUE',
    'UNDER',
    'UNDO',
    'UNION',
    'UNIQUE',
    'UNKNOWN',
    'UNNEST',
    'UNTIL',
    'UPDATE',
    'USAGE',
    'USER',
    'USING',
    'VALUE',
    'VALUES',
    'VARCHAR',
    'VARYING',
    'VIEW',
    'WHEN',
    'WHENEVER',
    'WHERE',
    'WHILE',
    'WITH',
    'WITHOUT',
    'WORK',
    'WRITE',
    'XOR',
    'YEAR',
)

sql03_reserved = (
    'ADD',
    'ALL',
    'ALLOCATE',
    'ALTER',
    'AND',
    'ANY',
    'ARE',
    'ARRAY',
    'AS',
    'ASENSITIVE',
    'ASYMMETRIC',
    'AT',
    'ATOMIC',
    'AUTHORIZATION',
    'BEGIN',
    'BETWEEN',
    'BIGINT',
    'BINARY',
    'BLOB',
    'BOOLEAN',
    'BOTH',
    'BY',
    'CALL',
    'CALLED',
    'CASCADED',
    'CASE',
    'CAST',
    'CHAR',
    'CHARACTER',
    'CHECK',
    'CLOB',
    'CLOSE',
    'COLLATE',
    'COLUMN',
    'COMMIT',
    'CONNECT',
    'CONSTRAINT',
    'CONTINUE',
    'CORRESPONDING',
    'CREATE',
    'CROSS',
    'CUBE',
    'CURRENT',
    'CURRENT_DATE',
    'CURRENT_DEFAULT_TRANSFORM_GROUP',
    'CURRENT_PATH',
    'CURRENT_ROLE',
    'CURRENT_TIME',
    'CURRENT_TIMESTAMP',
    'CURRENT_TRANSFORM_GROUP_FOR_TYPE',
    'CURRENT_USER',
    'CURSOR',
    'CYCLE',
    'DATE',
    'DAY',
    'DEALLOCATE',
    'DEC',
    'DECIMAL',
    'DECLARE',
    'DEFAULT',
    'DELETE',
    'DEREF',
    'DESCRIBE',
    'DETERMINISTIC',
    'DISCONNECT',
    'DISTINCT',
    'DOUBLE',
    'DROP',
    'DYNAMIC',
    'EACH',
    'ELEMENT',
    'ELSE',
    'END',
    'END-EXEC',
    'ESCAPE',
    'EXCEPT',
    'EXEC',
    'EXECUTE',
    'EXISTS',
    'EXTERNAL',
    'FALSE',
    'FETCH',
    'FILTER',
    'FLOAT',
    'FOR',
    'FOREIGN',
    'FREE',
    'FROM',
    'FULL',
    'FUNCTION',
    'GET',
    'GLOBAL',
    'GRANT',
    'GROUP',
    'GROUPING',
    'HAVING',
    'HOLD',
    'HOUR',
    'IDENTITY',
    'IMMEDIATE',
    'IN',
    'INDICATOR',
    'INNER',
    'INOUT',
    'INPUT',
    'INSENSITIVE',
    'INSERT',
    'INT',
    'INTEGER',
    'INTERSECT',
    'INTERVAL',
    'INTO',
    'IS',
    'ISOLATION',
    'JOIN',
    'LANGUAGE',
    'LARGE',
    'LATERAL',
    'LEADING',
    'LEFT',
    'LIKE',
    'LOCAL',
    'LOCALTIME',
    'LOCALTIMESTAMP',
    'MATCH',
    'MEMBER',
    'MERGE',
    'METHOD',
    'MINUTE',
    'MODIFIES',
    'MODULE',
    'MONTH',
    'MULTISET',
    'NATIONAL',
    'NATURAL',
    'NCHAR',
    'NCLOB',
    'NEW',
    'NO',
    'NONE',
    'NOT',
    'NULL',
    'NUMERIC',
    'OF',
    'OLD',
    'ON',
    'ONLY',
    'OPEN',
    'OR',
    'ORDER',
    'OUT',
    'OUTER',
    'OUTPUT',
    'OVER',
    'OVERLAPS',
    'PARAMETER',
    'PARTITION',
    'PRECISION',
    'PREPARE',
    'PRIMARY',
    'PROCEDURE',
    'RANGE',
    'READS',
    'REAL',
    'RECURSIVE',
    'REF',
    'REFERENCES',
    'REFERENCING',
    'REGR_AVGX',
    'REGR_AVGY',
    'REGR_COUNT',
    'REGR_INTERCEPT',
    'REGR_R2',
    'REGR_SLOPE',
    'REGR_SXX',
    'REGR_SXY',
    'REGR_SYY',
    'RELEASE',
    'RESULT',
    'RETURN',
    'RETURNS',
    'REVOKE',
    'RIGHT',
    'ROLLBACK',
    'ROLLUP',
    'ROW',
    'ROWS',
    'SAVEPOINT',
    'SCROLL',
    'SEARCH',
    'SECOND',
    'SELECT',
    'SENSITIVE',
    'SESSION_USER',
    'SET',
    'SIMILAR',
    'SMALLINT',
    'SOME',
    'SPECIFIC',
    'SPECIFICTYPE',
    'SQL',
    'SQLEXCEPTION',
    'SQLSTATE',
    'SQLWARNING',
    'START',
    'STATIC',
    'SUBMULTISET',
    'SYMMETRIC',
    'SYSTEM',
    'SYSTEM_USER',
    'TABLE',
    'THEN',
    'TIME',
    'TIMEZONE_HOUR',
    'TIMEZONE_MINUTE',
    'TO',
    'TRAILING',
    'TRANSLATION',
    'TREAT',
    'TRIGGER',
    'TRUE',
    'UESCAPE',
    'UNION',
    'UNIQUE',
    'UNKNOWN',
    'UNNEST',
    'UPDATE',
    'UPPER',
    'USER',
    'USING',
    'VALUE',
    'VALUES',
    'VAR_POP',
    'VAR_SAMP',
    'VARCHAR',
    'VARYING',
    'WHEN',
    'WHENEVER',
    'WHERE',
    'WIDTH_BUCKET',
    'WINDOW',
    'WITH',
    'WITHIN',
    'WITHOUT',
    'XOR',
    'YEAR',
)

reversed = (
    'ADD',
    'ADDDATE',
    'ADDTIME',
    'ALL',
    'ALTER',
    'ANALYZE',
    'AND',
    'ARRAY',
    'AS',
    'ASC',
    'ATAN2',
    'BETWEEN',
    'BIGINT',
    'BINARY',
    'BLOB',
    'BOTH',
    'BY',
    'CASCADE',
    'CASE',
    'CAST',
    'CHANGE',
    'CHAR',
    'CHARACTER',
    'CHECK',
    'COLLATE',
    'CONCAT',
    'CONSTRAINT',
    'CONTINUE',
    'CONVERT',
    'CREATE',
    'CROSS',
    'CUME_DIST',
    'CURDATE',
    'CURRENT_DATE',
    'CURRENT_ROLE',
    'CURRENT_TIME',
    'CURRENT_TIMESTAMP',
    'CURRENT_USER',
    'CURSOR',
    'CURTIME',
    'DATABASE',
    'DATABASES',
    'DATEDIFF',
    'DATE_ADD',
    'DATE_SUB',
    'DAY_HOUR',
    'DAY_MICROSECOND',
    'DAY_MINUTE',
    'DAY_SECOND',
    'DEC',
    'DECIMAL',
    'DEFAULT',
    'DELAYED',
    'DELETE',
    'DENSE_RANK',
    'DESC',
    'DESCRIBE',
    'DISTINCT',
    'DISTINCTROW',
    'DIV',
    'DOUBLE',
    'DROP',
    'DUAL',
    'ELSE',
    'ELSEIF',
    'ENCLOSED',
    'ESCAPED',
    'EXCEPT',
    'EXISTS',
    'EXIT',
    'EXPLAIN',
    'EXTRACT',
    'FALSE',
    'FETCH',
    'FIRST_VALUE',
    'FLOAT',
    'FOR',
    'FORCE',
    'FOREIGN',
    'FROM',
    'FULLTEXT',
    'GENERATED',
    'GET_FORMAT',
    'GRANT',
    'GROUP',
    'GROUPS',
    'GROUP_CONCAT',
    'HAVING',
    'HIGH_PRIORITY',
    'HOUR_MICROSECOND',
    'HOUR_MINUTE',
    'HOUR_SECOND',
    'IF',
    'IGNORE',
    'ILIKE',
    'IN',
    'INDEX',
    'INFILE',
    'INNER',
    'INOUT',
    'INSERT',
    'INT',
    'INT1',
    'INT2',
    'INT3',
    'INT4',
    'INT8',
    'INTEGER',
    'INTERSECT',
    'JOIN',
    'KEY',
    'KEYS',
    'KILL',
    'LAG',
    'LEAD',
    'LEADING',
    'LEAVE',
    'LEFT',
    'LIKE',
    'LIMIT',
    'LINEAR',
    'LINES',
    'LOAD',
    'LOCALTIME',
    'LOCALTIMESTAMP',
    'LOCK',
    'LONG',
    'LONGBLOB',
    'LONGTEXT',
    'LOW_PRIORITY',
    'MATCH',
    'MAXVALUE',
    'MEDIUMBLOB',
    'MEDIUMINT',
    'MEDIUMTEXT',
    'MIN',
    'MINUTE_MICROSECOND',
    'MINUTE_SECOND',
    'MOD',
    'NATURAL',
    'NOT',
    'NO_WRITE_TO_BINLOG',
    'NTH_VALUE',
    'NTILE',
    'NULL',
    'NUMERIC',
    'ON',
    'OPTIMIZE',
    'OPTION',
    'OPTIONALLY',
    'ORDER',
    'OUT',
    'OUTER',
    'OUTFILE',
    'PARTITION',
    'PERCENT_RANK',
    'PRECISION',
    'PRIMARY',
    'PROCEDURE',
    'RADIANS',
    'RAND',
    'RANGE',
    'READ',
    'REAL',
    'RECURSIVE',
    'REFERENCES',
    'REGEXP',
    'RELEASE',
    'RENAME',
    'REPEAT',
    'REQUIRE',
    'RESIGNAL',
    'RESTRICT',
    'RETURNED_SQLSTATE',
    'REVOKE',
    'RIGHT',
    'RLIKE',
    'ROW_NUMBER',
    'SECOND_MICROSECOND',
    'SELECT',
    'SET',
    'SHOW',
    'SIGNAL',
    'SIN',
    'SMALLINT',
    'SQL',
    'SQLEXCEPTION',
    'SQLSTATE',
    'SQLWARNING',
    'SQL_BIG_RESULT',
    'SQRT',
    'SSL',
    'STARTING',
    'STATS_EXTENDED',
    'STD',
    'STDDEV',
    'STDDEV_POP',
    'STDDEV_SAMP',
    'STRING',
    'SUBDATE',
    'SUBSTRING',
    'TABLE',
    'TABLESAMPLE',
    'TAN',
    'TERMINATED',
    'THEN',
    'TIMESTAMPADD',
    'TIMESTAMPDIFF',
    'TINYBLOB',
    'TINYINT',
    'TINYTEXT',
    'TO',
    'TRAILING',
    'TRIGGER',
    'TRIM',
    'TRUE',
    'UNION',
    'UNSIGNED',
    'UNTIL',
    'UPDATE',
    'USAGE',
    'USE',
    'USING',
    'UTC_DATE',
    'UTC_TIME',
    'UTC_TIMESTAMP',
    'VARBINARY',
    'VARCHACTER',
    'VARCHAR',
    'VARYING',
    'VAR_POP',
    'VAR_SAMP',
    'VIRTUAL',
    'WHEN',
    'WHERE',
    'WHILE',
    'WINDOW',
    'YEAR_MONTH',
    '_BINARY',
)

# resvered word in mysql but can be used as token
nonreserved = (
    'ABS',
    'ACOS',
    'AES_DECRYPT',
    'AES_ENCRYPT',
    'ANY_VALUE',
    'ASIN',
    'ASYNCHRONOUS_CONNECTION_FAILOVER_ADD_MANAGED',
    'ASYNCHRONOUS_CONNECTION_FAILOVER_ADD_SOURCE',
    'ASYNCHRONOUS_CONNECTION_FAILOVER_DELETE_MANAGED',
    'ASYNCHRONOUS_CONNECTION_FAILOVER_DELETE_SOURCE',
    'ASYNCHRONOUS_CONNECTION_FAILOVER_RESET',
    'ATAN',
    'BENCHMARK',
    'BIN',
    'BIN_TO_UUID',
    'BIT_COUNT',
    'BIT_LENGTH',
    'BRIEF',
    'CALL',
    'CELIING',
    'CEIL',
    'CEILING',
    'CHARACTER_LENGTH',
    'CHAR_LENGTH',
    'COERCIBILITY',
    'COLUMN',
    'COPY',
    'COMPRESS',
    'CONCAT_WS',
    'CONNECTION_ID',
    'CONY',
    'CONVERT_TZ',
    'COS',
    'COT',
    'COUNT',
    'CRC32',
    'DAYNAME',
    'DATE_FORMAT',
    'DAYOFMONTH',
    'DAYOFWEEK',
    'DAYOFYEAR',
    'DEGREES',
    'ELT',
    'EXP',
    'EXPORT_SET',
    'EXTRACTVALUE',
    'EXTRACTVALUEEXP',
    'FIELD',
    'FIND_IN_SET',
    'FLOOR',
    'FOUND_ROWS',
    'FROM_BASE64',
    'FROM_DAYS',
    'FROM_UNIXTIME',
    'GET_LOCK',
    'GREATEST',
    'GROUPING',
    'GROUP_REPLICATION_DISABLE_MEMBER_ACTION',
    'GROUP_REPLICATION_ENABLE_MEMBER_ACTION',
    'GROUP_REPLICATION_GET_COMMUNICATION_PROTOCOL',
    'GROUP_REPLICATION_GET_WRITE_CONCURRENCY',
    'GROUP_REPLICATION_RESET_MEMBER_ACTIONS',
    'GROUP_REPLICATION_SET_AS_PRIMARY',
    'GROUP_REPLICATION_SET_COMMUNICATION_PROTOCOL',
    'GROUP_REPLICATION_SET_WRITE_CONCURRENCY',
    'GROUP_REPLICATION_SWITCH_TO_MULTI_PRIMARY_MODE',
    'GROUP_REPLICATION_SWITCH_TO_SINGLE_PRIMARY_MODE',
    'GTID_SUBSET',
    'GTID_SUBTRACT',
    'HEX',
    'ICU_VERSION',
    'IFNULL',
    'INET6_ATON',
    'INET6_NTOA',
    'INET_ATON',
    'INET_NTOA',
    'INSTR',
    'INTO',
    'INTERVAL',
    'IS',
    'ISNULL',
    'IS_FREE_LOCK',
    'IS_IPV4',
    'IS_IPV4_COMPAT',
    'IS_IPV4_MAPPED',
    'IS_IPV6',
    'IS_USED_LOCK',
    'IS_UUID',
    'ITERATE',
    'JSON_ARRAY',
    'JSON_ARRAYAGG',
    'JSON_ARRAY_APPEND',
    'JSON_ARRAY_INSERT',
    'JSON_CONTAINS',
    'JSON_CONTAINS_PATH',
    'JSON_DEPTH',
    'JSON_EXTRACT',
    'JSON_INSERT',
    'JSON_KEYS',
    'JSON_LENGTH',
    'JSON_MERGE',
    'JSON_MERGE_PATCH',
    'JSON_MERGE_PRESERVE',
    'JSON_OBJECT',
    'JSON_OVERLAPS',
    'JSON_PERTTY',
    'JSON_QUOTE',
    'JSON_REMOVE',
    'JSON_REPLACE',
    'JSON_SCHEMA_VALID',
    'JSON_SCHEMA_VALIDATION_REPORT',
    'JSON_SEARCH',
    'JSON_SET',
    'JSON_STORAGE_FREE',
    'JSON_STORAGE_SIZE',
    'JSON_TABLE',
    'JSON_TYPE',
    'JSON_UNQUOTE',
    'JSON_VAILD',
    'JSON_VALUE',
    'LAST_DAY',
    'LAST_INSERT_ID',
    'LAST_VALUE',
    'LATERAL',
    'LCASE',
    'LEAST',
    'LENGTH',
    'LN',
    'LOAD_FILE',
    'LOCATE',
    'LOG',
    'LOG10',
    'LOG2',
    'LOWER',
    'LPAD',
    'LTRIM',
    'MAKEDATE',
    'MAKE_SET',
    'MASTER_POS_WAIT',
    'MD5',
    'MID',
    'MONTHNAME',
    'NAME_CONST',
    'NULLIF',
    'OCT',
    'OCTET_LENGTH',
    'OF',
    'OR',
    'ORD',
    'OVER',
    'PARAMETER',
    'PERIOD_ADD',
    'PERIOD_DIFF',
    'PI',
    'POSITION',
    'POW',
    'POWER',
    'QUOTE',
    'RANDOM_BYTES',
    'RANK',
    'READS',
    'REDOFILE',
    'REGEXP_INSTR',
    'REGEXP_LIKE',
    'REGEXP_REPLACE',
    'REGEXP_SUBSTR',
    'RELEASE_ALL_LOCKS',
    'RELEASE_LOCK',
    'REPLACE',
    'REPLICATE',
    'RESET',
    'RETURN',
    'RETURNS',
    'ROLES_GRAPHML',
    'ROUND',
    'RPAD',
    'RTRIM',
    'SCHEMA',
    'SEC_TO_TIME',
    'SESSION_USER',
    'SHA',
    'SHA1',
    'SHA2',
    'SKIP',
    'SLEEP',
    'SONAME',
    'SOUNDEX',
    'SOUNDS',
    'SOURCE_POS_WAIT',
    'SPACE',
    'SPATIAL',
    'SPECIFIC',
    'SQL_AFTER_GTIDS',
    'SQL_AFTER_MTS_GAPS',
    'SQL_BEFORE_GTIDS',
    'SQL_CALC_FOUND_ROWS',
    'SQL_SMALL_RESULT',
    'SQL_THREAD',
    'STACKED',
    'STATEMENT_DIGEST',
    'STATEMENT_DIGEST_TEXT',
    'STOP',
    'STORED',
    'STRAIGHT_JOIN',
    'STRCMP',
    'STR_TO_DATE',
    'SUBCLASS_ORIGIN',
    'SUBSTR',
    'SUBSTRING_INDEX',
    'SUBTIME',
    'SUSPEND',
    'SYSDATE',
    'SYSTEM_USER',
    'TIMEDIFF',
    'TIME_FORMAT',
    'TIME_TO_SEC',
    'TOP',
    'TO_BASE64',
    'TO_DAYS',
    'TO_SECONDS',
    'TYPES',
    'UCASE',
    'UNCOMPRESS',
    'UNCOMPRESSED_LENGTH',
    'UNDO',
    'UNDO_BUFFER_SIZE',
    'UNHEX',
    'UNINSTALL',
    'UNIQUE',
    'UNIX_TIMESTAMP',
    'UNLOCK',
    'UPDATEXML',
    'UPPER',
    'UUID',
    'UUID_SHORT',
    'UUID_TO_BIN',
    'VALIDATE_PASSWORD_STRENGTH',
    'VALUES',
    'VARIANCE',
    'VAR_VARIANCE',
    'VERSION',
    'WAIT_FOR_EXECUTED_GTID_SET',
    'WAIT_UNTIL_SQL_THREAD_AFTER_GTIDS',
    'WEEKDAY',
    'WEEKOFYEAR',
    'WITH',
    'WORK',
    'WRAPPER',
    'WRITE',
    'XA',
    'XID',
    'XML',
    'XOR',
    'YEARWEEK',
    'ZEROFILL',
)

not_keyword_token = (
    "ACCOUNT",
    "ACTION",
    "ADVISE",
    "AFTER",
    "AGAINST",
    "AGO",
    "ALGORITHM",
    "ALWAYS",
    "ANY",
    "ASCII",
    "AUTO_INCREMENT",
    "AVG",
    "AVG_ROW_LENGTH",
    "BACKUP",
    "BEGIN",
    "BINLOG",
    "BIT",
    "BOOL",
    "BOOLEAN",
    "BTREE",
    "BYTE",
    "CACHE",
    "CAPTURE",
    "CASCADED",
    "CAUSAL",
    "CHARSET",
    "CLEANUP",
    "CLIENT",
    "COALESCE",
    "COLLATION",
    "COLUMNS",
    "COLUMN_FORMAT",
    "COMMENT",
    "COMMIT",
    "COMMITTED",
    "COMPACT",
    "COMPRESSED",
    "COMPRESSION",
    "CONCURRENCY",
    "CONNECTION",
    "CONSISTENCY",
    "CONSISTENT",
    "CONTEXT",
    "CPU",
    "CURRENT",
    "CYCLE",
    "DATA",
    "DATE",
    "DATETIME",
    "DAY",
    "DECLARE",
    "DISABLE",
    "DISABLED",
    "DISCARD",
    "DISK",
    "DO",
    "DUPLICATE",
    "DYNAMIC",
    "ENABLE",
    "ENABLED",
    "END",
    "ENFORCED",
    "ENGINE",
    "ENUM",
    "ERROR",
    "ESCAPE",
    "EVENT",
    "EVENTS",
    "EXECUTE",
    "EXPANSION",
    "EXTENDED",
    "FIELDS",
    "FILE",
    "FIRST",
    "FLUSH",
    "FOLLOWING",
    "FORMAT",
    "FOUND",
    "FULL",
    "FUNCTION",
    "GENERAL",
    "GLOBAL",
    "GRANTS",
    "HANDLER",
    "HASH",
    "HELP",
    "HOSTS",
    "HOUR",
    "IDENTIFIED",
    "IMPORT",
    "INDEXES",
    "INSERT_METHOD",
    "INSTANCE",
    "INVISIBLE",
    "INVOKER",
    "IO",
    "IPC",
    "ISOLATION",
    "ISSUER",
    "JSON",
    "KEY_BLOCK_SIZE",
    "LANGUAGE",
    "LAST",
    "LESS",
    "LEVEL",
    "LIST",
    "LOCAL",
    "LOCATION",
    "LOCKED",
    "LOGS",
    "MASTER",
    'MAX',
    "MAX_ROWS",
    "MB",
    "MEMBER",
    "MEMORY",
    "MERGE",
    "MICROSECOND",
    "MINUTE",
    "MINVALUE",
    "MIN_ROWS",
    "MODE",
    "MODIFY",
    "MONTH",
    "NAMES",
    "NATIONAL",
    "NEVER",
    "NEXT",
    "NODEGROUP",
    "NONE",
    'NOW',
    "NOWAIT",
    "NULLS",
    "NVARCHAR",
    "OFF",
    "OFFSET",
    "ONLINE",
    "ONLY",
    "ON_DUPLICATE",
    "OPEN",
    "OPTIONAL",
    "PACK_KEYS",
    "PAGE",
    "PARSER",
    "PARTIAL",
    "PARTITIONING",
    "PARTITIONS",
    "PASSWORD",
    "PAUSE",
    "PER_DB",
    "PER_TABLE",
    "PLUGINS",
    "POINT",
    "POLICY",
    "PRECEDING",
    "PRESERVE",
    "PRIVILEGES",
    "PROCESSLIST",
    "PROFILE",
    "PROXY",
    "PURGE",
    "QUARTER",
    "QUERY",
    "QUICK",
    "REBUILD",
    "RECOVER",
    "REDUNDANT",
    "RELOAD",
    "REMOVE",
    "REORGANIZE",
    "REPAIR",
    "REPLICATION",
    "RESOURCE",
    "RESPECT",
    "RESTORE",
    "RESUME",
    "REVERSE",
    "ROLLBACK",
    'ROLLUP',
    'ROW',
    'ROWS',
    "ROW_COUNT",
    "ROW_FORMAT",
    "RTREE",
    "SAVEPOINT",
    "SECOND",
    "SEPARATOR",
    "SERIALIZABLE",
    "SESSION",
    "SHARE",
    "SHUTDOWN",
    'SIGN',
    "SIGNED",
    "SIMPLE",
    "SLAVE",
    "SLOW",
    "SNAPSHOT",
    "SOME",
    "SOURCE",
    "SQL_BUFFER_RESULT",
    "SQL_CACHE",
    "SQL_NO_CACHE",
    "SQL_TSI_DAY",
    "SQL_TSI_HOUR",
    "SQL_TSI_MINUTE",
    "SQL_TSI_MONTH",
    "SQL_TSI_QUARTER",
    "SQL_TSI_SECOND",
    "SQL_TSI_WEEK",
    "SQL_TSI_YEAR",
    "START",
    "STATS_AUTO_RECALC",
    "STATS_PERSISTENT",
    "STATS_SAMPLE_PAGES",
    "STATUS",
    "STORAGE",
    "SUBJECT",
    "SUPER",
    'SUM',
    "TABLES",
    "TABLESPACE",
    "TABLE_CHECKSUM",
    "TEMPORARY",
    "TEMPTABLE",
    "TIME",
    "TIMESTAMP",
    "TRANSACTION",
    "TRIGGERS",
    "TRUNCATE",
    "TYPE",
    "UNBOUNDED",
    "UNCOMMITTED",
    "UNDEFINED",
    "UNKNOWN",
    "USER",
    "VALIDATION",
    "VALUE",
    "VARIABLES",
    "WAIT",
    "WARNINGS",
    "WEEK",
    "WEIGHT_STRING",
    "WITHOUT",
    "X509",
    "YEAR",
)