import ast
import re
from typing import Dict, Any, Type

from string_conditions.errors import BadSyntaxError
from string_conditions.visitor import BooleanEvaluationVisitor

__version__ = '0.0.1'

RE_VAR = re.compile(r"^[A-Za-z_]\w*$")


def evaluate_condition(
        condition: str,
        context: Dict[str, Any] = None,
        visitor_cls: Type[BooleanEvaluationVisitor] = BooleanEvaluationVisitor) -> bool:
    """
    Uses the AST module to evaluate a Python boolean expression provided as a string
    Example of usage:
    .. code-block:: python
       res = evaluate_condition(
            condition = "(year not in (2020,2021) and 4 > month > 10) or type.lower() == 'sometype'",
            context = {
                'type': "SomeType",
                'year': 2023,
                'month': 6,
            }
       )
    Only a limited number of python functions are supported, giving control on with operators/functions
    are accessible. It's also possible to modify behavior by creating a custom visitor class.
    :param condition: String condition using Python language
    :param context: Dictionary of variables made available for the evaluation of the condition
    :param visitor_cls: Visitor class that will evaluate different elements of the condition.
        Expected to be a subclass of :class:`~string_conditions.visitor.BooleanEvaluationVisitor`
    :return: True or False
    :raises InvalidContextError: Context dict is not as expected
    :raises UnsupportedSyntaxError: Expression in condition is calling an unsupported node
    :raises UnknownVariableError: Expression refers to a variable not present in the context
    :raises BadSyntaxError: Using an invalid Python synthax
    """

    if not issubclass(visitor_cls, BooleanEvaluationVisitor):
        raise ValueError("Evaluation class doesn't inherit from 'BooleanEvaluationVisitor'")

    validate_context(context)

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


def validate_context(context: Dict):
    if not isinstance(context, dict):
        raise ValueError("context must be dict")

    for k in context.keys():
        if not isinstance(k, str):
            raise ValueError(f"context dict keys must be strings, found {type(k)} with value '{k}'")
        if not RE_VAR.match(k):
            raise ValueError(f"context dict keys must be valid variable names, found '{k}'")
