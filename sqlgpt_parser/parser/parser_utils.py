# coding=utf-8
"""

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""
import copy

from sqlgpt_parser.parser.tree.grouping import GroupingSets, SimpleGroupBy
from sqlgpt_parser.parser.tree.literal import StringLiteral, Literal
from sqlgpt_parser.parser.tree.visitor import DefaultTraversalVisitor
from sqlgpt_parser.parser.tree.expression import (
    InListExpression,
    QualifiedNameReference,
    SubqueryExpression,
)
from sqlgpt_parser.parser.tree.query_specification import QuerySpecification
from sqlgpt_parser.parser.tree.join_criteria import JoinOn, JoinUsing
from sqlgpt_parser.parser.tree.relation import AliasedRelation
from sqlgpt_parser.parser.tree.table import Table
from sqlgpt_parser.utils.untils import (
    convert_nested_strings_to_lowercase,
    get_string_values,
)
from sqlgpt_parser.parser.tree.statement import Query
from sqlgpt_parser.parser.tree.set_operation import Except


class ParserUtils(object):
    class CollectInfo:
        COLLECT_FILTER_COLUMN = 1
        COLLECT_PROJECT_COLUMN = 2
        COLLECT_TABLE = 4
        COLLECT_MIN_MAX_EXPRESSION_COLUMN = 8
        COLLECT_IN_EXPRESSION_COLUMN = 16
        COLLECT_ORDER_BY_COLUMN = 32
        COLLECT_GROUP_BY_COLUMN = 64
        COLLECT_HAVING_COLUMN = 128

    @staticmethod
    def format_statement(statement):
        class FormatVisitor(DefaultTraversalVisitor):
            def __init__(self):
                """
                [
                    {
                        alias :
                        table_name :
                        filter_column_list: [
                            {
                                column_name :
                                opt :
                            },
                        ]
                    },
                    ...
                ]
                """
                self.table_list = []
                self.projection_column_list = []
                self.order_list = []
                self.min_max_list = []
                self.in_count_list = []
                self.limit_number = 0
                self.columns = []
                self.join_columns = []
                self.project_columns = []
                self.filter_columns = []
                self.having_columns = []
                self.in_columns = []
                self.group_by_columns = []
                self.order_by_columns = []
                self.recursion_count = 0
                self.table_dict = {}
                self.subquery_alias_projection = {}
                self.join_relations = []
                self.in_relations = []
                self.compare_filters = []
                self.alias_columns = {}

            def add_project_column(self, project_column):
                self.projection_column_list.append(project_column)

            def add_table(self, table_name, alias=""):
                self.table_list.append(
                    {"table_name": table_name, "alias": alias, "filter_column_list": []}
                )
                if alias == "":
                    self.table_dict[table_name.lower()] = table_name.lower()
                else:
                    if isinstance(table_name, dict):
                        self.table_dict[alias.lower()] = table_name
                    else:
                        self.table_dict[alias.lower()] = table_name.lower()

            def add_filter_column(
                self, filter_col, compare_type, table_or_alias_name=None
            ):
                filter_column_list = None
                if table_or_alias_name is not None:
                    for table in self.table_list:
                        if table["alias"].lower() == table_or_alias_name.lower() or (
                            not isinstance(table["table_name"], dict)
                            and table["table_name"].lower()
                            == table_or_alias_name.lower()
                        ):
                            filter_column_list = table["filter_column_list"]
                else:
                    filter_column_list = self.table_list[-1]["filter_column_list"]
                filter_column_list.append(
                    {"column_name": filter_col, "opt": compare_type}
                )

            def visit_table(self, node, context):
                table_name = node.name.parts[-1]
                self.add_table(table_name)
                context["tables"][table_name] = table_name
                return self.visit_query_body(node, context)

            def visit_aliased_relation(self, node, context):
                if len(node.alias) == 2:
                    alias = node.alias[1]
                else:
                    alias = node.alias[0]
                if (
                    not isinstance(node.relation, SubqueryExpression)
                    and context["op"] & ParserUtils.CollectInfo.COLLECT_TABLE
                ):
                    table_name = node.relation.name.parts[-1]
                    self.add_table(table_name, alias)
                    context["tables"][alias] = table_name
                    context["current_table"][alias] = table_name
                else:
                    context["alias"] = alias
                    return self.process(node.relation, context)

            def visit_subquery_expression(self, node, context):
                # copy_context 和 context 换一下
                table_dict = {}
                alias = None
                copy_context = copy.deepcopy(context)
                if context["op"] & ParserUtils.CollectInfo.COLLECT_TABLE:
                    table_dict = context["tables"]
                    copy_context["tables"] = {}
                    if "alias" in context:
                        alias = context["alias"]
                self.process(node.query, copy_context)
                if context["op"] & ParserUtils.CollectInfo.COLLECT_TABLE:
                    context_tables = copy_context["tables"]
                    if alias is not None:
                        # Associate the alias of a subquery with the table used in the subquery.
                        table_dict[alias.lower()] = context_tables
                        self.add_table(context_tables, alias)
                        self.subquery_alias_projection[alias.lower()] = copy_context[
                            "project_column"
                        ]
                    else:
                        table_dict.update(context_tables)
                    context["tables"] = table_dict
                context["subquery_project_column"] = copy_context["project_column"]

            def visit_logical_binary_expression(self, node, context):
                self.recursion_count = self.recursion_count + 1
                # A case similar to test_parser_utils.test_recursion_error may appear
                # discard the following data
                if self.recursion_count > 300:
                    return
                self.process(node.left, context)
                self.process(node.right, context)
                return None

            def visit_comparison_expression(self, node, context):
                left = node.left
                right = node.right
                if "collect_join" in context:
                    if isinstance(right, QualifiedNameReference) and isinstance(
                        left, QualifiedNameReference
                    ):
                        context["join_column"].append(left.name.parts)
                        context["join_column"].append(right.name.parts)
                        context["join_relations"].append(
                            [left.name.parts, right.name.parts]
                        )

                def add_filter_column(name):
                    table_name = None
                    if len(name.parts) > 2:
                        table_name = name.parts[-2]
                    self.add_filter_column(name.parts[-1], node.type, table_name)

                def compare_process(node, context):
                    if isinstance(node, QualifiedNameReference):
                        add_filter_column(node.name)
                    self.process(node, context)

                def process_in_relation(context, single_column, subquery):
                    select_items = subquery.query.select.select_items
                    if len(select_items) == 1 and isinstance(
                        select_items[0].expression, QualifiedNameReference
                    ):
                        if len(select_items) == 1 and isinstance(
                            select_items[0].expression, QualifiedNameReference
                        ):
                            in_column = context["subquery_project_column"]
                            context["in_relations"].append(
                                [single_column.name.parts, in_column[0]]
                            )

                if isinstance(left, QualifiedNameReference) and isinstance(
                    right, Literal
                ):
                    context["compare_filters"].append(
                        [left.name.parts, node.type, right.value]
                    )

                compare_process(left, context)
                compare_process(right, context)

                if node.type == "=":
                    if isinstance(left, QualifiedNameReference) and isinstance(
                        right, SubqueryExpression
                    ):
                        process_in_relation(context, left, right)
                    elif isinstance(right, QualifiedNameReference) and isinstance(
                        left, SubqueryExpression
                    ):
                        process_in_relation(context, right, left)
                    elif isinstance(left, QualifiedNameReference) and isinstance(
                        right, QualifiedNameReference
                    ):
                        context["join_relations"].append(
                            [left.name.parts, right.name.parts]
                        )
                        context["join_column"].append(left.name.parts)
                        context["join_column"].append(right.name.parts)

            def visit_single_column(self, node, context):
                alias_name = None
                if node.alias is not None and len(node.alias) != 0:
                    alias = node.alias[1] if len(node.alias) == 2 else node.alias[0]
                    alias_name = (
                        alias.value if isinstance(alias, StringLiteral) else alias
                    )
                now_filter = len(context["filter_column"])
                now_project = len(context["project_column"])
                self.process(node.expression, context)
                if alias_name is not None:
                    new_filter = context["filter_column"][now_filter:]
                    new_project = context["project_column"][now_project:]
                    new_filter.extend(new_project)
                    context["column_alias"][alias_name] = new_filter

            def visit_like_predicate(self, node, context):
                if isinstance(node.value, QualifiedNameReference):
                    self.process(node.value, context)

                if isinstance(node.value, QualifiedNameReference):
                    pattern = node.pattern
                    if isinstance(pattern, StringLiteral):
                        if not pattern.value.startswith("%"):
                            pass
                else:
                    self.process(node.value, context)
                    self.process(node.pattern, context)

            def visit_not_expression(self, node, context):
                return self.process(node.value, context)

            def visit_in_predicate(self, node, context):
                value = node.value
                self.process(value, context)
                if not node.is_not:
                    if (
                        isinstance(node.value_list, InListExpression)
                        and context["op"]
                        & ParserUtils.CollectInfo.COLLECT_IN_EXPRESSION_COLUMN
                    ):
                        self.in_count_list.append(len(node.value_list.values))
                self.process(node.value_list, context)
                if isinstance(node.value_list, SubqueryExpression):
                    query = node.value_list.query
                    in_column = context["subquery_project_column"]
                    if isinstance(query, QuerySpecification):
                        if isinstance(
                            query.select.select_items[0].expression,
                            QualifiedNameReference,
                        ):
                            context["in_relations"].append(
                                [value.name.parts, in_column[0]]
                            )
                    elif isinstance(query, Query):
                        if isinstance(query.query_body, Except):
                            except_expression = query.query_body
                            if isinstance(
                                except_expression.left.select.select_items[
                                    0
                                ].expression,
                                QualifiedNameReference,
                            ):
                                context["in_relations"].append(
                                    [value.name.parts, in_column[0]]
                                )
                            elif isinstance(
                                except_expression.right.select.select_items[
                                    0
                                ].expression,
                                QualifiedNameReference,
                            ):
                                context["in_relations"].append(
                                    [value.name.parts, in_column[1]]
                                )
                        else:
                            for index, relation in enumerate(
                                query.query_body.relations
                            ):
                                if isinstance(
                                    relation.select.select_items[0].expression,
                                    QualifiedNameReference,
                                ):
                                    context["in_relations"].append(
                                        [value.name.parts, in_column[index]]
                                    )
                return None

            def visit_select(self, node, context):
                for item in node.select_items:
                    self.process(item, context)

            def visit_qualified_name_reference(self, node, context):
                if context["op"] & ParserUtils.CollectInfo.COLLECT_FILTER_COLUMN:
                    table_name = None
                    if len(node.name.parts) > 1:
                        table_name = node.name.parts[-2]
                    self.add_filter_column(node.name.parts[-1], None, table_name)
                    context["filter_column"].append(node.name.parts)

                if context["op"] & ParserUtils.CollectInfo.COLLECT_PROJECT_COLUMN:
                    context["project_column"].append(node.name.parts)
                    self.add_project_column(node.name.parts)

                if context["op"] & ParserUtils.CollectInfo.COLLECT_ORDER_BY_COLUMN:
                    context["order_by_column"].append(node.name.parts)

                if context["op"] & ParserUtils.CollectInfo.COLLECT_GROUP_BY_COLUMN:
                    context["group_by_column"].append(node.name.parts)

                if context["op"] & ParserUtils.CollectInfo.COLLECT_HAVING_COLUMN:
                    context["having_column"].append(node.name.parts)

            def visit_aggregate_func(self, node, context):
                if node.name.lower() == "count" and node.arguments[0] == "*":
                    if context["op"] & ParserUtils.CollectInfo.COLLECT_PROJECT_COLUMN:
                        context["project_column"].append(["*"])
                        self.add_project_column(["*"])
                    if context["op"] & ParserUtils.CollectInfo.COLLECT_FILTER_COLUMN:
                        context["filter_column"].append(["*"])

                    if context["op"] & ParserUtils.CollectInfo.COLLECT_ORDER_BY_COLUMN:
                        context["order_by_column"].append(["*"])

                    if context["op"] & ParserUtils.CollectInfo.COLLECT_GROUP_BY_COLUMN:
                        context["group_by_column"].append(["*"])

                    if context["op"] & ParserUtils.CollectInfo.COLLECT_HAVING_COLUMN:
                        context["having_column"].append(["*"])

                else:
                    for arg in node.arguments:
                        self.process(arg, context)
                    if (
                        context["op"]
                        & ParserUtils.CollectInfo.COLLECT_MIN_MAX_EXPRESSION_COLUMN
                    ):
                        context["min_max_expression_column"].append(node.arguments)
                        if node.name == "max" or node.name == "min":
                            # min or max only has one argument
                            self.min_max_list.append(node.arguments[0])

            def visit_sort_item(self, node, context):
                sort_key = node.sort_key
                ordering = node.ordering
                if isinstance(sort_key, QualifiedNameReference):
                    name = sort_key.name
                    self.order_list.append(
                        {"ordering": ordering, "column_name": name.parts}
                    )
                self.process(node.sort_key, context)

            def visit_query_specification(self, node, context):
                self.limit_number = node.limit

                context["tables"] = {}
                context["filter_column"] = []
                context["project_column"] = []
                context["order_by_column"] = []
                context["group_by_column"] = []
                context["having_column"] = []
                context["join_column"] = []
                context["min_max_expression_column"] = []
                context["column_alias"] = {}
                context["join_relations"] = []
                context["in_relations"] = []
                context["current_table"] = {}
                context["compare_filters"] = []
                context["column_alias"] = {}

                context["op"] = (
                    ParserUtils.CollectInfo.COLLECT_TABLE
                    | ParserUtils.CollectInfo.COLLECT_MIN_MAX_EXPRESSION_COLUMN
                    | ParserUtils.CollectInfo.COLLECT_IN_EXPRESSION_COLUMN
                )
                if node.from_:
                    if isinstance(node.from_, list):
                        for item in node.from_:
                            self.process(item, context)
                    else:
                        self.process(node.from_, context)
                context["op"] = (
                    ParserUtils.CollectInfo.COLLECT_PROJECT_COLUMN
                    | ParserUtils.CollectInfo.COLLECT_MIN_MAX_EXPRESSION_COLUMN
                    | ParserUtils.CollectInfo.COLLECT_IN_EXPRESSION_COLUMN
                )
                self.process(node.select, context)
                context["op"] = (
                    ParserUtils.CollectInfo.COLLECT_FILTER_COLUMN
                    | ParserUtils.CollectInfo.COLLECT_MIN_MAX_EXPRESSION_COLUMN
                    | ParserUtils.CollectInfo.COLLECT_IN_EXPRESSION_COLUMN
                )
                if node.where:
                    self.process(node.where, context)
                context["op"] = (
                    ParserUtils.CollectInfo.COLLECT_GROUP_BY_COLUMN
                    | ParserUtils.CollectInfo.COLLECT_IN_EXPRESSION_COLUMN
                    | ParserUtils.CollectInfo.COLLECT_MIN_MAX_EXPRESSION_COLUMN
                )
                if node.group_by:
                    grouping_elements = []
                    if isinstance(node.group_by, SimpleGroupBy):
                        grouping_elements = node.group_by.columns
                    elif isinstance(node.group_by, GroupingSets):
                        grouping_elements = node.group_by.sets
                    for grouping_element in grouping_elements:
                        self.process(grouping_element, context)
                context["op"] = (
                    ParserUtils.CollectInfo.COLLECT_HAVING_COLUMN
                    | ParserUtils.CollectInfo.COLLECT_IN_EXPRESSION_COLUMN
                    | ParserUtils.CollectInfo.COLLECT_MIN_MAX_EXPRESSION_COLUMN
                )
                if node.having:
                    self.process(node.having, context)

                context["op"] = (
                    ParserUtils.CollectInfo.COLLECT_ORDER_BY_COLUMN
                    | ParserUtils.CollectInfo.COLLECT_IN_EXPRESSION_COLUMN
                    | ParserUtils.CollectInfo.COLLECT_FILTER_COLUMN
                )
                for sort_item in node.order_by:
                    self.process(sort_item, context)

                tables = context["tables"]

                project_columns = self.convert_used_columns(
                    copy.deepcopy(context["project_column"]), tables
                )
                filter_columns = self.convert_used_columns(
                    copy.deepcopy(context["filter_column"]), tables
                )
                order_by_columns = self.convert_used_columns(
                    copy.deepcopy(context["order_by_column"]), tables
                )
                group_by_columns = self.convert_used_columns(
                    copy.deepcopy(context["group_by_column"]), tables
                )
                having_columns = self.convert_used_columns(
                    copy.deepcopy(context["having_column"]), tables
                )
                join_columns = self.convert_used_columns(
                    copy.deepcopy(context["join_column"]), tables
                )
                used_columns = []
                used_columns.extend(project_columns)
                used_columns.extend(filter_columns)
                used_columns.extend(order_by_columns)
                used_columns.extend(group_by_columns)
                used_columns.extend(having_columns)
                used_columns.extend(join_columns)

                # Join 处理
                join_relations = context["join_relations"]
                convert_nested_strings_to_lowercase(join_relations)
                for index, join_relation in enumerate(join_relations):
                    join_relations[index][0] = self.extract_used_table_column(
                        join_relations[index][0], tables
                    )[0]
                    join_relations[index][1] = self.extract_used_table_column(
                        join_relations[index][1], tables
                    )[0]
                # in expression of subquery
                in_relations = context["in_relations"]
                convert_nested_strings_to_lowercase(in_relations)
                for index, in_relation in enumerate(in_relations):
                    # in_relation[1] come from subquery, already get source name
                    in_relations[index][0] = self.get_source_table_name(
                        tables, in_relations[index][0]
                    )[0]
                    self.in_columns.extend(in_relations[index])

                # compare
                compare_filters = copy.deepcopy(context["compare_filters"])
                for compare_filter in compare_filters:
                    compare_filter[0] = self.get_source_table_name(
                        tables, compare_filter[0]
                    )[0]
                column_alias = copy.deepcopy(context["column_alias"])
                convert_nested_strings_to_lowercase(column_alias)
                for key, alias_column_names in column_alias.items():
                    column_source_table_name = []
                    for alias_column_name in alias_column_names:
                        column_source_table_name.extend(
                            self.extract_used_table_column(alias_column_name, tables)
                        )
                    column_alias[key] = column_source_table_name

                self.join_relations.extend(join_relations)
                self.in_relations.extend(in_relations)
                self.compare_filters.extend(compare_filters)
                self.alias_columns.update(column_alias)
                self.columns.extend(used_columns)
                self.filter_columns.extend(filter_columns)
                self.join_columns.extend(join_columns)
                self.order_by_columns.extend(order_by_columns)
                self.group_by_columns.extend(group_by_columns)
                self.having_columns.extend(having_columns)
                self.project_columns = project_columns
                context["tables"] = tables
                context["filter_column"] = []
                context["join_relations"] = []
                context["in_relations"] = []
                context["compare_filters"] = []
                context["column_alias"] = {}
                context["project_column"] = project_columns
                return None

            def convert_used_columns(self, used_columns, tables):
                convert_nested_strings_to_lowercase(used_columns)
                convert_nested_strings_to_lowercase(tables)
                order_by_columns = []
                for order_by_column in copy.deepcopy(used_columns):
                    order_by_columns.extend(
                        self.extract_used_table_column(order_by_column, tables)
                    )
                return order_by_columns

            def extract_used_table_column(self, alias_column_names, tables):
                used_columns = []
                if len(alias_column_names) == 1:
                    column_name = alias_column_names[0]
                else:
                    column_name = alias_column_names[1]
                if column_name in self.alias_columns:
                    used_columns.extend(self.alias_columns[column_name])
                else:
                    used_columns.extend(
                        self.get_source_table_name(tables, alias_column_names)
                    )
                return used_columns

            def get_source_table_name(self, tables, used_column_name):
                source_table_name_used_columns = []
                if len(used_column_name) > 1:
                    used_column = self.convert_from_alias_to_table(
                        used_column_name[0], used_column_name[1], tables
                    )
                    source_table_name_used_columns.append(used_column)
                elif used_column_name[0] == "*":
                    for table in tables:
                        source_table_name_used_columns.append([tables[table], "*"])
                else:
                    if len(tables) == 1:
                        table_name = tables[list(tables.keys())[0]]
                        source_table_name_used_columns.append(
                            [table_name, used_column_name[0]]
                        )
                    else:
                        source_table_name_used_columns.append(
                            [get_string_values(tables), used_column_name[0]]
                        )
                return source_table_name_used_columns

            def convert_from_alias_to_table(self, table_name, column_name, tables):
                # if the column may come from multi table,table_name will be a list
                if isinstance(table_name, list):
                    table_name_list = []
                    for alias_table_name in table_name:
                        used_table_name = self.extract_used_table_name(
                            alias_table_name, column_name, tables
                        )
                        table_name_list.append(used_table_name)
                    table_name = table_name_list
                else:
                    alias_table_name = table_name
                    table_name = self.extract_used_table_name(
                        alias_table_name, column_name, tables
                    )
                return [table_name, column_name]

            def extract_used_table_name(self, alias_table_name, column_name, tables):
                alias_table_name = alias_table_name.lower()
                if alias_table_name in tables:
                    if alias_table_name in self.subquery_alias_projection:
                        used_table_name = self.subquery_alias(
                            alias_table_name, column_name
                        )
                    else:
                        used_table_name = tables[alias_table_name]
                else:
                    used_table_name = self.table_dict[alias_table_name]
                return used_table_name

            def visit_update(self, node, context):
                table_list = node.table
                context = (
                    ParserUtils.CollectInfo.COLLECT_TABLE
                    | ParserUtils.CollectInfo.COLLECT_FILTER_COLUMN
                )
                if table_list:
                    for _table in table_list:
                        self.process(_table, context)
                if node.where:
                    self.process(node.where, context)
                return None

            def visit_delete(self, node, context):
                table_list = node.table
                context = (
                    ParserUtils.CollectInfo.COLLECT_TABLE
                    | ParserUtils.CollectInfo.COLLECT_FILTER_COLUMN
                )
                if table_list:
                    for _table in table_list:
                        self.process(_table, context)
                if node.where:
                    self.process(node.where, context)
                return None

            def visit_query(self, node, context):
                context["tables"] = {}
                context["filter_column"] = []
                context["project_column"] = []
                context["order_by_column"] = []
                context["group_by_column"] = []
                context["having_column"] = []
                context["join_column"] = []
                context["column_alias"] = {}
                context["join_relations"] = []
                context["in_relations"] = []
                context["current_table"] = {}
                context["compare_filters"] = []
                context["column_alias"] = {}

                context["op"] = 0
                self.process(node.query_body, context)
                context["op"] = ParserUtils.CollectInfo.COLLECT_ORDER_BY_COLUMN
                for sort_item in node.order_by:
                    self.process(sort_item, context)
                tables = context["tables"]
                used_columns = copy.deepcopy(context["order_by_column"])
                convert_nested_strings_to_lowercase(used_columns)
                convert_nested_strings_to_lowercase(tables)

                temp_used_columns = []
                for used_column_name in used_columns:
                    temp_used_columns.extend(
                        self.extract_used_table_column(used_column_name, tables)
                    )
                self.columns.extend(temp_used_columns)
                self.order_by_columns.extend(temp_used_columns)
                return None

            def visit_join(self, node, context):
                def join_table_alias(join_node, context):
                    if isinstance(join_node, Table):
                        alias = join_node.name.parts[0]
                    elif not isinstance(join_node, AliasedRelation):
                        alias = context["join_table"]
                    elif len(join_node.alias) == 2:
                        alias = join_node.alias[1]
                    else:
                        alias = join_node.alias[0]
                    return alias

                if isinstance(node.left, list):
                    for sub_node in node.left:
                        self.process(sub_node, context)
                else:
                    self.process(node.left, context)
                left_alias = join_table_alias(node.left, context)
                if isinstance(node.right, list):
                    for sub_node in node.right:
                        self.process(sub_node, context)
                else:
                    self.process(node.right, context)
                right_alias = join_table_alias(node.right, context)
                context["collect_join"] = True
                if isinstance(node.criteria, JoinOn):
                    alias = []
                    if isinstance(left_alias, str):
                        alias.append(left_alias)
                    else:
                        alias.extend(left_alias)
                    if isinstance(right_alias, str):
                        alias.append(right_alias)
                    else:
                        alias.extend(left_alias)
                    self.process(node.criteria.expression, context)
                    join_relations = context["join_relations"]
                    for join_relation in join_relations:
                        if len(join_relation[0]) == 1:
                            join_relation[0] = [alias, join_relation[0][0]]
                        if len(join_relation[1]) == 1:
                            join_relation[1] = [alias, join_relation[1][0]]
                elif isinstance(node.criteria, JoinUsing):
                    join_relations = context["join_relations"]
                    for column in node.criteria.columns:
                        left_key = [left_alias, column]
                        right_key = [right_alias, column]
                        join_relations.append([left_key, right_key])
                        context["join_column"].append(left_key)
                        context["join_column"].append(right_key)
                        self.process(column)
                context["join_table"] = [left_alias, right_alias]
                del context["collect_join"]
                return None

            def subquery_alias(self, alias_table_name, column_name):
                for sub_project_column in self.subquery_alias_projection[
                    alias_table_name
                ]:
                    if (
                        sub_project_column[-1].lower() == column_name.lower()
                        or sub_project_column[-1] == "*"
                    ):
                        if len(sub_project_column) > 1:
                            used_table = sub_project_column[-2]
                            return used_table

            def visit_between_predicate(self, node, context):
                self.process(node.value, context)
                self.process(node.max, context)
                self.process(node.min, context)
                return None

            def visit_union(self, node, context):
                tables, project_column = {}, []
                for relation in node.relations:
                    self.process(relation, context)
                    if "tables" in context:
                        tables.update(context["tables"])
                        context["tables"] = {}
                    if "project_column" in context:
                        project_column.extend(context["project_column"])
                        context["project_column"] = []
                context["tables"] = tables
                context["project_column"] = project_column
                self.project_columns = context["project_column"]
                return None

            def visit_intersect(self, node, context):
                tables = {}
                project_column = []
                for relation in node.relations:
                    self.process(relation, context)
                    if "tables" in context:
                        tables.update(context["tables"])
                        context["tables"] = {}
                    if "project_column" in context:
                        project_column.extend(context["project_column"])
                        context["project_column"] = []
                context["tables"] = tables
                context["project_column"].extend(project_column)
                self.project_columns = project_column
                return None

            def visit_except(self, node, context):
                tables = {}
                project_column = []
                self.process(node.left, context)
                if "tables" in context:
                    tables.update(context["tables"])
                    context["tables"] = {}
                if "project_column" in context:
                    project_column.extend(context["project_column"])
                    context["project_column"] = []

                self.process(node.right, context)
                if "tables" in context:
                    tables.update(context["tables"])
                    context["tables"] = {}
                if "project_column" in context:
                    project_column.extend(context["project_column"])
                    context["project_column"] = []

                context["tables"] = tables
                context["project_column"] = project_column
                self.project_columns = project_column
                return None

            def add_filter_column_with_qualified_name_reference(
                self, qualified_name_reference: QualifiedNameReference, opt
            ):
                if len(qualified_name_reference.name.parts) == 2:
                    table_or_alias_name = qualified_name_reference.name.parts[0]
                    for _table in self.table_list:
                        if (
                            _table["alias"] == table_or_alias_name
                            or _table["table_name"] == table_or_alias_name
                        ):
                            filter_column_list = _table["filter_column_list"]
                            filter_column_list.append(
                                {
                                    "column_name": qualified_name_reference.name.parts[
                                        1
                                    ],
                                    "opt": opt,
                                }
                            )
                else:
                    filter_column_list = self.table_list[-1]["filter_column_list"]
                    filter_column_list.append(
                        {
                            "column_name": qualified_name_reference.name.parts[0],
                            "opt": opt,
                        }
                    )

        visitor = FormatVisitor()
        visitor.process(statement, {})
        return visitor

    @staticmethod
    def parameterized_query(statement):
        """
        Parameterized/normalized statement, used to normalize homogeneous SQL
        1. Parameterized
        2. Turn multiple in into single in
        3. Limit parameterized

        :param statement:
        :return:
        """

        class Visitor(DefaultTraversalVisitor):
            def visit_long_literal(self, node, context):
                node.value = "?"

            def visit_double_literal(self, node, context):
                node.value = "?"

            def visit_interval_literal(self, node, context):
                node.value = "?"

            def visit_timestamp_literal(self, node, context):
                node.value = "?"

            def visit_string_literal(self, node, context):
                node.value = "?"

            def visit_in_predicate(self, node, context):
                value_list = node.value_list
                if isinstance(value_list, InListExpression):
                    node.value_list.values = node.value_list.values[0:1]
                self.process(node.value, context)
                self.process(node.value_list, context)

            def visit_query_specification(self, node, context):
                node.limit = "?"
                self.process(node.select, context)
                if node.from_:
                    if isinstance(node.from_, list):
                        for item in node.from_:
                            self.process(item, context)
                    else:
                        self.process(node.from_, context)
                if node.where:
                    self.process(node.where, context)
                if node.group_by:
                    grouping_elements = []
                    if isinstance(node.group_by, SimpleGroupBy):
                        grouping_elements = node.group_by.columns
                    elif isinstance(node.group_by, GroupingSets):
                        grouping_elements = node.group_by.sets
                    for grouping_element in grouping_elements:
                        self.process(grouping_element, context)
                if node.having:
                    self.process(node.having, context)
                for sort_item in node.order_by:
                    self.process(sort_item, context)
                return None

        visitor = Visitor()
        visitor.process(statement, 0)
        return statement


def node_str_omit_none(node, *args):
    fields = ", ".join([": ".join([a[0], str(a[1])]) for a in args if a[1]])
    return "{class_name}({fields})".format(
        class_name=node.__class__.__name__, fields=fields
    )


def node_str(node, *args):
    fields = ", ".join([": ".join([a[0], a[1] or "None"]) for a in args])
    return "({fields})".format(fields=fields)


FIELD_REFERENCE_PREFIX = "$field_reference$"


def mangle_field_reference(field_name):
    return FIELD_REFERENCE_PREFIX + field_name


def unmangle_field_reference(mangled_name):
    if not mangled_name.startswith(FIELD_REFERENCE_PREFIX):
        raise ValueError("Invalid mangled name: %s" % mangled_name)
    return mangled_name[len(FIELD_REFERENCE_PREFIX) :]
