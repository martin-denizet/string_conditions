[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/martin-denizet/string_conditions/graph/badge.svg?token=8NOUUP037M)](https://codecov.io/gh/martin-denizet/string_conditions)
# string_conditions
Evaluate string Python conditions while keeping control on functions and variables accessible.

## Usage
### Python
```python
from string_conditions import evaluate_condition
evaluate_condition(
    condition="(year not in (2020,2021) and 10 > month > 4) or type.lower() == 'sometype'",
    context={
        'type': "SomeType",
        'year': 2023,
        'month': 6,
    }
)
```
### CLI
```commandline
python -m string_conditions "(year > 2020 and type not in ('std', 'premium')) or message.lower().startswith('hello')"  -c '{"year":2021, "type":"new", "message":"Hello World"}'
```
