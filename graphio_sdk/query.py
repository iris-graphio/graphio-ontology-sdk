"""
쿼리 빌더 클래스
"""

from typing import List, Optional, Dict, Any, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .operators import Condition, LogicalCondition


class ObjectSetQuery:
    """
    Object Set 쿼리 빌더

    Fluent API 스타일로 쿼리를 구성합니다.
    실제 데이터베이스에서 데이터를 조회합니다.
    """

    def __init__(self, object_type_class: type, client):
        self.object_type_class = object_type_class
        self.client = client
        self._select_fields: List[str] = []
        self._select_all = False  # '*' 선택 여부
        self._conditions: List[Union['Condition', 'LogicalCondition']] = []
        self._limit_value: Optional[int] = None

    def select(self, *fields: str) -> 'ObjectSetQuery':
        """
        조회할 필드 선택

        Args:
            *fields: 조회할 필드명들. '*'를 사용하면 모든 필드 선택
                    아무것도 입력하지 않으면 자동으로 모든 필드('*') 선택

        Returns:
            자기 자신 (메서드 체이닝용)

        Example:
            query.select("name", "age")
            query.select("*")  # 모든 필드
            query.select()  # 모든 필드 (자동으로 '*')
        """
        # 필드가 없거나 '*'이면 자동으로 모든 필드 선택
        if not fields or "*" in fields:
            self._select_all = True
            self._select_fields = []
        else:
            self._select_all = False
            self._select_fields.extend(fields)
        return self

    def where(self, *conditions: Union['Condition', 'LogicalCondition']) -> 'ObjectSetQuery':
        """
        조건 추가

        Args:
            *conditions: 조건들

        Returns:
            자기 자신 (메서드 체이닝용)
        """
        self._conditions.extend(conditions)
        return self

    def limit(self, count: int) -> 'ObjectSetQuery':
        """
        결과 개수 제한

        Args:
            count: 최대 개수

        Returns:
            자기 자신 (메서드 체이닝용)
        """
        self._limit_value = count
        return self

    def _build_where_clause(self) -> Optional[Dict[str, Any]]:
        """where 조건을 API 형식으로 변환"""
        from .operators import LogicalCondition

        if not self._conditions:
            return None

        if len(self._conditions) == 1:
            return self._conditions[0].to_dict()

        # 여러 조건은 AND로 결합
        return LogicalCondition("and", self._conditions).to_dict()

    def _get_select_fields(self) -> List[str]:
        """
        선택할 필드 리스트 반환

        Returns:
            필드 리스트. '*' 선택 시 모든 properties 반환
        """
        if self._select_all:
            # 모든 properties 반환
            if self.object_type_class._properties:
                return self.object_type_class._properties
            else:
                # properties가 없으면 빈 리스트 (서버에서 처리)
                return []
        else:
            return self._select_fields

    def execute(self) -> List[Dict[str, Any]]:
        """
        쿼리 실행 - 실제 데이터베이스에서 데이터 조회

        Returns:
            조회된 데이터 리스트

        Raises:
            ValueError: select 필드가 없을 때
            Exception: API 호출 실패 시
        """
        select_fields = self._get_select_fields()

        # '*' 선택이 아니고 필드가 없으면 에러
        if not self._select_all and not select_fields:
            raise ValueError("select() 메서드로 최소 하나의 필드를 선택해야 합니다.")

        # ObjectSetSelectDto 형식으로 구성
        select_dto = {
            "select": select_fields if select_fields else ["*"],  # 빈 리스트면 '*' 전달
            "from": self.object_type_class._object_type_id
        }

        where_clause = self._build_where_clause()
        if where_clause:
            select_dto["where"] = where_clause

        if self._limit_value:
            select_dto["limit"] = self._limit_value

        # 실제 데이터 조회
        return self.client._execute_select(select_dto)

    def count(self) -> int:
        """
        조건에 맞는 레코드 개수 반환

        Returns:
            레코드 개수
        """
        # 첫 번째 필드만 선택해서 조회 (성능 최적화)
        if not self._select_fields and self.object_type_class._properties:
            temp_field = self.object_type_class._properties[0]
        elif self._select_fields:
            temp_field = self._select_fields[0]
        else:
            raise ValueError("count()를 사용하려면 ObjectType에 최소 하나의 property가 필요합니다.")

        select_dto = {
            "select": [temp_field],
            "from": self.object_type_class._object_type_id
        }

        where_clause = self._build_where_clause()
        if where_clause:
            select_dto["where"] = where_clause

        result = self.client._execute_select(select_dto)
        return len(result)

    def first(self) -> Optional[Dict[str, Any]]:
        """
        첫 번째 레코드만 반환

        Returns:
            첫 번째 레코드 또는 None
        """
        original_limit = self._limit_value
        self._limit_value = 1

        try:
            result = self.execute()
            return result[0] if result else None
        finally:
            self._limit_value = original_limit

    def exists(self) -> bool:
        """
        조건에 맞는 레코드가 존재하는지 확인

        Returns:
            존재 여부
        """
        return self.first() is not None