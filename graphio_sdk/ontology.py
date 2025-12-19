"""
Ontology 네임스페이스 및 ObjectType 관리 (Lazy Loading Only)
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
import threading

from .object_type import ObjectTypeBase
from .operators import PropertyDescriptor
from .edits import OntologyEditsBuilder

if TYPE_CHECKING:
    from .client import GraphioClient


class OntologyNamespace:
    """ontology 네임스페이스 - Lazy Loading 전용"""

    def __init__(self, client: 'GraphioClient'):
        self.client = client
        self._object_types: Dict[str, type] = {}
        self._object_type_id_to_name: Dict[str, str] = {}
        self._cache_lock = threading.Lock()  # 스레드 안전성

    def register_object_type(
            self,
            name: str,
            object_type_id: str,
            properties: Optional[List[str]] = None
    ) -> type:
        """
        ObjectType 수동 등록

        Args:
            name: ObjectType 이름 (예: "Employee", "Ticket")
            object_type_id: ObjectType UUID
            properties: 속성 이름 리스트 (선택적)

        Returns:
            생성된 ObjectType 클래스
        """
        with self._cache_lock:
            # 이미 등록된 경우 기존 클래스 반환
            if name in self._object_types:
                return self._object_types[name]

            # 동적으로 클래스 생성
            cls = type(name, (ObjectTypeBase,), {
                "_object_type_id": object_type_id,
                "_object_type_name": name,
                "_client": self.client,
                "_properties": properties or []
            })

            # 속성 디스크립터 동적 생성
            if properties:
                for prop_name in properties:
                    setattr(cls, prop_name, PropertyDescriptor(prop_name))

            self._object_types[name] = cls
            self._object_type_id_to_name[object_type_id] = name

            # objects 네임스페이스에 등록
            setattr(self.objects, name, cls)

            return cls

    def add_property(self, object_type_name: str, property_name: str):
        """ObjectType에 속성 추가"""
        if object_type_name not in self._object_types:
            raise ValueError(f"ObjectType '{object_type_name}'이 등록되지 않았습니다.")

        cls = self._object_types[object_type_name]
        setattr(cls, property_name, PropertyDescriptor(property_name))
        cls._properties.append(property_name)

    def load_object_type(
            self,
            object_type_id: Optional[str] = None,
            name: Optional[str] = None
    ) -> type:
        """
        특정 ObjectType을 서버에서 가져와 등록

        Args:
            object_type_id: ObjectType UUID (id 또는 name 중 하나 필수)
            name: ObjectType 이름 (id 또는 name 중 하나 필수)

        Returns:
            등록된 ObjectType 클래스
        """
        # name으로 이미 로드된 경우
        if name and name in self._object_types:
            return self._object_types[name]

        # id로 이미 로드된 경우
        if object_type_id and object_type_id in self._object_type_id_to_name:
            cached_name = self._object_type_id_to_name[object_type_id]
            return self._object_types[cached_name]

        # 서버에서 로드
        if object_type_id:
            ot_data = self.client._fetch_object_type_by_id(object_type_id)
        elif name:
            # name으로 검색
            results = self.client._fetch_object_types(name=name)
            if not results:
                raise ValueError(f"ObjectType '{name}'을 찾을 수 없습니다.")
            ot_data = results[0]  # 첫 번째 결과 사용
        else:
            raise ValueError("object_type_id 또는 name 중 하나는 필수입니다.")

        object_type_id = ot_data.get("id")
        name = ot_data.get("name")

        if not object_type_id or not name:
            raise ValueError(f"유효하지 않은 ObjectType 데이터: {ot_data}")

        # Properties 가져오기
        properties = self.client._fetch_object_type_properties(object_type_id)
        property_names = [prop["name"] for prop in properties]

        # ObjectType 등록
        return self.register_object_type(name, object_type_id, property_names)

    def get_object_type(self, name: str) -> Optional[type]:
        """
        ObjectType 클래스 가져오기 (Lazy Loading)

        캐시에 없으면 자동으로 서버에서 로드합니다.

        Args:
            name: ObjectType 이름

        Returns:
            ObjectType 클래스 또는 None (로드 실패 시)
        """
        # 캐시에서 찾기
        if name in self._object_types:
            return self._object_types[name]

        # 자동 로드
        try:
            return self.load_object_type(name=name)
        except Exception:
            # 로드 실패 시 None 반환
            return None

    def list_object_types(self) -> List[str]:
        """
        캐시된 ObjectType 이름 목록

        Returns:
            ObjectType 이름 리스트
        """
        return list(self._object_types.keys())

    def clear_cache(self):
        """캐시된 ObjectType 모두 제거"""
        with self._cache_lock:
            self._object_types.clear()
            self._object_type_id_to_name.clear()
            self._objects_namespace = type('ObjectsNamespace', (), {})()

    @property
    def objects(self):
        """objects 네임스페이스 - 동적 속성 접근용"""
        if not hasattr(self, '_objects_namespace'):
            self._objects_namespace = type('ObjectsNamespace', (), {})()
        return self._objects_namespace

    def edits(self) -> OntologyEditsBuilder:
        """편집 세션 시작"""
        return OntologyEditsBuilder(self.client, self._object_types)
