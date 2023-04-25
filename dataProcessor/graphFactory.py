import plotly
import plotly.express as px
from plotly.graph_objs import Figure
import pandas as pd
from typing import Any, Literal
from abc import ABC, abstractmethod

class Graph(ABC):
  @abstractmethod
  def get_graph(self, dataframe: pd.DataFrame) -> Figure: ...
  
  @abstractmethod
  def validate_kwargs(self, kwargs, required_kwargs) -> None:
    missing_kwargs = [kwarg for kwarg in required_kwargs if kwarg not in kwargs]
    if missing_kwargs:
        raise ValueError(f"Missing required keyword argument(s): {missing_kwargs}")
    unexpected_kwargs = [kwarg for kwarg in kwargs if kwarg not in required_kwargs]
    if unexpected_kwargs:
        raise ValueError(f"Unexpected keyword argument(s): {unexpected_kwargs}")

class TotalSalesCountGraph(Graph):
  def __init__(self, dataframe: pd.DataFrame) -> None:
    self.df = dataframe
    self.__dfs = []
    self.__required_kwargs = ["marketplaces", "variants", "groupby", "time_frame"]
  
  def get_graph(self, **kwargs):
    self.validate_kwargs(kwargs)
    marketplaces: list[str] = kwargs.get("marketplaces") # type: ignore
    variants: list[str] = kwargs.get("variants") # type: ignore
    groupby: str|None = kwargs.get("groupby")
    time_frame: list[str] = kwargs.get("time_frame") # type: ignore
    
    self.handle_data_process(marketplaces, variants, groupby, time_frame)
    
    return self.__get_graph(groupby)
  
  def __get_graph(self, groupby: str|None):
    if groupby is None:
      color = None
    elif groupby == "Marketplace":
      color = "MarketplaceName"
    else:
      color = "Variant.All"
    return px.line(
      data_frame=self.df,
      x="PostedDate",
      y="QuantityShippedTrueCumulative",
      color=color
    )
  
  def handle_data_process(self, marketplaces: list[str], variants: list[str], groupby: str|None, time_frame: list[str]) -> None:
    self.filter_dataframe(marketplaces, variants)
    self.df["QuantityShippedTrue"] = self.df.apply(lambda row: self.get_quantity_shipped_true(row), axis=1)
    self.df["PostedDate"] = pd.to_datetime(self.df["PostedDate"].str.split("T", expand=True)[0])
    self.df = self.df[(self.df["PostedDate"] >= time_frame[0]) & (self.df["PostedDate"] <= time_frame[-1])].reset_index(drop=True)
    self.groupby_filter(marketplaces, variants, groupby)
    self.__dfs = list(map(self.fill_spaces_between_dates, self.__dfs))
    for df_ in self.__dfs:
      df_["QuantityShippedTrueCumulative"] = df_["QuantityShippedTrue"].cumsum()
    self.df = pd.concat(self.__dfs)
    print(time_frame)
  
  def filter_dataframe(self, marketplaces: list[str], variants: list[str]) -> None:
    self.df = self.df[self.df["MarketplaceName"].isin(marketplaces)]
    variant_columns = [column for column in self.df.columns if "Variant." in column]
    for col in variant_columns:
      self.df = self.df[self.df[col].isin(variants)]
  
  @staticmethod
  def get_quantity_shipped_true(row) -> int:
    """Turns QuantityShipped value to negative if shipments is a refund"""
    if row["ShipmentType"] == "Order":
      return row["QuantityShipped"]
    else:
      return -row["QuantityShipped"]
  
  def groupby_filter(self, marketplaces: list[str], variants: list[str], groupby: str|None):
    if groupby is None:
      df_ = self.df.copy().groupby(by="PostedDate").agg("sum", numeric_only=True).reset_index()
      self.__dfs = [df_]
    elif groupby == "Marketplace":
      for marketplace in marketplaces:
        df_ = self.df[self.df["MarketplaceName"] == marketplace].copy()
        df_ = df_.groupby(by="PostedDate").agg("sum").reset_index()
        df_["MarketplaceName"] = marketplace
        self.__dfs.append(df_)
    elif groupby == "Variant":
      variant_columns = [column for column in self.df.columns if "Variant." in column]
      self.df["Variant.All"] = self.df[variant_columns].agg(" - ".join, axis=1)
      for variant in variants:
        df_ = self.df[self.df["Variant.All"] == variant].copy()
        df_ = df_.groupby(by="PostedDate").agg("sum", numeric_only=True).reset_index()
        df_["Variant.All"] = variant
        self.__dfs.append(df_)
  
  @staticmethod
  def fill_spaces_between_dates(dataframe: pd.DataFrame, time_frame=None):
    if dataframe.empty:
      return dataframe
    all_dates = pd.DataFrame(pd.date_range(dataframe["PostedDate"].min(), dataframe["PostedDate"].max()), columns=["PostedDate"])
    all_dates_df = all_dates.merge(right=dataframe, how="left", on="PostedDate")
    all_dates_df[["QuantityShipped", "QuantityShippedTrue"]] = all_dates_df[["QuantityShipped", "QuantityShippedTrue"]].fillna(0.0).astype(int)
    return all_dates_df
  
  def validate_kwargs(self, kwargs) -> None:
    return super().validate_kwargs(kwargs, self.__required_kwargs)

class GraphFactory:
  factories = {
    "total_sales_count": TotalSalesCountGraph
  }
  
  GraphType = Literal["total_sales_count"]
  @classmethod
  def get_graph(cls, type_: GraphType, dataframe: pd.DataFrame, **kwargs):
    return cls.factories[type_](dataframe).get_graph(**kwargs)