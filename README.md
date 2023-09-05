# sqlgpt-parser

sqlgpt-parser is a Python implementation of an SQL parser that effectively converts SQL statements into Abstract Syntax Trees (AST). By leveraging AST tree comparisons between two SQL queries, it becomes possible to achieve robust evaluation of text-to-SQL models.

## Quick Start

```sh
pip install sqlgpt-parser
```

```sh
>>> from sql_parser.mysql_parser import parser as mysql_parser
>>> mysql_parser.parse("select * from t")
Query(query_body=QuerySpecification(select=Select(distinct=False, select_items=[SingleColumn(expression=QualifiedNameReference(name=QualifiedName.of("*")))]), from_=Table(name=QualifiedName.of("t"), for_update=False), order_by=[], limit=0, offset=0, for_update=False, nowait_or_wait=False), order_by=[], limit=0, offset=0)
>>> from sql_parser.oceanbase_parser import parser as oceanbase_parser
>>> oceanbase_parser.parse("select * from t")
Query(query_body=QuerySpecification(select=Select(distinct=False, select_items=[SingleColumn(expression=QualifiedNameReference(name=QualifiedName.of("*")))]), from_=Table(name=QualifiedName.of("t"), for_update=False), order_by=[], limit=0, offset=0, for_update=False, nowait_or_wait=False), order_by=[], limit=0, offset=0)
>>> from sql_parser.odps_parser import parser as odps_parser
>>> odps_parser.parse("select * from t")
Query(query_body=QuerySpecification(select=Select(distinct=False, select_items=[SingleColumn(expression=QualifiedNameReference(name=QualifiedName.of("*")))]), from_=Table(name=QualifiedName.of("t"), for_update=False), order_by=[], limit=0, offset=0, for_update=False, nowait_or_wait=False), order_by=[], limit=0, offset=0)
```

## Getting Started with SQL Parser Development

English Document: [SQL Parser Development Guide](./docs/docs-en/SQL%20Parser%20Development%20Guide.md)
中文文档：[SQL Parser 开发指南](./docs/docs-ch/SQL%20Parser%20开发指南.md)