from typing import Any
from dataclasses import dataclass

@dataclass(slots=True)
class ERANK_DATA_KEYS:
  word_count = "word_count"
  tag_occurrences = "tag_occurrences"
  average_searches = "average_searches"
  average_clicks = "average_clicks"
  average_ctr = "average_ctr"
  etsy_competition = "etsy_competition"
  google_searches = "google_searches"
  google_cpc = "google_cpc"
  long_tail = "long_tail"

class ErankNode:
  __slots__ = "left", "right", "key", "value", "data", "_sorted_by"
  
  def __init__(self, key: str, value: dict[str, Any], sort_by: ERANK_DATA_KEYS) -> None:
    self.left = None
    self.right = None
    self.key = key
    self.value = value
    self.data = {"keyword": key} | value
    self._sorted_by = sort_by
  
  def insert(self, key: str, value: dict[str, Any]):
    if self.key is None:
      self.key = key
      self.value = value
      self.data = {"keyword": key} | value
    else:
      if value[self._sorted_by] < self.value[self._sorted_by]: # type: ignore
        if self.left is None:
          self.left = ErankNode(key, value, self._sorted_by)
        else:
          self.left.insert(key, value)
      else:
        if self.right is None:
          self.right = ErankNode(key, value, self._sorted_by)
        else:
          self.right.insert(key, value)
  
  def traverse(self):
    if self.right is not None:
      yield from self.right.traverse()
    yield self.data
    if self.left is not None:
      yield from self.left.traverse()