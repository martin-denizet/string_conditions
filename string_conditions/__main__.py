import argparse
import ast
import json
import re
import sys
from json import JSONDecodeError

from string_conditions import evaluate_condition

RE_VAR = re.compile(r"^[A-Za-z_]\w*$")


def valid_json(arg_context: str) -> dict:
    """Custom argparse type for user provided json vars or Python literal
    :raises argparse.ArgumentTypeError:
    """
    context_dict = None  # type: None | dict
    try:
        context_dict = json.loads(arg_context)
    except JSONDecodeError:
        try:
            context_dict = ast.literal_eval(arg_context)
        except ValueError:
            raise argparse.ArgumentTypeError("context is neither a valid JSON or a valid Python dict")
    if not isinstance(context_dict, dict):
        raise argparse.ArgumentTypeError("context must be dict")

    for k in context_dict.keys():
        if not isinstance(k, str):
            raise argparse.ArgumentTypeError(f"context dict keys must be strings, found {type(k)} with value '{k}'")
        if not RE_VAR.match(k):
            raise argparse.ArgumentTypeError(f"context dict keys must be valid variable names, found '{k}'")

    return context_dict


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate a string condition using Python syntax and variables given as argument")
    parser.add_argument("condition", required=True, type=str,
                        help="A string without leading whitespace. Example:"
                             "\"(year > 2020 and type not in ('std', 'premium'))"
                             " or message.lower().startswith('hello')\"")
    parser.add_argument("context", required=False,
                        help="")
    return parser.parse_args()


def process_args(args):
    context = json.loads(args.context)

    if not evaluate_condition(args.condition, context):
        sys.exit(1)


if __name__ == "__main__":
    process_args(parse_args())
