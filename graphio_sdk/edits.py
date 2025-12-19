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
            properties: Optional[Dict[str, Any]] = None,
            **kwargs
    ) -> EditableObject:
        """새 객체 생성"""
        props = properties or {}
        props.update(kwargs)

        obj = EditableObject(
            object_type_id=self.object_type_class._object_type_id,
            properties=props
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

    def __getattr__(self, name: str) -> ObjectTypeEditor:
        if name in self._object_types:
            return ObjectTypeEditor(self._object_types[name], self._edits_builder)
        raise AttributeError(f"ObjectType '{name}'을 찾을 수 없습니다.")


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
            results['creates'] = self.client._execute_create(create_messages)

        if self._updates:
            update_messages = [obj.to_message() for obj in self._updates]
            results['updates'] = self.client._execute_update(update_messages)

        # 커밋 후 초기화
        self._creates.clear()
        self._updates.clear()

        return results