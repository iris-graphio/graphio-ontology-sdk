"""
쿼리 연산자와 조건 클래스
"""

from enum import Enum
from typing import Any, List, Union


class QueryOp(Enum):
    """쿼리 연산자"""
    EQ = "eq"      # equal
    NE = "ne"      # not equal
    GT = "gt"      # greater than
    GTE = "gte"    # greater than or equal
    LT = "lt"      # less than
    LTE = "lte"    # less than or equal
    LIKE = "like"  # SQL LIKE
    IN = "in"      # IN
    IS_NULL = "is_null"      # IS NULL
    IS_NOT_NULL = "is_not_null"  # IS NOT NULL


class Condition:
    """단일 조건을 나타내는 클래스"""

    def __init__(self, field: str, op: QueryOp, value: Any = None):
        self.field = field
        self.op = op
        self.value = value

    def to_dict(self) -> dict:
        """조건을 딕셔너리로 변환"""
        result = {
            "field": self.field,
            "op": self.op.value
        }
        if self.value is not None:
            result["value"] = self.value
        return result


class LogicalCondition:
    """AND/OR 논리 조건"""

    def __init__(self, operator: str, conditions: List[Union['Condition', 'LogicalCondition']]):
        self.operator = operator  # "and" or "or"
        self.conditions = conditions

    def to_dict(self) -> dict:
        """논리 조건을 딕셔너리로 변환"""
        return {
            self.operator: [
                cond.to_dict() for cond in self.conditions
            ]
        }


class PropertyDescriptor:
    """속성 디스크립터 - 쿼리 조건 생성용"""

    def __init__(self, field_name: str):
        self.field_name = field_name

    def __eq__(self, value) -> Condition:
        return Condition(self.field_name, QueryOp.EQ, value)

    def __ne__(self, value) -> Condition:
        return Condition(self.field_name, QueryOp.NE, value)

    def __gt__(self, value) -> Condition:
        return Condition(self.field_name, QueryOp.GT, value)

    def __ge__(self, value) -> Condition:
        return Condition(self.field_name, QueryOp.GTE, value)

    def __lt__(self, value) -> Condition:
        return Condition(self.field_name, QueryOp.LT, value)

    def __le__(self, value) -> Condition:
        return Condition(self.field_name, QueryOp.LTE, value)

    def like(self, pattern: str) -> Condition:
        """LIKE 연산자"""
        return Condition(self.field_name, QueryOp.LIKE, pattern)

    def is_in(self, values: List[Any]) -> Condition:
        """IN 연산자"""
        return Condition(self.field_name, QueryOp.IN, values)

    def is_null(self) -> Condition:
        """IS NULL 체크"""
        return Condition(self.field_name, QueryOp.IS_NULL)

    def is_not_null(self) -> Condition:
        """IS NOT NULL 체크"""
        return Condition(self.field_name, QueryOp.IS_NOT_NULL)