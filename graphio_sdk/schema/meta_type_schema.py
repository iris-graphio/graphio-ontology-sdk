"""
MetaType API 응답 처리용 Pydantic 모델

사용 예:
    from graphio_sdk import GraphIOClient
    from graphio_sdk.dataclass import MetaTypeDto, TagDto

    client = GraphIOClient()
    raw_list = client.meta_type.meta_type_manage.list()
    for item in raw_list:
        meta = MetaTypeDto.model_validate(item)  # 또는 MetaTypeDto.from_dict(item)
        print(meta.name, meta.id)
"""
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


def _to_camel(name: str) -> str:
    """snake_case -> camelCase (API JSON 키 매핑용)"""
    parts = name.split("_")
    return parts[0].lower() + "".join(p.capitalize() for p in parts[1:])


# 공통 설정: camelCase alias 허용, 필드명으로도 입력 허용
_common_config = ConfigDict(populate_by_name=True, extra="ignore")


# ---------- Enums (Java enum 대응) ----------


class MetaTypeKind(str, Enum):
    """메타타입 종류 (Java MetaTypeKind 대응)"""
    TABLE = "TABLE"
    VIEW = "VIEW"
    FILE = "FILE"
    UNKNOWN = "UNKNOWN"


class ConnectionStatus(str, Enum):
    """연결 상태 (Java ConnectionStatus 대응)"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class PropertyDataType(str, Enum):
    """속성 데이터 타입 (Java PropertyDataType 대응)"""
    STRING = "STRING"
    INTEGER = "INTEGER"
    LONG = "LONG"
    DOUBLE = "DOUBLE"
    BOOLEAN = "BOOLEAN"
    TIMESTAMP = "TIMESTAMP"
    UUID = "UUID"
    JSON = "JSON"
    UNKNOWN = "UNKNOWN"


class ConnectType(str, Enum):
    """리소스 연결 타입 (Java ConnectType 대응)"""
    FILE = "FILE"
    TABLE = "TABLE"
    DATABASE = "DATABASE"
    UNKNOWN = "UNKNOWN"


# ---------- TagDto ----------


class TagDto(BaseModel):
    """태그 DTO (Java TagDto 대응)"""
    model_config = _common_config
    id: str = ""
    name: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "TagDto":
        return cls.model_validate(d)


# ---------- RawData DTOs ----------


class MappedRawDataResponseDto(BaseModel):
    """매핑된 Raw Data 응답 DTO (Java MappedRawDataResponseDto 대응)"""
    model_config = ConfigDict(populate_by_name=True, extra="ignore", alias_generator=_to_camel)
    id: str = ""
    owner_id: str = ""
    name: str = ""
    data_type: str = ""
    display_path: Any = None

    @classmethod
    def from_dict(cls, data: dict) -> "MappedRawDataResponseDto":
        return cls.model_validate(data)


class RawDataMetaResponseDto(BaseModel):
    """Raw Data 메타 응답 DTO (Java RawDataMetaResponseDto 대응)"""
    model_config = _common_config
    raw: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "RawDataMetaResponseDto":
        return cls(raw=dict(data) if data else {})


class RawDataInfoResponseDto(BaseModel):
    """Raw Data 정보 응답 DTO (Java RawDataInfoResponseDto 대응)"""
    model_config = ConfigDict(populate_by_name=True, extra="ignore", alias_generator=_to_camel)
    id: Optional[str] = None
    resource_type: Optional[str] = Field(None, alias="resourceType")
    description: Optional[str] = None
    connection_name: Optional[str] = Field(None, alias="connectionName")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    owner_id: Optional[str] = Field(None, alias="ownerId")
    file_name: Optional[str] = Field(None, alias="fileName")
    file_extension: Optional[str] = Field(None, alias="fileExtension")
    tags: List[str] = Field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "RawDataInfoResponseDto":
        return cls.model_validate(d)


class ObjectTypeMetaResponseDto(BaseModel):
    """Object 타입 메타 응답 DTO (Java ObjectTypeMetaResponseDto 대응)"""
    model_config = _common_config
    raw: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict) -> "ObjectTypeMetaResponseDto":
        return cls(raw=dict(d) if d else {})


# ---------- MetaTypePropertyResponseDto ----------


class MetaTypePropertyResponseDto(BaseModel):
    """메타타입 속성 응답 DTO (Java MetaTypePropertyResponseDto 대응)"""
    model_config = ConfigDict(populate_by_name=True, extra="ignore", alias_generator=_to_camel)
    meta_type_id: Optional[str] = Field(None, alias="metaTypeId")
    id: Optional[str] = None
    name: Optional[str] = None
    data_type: Optional[str] = Field(None, alias="dataType")
    description: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> "MetaTypePropertyResponseDto":
        return cls.model_validate(d)


# ---------- Nested DTOs (READ_ONLY 등) ----------


class MetaTypePropertyDto(BaseModel):
    """
    메타타입 속성 DTO (Java MetaTypePropertyDto 대응)
    - id, createdAt, updatedAt(READ_ONLY), metaTypeId, ontologyId,
      dataType(PropertyDataType), metaTypePropertyName, rawDataPropertyName, description
    """
    model_config = ConfigDict(populate_by_name=True, extra="ignore", alias_generator=_to_camel)
    id: Optional[str] = None
    created_at: Optional[str] = Field(None, alias="createdAt")  # Timestamp
    updated_at: Optional[str] = Field(None, alias="updatedAt")  # Timestamp
    meta_type_id: Optional[str] = Field(None, alias="metaTypeId")
    ontology_id: Optional[str] = Field(None, alias="ontologyId")
    data_type: Optional[str] = Field(None, alias="dataType")  # PropertyDataType enum 값
    meta_type_property_name: Optional[str] = Field(None, alias="metaTypePropertyName")
    raw_data_property_name: Optional[str] = Field(None, alias="rawDataPropertyName")
    description: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> "MetaTypePropertyDto":
        return cls.model_validate(d)


class MetaMappingDto(BaseModel):
    """메타 매핑 DTO (Java MetaMappingDto 대응)"""
    model_config = _common_config
    raw: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict) -> "MetaMappingDto":
        return cls(raw=dict(d) if d else {})


class ObjectMappingDto(BaseModel):
    """오브젝트 매핑 DTO (Java ObjectMappingDto 대응)"""
    model_config = _common_config
    raw: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict) -> "ObjectMappingDto":
        return cls(raw=dict(d) if d else {})


class MetaTypeTagMappingDto(BaseModel):
    """메타타입-태그 매핑 DTO (Java MetaTypeTagMappingDto 대응)"""
    model_config = _common_config
    raw: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict) -> "MetaTypeTagMappingDto":
        return cls(raw=dict(d) if d else {})


# ---------- MetaTypeInspectDto ----------


class MetaTypeInspectDto(BaseModel):
    """메타타입 상세 조회(inspect) 응답 DTO (Java MetaTypeInspectDto 대응)"""
    model_config = ConfigDict(populate_by_name=True, extra="ignore", alias_generator=_to_camel)
    id: Optional[str] = None
    ontology_id: Optional[str] = Field(None, alias="ontologyId")
    owner_id: Optional[str] = Field(None, alias="ownerId")
    name: Optional[str] = None
    description: Optional[str] = None
    properties: Optional[List[MetaTypePropertyResponseDto]] = None
    meta_type_table_name: Optional[str] = Field(None, alias="metaTypeTableName")
    meta_type_schema_name: Optional[str] = Field(None, alias="metaTypeSchemaName")
    meta_type_kind: Optional[str] = Field(None, alias="metaTypeKind")
    connection_instance_id: Optional[str] = Field(None, alias="connectionInstanceId")
    tag_ids: List[str] = Field(default_factory=list, alias="tagIds")
    model_id: Optional[str] = Field(None, alias="modelId")
    created_at: Optional[str] = Field(None, alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    editable: Optional[bool] = None
    create_table: Optional[bool] = Field(None, alias="createTable")
    raw_data_meta_response_dto_list: Optional[List[RawDataMetaResponseDto]] = Field(None, alias="rawDataMetaResponseDtoList")
    object_meta_response_dto_list: Optional[List[ObjectTypeMetaResponseDto]] = Field(None, alias="objectMetaResponseDtoList")
    meta_mapping_dto_list: Optional[List[MetaMappingDto]] = Field(None, alias="metaMappingDtoList")
    object_mapping_dto_list: Optional[List[ObjectMappingDto]] = Field(None, alias="objectMappingDtoList")

    @classmethod
    def from_dict(cls, d: dict) -> "MetaTypeInspectDto":
        # Java 쪽 MetaMappingDtoList(대문자 M) 키 지원
        if isinstance(d, dict) and "MetaMappingDtoList" in d and "metaMappingDtoList" not in d:
            d = {**d, "metaMappingDtoList": d["MetaMappingDtoList"]}
        return cls.model_validate(d)


# ---------- CheckMetaTypeNameDto ----------


class CheckMetaTypeNameDto(BaseModel):
    """메타타입 이름 중복 체크 응답 DTO (Java CheckMetaTypeNameDto 대응)"""
    model_config = _common_config
    id: Optional[str] = None
    status: Optional[bool] = None
    error: Optional[Any] = None

    @classmethod
    def from_dict(cls, d: dict) -> "CheckMetaTypeNameDto":
        return cls.model_validate(d)


# ---------- MetaTypeDto ----------


class MetaTypeDto(BaseModel):
    """메타타입 DTO (Java MetaTypeDto 대응)"""
    model_config = ConfigDict(populate_by_name=True, extra="ignore", alias_generator=_to_camel)
    id: Optional[str] = None
    ontology_id: Optional[str] = Field(None, alias="ontologyId")
    owner_id: Optional[str] = Field(None, alias="ownerId")
    name: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[str] = Field(None, alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    meta_type_schema_name: Optional[str] = Field(None, alias="metaTypeSchemaName")
    meta_type_table_name: Optional[str] = Field(None, alias="metaTypeTableName")
    connection_instance_id: Optional[str] = Field(None, alias="connectionInstanceId")
    tag_ids: List[str] = Field(default_factory=list, alias="tagIds")
    model_id: Optional[str] = Field(None, alias="modelId")
    meta_type_kind: Optional[str] = Field(None, alias="metaTypeKind")
    editable: Optional[bool] = None
    create_table: Optional[bool] = Field(None, alias="createTable")
    data_frame: Optional[List[Dict[str, Any]]] = Field(None, alias="dataFrame")
    workflow_created: bool = Field(False, alias="workflowCreated")
    status: Optional[str] = None
    properties: Optional[List[MetaTypePropertyDto]] = None
    meta_mapping_dto_list: Optional[List[MetaMappingDto]] = Field(None, alias="metaMappingDtoList")
    object_mapping_dto_list: Optional[List[ObjectMappingDto]] = Field(None, alias="objectMappingDtoList")
    meta_type_tag_mapping_dto_list: Optional[List[MetaTypeTagMappingDto]] = Field(None, alias="metaTypeTagMappingDtoList")

    @classmethod
    def from_dict(cls, d: dict) -> "MetaTypeDto":
        return cls.model_validate(d)


# ---------- Page (raw-datas 등) ----------


    @classmethod
    def from_dict(cls, d: dict) -> "PageResponseDto":
        if not isinstance(d, dict):
            raise TypeError("dict expected")
        content_raw = d.get("content", d.get("data", []))
        content = [MappedRawDataResponseDto.model_validate(i) for i in content_raw] if isinstance(content_raw, list) else []
        return cls(
            content=content,
            total_elements=d.get("totalElements"),
            total_pages=d.get("totalPages"),
            size=d.get("size"),
            number=d.get("number"),
        )
