import ast

from string_conditions.errors import BadSyntaxError
from string_conditions.visitor import BooleanEvaluationVisitor


def evaluate_condition(condition, context=None, visitor_cls=BooleanEvaluationVisitor) -> bool:
    """
    Define a custom visitor to traverse the AST and evaluate the condition
    :param condition:
    :param context:
    :return:
    """

    if not issubclass(visitor_cls, BooleanEvaluationVisitor):
        raise ValueError("Evaluation class doesn't inherit from 'BooleanEvaluationVisitor'")



    # Parse the condition string into an AST (Abstract Syntax Tree)
    try:
        parsed_condition = ast.parse(condition, mode='eval')
    except SyntaxError as e:
        raise BadSyntaxError(f"Invalid condition string:\n"
                             f"{condition}\n"
                             f"context:\n"
                             f"{context}\n"
                             f"Exception:\n"
                             f"{e}")

    # Create an instance of the custom visitor and visit the parsed AST
    evaluator = visitor_cls(context)
    # The final result should be stored in the last node visited (the root of the AST)

    return bool(evaluator.visit(parsed_condition))
