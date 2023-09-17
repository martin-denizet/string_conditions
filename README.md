# string_conditions
Evaluate string Python conditions while keeping control on functions and variables accessible.

## Usage
### Python
```python
from string_conditions import evaluate_condition
evaluate_condition(
    condition="(year not in (2020,2021) and 4 > month > 10) or type.lower() == 'sometype'",
    context={
        'type': "SomeType",
        'year': 2023,
        'month': 6,
    }
)
```
### CLI
