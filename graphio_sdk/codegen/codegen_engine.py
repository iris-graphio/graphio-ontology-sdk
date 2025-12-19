"""
Codegen Engine - Schema를 Python class 코드로 변환
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CodegenEngine:
    """
    Schema를 Python class 코드로 변환하는 엔진
    """

    def __init__(self):
        pass

    def generate_object_type_class(self, schema: Dict[str, Any]) -> str:
        """
        ObjectType Schema로부터 Python class 코드 생성
        
        Args:
            schema: ObjectType Schema
            
        Returns:
            Python class 코드 문자열
        """
        class_name = schema["name"]
        object_type_id = schema["id"]
        properties = schema.get("properties", [])

        # Property 타입 힌트 생성
        property_type_hints = []
        property_assignments = []
        
        for prop in properties:
            prop_name = prop["name"]
            prop_type = self._python_type_from_ontology_type(prop["type"])
            nullable = prop.get("nullable", True)
            
            # 타입 힌트
            if nullable:
                type_hint = f"Optional[{prop_type}]"
            else:
                type_hint = prop_type
            
            property_type_hints.append(f"    {prop_name}: {type_hint} = None")
            
            # __init__에서 할당
            property_assignments.append(f"        self.{prop_name} = {prop_name}")

        # Property 타입 힌트 문자열
        property_hints_str = "\n".join(property_type_hints) if property_type_hints else "    pass"

        # Property 할당 문자열
        property_assign_str = "\n".join(property_assignments) if property_assignments else "        pass"

        # Class 코드 생성
        code = f'''"""
자동 생성된 ObjectType 클래스: {class_name}

이 파일은 codegen에 의해 자동 생성되었습니다. 수동으로 수정하지 마세요.
"""

from typing import Optional, Dict, Any
from ..base import TypedObject


class {class_name}(TypedObject):
    """
    {class_name} ObjectType
    
    ObjectType ID: {object_type_id}
    """
    
    _object_type_id = "{object_type_id}"
    _object_type_name = "{class_name}"

    def __init__(
        self,
        element_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
{property_hints_str}
    ):
        """
        {class_name} 객체 생성
        
        Args:
            element_id: Element ID (기존 객체인 경우)
            properties: 속성 딕셔너리
{self._generate_property_docstring(properties)}
        """
        # properties 딕셔너리 초기화
        props = properties or {{}}
        
        # kwargs에서 속성 추출하여 props에 추가
        kwargs_props = {{
{self._generate_kwargs_extraction(properties)}
        }}
        props.update({{k: v for k, v in kwargs_props.items() if v is not None}})
        
        # TypedObject 초기화
        super().__init__(
            element_id=element_id,
            object_type_id=self._object_type_id,
            object_type_name=self._object_type_name,
            properties=props
        )
        
        # 인스턴스 속성으로도 설정 (타입 힌트 지원)
        for prop_name, prop_value in props.items():
            setattr(self, prop_name, prop_value)
'''

        return code

    def generate_link_type_class(self, schema: Dict[str, Any]) -> str:
        """
        LinkType Schema로부터 Python class 코드 생성
        
        Args:
            schema: LinkType Schema
            
        Returns:
            Python class 코드 문자열
        """
        class_name = schema["name"]
        link_type_id = schema["id"]
        properties = schema.get("properties", [])

        # Property 타입 힌트 생성
        property_type_hints = []
        property_assignments = []
        
        for prop in properties:
            prop_name = prop["name"]
            prop_type = self._python_type_from_ontology_type(prop["type"])
            nullable = prop.get("nullable", True)
            
            if nullable:
                type_hint = f"Optional[{prop_type}]"
            else:
                type_hint = prop_type
            
            property_type_hints.append(f"    {prop_name}: {type_hint} = None")
            property_assignments.append(f"        self.{prop_name} = {prop_name}")

        property_hints_str = "\n".join(property_type_hints) if property_type_hints else "    pass"
        property_assign_str = "\n".join(property_assignments) if property_assignments else "        pass"

        code = f'''"""
자동 생성된 LinkType 클래스: {class_name}

이 파일은 codegen에 의해 자동 생성되었습니다. 수동으로 수정하지 마세요.
"""

from typing import Optional, Dict, Any
from ..base import TypedLink


class {class_name}(TypedLink):
    """
    {class_name} LinkType
    
    LinkType ID: {link_type_id}
    """
    
    _link_type_id = "{link_type_id}"
    _link_type_name = "{class_name}"

    def __init__(
        self,
        element_id: Optional[str] = None,
        source_element_id: Optional[str] = None,
        target_element_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
{property_hints_str}
    ):
        """
        {class_name} 링크 생성
        
        Args:
            element_id: Element ID (기존 링크인 경우)
            source_element_id: Source Element ID
            target_element_id: Target Element ID
            properties: 속성 딕셔너리
{self._generate_property_docstring(properties)}
        """
        props = properties or {{}}
        
        # kwargs에서 속성 추출하여 props에 추가
        kwargs_props = {{
{self._generate_kwargs_extraction(properties)}
        }}
        props.update({{k: v for k, v in kwargs_props.items() if v is not None}})
        
        super().__init__(
            element_id=element_id,
            link_type_id=self._link_type_id,
            link_type_name=self._link_type_name,
            source_element_id=source_element_id,
            target_element_id=target_element_id,
            properties=props
        )
        
        # 인스턴스 속성으로도 설정
        for prop_name, prop_value in props.items():
            setattr(self, prop_name, prop_value)
'''

        return code

    def _python_type_from_ontology_type(self, ontology_type: str) -> str:
        """Ontology 타입을 Python 타입으로 변환"""
        type_mapping = {
            "STRING": "str",
            "INTEGER": "int",
            "DOUBLE": "float",
            "BOOLEAN": "bool",
            "DATE": "str",  # ISO format string
            "TIMESTAMP": "str",  # ISO format string
            "JSON": "Dict[str, Any]",
        }
        return type_mapping.get(ontology_type.upper(), "Any")

    def _generate_property_docstring(self, properties: list) -> str:
        """Property docstring 생성"""
        if not properties:
            return ""
        
        lines = []
        for prop in properties:
            prop_name = prop["name"]
            prop_type = prop.get("type", "UNKNOWN")
            nullable = prop.get("nullable", True)
            nullable_str = " (nullable)" if nullable else " (required)"
            lines.append(f"            {prop_name}: {prop_type}{nullable_str}")
        
        return "\n".join(lines)

    def _generate_kwargs_extraction(self, properties: list) -> str:
        """kwargs에서 속성 추출 코드 생성"""
        if not properties:
            return "        }"
        
        lines = []
        for prop in properties:
            prop_name = prop["name"]
            lines.append(f'            "{prop_name}": {prop_name},')
        
        return "\n".join(lines)

