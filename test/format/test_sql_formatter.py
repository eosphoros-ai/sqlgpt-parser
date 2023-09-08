import unittest

from sqlgpt_parser.format.formatter import format_sql
from sqlgpt_parser.sql_parser.mysql_parser import parser


class MyTestCase(unittest.TestCase):
    def test_union_all(self):
        statement = parser.parse(
            """
                SELECT * FROM T1 WHERE C1 < 20000 UNION ALL
                SELECT * FROM T1 WHERE C2 < 30
                """
        )
        after_sql_rewrite_format = format_sql(statement, 0)
        assert (
            after_sql_rewrite_format
            == """SELECT
  *
FROM
  T1
WHERE C1 < 20000
UNION ALL
SELECT
  *
FROM
  T1
WHERE C2 < 30"""
        )

    def test_union(self):
        statement = parser.parse(
            """
                    SELECT * FROM T1 WHERE C1 < 20000 UNION
                    SELECT * FROM T1 WHERE C2 < 30
                    """
        )
        after_sql_rewrite_format = format_sql(statement, 0)
        assert (
            after_sql_rewrite_format
            == """SELECT
  *
FROM
  T1
WHERE C1 < 20000
UNION
SELECT
  *
FROM
  T1
WHERE C2 < 30"""
        )

    def test_as(self):
        statement = parser.parse("""SELECT a.* FROM d1 as a""")
        after_sql_rewrite_format = format_sql(statement, 0)
        assert (
            after_sql_rewrite_format
            == """SELECT
  a.*
FROM
  d1 AS a"""
        )

    def test_update(self):
        statement = parser.parse(
            """update t set a = 1,b = 2 where c= 3""",
        )
        after_sql_rewrite_format = format_sql(statement, 0)
        assert after_sql_rewrite_format == """UPDATE t SET a = 1 , b = 2 WHERE c = 3"""
        statement = parser.parse(
            """update t set a = 1,b = 2 where c= 3 order by c limit 1""",
        )
        after_sql_rewrite_format = format_sql(statement, 0)
        assert (
            after_sql_rewrite_format
            == """UPDATE t SET a = 1 , b = 2 WHERE c = 3
ORDER BY c ASC
LIMIT 1"""
        )

    def test_delete(self):
        statement = parser.parse("""delete from t where c= 3 and a = 1""")
        after_sql_rewrite_format = format_sql(statement, 0)
        assert after_sql_rewrite_format == """DELETE FROM t WHERE c = 3 AND a = 1"""

        statement = parser.parse(
            """delete from t where c= 3 and a = 1 order by c limit 1""",
        )
        after_sql_rewrite_format = format_sql(statement, 0)
        assert (
            after_sql_rewrite_format
            == """DELETE FROM t WHERE c = 3 AND a = 1
ORDER BY c ASC
LIMIT 1"""
        )

    def test_sql_1(self):
        statement = parser.parse(
            """select tnt_inst_id as tnt_inst_id,gmt_create as gmt_create,gmt_modified as gmt_modified,principal_id as principal_id,version as version from cu_version_control where (principal_id = 'TOKENREL|100100000003358587777|IPAY_HK'  )""",
        )
        after_sql_rewrite_format = format_sql(statement, 0)
        assert (
            after_sql_rewrite_format
            == """SELECT
  tnt_inst_id AS tnt_inst_id
, gmt_create AS gmt_create
, gmt_modified AS gmt_modified
, principal_id AS principal_id
, version AS version
FROM
  cu_version_control
WHERE principal_id = \'TOKENREL|100100000003358587777|IPAY_HK\'"""
        )

    def test_subquery_limit(self):
        statement = parser.parse(
            """
                SELECT COUNT(*) FROM ( SELECT * FROM customs_script_match_history LIMIT ? ) a
        """
        )
        after_sql_rewrite_format = format_sql(statement, 0)
        assert (
            after_sql_rewrite_format
            == """SELECT
  COUNT(*)
FROM
  (SELECT
     *
   FROM
     customs_script_match_history
   LIMIT ?) a"""
        )

    def test_cast_convert_format(self):
        test_sqls_except = {
            "select cast(1 as real)": "SELECT\n  CAST(1 AS REAL)",
            "select convert(1,real)": "SELECT\n  CONVERT(1, REAL)",
            "select convert(1 using 'utf-8')": "SELECT\n  CONVERT(1 USING 'utf-8')",
            "select binary 1+1": "SELECT\n  BINARY 1 + 1",
            "select _binary '1'": "SELECT\n  BINARY '1'",
        }
        for sql, except_sql in test_sqls_except.items():
            statement = parser.parse(sql)
            after_sql_rewrite_format = format_sql(statement, 0)
            assert after_sql_rewrite_format == except_sql

    def test_match_against(self):
        test_sqls_except = {
            "select articles.name from articles where match (title, content) against ('Python')": "SELECT\n  articles.name\nFROM\n  articles\nWHERE MATCH(title, content) AGAINST ('Python')",
            "select match (a) against ('abc' in natural language mode) from t": "SELECT\n  MATCH(a) AGAINST ('abc' IN NATURAL LANGUAGE MODE)\nFROM\n  t",
            "select match (a) against ('abc' in natural language mode with query expansion) from t": "SELECT\n  MATCH(a) AGAINST ('abc' IN NATURAL LANGUAGE MODE WITH QUERY EXPANSION)\nFROM\n  t",
        }
        for sql, except_sql in test_sqls_except.items():
            statement = parser.parse(sql)
            after_sql_rewrite_format = format_sql(statement, 0)
            assert after_sql_rewrite_format == except_sql

    def test_group_concat(self):
        test_sqls_except = {
            "select id, group_concat(category) as unique_categories\nfrom products\ngroup by id": "SELECT\n  id\n, GROUP_CONCAT(category) AS unique_categories\nFROM\n  products\nGROUP BY id",
            "select id, group_concat(distinct category) as unique_categories\nfrom products\ngroup by id": "SELECT\n  id\n, GROUP_CONCAT(DISTINCT category) AS unique_categories\nFROM\n  products\nGROUP BY id",
            "select id, group_concat(category separator ';') as all_categories from products group by id": "SELECT\n  id\n, GROUP_CONCAT(category SEPARATOR ';') AS all_categories\nFROM\n  products\nGROUP BY id",
        }
        for sql, except_sql in test_sqls_except.items():
            statement = parser.parse(sql)
            after_sql_rewrite_format = format_sql(statement, 0)
            assert after_sql_rewrite_format == except_sql

    def test_trim_func(self):
        test_sqls_except = {
            "SELECT TRIM('  bar   ')": "SELECT\n  TRIM(BOTH ' ' FROM '  bar   ')",
            "SELECT TRIM(LEADING 'x' FROM 'xxxbarxxx')": "SELECT\n  TRIM(LEADING 'x' FROM 'xxxbarxxx')",
            "SELECT TRIM('x' FROM 'xxxbarxxx')": "SELECT\n  TRIM(BOTH 'FROM' FROM 'xxxbarxxx')",
            "SELECT TRIM(TRAILING 'xyz' FROM 'barxxyz')": "SELECT\n  TRIM(TRAILING 'xyz' FROM 'barxxyz')",
        }
        for sql, except_sql in test_sqls_except.items():
            statement = parser.parse(sql)
            after_sql_rewrite_format = format_sql(statement, 0)
            assert after_sql_rewrite_format == except_sql

    def test_member_of(self):
        test_sqls_except = {
            """SELECT 'Horse' MEMBER OF( '[ "Cat", "Dog", "Bird" ]' )""": """SELECT\n  'Horse' MEMBER OF ('[ "Cat", "Dog", "Bird" ]')"""
        }
        for sql, except_sql in test_sqls_except.items():
            statement = parser.parse(sql)
            after_sql_rewrite_format = format_sql(statement, 0)
            print(after_sql_rewrite_format)
            assert after_sql_rewrite_format == except_sql


if __name__ == '__main__':
    unittest.main()
