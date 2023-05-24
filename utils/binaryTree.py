from typing import Any
from dataclasses import dataclass

class ErankNode:
  __slots__ = "left", "right", "data", "value"
  
  def __init__(self, value: int|float, data: dict[str, Any]) -> None:
    self.left = None
    self.right = None
    self.data = data
    self.value = value
  
  def insert(self, value: int|float, data: dict[str, Any]) -> None:
    if value < self.value:
      if self.left is None:
        self.left = ErankNode(value, data)
      else:
        self.left.insert(value, data)
    elif value > self.value:
      if self.right is None:
        self.right = ErankNode(value, data)
      else:
        self.right.insert(value, data)
  
  def traverse(self):
    if self.right is not None:
      yield from self.right.traverse()
    yield self.data
    if self.left is not None:
      yield from self.left.traverse()