import argparse
import ast
import json
import sys
from json import JSONDecodeError

from string_conditions import evaluate_condition, validate_context


def valid_context(arg_context: str) -> dict:
    """Custom argparse type for user provided json vars or Python literal
    :raises argparse.ArgumentTypeError:
    """
    context_dict = None  # type: None | dict
    try:
        context_dict = json.loads(arg_context)
    except JSONDecodeError:
        try:
            context_dict = ast.literal_eval(arg_context)
        except ValueError as e:
            raise argparse.ArgumentTypeError(f"context is neither a valid JSON or a valid Python dict.\nError: {e}")

    try:
        validate_context(context_dict)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e))

    return context_dict


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate a string condition using Python syntax and variables given as argument\n"
                    "Usage:\n"
                    '  "(year > 2020 and type not in (\'std\', \'premium\')) or message.lower().startswith(\'hello\')'
                    ' --context \'{"year":2020, "type":"new", "message": "hello world"}\'',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("condition", type=str,
                        help="A string without leading whitespace")
    parser.add_argument("-c", "--context", required=False, type=valid_context, default=dict(),
                        help="A dictionary, with variable name as a key. Can be either JSON or Python synthax")
    return parser.parse_args()


def process_args(args):
    if not evaluate_condition(args.condition, args.context):
        sys.exit(1)


if __name__ == "__main__":
    process_args(parse_args())
