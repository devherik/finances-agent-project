"""
===============
SmartPos Entities
===============

They represent the entities of the SmartPos API
"""

from decimal import Decimal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class SmartPosNfStatus(Enum):
    """
    The status of the invoice
    """

    PROCESSING = "PROCESSING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


class SmartPosStock(Enum):
    ADD = "ADD"
    REMOVE = "REMOVE"
    SET = "SET"


class SmartPosApiError(BaseModel):
    """
    The error of the API
    """

    codigo: int
    detalhes: str
    newApiError: bool


class AddressBase(BaseModel):
    """
    The address of the customer
    """

    address: str = Field(description="Endereço")
    street_type: str = Field(description="Rua")
    number: str = Field(description="Número")
    complement: str = Field(description="Complemento")
    district: str = Field(description="Bairro")
    state: str = Field(description="Estado")
    zip_code: str = Field(description="Código postal")


class CustomerBase(BaseModel):
    """
    The customer of the sale
    """

    id: int = Field(description="ID do cliente")
    type: str = Field(description="Tipo do cliente")
    person_type: str = Field(description="Tipo de pessoa")
    cpf_cnpj: str = Field(description="CPF/CNPJ do cliente")
    rg_ie: str = Field(description="RG/IE do cliente")
    isento_icms: bool = Field(description="Se o cliente é isento de ICMS")
    is_simples: bool = Field(description="Se o cliente é simples")
    observation: str = Field(description="Observação")
    email: str = Field(description="Email do cliente")
    phone: str = Field(description="Telefone do cliente")
    cellphone: str = Field(description="Celular do cliente")
    limiti: int = Field(description="Limite do cliente")
    address: AddressBase = Field(description="Endereço do cliente")


class SellerBase(BaseModel):
    """
    The seller of the sale
    """

    name: str = Field(description="Nome do vendedor")
    email: str = Field(description="Email do vendedor")
    phone: str = Field(description="Telefone do vendedor")
    commission_percentage: Decimal = Field(description="Porcentagem de comissão")


class DiscountCouponBase(BaseModel):
    """
    The discount coupon of the sale
    """

    name: str = Field(description="Nome do cupom")
    start_date: datetime = Field(description="Data de início")
    expiration_date: datetime = Field(description="Data de expiração")
    total_amount: Decimal = Field(description="Valor total")
    is_percent_discount_applied: bool = Field(description="Se o desconto é porcentagem")
    minimum_purchase_amount: Decimal = Field(description="Valor mínimo de compra")
    coupon_status: str = Field(description="Status do cupom")
    color: str = Field(description="Cor do cupom")


class VariantBase(BaseModel):
    """
    The variant of the sale
    """

    id: str = Field(description="ID da variante")
    name: str = Field(description="Nome da variante")
    sku: str = Field(description="SKU da variante")
    sell_value: Decimal = Field(description="Valor de venda")
    cost_value: Decimal = Field(description="Valor de custo")
    no_stock: bool = Field(description="Sem estoque")
    minimum_stock: int = Field(description="Estoque mínimo")
    position: int = Field(description="Posição")


class CategoryBase(BaseModel):
    """
    The category of the sale
    """

    description: str = Field(description="Descrição da categoria")
    view_mode: str = Field(description="Modo de visualização")
    text: str = Field(description="Texto da categoria")
    color: str = Field(description="Cor da categoria")
    show_catalog: bool = Field(description="Se a categoria é catalogada")


class UnitBase(BaseModel):
    """
    The unit of the sale
    """

    description: str = Field(description="Descrição da unidade")
    symbol: str = Field(description="Símbolo da unidade")


class NcmBase(BaseModel):
    """
    The NCM of the sale
    """

    code: int = Field(description="Código da NCM")
    code_string: str = Field(description="Código da NCM em string")
    description: str = Field(description="Descrição da NCM")


class TaxesRuleBase(BaseModel):
    """
    The taxes rule of the sale
    """

    id: str = Field(description="ID da regra de impostos")
    name: str = Field(description="Nome da regra de impostos")


