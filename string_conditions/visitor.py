import ast
import operator
import re
from _ast import BoolOp, Expr, Expression, Call, Tuple, BinOp, UnaryOp, Name, Attribute
from typing import Any, Dict

from string_conditions.errors import UnsupportedSyntaxError, UnknownVariableError, InvalidContextError


def operator_not_in(value, not_in_iterable):
    return value not in not_in_iterable


def operator_in(value, in_iterable):
    return value in in_iterable


class BooleanEvaluationVisitor(ast.NodeVisitor):
    # Define a dictionary to map operators to their corresponding functions
    OPERATORS = {
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.And: operator.and_,
        ast.Or: operator.or_,
        ast.Not: operator.not_,
        ast.NotIn: operator_not_in,
        ast.In: operator_in
    }

    TYPE_FUNCTIONS = {
        str: ('lower', 'upper', 'startswith', 'endswith'),

    }
    FUNCTIONS = {
        re: ('match',),
        str: None,
        len: None
    }

    def __init__(self, context: Dict[str, Any]):
        super().__init__()

        if context is None:
            context = dict()
        self.validate_context(context)
        self.context = context

    def validate_context(self, context):
        """
        Raise exception when context contains reserved keywords
        :param context:
        :return:
        """

        for reserved_keyword in [k.__name__ for k in self.FUNCTIONS.keys()]:
            if reserved_keyword in context.keys():
                raise InvalidContextError(
                    f"Keyword '{reserved_keyword}' is a reserved keyword and is forbidden in context")

    def generic_visit(self, node):
        """
        Catch-all unsupported
        """
        raise UnsupportedSyntaxError(f"{node} is not supported")

    def get_operator(self, operator_class):
        if operator_class not in self.OPERATORS:
            raise UnsupportedSyntaxError(f"Operator '{operator_class}' is not supported")
        return self.OPERATORS[operator_class]

    def visit_Expr(self, node: Expr) -> Any:
        return self.visit(node.value)

    def visit_Expression(self, node: Expression) -> Any:
        return self.visit(node.body)

    def visit_UnaryOp(self, node: UnaryOp) -> Any:
        return self.get_operator(node.op.__class__)(self.visit(node.operand))

    def visit_Assign(self, node):
        raise UnsupportedSyntaxError("Assignment is not supported")

    def visit_BinOp(self, node: BinOp):
        raise UnsupportedSyntaxError(f"Operation '{node.op}' not supported")

    def visit_BoolOp(self, node: BoolOp):
        # Visit all the operands
        values = []
        for v in node.values:
            values.append(self.visit(v))

        # Get the operator function based on the node's operator type
        op_func = self.get_operator(node.op.__class__)

        # Evaluate the operator function with all the values
        result = op_func(values.pop(), values.pop())
        while values:
            result = op_func(result, values.pop())

        return result

    def visit_Compare(self, node):
        results = []
        value = self.visit(node.left)
        for i, comparator in enumerate(node.comparators):
            op = node.ops[i]
            results.append(self.get_operator(op.__class__)(value, self.visit(comparator)))
            value = self.visit(comparator)
        return all(results)

    def visit_Constant(self, node):
        return node.value

    def visit_Name(self, node: Name):
        # If a Name node is encountered, retrieve its value from the context
        # Priority to functions
        for k, v in self.FUNCTIONS.items():
            if node.id == k.__name__:
                return k
        # Check if variable is available in context
        if node.id in self.context:
            return self.context[node.id]

        raise UnknownVariableError(f"Variable '{node.id}' doesn't exist in context")

    def visit_Call(self, node: Call):
        # Function called on variable
        func_name = self.visit(node.func)

        allowed_type_functions = self.TYPE_FUNCTIONS.get(type(func_name), [])
        if func_name in allowed_type_functions:
            return getattr(func_name, func_name)(*[self.visit(a) for a in node.args])

        return func_name(*[self.visit(a) for a in node.args])

    def visit_Attribute(self, node: Attribute) -> Any:
        base_object = self.visit(node.value)
        attr = node.attr
        if base_object in self.FUNCTIONS:
            allowed_attrs = self.FUNCTIONS.get(base_object, [])
            if attr in allowed_attrs:
                return getattr(base_object, attr)

        if type(base_object) in self.TYPE_FUNCTIONS:
            allowed_attrs = self.TYPE_FUNCTIONS.get(type(base_object), [])
            if attr in allowed_attrs:
                return getattr(base_object, attr)
        raise UnsupportedSyntaxError(f"Function not supported: {node}")

    def visit_Tuple(self, node: Tuple) -> Any:
        return tuple(self.visit(v) for v in node.elts)

    def visit_List(self, node) -> list:
        return [self.visit(v) for v in node.elts]

    def visit_Set(self, node) -> set:
        return set(self.visit(v) for v in node.elts)
