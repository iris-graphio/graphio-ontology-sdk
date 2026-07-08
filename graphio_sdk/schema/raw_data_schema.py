"""
Raw Data API 응답 처리용 Pydantic 모델
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from graphio_sdk.schema.meta_type_schema import _common_config, _to_camel


class RawDataConnectionDto(BaseModel):
    """원천 데이터 연결 정보 (ip, port)"""
    model_config = _common_config
    ip: Optional[str] = None
    port: Optional[int] = None

    @classmethod
    def from_dict(cls, d: dict) -> "RawDataConnectionDto":
        return cls.model_validate(d)


class RawDataLocationDto(BaseModel):
    """테이블 원천 데이터 위치 정보"""
    model_config = ConfigDict(populate_by_name=True, extra="ignore", alias_generator=_to_camel)
    database_name: Optional[str] = Field(None, alias="databaseName")
    schema_name: Optional[str] = Field(None, alias="schemaName")
    table_name: Optional[str] = Field(None, alias="tableName")

    @classmethod
    def from_dict(cls, d: dict) -> "RawDataLocationDto":
        return cls.model_validate(d)


class RawDataSourceInfoDto(BaseModel):
    """원천 데이터 연결 정보 응답 DTO (GET /raw-data/{id}/source-info)"""
    model_config = ConfigDict(populate_by_name=True, extra="ignore", alias_generator=_to_camel)
    data_type: Optional[str] = Field(None, alias="dataType")
    connection: Optional[RawDataConnectionDto] = None
    full_path: Optional[str] = Field(None, alias="fullPath")
    bucket_name: Optional[str] = Field(None, alias="bucketName")
    file_name: Optional[str] = Field(None, alias="fileName")
    location: Optional[RawDataLocationDto] = None

    @classmethod
    def from_dict(cls, d: dict) -> "RawDataSourceInfoDto":
        return cls.model_validate(d)
