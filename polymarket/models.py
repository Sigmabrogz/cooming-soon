"""Pydantic models for Polymarket data structures."""

from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class OrderSide(str, Enum):
    """Order side enum."""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """Order type enum."""
    GTC = "GTC"  # Good Till Cancelled
    GTD = "GTD"  # Good Till Date
    FOK = "FOK"  # Fill Or Kill
    FAK = "FAK"  # Fill And Kill


class OrderStatus(str, Enum):
    """Order status enum."""
    LIVE = "LIVE"
    MATCHED = "MATCHED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class ActivityType(str, Enum):
    """Activity type enum."""
    TRADE = "TRADE"
    CONVERT = "CONVERT"
    SPLIT = "SPLIT"
    MERGE = "MERGE"


class Order(BaseModel):
    """Order model."""
    order_id: Optional[str] = Field(None, alias="orderId")
    market: Optional[str] = None
    price: float
    size: float
    side: OrderSide
    type: OrderType
    status: Optional[OrderStatus] = None
    size_matched: Optional[float] = Field(None, alias="sizeMatched")
    expiration: Optional[int] = None
    signature: Optional[str] = None
    maker: Optional[str] = None
    taker: Optional[str] = None
    fee_rate_bps: Optional[int] = Field(None, alias="feeRateBps")
    
    class Config:
        populate_by_name = True


class Position(BaseModel):
    """Position model."""
    proxy_wallet: str = Field(alias="proxyWallet")
    asset: str
    condition_id: str = Field(alias="conditionId")
    size: float
    avg_price: float = Field(alias="avgPrice")
    initial_value: float = Field(alias="initialValue")
    current_value: float = Field(alias="currentValue")
    cash_pnl: float = Field(alias="cashPnl")
    percent_pnl: float = Field(alias="percentPnl")
    total_bought: float = Field(alias="totalBought")
    realized_pnl: float = Field(alias="realizedPnl")
    cur_price: float = Field(alias="curPrice")
    redeemable: bool
    mergeable: bool
    
    class Config:
        populate_by_name = True


class Trade(BaseModel):
    """Trade model."""
    proxy_wallet: str = Field(alias="proxyWallet")
    taker: str
    maker: str
    asset: str
    condition_id: str = Field(alias="conditionId")
    size: float
    price: float
    timestamp: int
    transaction_hash: str = Field(alias="transactionHash")
    status: str
    side: OrderSide
    
    class Config:
        populate_by_name = True


class Market(BaseModel):
    """Market model."""
    id: str
    question_id: Optional[str] = Field(None, alias="questionId")
    condition_id: str = Field(alias="conditionId")
    token0_id: str = Field(alias="token0Id")
    token1_id: str = Field(alias="token1Id")
    category: Optional[str] = None
    title: str
    slug: str
    type: str
    end_date: Optional[str] = Field(None, alias="endDate")
    liquidity: Optional[float] = None
    volume: Optional[float] = None
    status: Optional[str] = None
    min_order_size: Optional[float] = Field(None, alias="minOrderSize")
    tick_size: Optional[float] = Field(None, alias="tickSize")
    
    class Config:
        populate_by_name = True


class Event(BaseModel):
    """Event model."""
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    start_date: Optional[str] = Field(None, alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")
    liquidity: Optional[float] = None
    volume: Optional[float] = None
    neg_risk: Optional[bool] = Field(None, alias="negRisk")
    enable_neg_risk: Optional[bool] = Field(None, alias="enableNegRisk")
    
    class Config:
        populate_by_name = True


class Holder(BaseModel):
    """Holder model."""
    proxy_wallet: str = Field(alias="proxyWallet")
    amount: float
    pseudonym: Optional[str] = None
    display_username_public: Optional[bool] = Field(None, alias="displayUsernamePublic")
    profile_image: Optional[str] = Field(None, alias="profileImage")
    name: Optional[str] = None
    
    class Config:
        populate_by_name = True


class OrderBook(BaseModel):
    """Order book model."""
    buys: List[List[float]]  # [[price, size], ...]
    sells: List[List[float]]  # [[price, size], ...]
    best_bid: Optional[float] = Field(None, alias="bestBid")
    best_ask: Optional[float] = Field(None, alias="bestAsk")
    
    class Config:
        populate_by_name = True


class PriceUpdate(BaseModel):
    """Price update model."""
    symbol: str
    value: float
    timestamp: int


class CommentEvent(BaseModel):
    """Comment event model."""
    id: str
    parent_comment_id: Optional[str] = Field(None, alias="parentCommentID")
    parent_entity_id: str = Field(alias="parentEntityID")
    parent_entity_type: str = Field(alias="parentEntityType")
    body: Optional[str] = None
    created_at: str = Field(alias="createdAt")
    reaction_count: Optional[int] = Field(None, alias="reactionCount")
    report_count: Optional[int] = Field(None, alias="reportCount")
    
    class Config:
        populate_by_name = True