class SaleBase(BaseModel):
    """
    The sale of the SmartPos
    """

    id: str = Field(description="ID da venda")
    order_name: str = Field(description="Nome da ordem")
    creation_date: datetime = Field(description="Data de criação")
    total_amount: Decimal = Field(description="Valor total")
    discount_amount: Decimal = Field(description="Valor do desconto")
    observation: str = Field(description="Observação")
    additional_amount: Decimal = Field(description="Valor adicional")
    status: Optional[SmartPosNfStatus] = Field(description="Status")
    number_invoice: Optional[str] = Field(description="Número da NF")
    series_invoice: Optional[str] = Field(description="Série da NF")
    link_invoice_success: Optional[str] = Field(description="Link da NF")
    link_invoice_canceled: Optional[str] = Field(description="Link da NF")
    is_canceled: Optional[bool] = Field(description="Se a venda foi cancelada")
    date_transfer_sefaz: Optional[datetime] = Field(
        description="Data de transferência para a SEFAZ"
    )
    cancellation_date: Optional[datetime] = Field(description="Data de cancelamento")
    invoice_model: Optional[int] = Field(description="Modelo da NF")
    access_key: Optional[str] = Field(description="Chave de acesso")
    invoice_environment: Optional[str] = Field(description="Ambiente da NF")
    invoice_error_code: Optional[str] = Field(description="Código de erro")
    invoice_error_detail: Optional[str] = Field(description="Detalhes do erro")
    cancellation_detail: Optional[str] = Field(description="Detalhes do cancelamento")
    cancellation_reason: Optional[str] = Field(description="Motivo do cancelamento")
    device_id: Optional[str] = Field(description="ID do dispositivo")
    customer: Optional[CustomerBase] = Field(description="Cliente")
    seller: Optional[SellerBase] = Field(description="Vendedor")
    is_budget: Optional[bool] = Field(description="Se a venda é um orçamento")
    change_amount: Optional[Decimal] = Field(description="Valor do troco")
    profit: Optional[Decimal] = Field(description="Lucro")
    freight_type: Optional[str] = Field(description="Tipo de frete")
    terminal_type: Optional[str] = Field(description="Tipo de terminal")
    freight_amount: Optional[Decimal] = Field(description="Valor do frete")
    net_amount: Optional[Decimal] = Field(description="Valor líquido")
    commission_amount: Optional[Decimal] = Field(description="Valor da comissão")
    customer_document: Optional[str] = Field(description="Documento do cliente")
    receipt_number: Optional[str] = Field(description="Número do recibo")
    protocol_number: Optional[str] = Field(description="Número do protocolo")
    application_id: Optional[str] = Field(description="ID da aplicação")
    discount_coupon: Optional[DiscountCouponBase] = Field(
        description="Cupom de desconto"
    )
    discount_coupon_value: Optional[Decimal] = Field(
        description="Valor do cupom de desconto"
    )
    discount_coupon_percent: Optional[Decimal] = Field(
        description="Porcentagem do cupom de desconto"
    )
    is_totem_sale: Optional[bool] = Field(description="Se é uma venda de totem")
    processing_fee_amount: Optional[Decimal] = Field(
        description="Valor da taxa de processamento"
    )
    queue_number: Optional[int] = Field(description="Número da fila")
    items_identification_type: Optional[str] = Field(
        description="Tipo de identificação dos itens"
    )
    has_signature: Optional[bool] = Field(description="Se tem assinatura")


