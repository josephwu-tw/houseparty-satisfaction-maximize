"""
Menu handlers package.
"""
from .base import BaseMenu
from .optimization import OptimizationMenu
from .friends import FriendsMenu
from .foods import FoodsMenu
from .analysis import AnalysisMenu

__all__ = ['BaseMenu', 'OptimizationMenu', 'FriendsMenu', 'FoodsMenu', 'AnalysisMenu']