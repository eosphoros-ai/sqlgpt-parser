# coding=utf-8
"""

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
"""

from sqlgpt_parser.parser.tree.grouping import GroupingSets, SimpleGroupBy
from sqlgpt_parser.parser.tree.literal import StringLiteral
from sqlgpt_parser.parser.tree.visitor import DefaultTraversalVisitor
from sqlgpt_parser.parser.tree.expression import (
    InListExpression,
    QualifiedNameReference,
    SubqueryExpression,
)


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
                self.recursion_count = 0

            def add_project_column(self, project_column):
                self.projection_column_list.append(project_column)

            def add_table(self, table_name, alias=''):
                self.table_list.append(
                    {'table_name': table_name, 'alias': alias, 'filter_column_list': []}
                )

            def add_filter_column(
                self, filter_col, compare_type, table_or_alias_name=None
            ):
                filter_column_list = None
                if table_or_alias_name is not None:
                    for table in self.table_list:
                        if (
                            table['alias'] == table_or_alias_name
                            or table['table_name'] == table_or_alias_name
                        ):
                            filter_column_list = table['filter_column_list']
                else:
                    filter_column_list = self.table_list[-1]['filter_column_list']
                filter_column_list.append(
                    {"column_name": filter_col, 'opt': compare_type}
                )

            def visit_table(self, node, context):
                if context & ParserUtils.CollectInfo.COLLECT_TABLE:
                    table_name = node.name.parts[-1]
                    self.add_table(table_name)
                return self.visit_query_body(node, context)

            def visit_aliased_relation(self, node, context):
                alias = ""
                if len(node.alias) == 2:
                    alias = node.alias[1]
                else:
                    alias = node.alias[0]
                if (
                    not isinstance(node.relation, SubqueryExpression)
                    and context & ParserUtils.CollectInfo.COLLECT_TABLE
                ):
                    table_name = node.relation.name.parts[-1]
                    self.add_table(table_name, alias)
                else:
                    return self.process(node.relation, context)

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

                def add_filter_column(name):
                    table_name = None
                    if len(name.parts) > 2:
                        table_name = name.parts[-2]
                    self.add_filter_column(name.parts[-1], node.type, table_name)

                if isinstance(right, QualifiedNameReference):
                    if context & ParserUtils.CollectInfo.COLLECT_FILTER_COLUMN:
                        add_filter_column(right.name)
                else:
                    self.process(node.right, context)
                if isinstance(left, QualifiedNameReference):
                    if context & ParserUtils.CollectInfo.COLLECT_FILTER_COLUMN:
                        add_filter_column(left.name)
                else:
                    self.process(node.left, context)

            def visit_like_predicate(self, node, context):
                if isinstance(node.value, QualifiedNameReference):
                    can_query_range = False
                    pattern = node.pattern
                    if isinstance(pattern, StringLiteral):
                        if not pattern.value.startswith('%'):
                            can_query_range = True
                    if (
                        can_query_range
                        and context & ParserUtils.CollectInfo.COLLECT_FILTER_COLUMN
                    ):
                        value, table_name = node.value, None
                        if len(value.name.parts) > 2:
                            table_name = value.name.parts[-2]
                        self.add_filter_column(value.name.parts[-1], 'like', table_name)

                self.process(node.pattern, context)

            def visit_not_expression(self, node, context):
                return self.process(node.value, "not")

            def visit_in_predicate(self, node, context):
                value = node.value

                if not node.is_not:
                    if (
                        isinstance(node.value_list, InListExpression)
                        and context
                        & ParserUtils.CollectInfo.COLLECT_IN_EXPRESSION_COLUMN
                    ):
                        self.in_count_list.append(len(node.value_list.values))
                    if (
                        isinstance(value, QualifiedNameReference)
                        and context & ParserUtils.CollectInfo.COLLECT_FILTER_COLUMN
                    ):
                        table_name = None
                        if len(value.name.parts) > 2:
                            table_name = value.name.parts[-2]
                        self.add_filter_column(value.name.parts[-1], 'in', table_name)

                self.process(node.value, context)
                self.process(node.value_list, context)
                return None

            def visit_select(self, node, context):
                for item in node.select_items:
                    self.process(item, context)

            def visit_qualified_name_reference(self, node, context):
                if context & ParserUtils.CollectInfo.COLLECT_PROJECT_COLUMN:
                    self.add_project_column(node.name.parts[-1])

            def visit_aggregate_func(self, node, context):
                if node.name == "count" and node.arguments[0] == "*":
                    if context & ParserUtils.CollectInfo.COLLECT_PROJECT_COLUMN:
                        self.add_project_column("count(*)")
                else:
                    for arg in node.arguments:
                        self.process(arg, context)
                if context & ParserUtils.CollectInfo.COLLECT_MIN_MAX_EXPRESSION_COLUMN:
                    if node.name == 'max' or node.name == 'min':
                        # min or max only has one argument
                        self.min_max_list.append(node.arguments[0])

            def visit_sort_item(self, node, context):
                sort_key = node.sort_key
                ordering = node.ordering
                if isinstance(sort_key, QualifiedNameReference):
                    name = sort_key.name
                    if len(name.parts) == 2:
                        self.order_list.append(
                            {'ordering': ordering, 'column_name': name.parts[1]}
                        )
                    else:
                        self.order_list.append(
                            {'ordering': ordering, 'column_name': name.parts[0]}
                        )
                return self.process(node.sort_key, context)

            def visit_query_specification(self, node, context):
                self.limit_number = node.limit
                context = (
                    ParserUtils.CollectInfo.COLLECT_PROJECT_COLUMN
                    | ParserUtils.CollectInfo.COLLECT_MIN_MAX_EXPRESSION_COLUMN
                )
                self.process(node.select, context)
                context = ParserUtils.CollectInfo.COLLECT_TABLE
                if node.from_:
                    self.process(node.from_, context)
                context = (
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
                return None

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

            def visit_between_predicate(self, node, context):
                if (
                    isinstance(node.value, QualifiedNameReference)
                    and context & ParserUtils.CollectInfo.COLLECT_FILTER_COLUMN
                ):
                    parts = node.value.name.parts
                    table_name = parts[-2] if len(parts) > 2 else None
                    self.add_filter_column(parts[-1], "between", table_name)
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
        visitor.process(statement, 0)
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
