"""
SMARTPOS adapter module.

This module contains the SmartPOSAdapter class, which is responsible for
interacting with the SmartPOS API to retrieve sales items, handle stock management, and process transactions.
"""

# Standard Library
import httpx
from datetime import datetime

# Third-Party Libraries

# Local Modules
from core.settings import settings
from core.deps import get_httpx_client

from domain.entities.smartpos_entities import (
    SmartPosNfStatus,
    SaleBase,
    SaleItemBase,
    SmartPosStock,
)

# Step Guides
# 1. Import necessary modules and classes.
# 2. Define the SmartPOSAdapter class.
# 3. Implement methods to interact with the SmartPOS API.
# 4. Create a dependency injection function to provide the SmartPOSAdapter instance.

from typing import Optional, Any


class SmartPosException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class SmartPosAdapter:
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
    
    async def health_check(self) -> bool:
        try:
            client = await get_httpx_client()
            response = await client.get(f"{self.base_url}/sales/1", headers=self.headers)
            response.raise_for_status()
            return True
        except Exception:
            return False

    #   - get -> v1/sales/ -> list of sales -> params{start: datetime, end: datetime, status-nf: enum[PROCESSING, SUCCESS, ERROR]}
    async def get_sales(
        self,
        start: datetime,
        end: datetime,
        status: SmartPosNfStatus = SmartPosNfStatus.PROCESSING,
        is_retry: bool = False,
    ) -> list[SaleBase]:
        try:
            client = await get_httpx_client()
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

    #   - get -> v1/sales/{sale_id}/items/ -> list of sale items
    async def get_sale_items(
        self,
        sale_id: str,
        is_retry: bool = False,
    ) -> list[SaleItemBase]:
        try:
            client = await get_httpx_client()
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

    #   - get -> v1/products/ -> list of products -> params{page:int, size:int, nome?:str}
    async def get_products(
        self,
        page: int = 1,
        size: int = 50,
        name: Optional[str] = None,
        is_retry: bool = False,
    ) -> list[Any]:
        try:
            client = await get_httpx_client()
            params = {"page": page, "size": size}
            if name:
                params["nome"] = name
            response = await client.get(
                f"{self.base_url}/products",
                params=params,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if not is_retry:
                await self.get_products(page, size, name, is_retry=True)
            else:
                raise SmartPosException(f"Error fetching products: {str(e)}")
        except Exception as e:
            raise SmartPosException(f"Error fetching products: {str(e)}")

    #   - get -> v1/products/{product_id}/ -> product details
    async def get_product_details(
        self,
        product_id: int,
        is_retry: bool = False,
    ) -> Any:
        try:
            client = await get_httpx_client()
            response = await client.get(
                f"{self.base_url}/products/{product_id}",
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if not is_retry:
                await self.get_product_details(product_id, is_retry=True)
            else:
                raise SmartPosException(f"Error fetching product details: {str(e)}")
        except Exception as e:
            raise SmartPosException(f"Error fetching product details: {str(e)}")

    #   - put -> v1/products/{product_id}/ -> update product details -> params{new: update data}
    async def update_product_details(
        self,
        product_id: int,
        update_data: dict,
        is_retry: bool = False,
    ) -> Any:
        try:
            client = await get_httpx_client()
            response = await client.put(
                f"{self.base_url}/products/{product_id}",
                json=update_data,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if not is_retry:
                await self.update_product_details(
                    product_id, update_data, is_retry=True
                )
            else:
                raise SmartPosException(f"Error updating product details: {str(e)}")
        except Exception as e:
            raise SmartPosException(f"Error updating product details: {str(e)}")

    #   - put -> v1/products/stock/{product_id}/ -> adjust stock levels -> params{productId: int, productVarientId: int, quantity: int, stockOperation: enum[ADD, REMOVE, SET]}
    async def adjust_stock_levels(
        self,
        product_id: int,
        product_variant_id: int,
        quantity: float,
        stock_operation: SmartPosStock,
        is_retry: bool = False,
    ) -> Any:
        try:
            client = await get_httpx_client()
            response = await client.put(
                f"{self.base_url}/products/stock/{product_id}",
                json={
                    "productId": product_id,
                    "productVarientId": product_variant_id,
                    "quantity": quantity,
                    "stockOperation": stock_operation,
                },
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if not is_retry:
                await self.adjust_stock_levels(
                    product_id,
                    product_variant_id,
                    quantity,
                    stock_operation,
                    is_retry=True,
                )
            else:
                raise SmartPosException(f"Error adjusting stock levels: {str(e)}")
        except Exception as e:
            raise SmartPosException(f"Error adjusting stock levels: {str(e)}")
