import unittest

from sqlgpt_parser.parser.parser_utils import ParserUtils

from sqlgpt_parser.format.formatter import format_sql
from sqlgpt_parser.parser.oceanbase_parser import parser


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
            assert after_sql_rewrite_format == except_sql

    def test_time_interval(self):
        test_sqls_except = {
            "SELECT date FROM `inv` WHERE date=DATE_ADD(creation_time, INTERVAL 4 HOUR)": "SELECT\n  date\nFROM\n  inv\nWHERE date = DATE_ADD(creation_time, INTERVAL 4 HOUR)"
        }
        for sql, except_sql in test_sqls_except.items():
            statement = parser.parse(sql)
            after_sql_rewrite_format = format_sql(statement, 0)
            assert after_sql_rewrite_format == except_sql

    def test_windows_function(self):
        test_sqls_except = {
            "SELECT  first_value(value) OVER (PARTITION BY id ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND "
            "UNBOUNDED FOLLOWING) AS first_val FROM  my_table": "SELECT\n"
            "  FIRST_VALUE(value) OVER (ORDER BY date ASC ROWS BETWEEN UNBOUNDED  PRECEDING AND UNBOUNDED  FOLLOWING) AS first_val"
            "\nFROM\n  my_table",
            "SELECT first_value(value) OVER (PARTITION BY id ORDER BY date RANGE UNBOUNDED PRECEDING) "
            "AS first_val FROM my_table": "SELECT"
            "\n  FIRST_VALUE(value) OVER (ORDER BY date ASC RANGE UNBOUNDED  PRECEDING) AS first_val"
            "\nFROM"
            "\n  my_table",
        }
        for sql, except_sql in test_sqls_except.items():
            statement = parser.parse(sql)
            after_sql_rewrite_format = format_sql(statement, 0)
            assert after_sql_rewrite_format == except_sql

    def test_sql(self):
        test_sqls = [
            """
            SELECT T1.id 
FROM
    (SELECT T2.id
     FROM (SELECT T3.id FROM table1 AS T3) AS T2) AS T1 
           """,
            "update sqless_base set nick=1231 where a = 1 and b = 2 ",
            "select 1,t2.a from t1 left join t2 where t1.d > 2 and t2.a =1",
        ]
        except_table_list = [
            [
                {
                    "alias": "",
                    "filter_column_list": [
                        {"column_name": "a", "opt": "="},
                        {"column_name": "b", "opt": "="},
                    ],
                    "table_name": "sqless_base",
                }
            ],
            [
                {"alias": "", "filter_column_list": [], "table_name": "t1"},
                {
                    "alias": "",
                    "filter_column_list": [
                        {"column_name": "d", "opt": ">"},
                        {"column_name": "a", "opt": "="},
                    ],
                    "table_name": "t2",
                },
            ],
        ]
        except_projection_list = [[], ["a"]]
        for index, sql in enumerate(test_sqls):
            statement = parser.parse(sql)
            visitor = ParserUtils.format_statement(statement)
            columns = visitor.columns
            print(columns)
            assert visitor.table_list == except_table_list[index]
            assert visitor.projection_column_list == except_projection_list[index]

    def test_extract_columns_from_tables(self):
        test_sqls = [
            """SELECT bss.segment_code as segmentCode,
ss.name as segmentName,
t.count
from tb_biz_settle_segment_031 bss
INNER JOIN tb_settle_segment ss on bss.segment_code= ss.code
LEFT JOIN(
SELECT stn.segment_code, count(1) as count
from tt_settle_task_node stn
left join tt_settle_task st on stn.task_id = st.id
left join tb_settle_segment ss on stn.segment_code = ss.code
left join ts_biz_contract bc on st.biz_contract_id = bc.id
left join ts_settle_target sta on bc.settle_target_id = sta.id
WHERE
st.biz_type= '1'
and stn.id in
(
SELECT t1.id FROM tt_settle_task_node AS t1
RIGHT JOIN (SELECT max(gmt_create) maxtime,task_id FROM tt_settle_task_node GROUP BY task_id) t2 ON t2.maxtime =
t1.gmt_create AND t1.task_id = t2.task_id
)
and sta.target_name like CONCAT('%','1','%')
and stn.operator = '1'
and st.id = '1'
and st.status = '1'
and sta.target_id = '1'
and bc.contract_no = '1'
and st.bill_limit_time >= '2022-10-09 07:59:08.091'
and st.bill_limit_time <= '2022-10-09 07:59:08.09'
and stn.limit_time >= '2022-10-09 07:59:08.091'
and stn.limit_time <= '2022-10-09 07:59:08.089'
and bc.business like CONCAT('%','业务线','%')
and stn.assigner like CONCAT('%','william.ccz','%')
GROUP BY stn.segment_code) t on bss.segment_code= t.segment_code
WHERE bss.biz_type= '1'
ORDER BY bss.sort asc
            """,
            """
                        SELECT ID, TNT_INST_ID, TRACE_ID, STATUS, COMMAND_TYPE, EXECUTE_TIMES, NEXT_EXECUTE_TIME, BUSINESS_NO, CONTEXT, EVENT_CONTEXT, GMT_CREATE, CREATOR, GMT_MODIFY, MODIFIER, HOSTNAME, LOG_ENV FROM bk_fintaxprod084.ftp_asyn_executor_cmd_084 WHERE STATUS = 'PROCESSING' AND NEXT_EXECUTE_TIME < DATE_SUB(now(6),INTERVAL 300 SECOND) ORDER BY NEXT_EXECUTE_TIME LIMIT 0,50
            """,
            """
            select id, case_id, case_name, case_type, case_path, test_method, case_description, related_test_suite_id, elapsed_time, status, case_result, related_instruct_id, case_log, effectiveness, run_count, is_latest, tenant_code, bundle_name, execute_time, groups, case_owner, sharding_index, failed_type, failed_reason, trace_id, operator, method_path, case_granularity, old_result, validity, invalid_reason, validity_info, invalid_types, changed_type, gmt_create, gmt_modified from rtc_exec_case_serial_08 force index(idx_instruct_id) where 1=1 AND related_instruct_id = '20240704153733102900872062986108' AND is_latest = '1' AND case_result in ( 'SUCCESS' , 'FAIL' , 'IGNORE' , 'READY' , 'UNKNOWN' ) order by case_result asc ,id asc limit 0,15
            """,
            """
                        SELECT T1.id, T1.name FROM battle EXCEPT SELECT T1.id, T1.name FROM battle AS T1 JOIN ship AS T2 ON T1.id  =  T2.lost_in_battle WHERE T2.location  =  'English Channel'
            """,
            """
SELECT group_name, TRIM(LEADING 'Group' FROM group_name) AS trimmed_group_name FROM tb_user_loNMNhir WHERE add_days BETWEEN 30 AND 60
            """,
            """
SELECT industry_code, TRIM(TRAILING '_LOW' FROM capital_inflows) AS trimmed_capital_inflows FROM tb_capital_MxYu6qSm WHERE gmt_create > '2023-03-01 00:00:00'
            """,
            """
SELECT TRIM(user_id) AS trimmed_user_id, total_amount, total_profit FROM tb_detail_SgwKFFMT WHERE page_num = 1 AND channel = '基金'
            """,
            """
            select
  d.id
from
    dx_slm_branch_smoke_record as d,
     dx_slm_service as e,
   dx_slm_branch as b
where
  d.is_delete = 0
  and d.input_template is not null
  and d.node_id is not null
  and b.branch_id = d.branch_id
  and b.service_id = e.service_id
  and e.inst_id = 'ACDE_ALICE'
  and d.env = 'TEST'
  and d.status = 1
  and e.service_call_type = 'BT'
order by
  d.id DESC
            """,
            """
            SELECT Name FROM singer WHERE Singer_ID NOT IN (SELECT Singer_ID FROM song)
            """,
            """
            SELECT country FROM singer WHERE age  >  40 INTERSECT SELECT country FROM singer WHERE age  <  30
            """,
            """
            SELECT T1.fname ,  T1.age FROM student AS T1 JOIN has_pet AS T2 ON T1.stuid  =  T2.stuid JOIN pets AS T3 ON T3.petid  =  T2.petid WHERE T3.pettype  =  'dog' AND T1.stuid NOT IN (SELECT T1.stuid FROM student AS T1 JOIN has_pet AS T2 ON T1.stuid  =  T2.stuid JOIN pets AS T3 ON T3.petid  =  T2.petid WHERE T3.pettype  =  'cat')
            """,
            """
            SELECT stuid FROM student EXCEPT SELECT T1.stuid FROM student AS T1 JOIN has_pet AS T2 ON T1.stuid  =  T2.stuid JOIN pets AS T3 ON T3.petid  =  T2.petid WHERE T3.pettype  =  'cat'
            """,
            """
            SELECT count(*) FROM Dogs WHERE dog_id NOT IN ( SELECT dog_id FROM Treatments )
            """,
            """
            SELECT customer_details FROM customers UNION SELECT staff_details FROM staf
            """,
            """
            SELECT Users.Id AS \"user_link\", QuestionCounts.Number AS \"number_of_questions\", AnswerCounts.Number AS \"number_of_answers\", Users.Location FROM (SELECT OwnerUserId, COUNT(Id) AS Number FROM Posts WHERE PostTypeId = 1 GROUP BY OwnerUserId) AS QuestionCounts, (SELECT OwnerUserId, COUNT(Id) AS Number FROM Posts WHERE PostTypeId = 2 GROUP BY OwnerUserId) AS AnswerCounts, Users WHERE Users.Id = QuestionCounts.OwnerUserId AND Users.Id = AnswerCounts.OwnerUserId ORDER BY QuestionCounts.Number DESC
            """,
            """
            SELECT ( SELECT COUNT(customerNumber) FROM customers WHERE creditLimit <= 100000 AND customerNumber IN ( SELECT customerNumber FROM payments WHERE CONCAT(\"%Y\"| paymentDate) = \"2004\" ) ), T1.customerName FROM customers AS T1 INNER JOIN payments AS T2 ON T1.customerNumber = T2.customerNumber WHERE T1.creditLimit <= 100000 AND CONCAT(\"%Y\"| T2.paymentDate) = \"2004\" GROUP BY T1.customerNumber, T1.customerName ORDER BY SUM(T2.amount) DESC LIMIT 1
            """,
            """
            select property_name from Properties where property_type_code = 'hse' or property_type_code = 'apt' and room_count > 1
            """,
            """SELECT h.hours AS \"hour\", COUNT(counter) AS AmountOfActivity FROM (SELECT CONCAT(CreationDate, 
            \"%h\") AS active, 1 AS counter FROM Posts WHERE OwnerUserId = 21216 UNION ALL SELECT CONCAT(
            CreationDate, \"%h\") AS active, 1 AS counter FROM Comments WHERE UserId = 21216) AS a RIGHT JOIN (SELECT 
            DISTINCT CONCAT(CreationDate, \"%h\") AS hours FROM Posts) AS h ON a.active = h.hours GROUP BY 
            h.hours ORDER BY h.hours
            """,
            """
            SELECT RelatedPostId AS \"post_link\", COUNT(*) AS \"Number of duplicates\" FROM PostLinks JOIN Posts AS q ON q.Id = RelatedPostId JOIN PostTags AS pt ON q.Id = pt.PostId JOIN Tags AS t ON pt.TagId = t.Id WHERE LinkTypeId = 3 AND t.TagName = \"##Tag:string##\"
GROUP BY RelatedPostId
ORDER BY COUNT(*) DESC
LIMIT 100
            """,
            """
SELECT low,
       high
FROM
  (SELECT Id,
          low
   FROM
     (SELECT n1.Id AS ID,
             MIN(n2.Id) + 1 AS low
      FROM Posts AS n1
      INNER JOIN Posts AS n2 ON n1.Id < n2.Id
      WHERE n1.Id < 5000
        AND n2.Id < 5000
      GROUP BY n1.Id) AS t
   WHERE t.low NOT IN
       (SELECT Id
        FROM Posts)
     AND t.low <
       (SELECT MAX(Id)
        FROM Posts)) AS t
INNER JOIN
  (SELECT Id - 1 AS ID,
          high
   FROM
     (SELECT n1.Id AS ID,
             MIN(n2.Id) - 1 AS high
      FROM Posts AS n1
      INNER JOIN Posts AS n2 ON n1.Id < n2.Id
      WHERE n1.Id < 5000
        AND n2.Id < 5000
      GROUP BY n1.Id) AS t
   WHERE t.high NOT IN
       (SELECT Id
        FROM Posts)) AS t2 ON t.Id = t2.Id
            """,
            """
SELECT p.Id,
       p.Score AS ave
FROM Posts AS p
LEFT JOIN Users AS u ON p.OwnerUserId = u.Id
LEFT JOIN
  (SELECT u.Id AS u_id,
          MIN(p.Id) AS min_pid
   FROM Posts AS p
   LEFT JOIN Users AS u ON p.OwnerUserId = u.Id
   GROUP BY u.Id) AS mp ON mp.u_id = u.Id
AND mp.min_pid = p.Id
WHERE p.PostTypeId = 1
  AND p.Body LIKE \"%downvote%\"
  AND p.Id > 48750000
  AND p.Id < 50000000
ORDER BY p.Score DESC
            """,
            """
            SELECT DISTINCT course.department, course.name, course.number, semester.semester, semester.year, student_record.grade FROM course, semester, student_record WHERE student_record.course_id = course.course_id AND student_record.semester = semester.semester_id AND student_record.student_id = 1
            """,
            """
            SELECT SUM(IF(T3.name IS NULL, 1, 0)) AS \"result\" FROM enlist AS T1 INNER JOIN person AS T2 ON T1.name = T2.name LEFT JOIN male AS T3 ON T2.name = T3.name WHERE T1.organ = \"army\"
            """,
            """
            SELECT neighborhood.name FROM business, neighborhood, review, user WHERE neighborhood.business_id = business.business_id AND review.business_id = business.business_id AND user.name = "Michelle" AND user.user_id = review.user_id
            """,
            """
            (SELECT jyjgzbb.* FROM hz_info JOIN mzjzjlb JOIN jybgb JOIN jyjgzbb ON hz_info.YLJGDM = mzjzjlb.YLJGDM AND hz_info.KH = mzjzjlb.KH AND hz_info.KLX = mzjzjlb.KLX AND mzjzjlb.YLJGDM = jybgb.YLJGDM_MZJZJLB AND mzjzjlb.JZLSH = jybgb.JZLSH_MZJZJLB AND jybgb.YLJGDM = jyjgzbb.YLJGDM AND jybgb.BGDH = jyjgzbb.BGDH WHERE hz_info.RYBH = "90117993" AND jyjgzbb.JYRQ BETWEEN "2010-08-23" AND "2021-08-22" AND jyjgzbb.JCZBDM = "956786") UNION (SELECT jyjgzbb.* FROM hz_info JOIN zyjzjlb JOIN jybgb JOIN jyjgzbb ON hz_info.YLJGDM = zyjzjlb.YLJGDM AND hz_info.KH = zyjzjlb.KH AND hz_info.KLX = zyjzjlb.KLX AND zyjzjlb.YLJGDM = jybgb.YLJGDM_ZYJZJLB AND zyjzjlb.JZLSH = jybgb.JZLSH_ZYJZJLB AND jybgb.YLJGDM = jyjgzbb.YLJGDM AND jybgb.BGDH = jyjgzbb.BGDH WHERE hz_info.RYBH = "90117993" AND jyjgzbb.JYRQ BETWEEN "2010-08-23" AND "2021-08-22" AND jyjgzbb.JCZBDM = "956786")
            """,
            """
            SELECT DISTINCT T2.customer_name FROM customers AS T2 LEFT JOIN (orders AS T1 JOIN order_items AS T3 ON T1.order_id = T3.order_id AND T3.product_id IS NULL) ON T2.customer_id = T1.customer_id'
            """,
            """
            SELECT T3.customer_name, ((SELECT COUNT(*) FROM order_items WHERE order_id IN (SELECT order_id FROM orders WHERE customer_id = T3.customer_id)) / COUNT(*)) FROM orders AS T2 JOIN customers AS T3 ON T2.customer_id = T3.customer_id GROUP BY T3.customer_id HAVING count(*) <= 3
            """,
            """
            SELECT T1.company_name FROM Third_Party_Companies AS T1 JOIN Maintenance_Contracts AS T2 ON T1.company_id  =  T2.maintenance_contract_company_id JOIN Ref_Company_Types AS T3 ON T1.company_type_code  =  T3.company_type_code ORDER BY T2.contract_end_date DESC LIMIT 1
            """,
            """
            SELECT AVG(T3.list_movie_number) , SUM(CASE WHEN T1.rating_score = 5 THEN 1 ELSE 0 END) FROM ratings AS T1 INNER JOIN lists_users AS T2 ON T1.user_id = T2.user_id INNER JOIN lists AS T3 ON T2.user_id = T3.user_id WHERE T1.user_id = 8516503
            """,
            """
            SELECT T1.lesson_id FROM Lessons AS T1 JOIN Staff AS T2 ON T1.staff_id = T2.staff_id WHERE T2.first_name = "Janessa" AND T2.last_name = "Sawayn" AND nickname LIKE "%s%"
            """,
            """
                        SELECT T1.name, T1.won FROM teams AS T1 INNER JOIN ( SELECT * FROM teams WHERE year = 2004 ) AS T2 on T1.tmID = T2.tmID WHERE T1.year = 2005 and T1.won > T2.won""",
            """
            SELECT count(*) FROM department WHERE department_id NOT IN (SELECT department_id FROM management);
            """,
            """
SELECT T2.productName,
    SUM(T1.quantityOrdered * T1.priceEach)
FROM orderdetails AS T1
INNER JOIN
  (SELECT productCode,
          productName
   FROM products
   ORDER BY MSRP - buyPrice DESC
   LIMIT 1) AS T2 ON T1.productCode = T2.productCode
UNION
SELECT T2.productName,
       SUM(quantityOrdered * priceEach)
FROM orderdetails AS T1
INNER JOIN
  (SELECT productCode,
          productName
   FROM products
   ORDER BY MSRP - buyPrice ASC
   LIMIT 1) AS T2 ON T1.productCode = T2.productCode
            """,
            """
            SELECT avg(ranking) ,  T1.first_name FROM players AS T1 JOIN rankings AS T2 ON T1.player_id  =  T2.player_id GROUP BY T1.first_name
            """,
            """
            SELECT count(*)
                FROM routes
            WHERE dst_apid =
                (SELECT apid
                    FROM airports
                    WHERE country='Canada')
            AND src_apid =
                (SELECT t.apid
                    FROM airports AS t
                    WHERE country='United States')
            """,
            """SELECT T1.ProductModelID FROM ProductModelProductDescriptionCulture AS T1 INNER JOIN Culture AS T2 
            USING (cultureid) INNER JOIN ProductDescription AS T3 USING (productdescriptionid) WHERE T3.Description 
            LIKE 'Chromoly steel%' AND T2.Name = 'English'""",
            """SELECT T1.ProductModelID FROM ProductModelProductDescriptionCulture AS T1 INNER JOIN Culture AS T2 
            USING (cultureid) INNER JOIN ProductDescription AS T3 USING (productdescriptionid) WHERE T3.Description 
            LIKE 'Chromoly steel%' AND T2.Name = 'English""",
            """SELECT COUNT(T1.business_id) FROM Business AS T1 INNER JOIN Business_Categories ON T1.business_id = 
            Business_Categories.business_id INNER JOIN Categories AS T3 ON Business_Categories.category_id = 
            T3.category_id WHERE T1.stars = 5 AND T3.category_name LIKE 'Fashion'""",
            """
            SELECT T.title
                FROM
                (SELECT T3.title,
                    COUNT(T1.customer_id) AS num
                FROM rental AS T1
                INNER JOIN inventory AS T2 ON T1.inventory_id = T2.inventory_id
                INNER JOIN film AS T3 ON T2.film_id = T3.film_id
                GROUP BY T3.title) AS T
            ORDER BY T.num DESC
            LIMIT 1""",
        ]
        for index, sql in enumerate(test_sqls):
            statement = parser.parse(sql)
            visitor = ParserUtils.format_statement(statement)
            columns = visitor.columns
            print(columns)


if __name__ == "__main__":
    unittest.main()
