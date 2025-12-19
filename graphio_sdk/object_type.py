"""
ObjectType 기본 클래스
"""

from typing import List, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .query import ObjectSetQuery
    from .operators import Condition, LogicalCondition


class ObjectTypeBase:
    """
    오브젝트 타입 베이스 클래스

    사용자는 이 클래스를 상속받아 커스텀 ObjectType을 정의합니다.
    """
    _object_type_id: str = None
    _object_type_name: str = None
    _client = None
    _properties: List[str] = []

    def __init__(self):
        raise NotImplementedError(
            "ObjectType은 직접 인스턴스화할 수 없습니다. "
            "where() 또는 create()를 사용하세요."
        )

    @classmethod
    def _set_client(cls, client):
        """클라이언트 설정"""
        cls._client = client

    @classmethod
    def where(cls, *conditions: Union['Condition', 'LogicalCondition']) -> 'ObjectSetQuery':
        """쿼리 시작 - where 조건으로"""
        from .query import ObjectSetQuery
        return ObjectSetQuery(cls, cls._client).where(*conditions)

    @classmethod
    def select(cls, *fields: str) -> 'ObjectSetQuery':
        """쿼리 시작 - select로"""
        from .query import ObjectSetQuery
        return ObjectSetQuery(cls, cls._client).select(*fields)

    @classmethod
    def all(cls) -> 'ObjectSetQuery':
        """모든 객체 조회"""
        from .query import ObjectSetQuery
        return ObjectSetQuery(cls, cls._client)