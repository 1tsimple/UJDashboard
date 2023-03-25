# ---------- SETUP ----------
import os, logging, sys
from datetime import date
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, f"../logs/{date.today()}.log"))
logging.basicConfig(
  level=logging.INFO,
  format="[ %(asctime)s ] - %(thread)d - %(filename)s - %(funcName)s - [ %(levelname)s ] - %(message)s",
  datefmt="%Y-%m-%d %H:%M:%S",
  filename=LOG_DIR
)

# ---------- IMPORTS ----------

import threading
import multiprocessing as mp
import pymongo
import csv
from re import search
from itertools import cycle
from typing import Any, Self
from datetime import datetime, timezone, timedelta
from sp_api.base import Marketplaces
from sp_api.api import Orders, Finances

from amazon.api import AmazonApiManager
from utils.payloadKeyNames import Order, OItem
from utils.dtypeFixer import fix_dtype_cython # type: ignore

# ----- Singleton Database Manager -----
class DBManager:
  # debug_info={"ObjectID": id(self), "Childs": {"InserterID": id(self.inserter), "PullerID": id(self.puller)}}
  __slots__ = ("client", "inserter", "puller")
  
  _instance = None # Singleton Instance
  _lock = threading.Lock() # Thread Safety
  def __new__(cls) -> Self: # Singleton Constructor
    if cls._instance is None:
      with cls._lock:
        if not cls._instance:
          cls._instance = super().__new__(cls)
    return cls._instance
  
  def __init__(self) -> None:
    #self.client = pymongo.MongoClient("mongodb+srv://Arda:{password}@amazon.uwbxmpc.mongodb.net/?retryWrites=true&w=majority&authSource=admin".format(password=os.environ.get("mongodb_password")))
    self.client = pymongo.MongoClient
    self.inserter = Inserter(self.client)
    self.puller = Puller(self.client)
    logging.debug("DBManager object has been created and initialized. {debug_info}".format(debug_info={"ObjectID": id(self), "Childs": {"InserterID": id(self.inserter), "PullerID": id(self.puller)}}))

