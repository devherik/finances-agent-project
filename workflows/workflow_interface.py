from abc import ABC, abstractmethod


class IWorkflow(ABC):
    @abstractmethod
    async def arun(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def run(self, *args, **kwargs):
        pass
    