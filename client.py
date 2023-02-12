from __future__ import annotations
from typing import Any, Dict, Union

from http.client import HTTPConnection, HTTPSConnection, HTTPResponse
from urllib.parse import urlencode, urlparse

import json
import time


class HttpError(Exception):
  pass


class ClientError(HttpError):
  def __init__(self, message: str, response: ClientResponse) -> None:
    super().__init__(message)
    self.response = response


class ServerError(HttpError):
  pass


class NotFoundError(ClientError):
  pass


class BadRequestError(ClientError):
  pass


class ClientResponse(object):
  def __init__(self, body: Dict[str, Any], headers: Dict[str, str], status_code: int) -> None:
    self.body = body
    self.headers = headers
    self.status_code = status_code


class JsonHttpClient(object):
  DEFAULT_PORT = 80

  _conn: Union[HTTPConnection, HTTPSConnection]

  def __init__(self, url: str) -> None:
    uri = urlparse(url)
    host, port_str = uri.netloc.split(":")
    port = int(port_str or self.DEFAULT_PORT)

    if uri.scheme == "https":
      self._conn = HTTPSConnection(host, port)
    else:
      self._conn = HTTPConnection(host, port)

  def get(self, path: str, *, params: Dict[str, str] = {},
          headers: Dict[str, str] = {}) -> ClientResponse:
    path = self._compose_path(path, params)
    headers = self._add_default_headers(headers)
    self._conn.request("GET", path, headers=headers)
    response = self._conn.getresponse()
    body = json.loads(response.read())
    return ClientResponse(body, dict(response.headers), response.status)

  def post(self, path: str, *, body: Dict[str, Any],
           params: Dict[str, str] = {}, headers: Dict[str, str] = {}) -> ClientResponse:
    path = self._compose_path(path, params)
    headers = self._add_default_headers(headers)
    self._conn.request("POST", path, body=json.dumps(body), headers=headers)
    response = self._conn.getresponse()
    body = json.loads(response.read())
    return ClientResponse(body, dict(response.headers), response.status)

  def _compose_path(self, path: str, params: Dict[str, str]) -> str:
    query = urlencode(params)
    path_with_query = path
    if query:
      path_with_query += f"?{query}"
    return path_with_query

  def _add_default_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
    return {**headers, "Content-Type": "application/json"}


class Client(object):
  def __init__(self, url: str) -> None:
    self._client = JsonHttpClient(url)

  def register_player(self, username: str) -> ClientResponse:
    response = self._client.post(f"/players/{username}", body={})
    self._potentially_raise_error(response)
    return response

  def get_player(self, username: str) -> ClientResponse:
    response = self._client.get(f"/players/{username}")
    self._potentially_raise_error(response)
    return response

  def create_game(self, challenger: str, opponent: str) -> ClientResponse:
    response = self._client.post("/games", body={"challenger": challenger, "opponent": opponent})
    self._potentially_raise_error(response)
    return response

  def get_game(self, game_id: int) -> ClientResponse:
    response = self._client.get(f"/games/{game_id}")
    self._potentially_raise_error(response)
    return response

  def move(self, game_id: int, username: str, row: int, col: int) -> ClientResponse:
    params = {"username": username, "row": row, "col": col}
    response = self._client.post(f"/games/{game_id}/moves", body=params)
    self._potentially_raise_error(response)
    return response

  def _potentially_raise_error(self, response: ClientResponse) -> None:
    if "error" in response.body:
      error_message = response.body["error"]
    else:
      error_message = "An unexpected error occurred"

    if response.status_code == 400:
      raise BadRequestError(error_message, response)
    elif response.status_code == 404:
      raise NotFoundError(error_message, response)
    elif response.status_code // 100 == 4:
      raise ClientError(error_message, response)
    elif response.status_code // 100 == 5:
      raise ServerError(error_message, response)
