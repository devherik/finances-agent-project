from datetime import datetime
from uuid import UUID
from typing import Optional

from agno.tools import Toolkit

from domain.entities.smartpos_entities import SmartPosNfStatus, SaleBase, SaleItemBase, ProductBase

from infrastructure.adapters.smartpos_adapter import SmartPosAdapter


class SmartPosTools(Toolkit):
    def __init__(self, user_id: UUID):
        super().__init__(name="smartpos_tools")
        self.user_id: UUID = user_id
        self.smartpos_adapter: SmartPosAdapter = SmartPosAdapter()
        self.register(self.check_health)
        self.register(self.get_sales)
        self.register(self.get_sale_items)
    
    async def check_health(self) -> bool:
        return await self.smartpos_adapter.health_check()

    async def get_sales(
        self,
        start: datetime,
        end: datetime,
        status: SmartPosNfStatus = SmartPosNfStatus.PROCESSING,
    ) -> list[SaleBase]:
        return await self.smartpos_adapter.get_sales(start, end, status)

    async def get_sale_items(self, sale_id: str) -> list[SaleItemBase]:
        return await self.smartpos_adapter.get_sale_items(sale_id)
    
    async def get_products(
        self,
        page: int = 1,
        size: int = 100,
        name: Optional[str] = None,
    ) -> list[ProductBase]:
        return await self.smartpos_adapter.get_products(page, size, name)
    
    async def get_product_details(self, product_id: int) -> ProductBase:
        return await self.smartpos_adapter.get_product_details(product_id)
