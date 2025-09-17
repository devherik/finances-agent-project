import json


def safe_json_dumps_helper(data) -> str:
    """
    Safely convert data to JSON string, handling various data types.

    :param data: The data to convert.
    :return: A JSON string representation of the data.
    """
    try:
        if data is None:
            return "{}"
        elif isinstance(data, str):
            # If it's already a string, try to parse it as JSON to validate
            try:
                json.loads(data)
                return data  # Already valid JSON string
            except json.JSONDecodeError:
                # Not valid JSON, wrap it in a simple object
                return json.dumps({"content": data})
        elif isinstance(data, dict):
            return json.dumps(data, ensure_ascii=False, default=str)
        else:
            # For other types, convert to string and wrap in object
            return json.dumps({"value": str(data)})
    except Exception as e:
        print(f"Error converting metadata to JSON: {e}")
        return "{}"
