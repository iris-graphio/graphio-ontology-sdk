"""
MetaType 네임스페이스 - GraphIOClient와 함께 사용
"""

from typing import Any, Dict, List, TYPE_CHECKING

from graphio_sdk.schema import (
    MetaTypeDto,
    MetaTypeInspectDto,
    MetaTypePropertyResponseDto,
    RawDataInfoResponseDto,
    TagDto,
    MappedRawDataResponseDto,
)

if TYPE_CHECKING:
    from graphio_sdk.client import GraphioClient


# ============================
# 리소스별 래퍼
# ============================
class MetaTableAPI:
    """메타타입 테이블을 조작하는 래퍼 (GraphioClient 세션 사용)"""

    def __init__(self, client: "GraphioClient"):
        self._client = client

    def all_data(self, meta_type_id: str) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "metaTypeId": meta_type_id,
        }
        url = f"{self._client.api_base}/all-data"
        response = self._client._get_session().get(
            url, params=params, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        data = result.get("data", [])
        total_count = result.get("totalSize", None)
        self._client._check_response(result, "list all-data")
        return {"data": data, "totalCount": total_count}

    def meta_type_table(self, meta_type_id: str) -> Dict[str, Any]:
        """GET /meta-type-table/{meta-type-id} : Map<String, Object>"""
        url = f"{self._client.api_base}/meta-type-table/{meta_type_id}"
        response = self._client._get_session().get(
            url, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "list meta type table")
        return result.get("data", {})

    def table_list(
            self, connection_instance_id: str, schema_name: str, meta_type_kind: str
    ) -> List[str]:
        params: Dict[str, Any] = {
            "connectionInstanceId": connection_instance_id,
            "schemaName": schema_name,
            "metaTypeKind": meta_type_kind
        }
        url = f"{self._client.api_base}/table-list"
        response = self._client._get_session().get(
            url, params=params, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "list table from schema")
        return result.get("data", [])

    def table_columns(self, connection_instance_id: str, schema_name: str, table_name: str) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {
            "connectionInstanceId": connection_instance_id,
            "schemaName": schema_name,
            "tableName": table_name
        }
        url = f"{self._client.api_base}/table-columns"
        response = self._client._get_session().get(
            url, timeout=self._client.timeout, params=params
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "table columns")
        return result.get("data", [])

    def sample_data_param(
            self, meta_type_id: str, page: int, size: int
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {
            "metaTypeId": meta_type_id,
            "page": page,
            "size": size
        }
        url = f"{self._client.api_base}/sample-data-param"
        response = self._client._get_session().get(
            url, params=params, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "sample data")
        return result.get("data", [])


class MetaManageAPI:
    """메타타입을 관리하는 래퍼"""

    def __init__(self, client: "GraphioClient"):
        self._client = client

    def list(self) -> List[MetaTypeDto]:
        """GET / : List<MetaTypeDto>"""
        url = f"{self._client.api_base}"
        response = self._client._get_session().get(
            url, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "list all-meta")
        data = result.get("data", [])
        return [MetaTypeDto.model_validate(item) for item in data] if isinstance(data, list) else []

    def duplicate_check(self, meta_type_name: str) -> Dict[str, Any]:
        url = f"{self._client.api_base}/duplicate-check/{meta_type_name}"
        response = self._client._get_session().get(
            url, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "check meta_type name duplicate")
        data = dict(result.get("data", result))
        status = result.get("status", None)
        return {"meta_type_id": data.get("id"), "status": status}

    def raw_datas(
            self, meta_type_id: str, page: int, size: int
    ) -> List[MappedRawDataResponseDto]:
        params: Dict[str, Any] = {
            "metaTypeId": meta_type_id,
            "page": page,
            "size": size
        }
        url = f"{self._client.api_base}/raw-datas"
        response = self._client._get_session().get(
            url, params=params, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        data = result.get("data", result)
        self._client._check_response(result, "list raw data by meta type id")
        return [MappedRawDataResponseDto.model_validate(item) for item in data] if isinstance(data, list) else []

    def owner(self) -> List[str]:
        """GET /owner : List<UUID>"""
        url = f"{self._client.api_base}/owner"
        response = self._client._get_session().get(
            url, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "list meta type owner")
        data = result.get("data", [])
        return [str(x) for x in data] if isinstance(data, list) else []

    def kind_list(self, meta_type_kind: str) -> List[MetaTypeInspectDto]:
        """GET /kind-list : List<MetaTypeInspectDto>"""
        params: Dict[str, Any] = {
            "metaTypeKind": meta_type_kind
        }
        url = f"{self._client.api_base}/kind-list"
        response = self._client._get_session().get(
            url, params=params, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "list meta type by meta type kind")
        data = result.get("data", [])
        return [MetaTypeInspectDto.model_validate(item) for item in data] if isinstance(data, list) else []

    def inspect_property(
            self, meta_type_id: str
    ) -> List[MetaTypePropertyResponseDto]:
        """GET /inspect/property/{meta-type-id} : List<MetaTypePropertyResponseDto>"""
        url = f"{self._client.api_base}/inspect/property/{meta_type_id}"
        response = self._client._get_session().get(
            url, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "meta type propreties")
        data = result.get("data", [])
        return [MetaTypePropertyResponseDto.model_validate(item) for item in data] if isinstance(data, list) else []

    def inspect_profiling(self, meta_type_id: str) -> List[Dict[str, Any]]:
        """GET /inspect/profiling/{meta-type-id} : List<Map<String, Object>>"""
        url = f"{self._client.api_base}/inspect/profiling/{meta_type_id}"
        response = self._client._get_session().get(
            url, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "meta type profiling")
        return result.get("data", [])

    def inspect_data_source(
            self, meta_type_id: str
    ) -> List[RawDataInfoResponseDto]:
        """GET /inspect/data-source/{meta-type-id} : List<RawDataInfoResponseDto>"""
        url = f"{self._client.api_base}/inspect/data-source/{meta_type_id}"
        response = self._client._get_session().get(
            url, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "meta type data_source")
        return [RawDataInfoResponseDto.model_validate(item) for item in result] if isinstance(result, list) else []

    def inspect_basic(self, meta_type_id: str) -> MetaTypeInspectDto:
        """GET /inspect/basic/{meta-type-id} : MetaTypeInspectDto"""
        url = f"{self._client.api_base}/inspect/basic/{meta_type_id}"
        response = self._client._get_session().get(
            url, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "meta type basic inspect")
        data = result.get("data", result)
        return MetaTypeInspectDto.model_validate(data) if isinstance(data, dict) else MetaTypeInspectDto.model_validate(
            {})


class EtcAPI:
    def __init__(self, client: "GraphioClient"):
        self._client = client

    def tag_list(self) -> List[TagDto]:
        """GET /tag-list : List<TagDto>"""
        url = f"{self._client.api_base}/tag-list"
        response = self._client._get_session().get(
            url, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "get tag list")
        data = result.get("data", [])
        return [TagDto.model_validate(item) for item in data] if isinstance(data, list) else []


# ============================
# 최상위 진입점 (client.meta_type)
# ============================
class MetaTypeNamespace:
    """
    client.meta_type 네임스페이스.
    GraphIOClient와 함께 사용: client.meta_type.table_data.list() 등
    """

    def __init__(self, client: "GraphioClient"):
        self._client = client
        self.table_data = MetaTableAPI(client)
        self.manage = MetaManageAPI(client)
        self.etc = EtcAPI(client)


__all__ = [
    "MetaTableAPI",
    "MetaManageAPI",
    "MetaTypeNamespace",
]
