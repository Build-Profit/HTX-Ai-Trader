from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class ExecutionLog:
    timestamp: str
    event: str
    status: str
    symbol: str
    price: Optional[float]
    quantity: Optional[float]
    message: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "timestamp": self.timestamp,
            "event": self.event,
            "status": self.status,
            "symbol": self.symbol,
            "price": self.price,
            "quantity": self.quantity,
            "message": self.message,
        }