class Inserter: 
  # debug_info={"ObjectID": id(self), "Childs": {"AmazonApiManagerID": id(self.api)}}
  __slots__ = ("client", "api",)
  def __init__(self, client: pymongo.MongoClient) -> None:
    self.client = client
    self.api = AmazonApiManager()
    logging.debug("Inserter object has been created and initialized. {debug_info}".format(debug_info={"ObjectID": id(self), "Childs": {"AmazonApiManagerID": id(self.api)}}))
  
  def update_orders(self, created_after: str, marketplace=Marketplaces.US) -> None:
    logging.info("Updating the orders created after '{date}'. {debug_info}".format(date=created_after, debug_info={"ObjectID": id(self), "Childs": {"AmazonApiManagerID": id(self.api)}}))
    orders = self._get_orders(created_after, marketplace)
    order_items = [self._get_order_items(order["AmazonOrderId"]) for order in orders]
    order_finances = []
    logging.info("All the data of orders created after '{date}' has been pulled. {debug_info}".format(date=created_after, debug_info={"ObjectID": id(self), "Childs": {"AmazonApiManagerID": id(self.api)}}))
    
    logging.info("Changing data types of values in orders data created after '{date}' into appropriate form to insert into database. {debug_info}".format(date=created_after, debug_info={"ObjectID": id(self), "Childs": {"AmazonApiManagerID": id(self.api)}}))
    with mp.Pool(3) as pool:
      orders, order_items, order_finances = pool.map(self._fix_dtype, (orders, order_items, order_finances))
    orders = list(map(self.__order_to_json, orders))
    order_items = [item for items in map(self.__order_items_to_json, order_items) for item in items]
    logging.info("Data types of orders data created after '{date}' have been changed into appropriate form. {debug_info}".format(date=created_after, debug_info={"ObjectID": id(self), "Childs": {"AmazonApiManagerID": id(self.api)}}))
    
    logging.info("Inserting orders created after '{date}' into database. {debug_info}".format(date=created_after, debug_info={"ObjectID": id(self), "Childs": {"AmazonApiManagerID": id(self.api)}}))
    with mp.Pool(3) as pool:
      pool.starmap(self.insert_or_update_many, (("Orders", orders, "_id"), ("OrderItems", order_items, "_id")))
    logging.info("Orders created after '{date}' have been inserted into database. {debug_info}".format(date=created_after, debug_info={"ObjectID": id(self), "Childs": {"AmazonApiManagerID": id(self.api)}}))
  
  def _get_orders(self, created_after: str, marketplace=Marketplaces.US) -> list[dict[str, Any]]:
    logging.info("Getting orders created after '{date}' via api. {debug_info}".format(date=created_after, debug_info={"ObjectID": id(self), "Childs": {"AmazonApiManagerID": id(self.api)}}))
    try: 
      orders = self.api.get_payload(Orders, marketplace, "get_orders", "Orders", reqkwargs={"CreatedAfter": created_after})
    except Exception as e:
      logging.critical("Unable to get orders created after '{date}'. {debug_info}".format(date=created_after, debug_info={"ObjectID": id(self), "Childs": {"AmazonApiManagerID": id(self.api)}}))
    else:
      logging.info("Orders created after '{date}' have been acquired. {debug_info}".format(date=created_after, debug_info={"ObjectID": id(self), "Childs": {"AmazonApiManagerID": id(self.api)}}))
      return orders
  
  def _get_order_items(self, order_id: str, marketplace=Marketplaces.US) -> list[dict[str, Any]]:
    logging.info("Getting order items of '{order_id}' via api. {debug_info}".format(order_id=order_id, debug_info={"ObjectID": id(self), "Childs": {"AmazonApiManagerID": id(self.api)}}))
    try: 
      order_items = self.api.get_payload(Orders, marketplace, "get_order_items", reqkwargs={"order_id": order_id})
    except Exception as e:
      logging.critical("Unable to get order items of '{order_id}'. {debug_info}".format(order_id=order_id, debug_info={"ObjectID": id(self), "Childs": {"AmazonApiManagerID": id(self.api)}}))
    else:
      logging.info("Order items of '{order_id}' have been acquired. {debug_info}".format(order_id=order_id, debug_info={"ObjectID": id(self), "Childs": {"AmazonApiManagerID": id(self.api)}}))
      return order_items
  
  def _get_order_finances(self):
    raise NotImplemented()
  
  def _fix_dtype(self, value: Any) -> Any:
    return fix_dtype_cython(value, {"ObjectID": id(self), "Childs": {"AmazonApiManagerID": id(self.api)}})
  
  def _str_to_date(self, value: str|None, tzone: timezone|None=timezone.utc) -> datetime | None:
    if value is None:
      return value
    return datetime.fromisoformat(value).astimezone(tzone)
  
  def __order_to_json(self, order: dict[str, Any]) -> dict[str, Any]:
    copy = order.copy()
    copy.update({key: self._str_to_date(copy.get(key)) for key in [Order.EarliestDeliveryDate, Order.LatestDeliveryDate, Order.EarliestShipDate, Order.LatestShipDate, Order.LastUpdateDate, Order.PurchaseDate]})
    return {Order._id: copy.pop("AmazonOrderId")} | copy | {Order.UpdatedAt: datetime.today().astimezone()}
  
  def __order_items_to_json(self, order_items: dict[str, Any]) -> dict[str, Any]:
    copy = order_items.copy()
    return [{OItem._id: order_item.pop("OrderItemId")} | {OItem.Order_id: copy["AmazonOrderId"]} | order_item | {OItem.UpdatedAt: datetime.today().astimezone()} for order_item in copy["OrderItems"]]
  
  def __order_finances_to_json(self, order_finances):
    raise NotImplemented()
  
  def add_weekly_top_keywords(self, path: str) -> None:
    keywords = self._get_top_keywords(path)
    logging.info("Inserting weekly top 1 million keywords from path '{path}' into collection 'WeeklyTopKeywords'. {debug_info}".format(path=path, debug_info={"ObjectID": id(self), "Childs": {"AmazonApiManagerID": id(self.api)}}))
    try:
      self.insert_many("WeeklyTopKeywords", keywords)
    except Exception:
      pass
    else:
      logging.info("Weekly top 1 million keywords from path '{path}' have been inserted into collection 'WeeklyTopKeywords'. {debug_info}".format(path=path, debug_info={"ObjectID": id(self), "Childs": {"AmazonApiManagerID": id(self.api)}}))
  
  def _get_top_keywords(self, path) -> list[dict[str, str|int|float]]:
    logging.info("Getting weekly top 1 million keywords. {debug_info}".format(debug_info={"ObjectID": id(self), "Childs": {"AmazonApiManagerID": id(self.api)}}))
    keys = [
      "Department", "SearchTerm", "SearchFrequencyRank",
      "Num1ClickedASIN", "Num1ProductTitle", "Num1ClickShare", "Num1ConversionShare",
      "Num2ClickedASIN", "Num2ProductTitle", "Num2ClickShare", "Num2ConversionShare",
      "Num3ClickedASIN", "Num3ProductTitle", "Num3ClickShare", "Num3ConversionShare"
    ]
    share_keys = ["Num1ClickShare", "Num1ConversionShare", "Num2ClickShare", "Num2ConversionShare", "Num3ClickShare", "Num3ConversionShare"]
    str_keys = ["Department", "SearchTerm", "Num1ClickedASIN", "Num1ProductTitle", "Num2ClickedASIN", "Num2ProductTitle", "Num3ClickedASIN", "Num3ProductTitle"]
    def parse_date(date_str: str) -> tuple[datetime, datetime]:
      match_object = search(r"\[(.*?)\]", date_str)
      if match_object:
        start_date, end_date = match_object.group(1).split(" - ")
      else:
        logging.fatal("Unable to find date in string {string}. {debug_info}".format(string=date_str, debug_info=self.__debug_information))
        raise Exception(f"Unable to find date in file {date_str}")
      start_date, end_date = tuple(map(lambda x: datetime.strptime(x, "%m/%d/%y").astimezone(timezone.utc) + timedelta(hours=3), (start_date, end_date)))
      return (start_date, end_date) 
    def process_row(row: list[str], date: datetime) -> dict[str, str]:
      row_dict = dict(zip(keys, row))
      row_dict["SearchFrequencyRank"] = row_dict["SearchFrequencyRank"].replace(",", "")
      row_dict["SearchFrequencyRank"] = int(row_dict["SearchFrequencyRank"])
      for key in share_keys:
        if row_dict[key].lower() != "—":
          row_dict[key] = row_dict[key].rstrip("%")
          row_dict[key] = float(row_dict[key])
        else:
          row_dict[key] = None
      for key in str_keys:
        if row_dict[key].lower() in ["none", "null", "na", "nan", "—", "", " "]:
          row_dict[key] = None
      row_dict["Date"] = date
      return row_dict
    
    logging.info("Reading top keywords from path '{path}'. {debug_info}".format(path=path, debug_info={"ObjectID": id(self), "Childs": {"AmazonApiManagerID": id(self.api)}}))
    with open(path, newline='', encoding="utf-8") as csvfile:
      reader = csv.reader(csvfile)
      date_ = parse_date(next(reader)[-1])[-1]
      next(reader) # Skip Column Names
      data = list(map(process_row, reader, (date for date in cycle([date_]))))
    logging.info("Weekly top 1 million keywords of date '{date}' from path '{path}' have been read. {debug_info}".format(date=date_, path=path, debug_info={"ObjectID": id(self), "Childs": {"AmazonApiManagerID": id(self.api)}}))
    return data
  
  def insert_many(self, collection_name: str, documents: list[dict[str, Any]]) -> None:
    try:
      self.client.Amazon[collection_name].insert_many(documents)
    except Exception:
      logging.critical("Error occurred while inserting data into collection '{collection}'!".format(collection=collection_name), exc_info=True)
    else:
      logging.info("The data has been inserted into collection '{collection}'. {DebugInfo}".format(collection=collection_name, DebugInfo=self.__debug_information))
  
  def insert_or_update_one(self, collection_name: str, document: dict[str, Any], key: str) -> None:
    with self.client() as client:
      client.Amazon[collection_name].replace_one({key: document[key]}, document, upsert=True)
  
  def insert_or_update_many(self, collection_name: str, documents: list[dict[str, Any]], key: str) -> None:
    try:
      bulk_operations = [pymongo.ReplaceOne(
        filter={key: document[key]},
        replacement=document,
        upsert=True
      ) for document in documents]
      with self.client() as client:
        client.Amazon[collection_name].bulk_write(bulk_operations)
    except Exception:
      logging.critical("Error occurred while inserting data into collection '{collection}'!".format(collection=collection_name), exc_info=True)
    else:
      logging.info("The data has been inserted into collection '{collection}'. {debug_info}".format(collection=collection_name, debug_info={"ObjectID": id(self), "Childs": {"AmazonApiManagerID": id(self.api)}}))

class Puller:
  # debug_info={"ObjectID": id(self)}
  __slots__ = ("client", )
  def __init__(self, client: pymongo.MongoClient) -> None:
    self.client = client
    logging.debug("Puller object has been created and initialized. {debug_info}".format(debug_info={"ObjectID": id(self)}))
  
  def get(self, collection_name: str, fields: list[str]=[], filters: dict[str, Any]={}) -> Any:
    with self.client() as client:
      data = client.Amazon[collection_name].find(filters, {field: 1 for field in fields})
    return data

if __name__ == "__main__":
  import time
  from pprint import pprint
  db = DBManager()
  path = os.path.abspath(r"C:\Users\salih\Desktop\Downloaded Documents\Amazon Search Terms_Search Terms_US.csv")
  db.inserter._get_top_keywords(path)