import unittest

from string_conditions import evaluate_condition
from string_conditions.errors import BadSyntaxError, UnsupportedSyntaxError, UnknownVariableError


class TestStringMethods(unittest.TestCase):

    @property
    def context(self):
        return {
            'type': "SomeType",
            "msg": "hello World",
            'year': 2023,
            'month': 12,
            'strtuple': ("foo", "bar"),
            'mylist': [1, '2', 3.0]
        }

    def assertStringCondition(self, condition: str, value: bool):
        self.assertEqual(value,
                         evaluate_condition(
                             condition,
                             self.context
                         ))

    def assertStringConditionTrue(self, condition: str):
        self.assertStringCondition(condition, True)

    def assertStringConditionFalse(self, condition: str):
        self.assertStringCondition(condition, False)

    def test_sequences(self):
        # Tuple
        self.assertTrue(evaluate_condition(
            'type in ("SomeType","ValueNotInType")',
            self.context
        ))
        # List
        self.assertTrue(evaluate_condition(
            'type in ["SomeType","ValueNotInType"]',
            self.context
        ))

    def test_in(self):
        self.assertTrue(evaluate_condition(
            'type in ("SomeType","ValueNotInType")',
            self.context
        ))
        self.assertFalse(evaluate_condition(
            'type not in ("SomeType","ValueNotInType")',
            self.context
        ))

        self.assertFalse(evaluate_condition(
            'type in (1, "ValueNotInType")',
            self.context
        ))
        self.assertTrue(evaluate_condition(
            'type not in (1,"ValueNotInType")',
            self.context
        ))

    def test_in_variable(self):
        self.assertTrue(evaluate_condition(
            '"foo" in strtuple',
            self.context
        ))
        self.assertFalse(evaluate_condition(
            '"foo" not in strtuple',
            self.context
        ))

        self.assertFalse(evaluate_condition(
            '"Not Found" in strtuple',
            self.context
        ))
        self.assertTrue(evaluate_condition(
            '"Not Found" not in strtuple',
            self.context
        ))

    def test_compare(self):
        self.assertStringConditionTrue("year == 2023")
        self.assertStringConditionFalse("year == 2024")
        self.assertStringConditionTrue("year != 2024")
        # str int
        self.assertStringConditionFalse("year == '2023'")
        self.assertStringConditionTrue("year != '2023'")

        # Gt/Lt
        self.assertStringConditionTrue("year >= 2023")
        self.assertStringConditionFalse("year >= 2024")

        self.assertStringConditionTrue("year <= 2023")
        self.assertStringConditionFalse("year < 2023")

    def test_simple_logical_conditions(self):
        # Or
        self.assertStringConditionTrue("year == 2023 or month == 99")
        self.assertStringConditionFalse("year == 9999 or month == 99")

        self.assertStringConditionTrue("year == 9999 or month == 99 or type == 'SomeType'")
        self.assertStringConditionFalse("year == 9999 or month == 99 or type == '99'")

        # And
        self.assertStringConditionTrue("year == 2023 or month == 12 or type == 'SomeType'")
        self.assertStringConditionFalse("year == 9999 and month == 99 and type == 'SomeType'")

    def test_literal(self):
        self.assertStringConditionTrue("True")
        self.assertStringConditionFalse("False")

    def test_not(self):
        self.assertStringConditionTrue("not False")
        self.assertStringConditionFalse("not True")

    def test_complex_conditions(self):
        self.assertStringConditionTrue("(year == 2023 and month == 12) or type == '99'")
        self.assertStringConditionFalse("(year == 2023 and month == 99) or type == '99'")
        self.assertStringConditionTrue("(year not in (1,2,3,'foo') and month == 10) or type == 'SomeType'")
        self.assertStringConditionTrue("(year not in (1,2,3,'foo') and month > 10) or type == '99'")
        self.assertStringConditionFalse("(year in (1,2,3,'foo') and month > 10) or type == '99'")

    def test_unsupported_operator(self):
        with self.assertRaises(UnsupportedSyntaxError):
            self.assertStringConditionTrue("month * 2 == 24")
        with self.assertRaises(UnsupportedSyntaxError):
            self.assertStringConditionTrue("month / 2 == 6")
        with self.assertRaises(UnsupportedSyntaxError):
            self.assertStringConditionTrue("month +2 == 14")
        with self.assertRaises(UnsupportedSyntaxError):
            self.assertStringConditionTrue("month -2 == 10")
        with self.assertRaises(UnsupportedSyntaxError):
            self.assertStringConditionTrue("month % 2 == 0")

    def test_unsupported_syntax(self):
        with self.assertRaises(UnsupportedSyntaxError):
            self.assertStringConditionTrue("month is 12")

    def test_bad_syntax(self):
        with self.assertRaises(BadSyntaxError):
            evaluate_condition(
                " True ",
                self.context
            )
        with self.assertRaises(BadSyntaxError):
            evaluate_condition(
                "month =~ 12",
                self.context
            )
        with self.assertRaises(BadSyntaxError):
            evaluate_condition(
                "month === '12'",
                self.context
            )

    def test_unknown_var(self):
        with self.assertRaises(UnknownVariableError):
            evaluate_condition(
                "foo == 12",
                self.context
            )

    def test_type_functions(self):
        self.assertStringConditionTrue(
            "type.lower() == 'sometype'"
        )
        self.assertStringConditionFalse(
            "type.lower() == 'SomeType'"
        )
        self.assertStringConditionTrue(
            "type.lower().upper() == 'SOMETYPE'"
        )

        self.assertStringConditionTrue(
            "msg.lower().startswith('hello')"
        )
        self.assertStringConditionFalse(
            "msg.lower().startswith('world')"
        )

    def test_functions(self):
        self.assertStringConditionTrue(
            "re.match(r'\\w+', type)"
        )
        self.assertStringConditionFalse(
            "re.match(r'\\d+', type)"
        )

        self.assertStringConditionTrue(
            "str(year) == '2023'"
        )
        self.assertStringConditionFalse(
            "year == '2023'"
        )

    def test_functions_combined(self):
        self.assertStringConditionTrue(
            "str(year).lower() == '2023'"
        )

    def test_multi_compares(self):
        self.assertStringConditionTrue(
            "2023 == year == 2023"
        )
        self.assertStringConditionFalse(
            "2023 == year != 2023"
        )
        self.assertStringConditionFalse(
            "2023 != year == 2023"
        )
        self.assertStringConditionFalse(
            "2023 == year == 2024"
        )

        self.assertStringConditionTrue(
            "2022 < year < 2024"
        )
        self.assertStringConditionFalse(
            "9999 < year < 99999"
        )
        self.assertStringConditionTrue(
            "10 < 100 < 1000 < 10000"
        )
        self.assertStringConditionFalse(
            "10 < 100 < 1000 < 1000"
        )

        self.assertStringConditionTrue(
            "10 < 100 < 1000 < 10000 > 10"
        )


if __name__ == '__main__':
    unittest.main()
