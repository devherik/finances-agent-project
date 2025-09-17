from datetime import datetime, date
from typing import Any, Dict, List, Union
from abc import ABC, abstractmethod


class DataFlattener(ABC):
    """Abstract base class for data flattening strategies"""
    
    @abstractmethod
    def can_handle(self, data: Any) -> bool:
        """Check if this flattener can handle the data type"""
        pass
    
    @abstractmethod
    def flatten(self, data: Any, parent_key: str = "") -> Dict[str, Any]:
        """Flatten the data"""
        pass


class NotionDateFlattener(DataFlattener):
    """Handles Notion-style date objects with start/end dates"""
    
    def can_handle(self, data: Any) -> bool:
        return isinstance(data, dict) and ('start' in data or 'end' in data)
    
    def flatten(self, data: Dict[str, Any], parent_key: str = "") -> Dict[str, Any]:
        cleaned_data = {}
        
        start_date = data.get('start')
        end_date = data.get('end')
        
        if start_date:
            key = f"{parent_key}_start" if parent_key else "start"
            cleaned_data[key] = str(start_date)
        
        if end_date:
            key = f"{parent_key}_end" if parent_key else "end"
            cleaned_data[key] = str(end_date)
            
        return cleaned_data


class DictionaryFlattener(DataFlattener):
    """Handles generic dictionary flattening"""
    
    def __init__(self, handler=None):
        self.handler = handler
    
    def can_handle(self, data: Any) -> bool:
        return isinstance(data, dict)
    
    def flatten(self, data: Dict[str, Any], parent_key: str = "") -> Dict[str, Any]:
        cleaned_data = {}
        
        for key, value in data.items():
            new_key = f"{parent_key}_{key}" if parent_key else key
            # Use the handler passed during initialization to avoid infinite recursion
            if self.handler:
                cleaned_data.update(self.handler.flatten(value, new_key))
            
        return cleaned_data


class ListFlattener(DataFlattener):
    """Handles list flattening with indexing"""
    
    def __init__(self, handler=None):
        self.handler = handler
    
    def can_handle(self, data: Any) -> bool:
        return isinstance(data, list)
    
    def flatten(self, data: List[Any], parent_key: str = "") -> Dict[str, Any]:
        cleaned_data = {}
        
        for index, item in enumerate(data):
            new_key = f"{parent_key}_{index}" if parent_key else str(index)
            # Use the handler passed during initialization to avoid infinite recursion
            if self.handler:
                cleaned_data.update(self.handler.flatten(item, new_key))
            
        return cleaned_data


class DateTimeFlattener(DataFlattener):
    """Handles datetime and date objects"""
    
    def can_handle(self, data: Any) -> bool:
        return isinstance(data, (datetime, date))
    
    def flatten(self, data: Union[datetime, date], parent_key: str = "") -> Dict[str, Any]:
        if not parent_key:
            return {}
        return {parent_key: data.isoformat()}


class PrimitiveFlattener(DataFlattener):
    """Handles primitive types (str, int, float, bool, None)"""
    
    def can_handle(self, data: Any) -> bool:
        return isinstance(data, (str, int, float, bool)) or data is None
    
    def flatten(self, data: Any, parent_key: str = "") -> Dict[str, Any]:
        if not parent_key:
            return {}
        return {parent_key: data}


class GenericFlattener(DataFlattener):
    """Fallback for any other data types"""
    
    def can_handle(self, data: Any) -> bool:
        return True  # Always can handle as fallback
    
    def flatten(self, data: Any, parent_key: str = "") -> Dict[str, Any]:
        if not parent_key:
            return {}
        return {parent_key: data}
    
class DataHandler:
    """
    Handles metadata retrieval for any data source using the Strategy pattern.
    
    This follows the Open/Closed Principle: you can add new data type handlers
    without modifying the existing code.
    """
    
    def __init__(self):
        # Order matters - more specific handlers first
        # Pass self to flatteners that need recursive processing
        self.flatteners = [
            NotionDateFlattener(),
            DateTimeFlattener(),
            DictionaryFlattener(handler=self),  # Pass self for recursion
            ListFlattener(handler=self),        # Pass self for recursion
            PrimitiveFlattener(),
            GenericFlattener(),  # Fallback
        ]
    
    def flatten(self, data: Union[Dict, List, Any], parent_key: str = "") -> Dict[str, Any]:
        """
        Flatten any data structure into a flat dictionary.
        
        Args:
            data: The data to flatten
            parent_key: Key prefix for nested structures
            
        Returns:
            A flattened dictionary with all nested structures expanded
        """
        if not data:
            return {}
        
        # Find the first flattener that can handle this data type
        for flattener in self.flatteners:
            if flattener.can_handle(data):
                return flattener.flatten(data, parent_key)
        
        # Should never reach here due to GenericFlattener fallback
        return {}

# Example usage and testing:
if __name__ == "__main__":
    handler = DataHandler()
    
    # Test data with various nested structures
    data = { 
        "name": "John", 
        "age": 30, 
        "joined": {"start": "2023-01-01", "end": "2023-12-31"}, 
        "tags": ["vip", "premium"], 
        "last_login": datetime.now(),
        "nested": {
            "level1": {
                "level2": "deep_value"
            }
        }
    }
    
    flat_data = handler.flatten(data, "")
    print("Flattened data:")
    for key, value in flat_data.items():
        print(f"  {key}: {value}")
    
    try:
        # Assertions to verify correct flattening
        assert "name" in flat_data, "Expected 'name' key in flattened data"
        assert "age" in flat_data, "Expected 'age' key in flattened data"
        assert "joined_start" in flat_data, "Expected 'joined_start' from nested date object"
        assert "joined_end" in flat_data, "Expected 'joined_end' from nested date object"
        assert "tags_0" in flat_data, "Expected 'tags_0' from list flattening"
        assert "tags_1" in flat_data, "Expected 'tags_1' from list flattening"
        assert "last_login" in flat_data, "Expected 'last_login' from datetime conversion"
        assert "nested_level1_level2" in flat_data, "Expected deep nesting to be flattened"
        
        print("\n✅ All assertions passed! Data flattening works correctly.")
    except AssertionError as e:
        print(f"\n❌ Assertion failed: {e}")