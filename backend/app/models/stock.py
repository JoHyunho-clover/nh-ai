from sqlalchemy import Column, String, Float, Integer, Date, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import date
import uuid

from ..database import Base


class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)  # 1D, 1W, 1M
    date = Column(Date, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<StockPrice({self.symbol}, {self.timeframe}, {self.date}, close={self.close})>"
