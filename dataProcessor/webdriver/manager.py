import threading
import time
from typing import Self

from .factory import WebdriverController

class DriverControllerManager:
  __slots__ = "driver_controllers", 
  
  _instance = None # Singleton Instance
  _lock = threading.Lock() # Thread Safety
  def __new__(cls) -> Self: # Singleton Constructor
    if cls._instance is None:
      with cls._lock:
        if not cls._instance:
          cls._instance = super().__new__(cls)
    return cls._instance
  
  def __init__(self) -> None:
    self.driver_controllers: dict[str, WebdriverController] = {}
  
  def add_controller(self, controller: WebdriverController) -> None:
    self.driver_controllers[controller.session_id] = controller
  
  def remove_controller(self, controller: WebdriverController) -> None:
    self.driver_controllers.pop(controller.session_id)
  
  def check_controllers(self) -> None:
    while True:
      for session_id, controller in self.driver_controllers.items():
        if controller.is_closed:
          controller.driver.quit()
          self.remove_controller(controller)
          del controller
      
      time.sleep(1)
  
  def start(self) -> None:
    thread = threading.Thread(target=self.check_controllers, daemon=True)
    thread.start()