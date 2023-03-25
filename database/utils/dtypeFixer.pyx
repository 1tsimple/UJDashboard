# distutils: language = c++
# cython: language_level=3, boundscheck=False, wraparound=False, infer_types=True, cdivision=True


cimport cython
import logging
from datetime import date, datetime

@cython.boundscheck(False)
@cython.wraparound(False)
def fix_dtype_cython(value, dict debug_information):
  cdef str lower_val
  cdef int n
  cdef list list_copy
  cdef dict dict_copy
  if isinstance(value, (int, float, bool, type(None), date, datetime)):
    return value
  
  elif isinstance(value, str):
    if value.isnumeric():
      if len(value) >= 10:
        return value
      return int(value)
    try:
      return float(value)
    except ValueError:
      lower_val = value.lower()
      if lower_val == "false":
        return False
      elif lower_val == "true":
        return True
      elif lower_val == "" or lower_val == "null" or lower_val == "none":
        return None
      else:
        return value
  
  elif isinstance(value, list):
    list_copy = value
    n = len(list_copy)
    if n == 0:
      return None
    return [fix_dtype_cython(list_copy[i], debug_information) for i in range(n)]
  
  elif isinstance(value, dict):
    dict_copy = value
    if len(dict_copy) == 0:
      return None
    return {key: fix_dtype_cython(val, debug_information) for key, val in dict_copy.items()}
    
  else:
    logging.critical(f"Failed to fix value '{value}' Therefore, returned None. {debug_information}")
    return None