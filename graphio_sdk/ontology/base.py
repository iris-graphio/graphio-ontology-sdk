"""
Typed Object/Link Base Classes - 생성된 클래스들이 상속할 base class
"""

from typing import Dict, Any, Optional


class TypedObject:
    """
    Typed Object Base Class
    
    Codegen으로 생성된 ObjectType 클래스들이 상속하는 base class입니다.
    """

    _object_type_id: str
    _object_type_name: str

    def __init__(
        self,
        element_id: Optional[str] = None,
        object_type_id: str = None,
        object_type_name: str = None,
        properties: Optional[Dict[str, Any]] = None
    ):
        """
        Args:
            element_id: Element ID (기존 객체인 경우)
            object_type_id: ObjectType ID
            object_type_name: ObjectType 이름
            properties: 속성 딕셔너리
        """
        self._element_id = element_id
        self._properties = properties or {}
        
        # 클래스 속성에서 가져오기
        if object_type_id:
            self._object_type_id = object_type_id
        if object_type_name:
            self._object_type_name = object_type_name

    @property
    def element_id(self) -> Optional[str]:
        """Element ID"""
        return self._element_id

    @property
    def object_type_id(self) -> str:
        """ObjectType ID"""
        return getattr(self, '_object_type_id', None)

    @property
    def object_type_name(self) -> str:
        """ObjectType 이름"""
        return getattr(self, '_object_type_name', None)

    def to_contract(self) -> Dict[str, Any]:
        """
        Service Contract 형태로 변환
        
        Returns:
            {
                "objectType": "Employee",
                "elementId": "e-1",
                "properties": {...}
            }
        """
        contract = {
            "objectType": self._object_type_name,
            "properties": self._get_all_properties()
        }
        
        if self._element_id:
            contract["elementId"] = self._element_id
        
        return contract

    def _get_all_properties(self) -> Dict[str, Any]:
        """모든 속성을 딕셔너리로 반환"""
        props = {}
        
        # _properties 딕셔너리에서 가져오기
        props.update(self._properties)
        
        # 인스턴스 속성에서 가져오기 (단, private 속성 제외)
        for key, value in self.__dict__.items():
            if not key.startswith('_') and key not in ['element_id', 'object_type_id', 'object_type_name']:
                props[key] = value
        
        return props

    def __setattr__(self, name: str, value: Any):
        """속성 설정"""
        # private 속성은 그대로 설정
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            # 일반 속성은 _properties에도 저장
            if hasattr(self, '_properties'):
                self._properties[name] = value
            super().__setattr__(name, value)

    def __getattr__(self, name: str):
        """속성 가져오기"""
        # _properties에서 찾기
        if hasattr(self, '_properties') and name in self._properties:
            return self._properties[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


class TypedLink:
    """
    Typed Link Base Class
    
    Codegen으로 생성된 LinkType 클래스들이 상속하는 base class입니다.
    """

    _link_type_id: str
    _link_type_name: str

    def __init__(
        self,
        element_id: Optional[str] = None,
        link_type_id: str = None,
        link_type_name: str = None,
        source_element_id: Optional[str] = None,
        target_element_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ):
        """
        Args:
            element_id: Element ID (기존 링크인 경우)
            link_type_id: LinkType ID
            link_type_name: LinkType 이름
            source_element_id: Source Element ID
            target_element_id: Target Element ID
            properties: 속성 딕셔너리
        """
        self._element_id = element_id
        self._source_element_id = source_element_id
        self._target_element_id = target_element_id
        self._properties = properties or {}
        
        if link_type_id:
            self._link_type_id = link_type_id
        if link_type_name:
            self._link_type_name = link_type_name

    @property
    def element_id(self) -> Optional[str]:
        """Element ID"""
        return self._element_id

    @property
    def source_element_id(self) -> Optional[str]:
        """Source Element ID"""
        return self._source_element_id

    @property
    def target_element_id(self) -> Optional[str]:
        """Target Element ID"""
        return self._target_element_id

    @property
    def link_type_id(self) -> str:
        """LinkType ID"""
        return getattr(self, '_link_type_id', None)

    @property
    def link_type_name(self) -> str:
        """LinkType 이름"""
        return getattr(self, '_link_type_name', None)

    def to_contract(self) -> Dict[str, Any]:
        """
        Service Contract 형태로 변환
        
        Returns:
            {
                "linkType": "WorksFor",
                "elementId": "l-1",
                "sourceElementId": "e-1",
                "targetElementId": "e-2",
                "properties": {...}
            }
        """
        contract = {
            "linkType": self._link_type_name,
            "properties": self._get_all_properties()
        }
        
        if self._element_id:
            contract["elementId"] = self._element_id
        if self._source_element_id:
            contract["sourceElementId"] = self._source_element_id
        if self._target_element_id:
            contract["targetElementId"] = self._target_element_id
        
        return contract

    def _get_all_properties(self) -> Dict[str, Any]:
        """모든 속성을 딕셔너리로 반환"""
        props = {}
        props.update(self._properties)
        
        for key, value in self.__dict__.items():
            if not key.startswith('_') and key not in ['element_id', 'link_type_id', 'link_type_name', 
                                                       'source_element_id', 'target_element_id']:
                props[key] = value
        
        return props

    def __setattr__(self, name: str, value: Any):
        """속성 설정"""
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            if hasattr(self, '_properties'):
                self._properties[name] = value
            super().__setattr__(name, value)

    def __getattr__(self, name: str):
        """속성 가져오기"""
        if hasattr(self, '_properties') and name in self._properties:
            return self._properties[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

