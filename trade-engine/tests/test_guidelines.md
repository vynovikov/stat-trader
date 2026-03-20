# Test Writing Guidelines

## 1. Test Structure
- Use table-driven tests (parameterized) to check different scenarios
- Each test case should have a unique name starting with a number
- Test name should indicate what is being tested

## 2. Test Case Organization
```python
test_cases = [
    {
        "name": "0. Brief scenario description",
        "input_data": ...,  # Input data
        "expected": ...,    # Expected result
        "params": ...,      # Additional parameters (if needed)
    }
]
```

## 3. Naming Conventions
- Test files: `test_<module_name>.py`
- Test functions: `test_<method_name>_<scenario>`
- For table-driven tests: `test_<method_name>_table_driven`

## 4. Test Function Structure
```python
@pytest.mark.parametrize("case", test_cases, ids=[c["name"] for c in test_cases])
def test_<method>_table_driven(case):
    # ARRANGE - prepare test data
    # ACT - execute the tested action
    # ASSERT - verify results
```

## 5. Assertions
- Each test should verify one specific aspect
- Use clear error messages
- Test edge cases and exceptions

## 6. Documentation
- Each test case should have a clear description in its name
- Complex test cases should have comments
- Document special conditions or assumptions

## 7. Data Organization
- Test data should be minimal but sufficient
- Use fixtures for repetitive data
- Keep tests isolated from each other

## 8. Maintenance
- Tests should be easily extendable
- Avoid code duplication in tests
- Update tests regularly when code changes

## 9. Execution
- Tests should be fast
- Should not depend on external resources
- Should be reproducible

## 10. Coverage
- Aim for complete code coverage
- Test both positive and negative scenarios
- Include exception testing

## Table-Driven Test Example

```python
import pytest

test_cases = [
    {
        "name": "0. Empty input",
        "input": [],
        "expected": [],
    },
    {
        "name": "1. Single element",
        "input": [1],
        "expected": [1],
    },
]

@pytest.mark.parametrize("case", test_cases, ids=[c["name"] for c in test_cases])
def test_example_table_driven(case):
    # ARRANGE
    input_data = case["input"]

    # ACT
    result = function_under_test(input_data)

    # ASSERT
    assert result == case["expected"], f"Case: {case['name']}"
```