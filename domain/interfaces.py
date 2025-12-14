from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict
from dataclasses import dataclass
from enum import Enum

# --- Data Class Definitions ---
class DataFormat(Enum):
    """Supported data formats"""
    JSON = "json"
    PDF = "pdf"
    CSV = "csv"
    TXT = "txt"
    XML = "xml"
    ROWS = "rows"  # List of dictionaries
    XLSX = "xlsx"


@dataclass
class DataSource:
    """Represents a data source with metadata"""
    path: Optional[str] = None
    format: Optional[DataFormat] = None
    data: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ProcessedData:
    """Represents processed data with rich metadata"""
    content: str
    metadata: Dict[str, Any]
    source_info: Dict[str, Any]
    chunk_id: str
    document_id: str


@dataclass
class AgentStep:
    """Represents a single step in an agent's reasoning process"""
    action: str
    action_input: Any
    observation: Any
    log: str


# --- Interface Definitions ---

class IWorkflow(ABC):
    def __init__(self, session_id: str):
        self.steps: List[Any] = []
        self.session_id = session_id

    @abstractmethod
    def run(self, *args, **kwargs) -> bool:
        pass
    
    @abstractmethod
    async def arun(self, *args, **kwargs) -> bool:
        pass


class IDataProcessor(ABC):
    """
    Abstract base class for data processors.
    
    Each processor handles a specific data format (JSON, PDF, etc.)
    following the Single Responsibility Principle.
    """
    
    @abstractmethod
    def can_process(self, source: DataSource) -> bool:
        """Check if this processor can handle the data source"""
        pass
    
    @abstractmethod
    async def process(self, source: DataSource) -> List[ProcessedData]:
        """Process the data source and return processed data"""
        pass


class IDataTransformer(ABC):
    """
    Abstract base class for data transformers.
    
    Transformers modify or enrich the processed data.
    """
    
    @abstractmethod
    async def transform(self, data: List[ProcessedData]) -> List[ProcessedData]:
        """Transform the processed data"""
        pass


class IDataOutput(ABC):
    """
    Abstract base class for data outputs.
    
    Outputs handle where the processed data goes (vector DB, file, etc.)
    """
    
    @abstractmethod
    async def output(self, data: List[ProcessedData]) -> bool:
        """Output the processed data and return success status"""
        pass


class ISenderMessage(ABC):
    """
    Abstract base class for sending messages.
    
    Implementations can send messages via email, SMS, etc.
    """
    
    @abstractmethod
    async def send(self, recipient: str, subject: str, body: str) -> bool:
        """Send a message and return success status"""
        pass