class SaleItemBase(BaseModel):
    id: int = Field(description="ID do item")
    alpha_code: str = Field(description="Código alfa")
    name: str = Field(description="Nome do item")
    sell_value: Decimal = Field(description="Valor de venda")
    cost_value: Decimal = Field(description="Valor de custo")
    ean_code: str = Field(description="Código EAN")
    net_weight: Decimal = Field(description="Peso líquido")
    gross_weight: Decimal = Field(description="Peso bruto")
    minimum_stock: int = Field(description="Estoque mínimo")
    observation: str = Field(description="Observação")
    ex_tipi: str = Field(description="Ex Tipi")
    cest: str = Field(description="CEST")
    is_fractional: bool = Field(description="Se é fracionário")
    favorite: int = Field(description="Favorito")
    no_stock: bool = Field(description="Sem estoque")
    is_open_value: bool = Field(description="Se é valor aberto")
    is_hidden: bool = Field(description="Se é oculto")
    updated_at: datetime = Field(description="Data de atualização")
    show_catalog: bool = Field(description="Se é catalogo")
    has_variant: bool = Field(description="Se tem variante")
    is_archived: bool = Field(description="Se é arquivado")
    promotional_display_timer: bool = Field(
        description="Se é timer de display promocional"
    )
    promotional_value: Decimal = Field(description="Valor promocional")
    promotional_expiration_date: datetime = Field(
        description="Data de expiração promocional"
    )
    category: CategoryBase = Field(description="Categoria")
    supplier: CustomerBase = Field(description="Fornecedor")
    unit: UnitBase = Field(description="Unidade")
    ncm: NcmBase = Field(description="NCM")
    product_origin: str = Field(description="Origem do produto")
    taxes_rule: TaxesRuleBase = Field(description="Regra de impostos")
    product_type: str = Field(description="Tipo do produto")
    warranty_duration_type: str = Field(description="Tipo de duração da garantia")
    warranty_duration: int = Field(description="Duração da garantia")
    warranty_time: int = Field(description="Tempo da garantia")
    variant: VariantBase = Field(description="Variante")
    observation: str = Field(description="Observação")
    quantity: Decimal = Field(description="Quantidade")
    cost_price: Decimal = Field(description="Preço de custo")
    list_price: Decimal = Field(description="Preço de lista")
    used_price: Decimal = Field(description="Preço de uso")
    item_discount: Decimal = Field(description="Desconto do item")
    item_surcharge: Decimal = Field(description="Acréscimo do item")
    net_item: Decimal = Field(description="Item líquido")
    item_commission: Decimal = Field(description="Comissão do item")
    inclusion_date: datetime = Field(description="Data de inclusão")
    discount_prorating: Decimal = Field(description="Prorata de desconto")
    surcharge_prorating: Decimal = Field(description="Prorata de acréscimo")
    profit: Decimal = Field(description="Lucro")
    total_taxes_percent: Decimal = Field(description="Percentual de impostos")
    total_taxes_amount: Decimal = Field(description="Valor de impostos")
    federal_taxes_percent: Decimal = Field(
        description="Percentual de impostos federais"
    )
    federal_taxes_amount: Decimal = Field(description="Valor de impostos federais")
    state_taxes_percent: Decimal = Field(description="Percentual de impostos estaduais")
    state_taxes_amount: Decimal = Field(description="Valor de impostos estaduais")
    municipal_taxes_percent: Decimal = Field(
        description="Percentual de impostos municipais"
    )
    municipal_taxes_amount: Decimal = Field(description="Valor de impostos municipais")
    iva_value: Decimal = Field(description="Valor de IVA")
    product_type: str = Field(description="Tipo do produto")
    warranty_duration: datetime = Field(description="Duração da garantia")
    warranty_type: str = Field(description="Tipo da garantia")
    warranty_time: int = Field(description="Tempo da garantia")

class ProductBase(BaseModel):
    id: int = Field(description="ID do produto")
    name: str = Field(description="Nome do produto")
    description: str = Field(description="Descrição do produto")
    sell_value: Decimal = Field(description="Valor de venda")
    cost_value: Decimal = Field(description="Valor de custo")
    ean_code: str = Field(description="Código EAN")
    net_weight: Decimal = Field(description="Peso líquido")
    gross_weight: Decimal = Field(description="Peso bruto")
    minimum_stock: int = Field(description="Estoque mínimo")
    observation: str = Field(description="Observação")
    ex_tipi: str = Field(description="Ex Tipi")
    cest: str = Field(description="CEST")
    is_fractional: bool = Field(description="Se é fracionário")
