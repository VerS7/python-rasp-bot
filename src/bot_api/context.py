"""
Контекст с метаданными для работы команд
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Context:
    """Контекст с метаданными"""

    peer: int
    args: List[str]
