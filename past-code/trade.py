from enum import Enum
class Position(Enum):
    """represents long, for long a, etc"""
    A = "A"
    A_PARTIAL = "A_PARTIAL"
    NONE = "NONE"
    B = "B"
    B_PARTIAL = "B_PARTIAL"
    
class Trade:
    """represents a trade to execute"""
    def __init__(self, to_trade, liquidate=False, long=False, short=False):
        """
        - to_trade: Whether to actually trade. If False, ignore the rest
        - liquidate: Whether to liquidate holdings (True) to repay loan, or take out loan (False)
        - long: Which asset to go long (If not liquidate) or which long asset to sell (if liquidate)
        - short: Which asset to go short (If not liquidate) or which short asset to buy back and repay loan
        """
        self.to_trade = to_trade
        self.liquidate = liquidate
        self.long = long
        self.short = short
        
    def to_json(self):
        """returns trade as a dictionary if trade else None"""
        return {"liquidate":self.liquidate, "long":self.long, "short":self.short} if self.to_trade else None
    