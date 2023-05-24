from pydantic import BaseModel, validator
from typing import Optional, Literal

class ErankKeywordData(BaseModel):
  __slots__ = "keyword", "word_count", "character_count", "tag_occurrences", "average_searches", "average_clicks", "average_ctr", "average_csi", "etsy_competition", "google_searches", "google_cpc", "google_competition", "long_tail_keyword"

  keyword: str
  word_count: int = -1
  character_count: int = -1
  tag_occurrences: Optional[int]
  average_searches: Optional[int]
  average_clicks: Optional[int]
  average_ctr: Optional[float] = -1.0
  etsy_competition: Optional[int]
  average_csi: Optional[float] = -1.0
  google_searches: Optional[int]
  google_cpc: Optional[float]
  google_competition: Optional[float]
  long_tail_keyword: Literal["Yes", "Maybe", "No"]
  
  @validator("word_count", always=True)
  def calculate_word_count(cls, value, values):
    keyword = values.get("keyword")
    return len(keyword.split(" "))

  @validator("character_count", always=True)
  def calculate_character_count(cls, value, values):
    keyword = values.get("keyword")
    return len(keyword)
  
  @validator("average_searches", "average_clicks", "etsy_competition", "google_searches", "google_cpc", "google_competition", pre=True)
  def validate_field(cls, value):
    if isinstance(value, str):
      if value in ("", "Unknown", "< 20"):
        return None
      if "%" in value:
        value = value.replace("%", "")
      if "," in value:
        value = value.replace(",", "")
    return value

  @validator("average_ctr", always=True)
  def calculate_average_ctr(cls, value, values):
    average_searches = values.get("average_searches")
    average_clicks = values.get("average_clicks")
    if average_clicks is not None and average_searches is not None and average_searches != 0:
      return (average_clicks / average_searches) * 100
    return None
  
  @validator("average_csi", always=True)
  def calculate_average_csi(cls, value, values):
    average_searches = values.get("average_searches")
    average_clicks = values.get("average_clicks")
    etsy_competition = values.get("etsy_competition")
    if average_clicks is not None and average_searches is not None and etsy_competition is not None and average_searches != 0 and average_clicks != 0:
      return etsy_competition / (((average_searches * average_clicks) ** 0.5) * average_clicks / average_searches)
    return None

class MinMaxField(BaseModel):
  min: Optional[int|float]
  max: Optional[int|float]

class SortByField(BaseModel):
  column: Literal["word_count", "etsy_competition", "google_searches", "google_cpc", "average_searches", "average_clicks", "average_ctr", "average_csi", "tag_occurrences", "long_tail_keyword"]
  order: Literal["desc", "asc", None]

class ErankFilterQuery(BaseModel):
  word_count: MinMaxField = MinMaxField(min=None, max=None)
  etsy_competition: MinMaxField = MinMaxField(min=None, max=None)
  google_searches: MinMaxField = MinMaxField(min=None, max=None)
  google_cpc: MinMaxField = MinMaxField(min=None, max=None)
  average_searches: MinMaxField = MinMaxField(min=None, max=None)
  average_clicks: MinMaxField = MinMaxField(min=None, max=None)
  average_ctr: MinMaxField = MinMaxField(min=None, max=None)
  average_csi: MinMaxField = MinMaxField(min=None, max=None)
  tag_occurrences: MinMaxField = MinMaxField(min=None, max=None)
  include_keywords: list[str] = []
  exclude_keywords: list[str] = []
  long_tail_keyword: list[str] = []
  sort_by: SortByField = SortByField(column="average_searches", order="desc")