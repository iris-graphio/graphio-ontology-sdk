"""
객체 생성 및 편집 관련 클래스
"""

from typing import List, Dict, Any, Optional, Union


class EditableObject:
    """편집 가능한 객체"""

    def __init__(
            self,
            object_type_id: str,
            properties: Dict[str, Any],
            element_id: Optional[str] = None
    ):
        self.object_type_id = object_type_id
        self.element_id = element_id
        self._properties = properties if properties else {}

    def __setattr__(self, name: str, value: Any):
        if name.startswith('_') or name in ('object_type_id', 'element_id'):
            super().__setattr__(name, value)
        else:
            # 속성 설정은 _properties에 저장
            self._properties[name] = value

    def __getattr__(self, name: str):
        if name in self._properties:
            return self._properties[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def get_properties(self) -> Dict[str, Any]:
        """속성 딕셔너리 반환"""
        return self._properties.copy()

    def to_message(self) -> Dict[str, Any]:
        """ObjectMessage 형식으로 변환"""
        message = {
            "objectTypeId": self.object_type_id,
            "properties": self._properties
        }
        if self.element_id:
            message["elementId"] = self.element_id
        return message


class ObjectTypeEditor:
    """특정 ObjectType에 대한 편집 헬퍼"""

    def __init__(self, object_type_class: type, edits_builder: 'OntologyEditsBuilder'):
        self.object_type_class = object_type_class
        self.edits_builder = edits_builder

    def create(
            self,
            new_object: Union[Dict[str, Any], EditableObject],
            **kwargs
    ) -> EditableObject:
        """새 객체 생성"""
        if isinstance(new_object, dict):
            element_id = new_object.get("elementId")
            properties = new_object.get("properties", {})
            # properties 키가 없으면 전체 딕셔너리를 properties로 사용
            # (기존 호환성)
            if ("properties" not in new_object and
                    "elementId" not in new_object):
                properties = new_object
            properties.update(kwargs)
        elif isinstance(new_object, EditableObject):
            element_id = new_object.element_id
            properties = new_object.get_properties()
        else:
            raise ValueError("new_object는 dict 또는 EditableObject여야 합니다.")

        obj = EditableObject(
            object_type_id=self.object_type_class._object_type_id,
            properties=properties,
            element_id=element_id
        )

        self.edits_builder._add_create(obj)
        return obj

    def edit(self, existing_object: Union[Dict[str, Any], EditableObject]) -> EditableObject:
        """기존 객체 편집"""
        if isinstance(existing_object, dict):
            element_id = existing_object.get("elementId")
            properties = existing_object.get("properties", {})
        elif isinstance(existing_object, EditableObject):
            element_id = existing_object.element_id
            properties = existing_object.get_properties()
        else:
            raise ValueError("existing_object는 dict 또는 EditableObject여야 합니다.")

        if not element_id:
            raise ValueError("편집하려면 elementId가 필요합니다.")

        obj = EditableObject(
            object_type_id=self.object_type_class._object_type_id,
            properties=properties,
            element_id=element_id
        )

        self.edits_builder._add_update(obj)
        return obj


class ObjectsAccessor:
    """objects.XXX 형태로 접근하기 위한 헬퍼"""

    def __init__(self, edits_builder: 'OntologyEditsBuilder', object_types: Dict[str, type]):
        self._edits_builder = edits_builder
        self._object_types = object_types
        self._dynamic_attributes: Dict[str, type] = {}  # 동적으로 할당된 ObjectType 클래스들

    def __getattr__(self, name: str) -> ObjectTypeEditor:
        # 1. 먼저 이름으로 등록된 ObjectType 찾기
        if name in self._object_types:
            return ObjectTypeEditor(self._object_types[name], self._edits_builder)
        
        # 2. 동적으로 할당된 ObjectType 클래스 찾기
        if name in self._dynamic_attributes:
            return ObjectTypeEditor(self._dynamic_attributes[name], self._edits_builder)
        
        raise AttributeError(f"ObjectType '{name}'을 찾을 수 없습니다.")

    def __setattr__(self, name: str, value: Any):
        # 내부 속성은 일반적으로 설정
        if name.startswith('_') or name in ('_edits_builder', '_object_types', '_dynamic_attributes'):
            super().__setattr__(name, value)
            return
        
        # ObjectType 클래스를 할당하는 경우
        from .object_type import ObjectTypeBase
        if isinstance(value, type) and issubclass(value, ObjectTypeBase):
            if not hasattr(self, '_dynamic_attributes'):
                self._dynamic_attributes = {}
            self._dynamic_attributes[name] = value
            return
        
        # 일반 속성 설정
        super().__setattr__(name, value)

    def __call__(self, object_type_class: type) -> ObjectTypeEditor:
        """
        ObjectType 클래스를 직접 전달받아 ObjectTypeEditor 반환
        
        Args:
            object_type_class: ObjectType 클래스 (예: unit_ot)
            
        Returns:
            ObjectTypeEditor 인스턴스
            
        Example:
            unit_ot = client.ontology.get_object_type("유닛")
            edits.objects(unit_ot).edit({...})
        """
        # ObjectTypeBase를 상속받은 클래스인지 확인
        from .object_type import ObjectTypeBase
        if not isinstance(object_type_class, type) or not issubclass(object_type_class, ObjectTypeBase):
            raise ValueError(f"ObjectType 클래스가 아닙니다: {object_type_class}")
        
        # _object_type_id가 있는지 확인
        if not hasattr(object_type_class, '_object_type_id') or not object_type_class._object_type_id:
            raise ValueError(f"ObjectType 클래스에 _object_type_id가 없습니다: {object_type_class}")
        
        return ObjectTypeEditor(object_type_class, self._edits_builder)


class OntologyEditsBuilder:
    """Ontology 편집 빌더"""

    def __init__(self, client, object_types: Dict[str, type]):
        self.client = client
        self._creates: List[EditableObject] = []
        self._updates: List[EditableObject] = []
        self.objects = ObjectsAccessor(self, object_types)

    def _add_create(self, obj: EditableObject):
        """생성 목록에 추가"""
        self._creates.append(obj)

    def _add_update(self, obj: EditableObject):
        """업데이트 목록에 추가"""
        self._updates.append(obj)

    def get_edits(self) -> List[Dict[str, Any]]:
        """모든 편집 내용을 리스트로 반환 (커밋하지 않음)"""
        all_edits = []
        all_edits.extend([obj.to_message() for obj in self._creates])
        all_edits.extend([obj.to_message() for obj in self._updates])
        return all_edits

    def commit(self) -> Dict[str, Any]:
        """변경사항을 서버에 커밋"""
        results = {}

        if self._creates:
            create_messages = [obj.to_message() for obj in self._creates]
            results['creates'] = self.client.ontology._execute_create(create_messages)

        if self._updates:
            update_messages = [obj.to_message() for obj in self._updates]
            results['updates'] = self.client.ontology._execute_update(update_messages)

        # 커밋 후 초기화
        self._creates.clear()
        self._updates.clear()

        return results