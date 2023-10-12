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
from sqlgpt_parser.parser.tree.literal import StringLiteral
from sqlgpt_parser.parser.tree.visitor import DefaultTraversalVisitor
from sqlgpt_parser.parser.tree.expression import (
    InListExpression,
    QualifiedNameReference,
    SubqueryExpression,
)
from sqlgpt_parser.parser.tree.join_criteria import JoinOn, JoinUsing
from sqlgpt_parser.parser.tree.relation import AliasedRelation
from sqlgpt_parser.parser.tree.table import Table


class ParserUtils(object):
    class CollectInfo:
        COLLECT_FILTER_COLUMN = 1
        COLLECT_PROJECT_COLUMN = 2
        COLLECT_TABLE = 4
        COLLECT_MIN_MAX_EXPRESSION_COLUMN = 8
        COLLECT_IN_EXPRESSION_COLUMN = 16

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
                self.recursion_count = 0
                self.table_dict = {}
                self.subquery_alias_projection = {}
                self.join_realtions = []

            def add_project_column(self, project_column):
                self.projection_column_list.append(project_column)

            def add_table(self, table_name, alias=''):
                self.table_list.append(
                    {'table_name': table_name, 'alias': alias, 'filter_column_list': []}
                )
                if alias == '':
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
                        if table['alias'].lower() == table_or_alias_name.lower() or (
                            not isinstance(table['table_name'], dict)
                            and table['table_name'].lower()
                            == table_or_alias_name.lower()
                        ):
                            filter_column_list = table['filter_column_list']
                else:
                    filter_column_list = self.table_list[-1]['filter_column_list']
                filter_column_list.append(
                    {"column_name": filter_col, 'opt': compare_type}
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
                else:
                    context["alias"] = alias
                    return self.process(node.relation, context)

            def visit_subquery_expression(self, node, context):
                # copy_context 和 context 换一下
                table_dict = {}
                alias = None
                copy_context = copy.deepcopy(context)
                if copy_context["op"] & ParserUtils.CollectInfo.COLLECT_TABLE:
                    table_dict = context["tables"]
                    copy_context["tables"] = {}
                    if "alias" in context:
                        alias = context["alias"]
                self.process(node.query, copy_context)
                if context["op"] & ParserUtils.CollectInfo.COLLECT_TABLE:
                    context_tables = copy_context["tables"]
                    if alias is not None:
                        if len(context_tables) == 1:
                            # 如果子查询只有使用了一个表，那么就让 alias 和子查询使用的表关联起来
                            for key in context_tables:
                                table_dict[alias.lower()] = context_tables[key]
                                self.add_table(context_tables[key], alias)
                        else:
                            # 让表别名 和 子查询使用的列关联起来
                            table_dict[alias.lower()] = context_tables
                            self.add_table(context_tables, alias)
                            self.subquery_alias_projection[
                                alias.lower()
                            ] = copy_context["project_column"]
                    else:
                        table_dict.update(context_tables)
                    context["tables"] = table_dict

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
                        context["join_relations"].append(
                            [left.name.parts, right.name.parts]
                        )

                def add_filter_column(name):
                    table_name = None
                    if len(name.parts) > 2:
                        table_name = name.parts[-2]
                    self.add_filter_column(name.parts[-1], node.type, table_name)

                if isinstance(right, QualifiedNameReference):
                    if context["op"] & ParserUtils.CollectInfo.COLLECT_FILTER_COLUMN:
                        context["filter_columns"].append(right.name.parts)
                        add_filter_column(right.name)
                else:
                    self.process(node.right, context)
                if isinstance(left, QualifiedNameReference):
                    if context["op"] & ParserUtils.CollectInfo.COLLECT_FILTER_COLUMN:
                        context["filter_columns"].append(left.name.parts)
                        add_filter_column(left.name)
                    if context['op'] & ParserUtils.CollectInfo.COLLECT_PROJECT_COLUMN:
                        context['project_column'].append(left.name.parts)
                else:
                    self.process(node.left, context)

            def visit_like_predicate(self, node, context):
                if isinstance(node.value, QualifiedNameReference):
                    parts = node.value.name.parts
                    table_name = parts[-2] if len(parts) > 2 else None
                    if context["op"] & ParserUtils.CollectInfo.COLLECT_FILTER_COLUMN:
                        self.add_filter_column(
                            node.value.name.parts[-1], 'like', table_name
                        )
                        context["filter_columns"].append(parts)
                    if context["op"] & ParserUtils.CollectInfo.COLLECT_PROJECT_COLUMN:
                        context["project_column"].append(parts)

                if isinstance(node.value, QualifiedNameReference):
                    pattern = node.pattern
                    if isinstance(pattern, StringLiteral):
                        if not pattern.value.startswith('%'):
                            pass
                else:
                    self.process(node.value, context)
                    self.process(node.pattern, context)

            def visit_not_expression(self, node, context):
                return self.process(node.value, context)

            def visit_in_predicate(self, node, context):
                value = node.value
                table_name = None
                if isinstance(value, QualifiedNameReference):
                    if len(value.name.parts) > 2:
                        table_name = value.name.parts[-2]
                    if context["op"] & ParserUtils.CollectInfo.COLLECT_FILTER_COLUMN:
                        self.add_filter_column(value.name.parts[-1], 'in', table_name)
                        context["filter_columns"].append(value.name.parts)
                    elif context["op"] & ParserUtils.CollectInfo.COLLECT_PROJECT_COLUMN:
                        context["project_column"].append(value.name.parts)
                else:
                    self.process(node.value, context)
                if not node.is_not:
                    if (
                        isinstance(node.value_list, InListExpression)
                        and context["op"]
                        & ParserUtils.CollectInfo.COLLECT_IN_EXPRESSION_COLUMN
                    ):
                        self.in_count_list.append(len(node.value_list.values))

                self.process(node.value_list, context)
                return None

            def visit_select(self, node, context):
                for item in node.select_items:
                    self.process(item, context)

            def visit_qualified_name_reference(self, node, context):
                if context["op"] & ParserUtils.CollectInfo.COLLECT_PROJECT_COLUMN:
                    context["project_column"].append(node.name.parts)
                    self.add_project_column(node.name.parts)
                elif context["op"] & ParserUtils.CollectInfo.COLLECT_FILTER_COLUMN:
                    table_name = None
                    if len(node.name.parts) > 1:
                        table_name = node.name.parts[-2]
                    self.add_filter_column(node.name.parts[-1], None, table_name)
                    context["filter_columns"].append(node.name.parts)

            def visit_aggregate_func(self, node, context):
                if node.name.lower() == "count" and node.arguments[0] == "*":
                    if context["op"] & ParserUtils.CollectInfo.COLLECT_PROJECT_COLUMN:
                        context["project_column"].append(["*"])
                        self.add_project_column(["*"])
                    if context["op"] & ParserUtils.CollectInfo.COLLECT_FILTER_COLUMN:
                        context["filter_columns"].append(["*"])
                else:
                    for arg in node.arguments:
                        self.process(arg, context)
                if (
                    context["op"]
                    & ParserUtils.CollectInfo.COLLECT_MIN_MAX_EXPRESSION_COLUMN
                ):
                    if node.name == 'max' or node.name == 'min':
                        # min or max only has one argument
                        self.min_max_list.append(node.arguments[0])

            def visit_sort_item(self, node, context):
                sort_key = node.sort_key
                ordering = node.ordering
                if isinstance(sort_key, QualifiedNameReference):
                    name = sort_key.name
                    self.order_list.append(
                        {'ordering': ordering, 'column_name': name.parts}
                    )
                return self.process(node.sort_key, context)

            def visit_query_specification(self, node, context):
                self.limit_number = node.limit
                context["op"] = (
                    ParserUtils.CollectInfo.COLLECT_PROJECT_COLUMN
                    | ParserUtils.CollectInfo.COLLECT_MIN_MAX_EXPRESSION_COLUMN
                )
                context["project_column"] = []
                context["tables"] = {}
                context["filter_columns"] = []
                context["join_relations"] = []
                self.process(node.select, context)
                project_columns = context["project_column"]
                context["op"] = (
                    ParserUtils.CollectInfo.COLLECT_TABLE
                    | ParserUtils.CollectInfo.COLLECT_FILTER_COLUMN
                )
                if node.from_:
                    if isinstance(node.from_, list):
                        for item in node.from_:
                            self.process(item, context)
                    else:
                        self.process(node.from_, context)
                tables = context["tables"]
                subquery_projection = copy.deepcopy(context["project_column"])
                context["op"] = (
                    ParserUtils.CollectInfo.COLLECT_IN_EXPRESSION_COLUMN
                    | ParserUtils.CollectInfo.COLLECT_FILTER_COLUMN
                )
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
                project_columns.extend(context["filter_columns"])
                temp_project_columns = []
                for index in range(len(project_columns)):
                    for i in range(len(project_columns[index])):
                        if isinstance(project_columns[index][i], list):
                            project_columns[index][i] = [
                                x.lower() for x in project_columns[index][i]
                            ]
                        else:
                            project_columns[index][i] = project_columns[index][
                                i
                            ].lower()
                temp_tables = {}
                for alias, table in tables.items():
                    if isinstance(table, dict):
                        temp_tables[alias.lower()] = table
                    else:
                        temp_tables[alias.lower()] = table.lower()
                tables = temp_tables
                for project_column in project_columns:
                    if len(project_column) > 1:
                        self.convert_from_alias_to_source_name(project_column, tables)
                        temp_project_columns.append(project_column)
                    elif project_column[0] == "*":
                        for table in tables:
                            temp_project_columns.append([tables[table], "*"])
                    else:
                        if len(tables) == 1:
                            table_name = tables[list(tables.keys())[0]]
                            temp_project_columns.append([table_name, project_column[0]])

                # Join 处理
                join_relations = context["join_relations"]
                # for index in range(len(join_relations)):
                #     for i in range(len(join_relations[index])):
                #         for j in range(len(join_relations[index][index])):
                #             join_relations[index][i][j] = join_relations[index][i][j].lower()
                # for join_relation in join_relations:
                #     self.convert_from_alias_to_source_name(join_relation[0], tables)
                #     self.convert_from_alias_to_source_name(join_relation[1], tables)
                self.columns.extend(temp_project_columns)
                self.join_realtions.extend(join_relations)
                context["tables"] = tables
                context["filter_columns"] = []
                context["project_column"] = subquery_projection
                return None

            def convert_from_alias_to_source_name(self, project_column, tables):
                column_name = project_column[-1]
                if isinstance(project_column[-2], list):
                    table_name_dict = {}
                    for alias_table_name in project_column[-2]:
                        used_table_name = self.extract_used_table_name(
                            alias_table_name, tables, column_name
                        )
                        table_name_dict[alias_table_name] = used_table_name
                    project_column[-2] = table_name_dict
                else:
                    alias_table_name = project_column[-2]
                    used_table_name = self.extract_used_table_name(
                        alias_table_name, tables, column_name
                    )
                    project_column[-2] = used_table_name

            def extract_used_table_name(self, alias_table_name, tables, column_name):
                if alias_table_name in tables:
                    real_alias_table, isChange = self.subquery_alias(
                        alias_table_name, column_name
                    )
                    while isinstance(real_alias_table, dict):
                        real_alias_table, _ = self.subquery_alias(
                            alias_table_name, column_name
                        )
                    if isChange:
                        used_table_name = tables[alias_table_name][real_alias_table]
                    else:
                        used_table_name = tables[real_alias_table]
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
                copy_context = {}
                self.process(node.query_body, copy_context)
                copy_context["filter_columns"] = []
                for sort_item in node.order_by:
                    self.process(sort_item, copy_context)
                tables = copy_context["tables"]
                project_columns = copy_context["filter_columns"]
                temp_project_columns = []
                for index in range(len(project_columns)):
                    for i in range(len(project_columns[index])):
                        project_columns[index][i] = project_columns[index][i].lower()
                temp_tables = {}
                for alias, table in tables.items():
                    if isinstance(table, dict):
                        temp_tables[alias.lower()] = table
                    else:
                        temp_tables[alias.lower()] = table.lower()
                tables = temp_tables
                for project_column in project_columns:
                    if len(project_column) > 1:
                        alias_table_name = project_column[-2]
                        real_alias_table, isChange = self.subquery_alias(
                            project_column[-2], project_column[-1]
                        )
                        if isChange:
                            used_table_name = tables[alias_table_name][real_alias_table]
                        else:
                            used_table_name = tables[real_alias_table]
                        project_column[-2] = used_table_name
                        temp_project_columns.append(project_column)
                    elif project_column[0] == "*":
                        for table in tables:
                            temp_project_columns.append([tables[table], "*"])
                    else:
                        if len(tables) == 1:
                            table_name = tables[list(tables.keys())[0]]
                            temp_project_columns.append([table_name, project_column[0]])
                self.columns.extend(temp_project_columns)
                if "tables" in context:
                    context["tables"].update(copy_context["tables"])
                else:
                    context["tables"] = copy_context["tables"]
                return None

            def visit_join(self, node, context):
                self.process(node.left, context)
                left_alias = self.join_table_alias(context, node.left)
                self.process(node.right, context)
                right_alias = self.join_table_alias(context, node.right)
                context["collect_join"] = True
                if isinstance(node.criteria, JoinOn):
                    self.process(node.criteria.expression, context)
                elif isinstance(node.criteria, JoinUsing):
                    join_relations = context["join_relations"]
                    filter_columns = context['filter_columns']
                    for column in node.criteria.columns:
                        left_key = [left_alias, column]
                        right_key = [right_alias, column]
                        join_relations.append([left_key, right_key])
                        filter_columns.append(left_key)
                        filter_columns.append(right_key)
                        self.process(column)
                context["join_table"] = [left_alias, right_alias]
                del context["collect_join"]
                return None

            def join_table_alias(self, context, node):
                if isinstance(node, Table):
                    left_alias = node.name.parts[0]
                elif not isinstance(node, AliasedRelation):
                    left_alias = context["join_table"]
                elif len(node.alias) == 2:
                    left_alias = node.alias[1]
                else:
                    left_alias = node.alias[0]
                return left_alias

            def subquery_alias(self, alias_table_name, column_name):
                used_table = alias_table_name
                if alias_table_name in self.subquery_alias_projection:
                    for sub_project_column in self.subquery_alias_projection[
                        alias_table_name
                    ]:
                        if sub_project_column[-1].lower() == column_name.lower():
                            if len(sub_project_column) > 1:
                                used_table = sub_project_column[-2].lower()
                                return used_table, True
                return used_table, False

            def visit_between_predicate(self, node, context):
                if isinstance(node.value, QualifiedNameReference):
                    parts = node.value.name.parts
                    table_name = parts[-2] if len(parts) > 2 else None
                    if context["op"] & ParserUtils.CollectInfo.COLLECT_FILTER_COLUMN:
                        self.add_filter_column(parts[-1], "between", table_name)
                        context["filter_columns"].append(parts)
                    if context["op"] & ParserUtils.CollectInfo.COLLECT_PROJECT_COLUMN:
                        context["project_column"].append(parts)
                else:
                    self.process(node.value, context)
                self.process(node.max, context)
                self.process(node.min, context)
                return None

            def visit_union(self, node, context):
                tables = {}
                if "tables" in context:
                    tables.update(context["tables"])
                    context["tables"] = {}
                for relation in node.relations:
                    self.process(relation, context)
                    if "tables" in context:
                        tables.update(context["tables"])
                        context["tables"] = {}
                context["tables"] = tables
                return None

            def visit_intersect(self, node, context):
                tables = {}
                for relation in node.relations:
                    if "tables" in context:
                        tables.update(context["tables"])
                        context["tables"] = {}
                    self.process(relation, context)
                context["tables"] = tables
                return None

            def visit_except(self, node, context):
                tables = {}
                if "tables" in context:
                    tables.update(context["tables"])
                    context["tables"] = {}
                self.process(node.left, context)
                if "tables" in context:
                    tables.update(context["tables"])
                    context["tables"] = {}
                self.process(node.right, context)
                if "tables" in context:
                    tables.update(context["tables"])
                context["tables"] = tables
                return None

            def add_filter_column_with_qualified_name_reference(
                self, qualified_name_reference: QualifiedNameReference, opt
            ):
                if len(qualified_name_reference.name.parts) == 2:
                    table_or_alias_name = qualified_name_reference.name.parts[0]
                    for _table in self.table_list:
                        if (
                            _table['alias'] == table_or_alias_name
                            or _table['table_name'] == table_or_alias_name
                        ):
                            filter_column_list = _table['filter_column_list']
                            filter_column_list.append(
                                {
                                    'column_name': qualified_name_reference.name.parts[
                                        1
                                    ],
                                    'opt': opt,
                                }
                            )
                else:
                    filter_column_list = self.table_list[-1]['filter_column_list']
                    filter_column_list.append(
                        {
                            'column_name': qualified_name_reference.name.parts[0],
                            'opt': opt,
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
                node.value = '?'

            def visit_double_literal(self, node, context):
                node.value = '?'

            def visit_interval_literal(self, node, context):
                node.value = '?'

            def visit_timestamp_literal(self, node, context):
                node.value = '?'

            def visit_string_literal(self, node, context):
                node.value = '?'

            def visit_in_predicate(self, node, context):
                value_list = node.value_list
                if isinstance(value_list, InListExpression):
                    node.value_list.values = node.value_list.values[0:1]
                self.process(node.value, context)
                self.process(node.value_list, context)

            def visit_query_specification(self, node, context):
                node.limit = '?'
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
