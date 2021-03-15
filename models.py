from __future__ import annotations
from typing import List, Type

from app import db
from datetime import datetime
import itertools


def timestamps(klass: Type[db.Model]) -> None:
  klass.created_at = db.Column(
    db.DateTime, nullable=False, default=datetime.now)
  klass.updated_at = db.Column(
    db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class PlayerRecord(db.Model):
  __tablename__ = "players"

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(255), nullable=False)


timestamps(PlayerRecord)


class Board(object):
  WIDTH: int = 3
  HEIGHT: int = 3
  SQUARES: int = WIDTH * HEIGHT
  BLANK = "-"

  @classmethod
  def from_str(cls, data: str) -> Board:
    parts = list(data)

    assert len(parts) == cls.SQUARES, \
      f"Expected board to contain {cls.SQUARES} elements, but found {len(parts)}"

    matrix = [
      parts[row * cls.WIDTH:row * cls.WIDTH + cls.WIDTH]
      for row in range(cls.HEIGHT)]

    return Board(matrix)

  def __init__(self, matrix: List[List[str]]) -> None:
    self.matrix = matrix

  def __repr__(self) -> str:
    rows = ["| " + " | ".join(row) + " |" for row in self.matrix]
    border = "+" + "+".join("---" for _ in range(self.WIDTH)) + "+"
    rows = list(itertools.chain(*zip(rows, [border for _ in range(len(rows))])))
    return "\n".join([border, *rows])
