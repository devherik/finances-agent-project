from datetime import datetime
import httpx
from pydantic.main import BaseModel
from decimal import Decimal
from typing import Optional, Any
from uuid import UUID
from enum import Enum

from agno.tools import Toolkit

from core.settings import settings
from core.deps import get_httpx_client

from domain.entities.smartpos_entities import SmartPosNfStatus, SaleBase, SaleItemBase


class SmartPosException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class SmartPosService:
    def __init__(self):
        if not settings.smartpos_api_url:
            raise SmartPosException("SmartPOS API URL not found in settings.")
        self.base_url = settings.smartpos_api_url
        self.headers = self._set_api_headers()

    def _set_api_headers(self) -> dict:
        key = settings.smartpos_api_key
        secret = settings.smartpos_api_secret
        if not key or not secret:
            raise SmartPosException("SmartPOS API key or secret not found in settings.")
        return {
            "Accept": "application/json",
            "X-Api-Key": key,
            "X-Api-Secret": secret,
        }

    def _handle_api_error(self, response: dict) -> None:
        if "error" in response:
            raise SmartPosException(response["error"]["message"])

    async def get_sales(
        self,
        start: datetime,
        end: datetime,
        status: SmartPosNfStatus = SmartPosNfStatus.PROCESSING,
        is_retry: bool = False,
    ) -> list[SaleBase]:
        try:
            async with get_httpx_client() as client:
                response = await client.get(
                    f"{self.base_url}/sales",
                    params={
                        "start": start.isoformat(),
                        "end": end.isoformat(),
                        "status_nf": status.value,
                    },
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if not is_retry:
                await self.get_sales(start, end, is_retry=True)
            else:
                raise SmartPosException(f"Error fetching sales: {str(e)}")
        except Exception as e:
            raise SmartPosException(f"Error fetching sales: {str(e)}")

    async def get_sale_items(
        self,
        sale_id: str,
        is_retry: bool = False,
    ) -> list[SaleItemBase]:
        try:
            async with get_httpx_client() as client:
                response = await client.get(
                    f"{self.base_url}/sales/{sale_id}/items",
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if not is_retry:
                await self.get_sale_items(sale_id, is_retry=True)
            else:
                raise SmartPosException(f"Error fetching sale items: {str(e)}")
        except Exception as e:
            raise SmartPosException(f"Error fetching sale items: {str(e)}")


class SmartPosTools(Toolkit):
    def __init__(self, user_id: UUID):
        super().__init__(name="smartpos_tools")
        self.user_id = user_id
        self.smartpos_service = SmartPosService()
        self.register(self.get_sales)
        self.register(self.get_sale_items)

    def get_sales(
        self,
        start: datetime,
        end: datetime,
        status: SmartPosNfStatus = SmartPosNfStatus.PROCESSING,
    ) -> list[SaleBase]:
        return self.smartpos_service.get_sales(start, end, status)

    def get_sale_items(self, sale_id: str) -> list[SaleItemBase]:
        return self.smartpos_service.get_sale_items(sale_id)
