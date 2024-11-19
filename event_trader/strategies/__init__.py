from .base_strategy import BaseStrategy
from .simple_moving_average_strategy import SimpleMovingAverageStrategy
from .stochastic_oscillator_strategy import StochasticOscillatorStrategy
from .one_moving_average_strategy import OneMovingAverageStrategy
from .traditional_boll_strategy import TraditionalBollStrategy

STRATEGIES = {
    'SMA': SimpleMovingAverageStrategy,
    'SO': StochasticOscillatorStrategy,
    'OMA': OneMovingAverageStrategy,
    'TB': TraditionalBollStrategy
}