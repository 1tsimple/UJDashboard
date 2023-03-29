# ---------- SETUP ----------
import os, logging, sys
from dotenv import load_dotenv
from datetime import date
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, f"../../logs/{date.today()}.log"))
logging.basicConfig(
  level=logging.INFO,
  format="[ %(asctime)s ] - %(thread)d - %(filename)s - %(funcName)s - [ %(levelname)s ] - %(message)s",
  datefmt="%Y-%m-%d %H:%M:%S",
  filename=LOG_DIR
)
load_dotenv(os.path.abspath(os.path.join(SCRIPT_DIR, "../../.env")))

# ---------- IMPORTS ----------
import time
from typing import Callable
from sp_api.base import SellingApiRequestThrottledException, Marketplaces

class AmazonApiManager:
  __slots__ = tuple()
  def __init__(self) -> None:
    logging.debug("AmazonApiManager object has been created and initialized. {debug_info}".format(debug_info={"ObjectID": id(self)}))
  
  def get_payload(self, request_handler: Callable, marketplace: Marketplaces, request: str, *args: str, **kwargs: dict[str, str]):
    logging.info("Getting payload. {debug_info}".format(debug_info={"Request Handler": request_handler, "Marketplace": marketplace, "Request": request, "args": args, "kwargs": kwargs}))
    try:
      if kwargs.get("response") is not None:
        response = request_handler(credentials=self.keys, marketplace=marketplace, **kwargs["response"])
      else:
        response = request_handler(credentials=self.keys, marketplace=marketplace)
      if kwargs.get("reqkwargs") is not None:
        data = getattr(response, request)(**kwargs["reqkwargs"])
      else:
        data = getattr(response, request)()
      payload = data.payload
      try:
        for arg in args:
          payload = payload.get(arg)
      except AttributeError as e:
        logging.exception("Failed to retrieve payload of response! Unvalid argument(s). {debug_info}".format(debug_info={"Request Handler": request_handler, "Marketplace": marketplace, "Method": request, "args": args, "kwargs": kwargs}))
        raise e
      else:
        return payload
    except SellingApiRequestThrottledException:
      logging.warning(f"API quota has been exceeded. Waiting for 5 seconds to refresh quota.")
      time.sleep(5)
      return self.get_payload(request_handler, marketplace, request, *args, **kwargs)
    finally:
      logging.info("Payload retrieved. {debug_info}".format(debug_info={"Request Handler": request_handler, "Marketplace": marketplace, "Request": request, "args": args, "kwargs": kwargs}))
  
  @property
  def keys(self) -> dict[str, str]:
    return {
      "lwa_app_id": os.environ.get("lwa_app_id"),
      "lwa_client_secret": os.environ.get("lwa_client_secret"),
      "aws_access_key": os.environ.get("aws_access_key"),
      "aws_secret_key": os.environ.get("aws_secret_key"),
      "role_arn": os.environ.get("role_arn"),
      "refresh_token": os.environ.get("refresh_token")
    }
  
  def get_report(self):
    raise NotImplementedError()

if __name__ == "__main__":
  api = AmazonApiManager()
  print(api.keys)