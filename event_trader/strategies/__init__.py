from .base_strategy import BaseStrategy
from .ma2_strategy import MA2Strategy
from .kdj_strategy import KDJStrategy
from .ma1_strategy import MA1Strategy
from .boll_strategy import BollStrategy
from .macd_strategy import MACDStrategy
from .vma_strategy import VMAStrategy
from .pd_strategy import PriceDeviationStrategy

STRATEGIES = [
    MA2Strategy,
    KDJStrategy,
    MA1Strategy,
    BollStrategy,
    MACDStrategy,
    VMAStrategy,
    PriceDeviationStrategy
]

