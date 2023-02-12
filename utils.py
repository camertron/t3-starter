from __future__ import annotations
from typing import Any, Callable, Dict, Tuple

from flask import jsonify, make_response, request, Response

import json


JsonResponse = Tuple[Dict[str, Any], int]


def as_json(func: Callable[..., JsonResponse]) -> Callable[..., Response]:
  def check_json(*args, **kwargs) -> Response:
    if not request.is_json:
      body = {"error": "Content-Type must be application/json"}
      code = 404
    else:
      try:
        body, code = func(*args, **kwargs)
      except Exception as e:
        body = {"error": f"{type(e).__name__}: {e.args[0]}"}
        code = 500

    return make_response(jsonify(body), code)

  # rename the function to avoid this error:
  # https://stackoverflow.com/questions/17256602
  check_json.__name__ = func.__name__
  return check_json
