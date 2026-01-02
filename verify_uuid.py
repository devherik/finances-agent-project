from uuid import UUID
from typing import Any


class MockFinanceTools:
    def _parse_uuid(self, value: Any) -> UUID:
        if isinstance(value, UUID):
            return value
        if isinstance(value, str):
            try:
                return UUID(value)
            except ValueError:
                pass
        if isinstance(value, dict):
            for key in ["id", "account_id", "uuid", "value"]:
                if key in value:
                    return self._parse_uuid(value[key])
        raise ValueError(f"Invalid UUID format: {value}")


def test_parse_uuid():
    tools = MockFinanceTools()
    test_uuid_str = "550e8400-e29b-41d4-a716-446655440000"
    test_uuid = UUID(test_uuid_str)

    # Test cases
    cases = [
        ("Raw UUID", test_uuid, test_uuid),
        ("Raw String", test_uuid_str, test_uuid),
        ("Dict with 'id'", {"id": test_uuid_str}, test_uuid),
        ("Dict with 'account_id'", {"account_id": test_uuid_str}, test_uuid),
        ("Dict with 'uuid'", {"uuid": test_uuid_str}, test_uuid),
        (
            "Nested Dict",
            {"data": {"id": test_uuid_str}},
            None,
        ),  # Should fail unless we search recursively (which we don't yet, and maybe shouldn't)
        ("Dict with 'id' as UUID object", {"id": test_uuid}, test_uuid),
    ]

    for name, input_val, expected in cases:
        try:
            result = tools._parse_uuid(input_val)
            assert result == expected
            print(f"PASSED: {name}")
        except Exception as e:
            if expected is None:
                print(f"PASSED: {name} (Expected Failure)")
            else:
                print(f"FAILED: {name} - {str(e)}")


if __name__ == "__main__":
    test_parse_uuid()
