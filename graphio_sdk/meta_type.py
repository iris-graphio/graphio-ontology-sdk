"""
MetaType 네임스페이스 - GraphIOClient와 함께 사용
"""

from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from graphio_sdk.client import GraphioClient


# ============================
# 리소스별 래퍼
# ============================
class MetaTableAPI:
    """메타타입 테이블을 조작하는 래퍼 (GraphioClient 세션 사용)"""

    def __init__(self, client: "GraphioClient"):
        self._client = client

    def all_data(self, meta_type_id: str) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {
            "meta_type_id": meta_type_id,
        }
        url = f"{self._client.api_base}/all-data"
        response = self._client._get_session().get(
            url, params=params, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "list all-data")
        return result.get("data", [])

    def meta_type_table(self, meta_type_id: str):
        url = f"{self._client.api_base}/meta-type-table/{meta_type_id}"
        response = self._client._get_session().get(
            url, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "list meta type table")
        return result.get("data", [])

    def table_list(self, connection_instance_id: str, schema_name: str) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {
            "connection_instance_id": connection_instance_id,
            "schema_name": schema_name
        }
        url = f"{self._client.api_base}/table-list"
        response = self._client._get_session().get(
            url, params=params, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "list table from schema")
        return result.get("data", [])

    def sampe_data_param(self, meta_type_id: str, page: int, size: int) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {
            "meta_type_id": meta_type_id,
            "page": page,
            "sizw": size
        }
        url = f"{self._client.api_base}/sampe_data_param"
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

    def list(self):
        url = f"{self._client.api_base}/"
        response = self._client._get_session().get(
            url, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "list all-meta")
        return result.get("data", [])

    def duplicate_check(self, meta_type_name: str):
        url = f"{self._client.api_base}/duplicate-check/{meta_type_name}"
        response = self._client._get_session().get(
            url, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "check meta_type name duplicate")
        return result.get("status", [])

    def raw_datas(self, meta_type_id: str, page: int, size: int) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {
            "meta_type_id": meta_type_id,
            "page": page,
            "size": size
        }
        url = f"{self._client.api_base}/raw-datas"
        response = self._client._get_session().get(
            url, params=params, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "list raw data by meta type id")
        return result.get("data", [])

    def owner(self):
        url = f"{self._client.api_base}/owners"
        response = self._client._get_session().get(
            url, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "list meta type owner")
        return result.get("data", [])

    def kind_list(self, meta_type_kind: str) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {
            "meta_type_kind": meta_type_kind
        }
        url = f"{self._client.api_base}/kind_list"
        response = self._client._get_session().get(
            url, params=params, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "list meta type by meta type kind")
        return result.get("data", [])

    def inspect_property(self, meta_type_id: str):
        url = f"{self._client.api_base}/inspect/property/{meta_type_id}"
        response = self._client._get_session().get(
            url, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "meta type propreties")
        return result.get("data", [])

    def inspect_profiling(self, meta_type_id: str):
        url = f"{self._client.api_base}/inspect/profiling/{meta_type_id}"
        response = self._client._get_session().get(
            url, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "meta type profiling")
        return result.get("data", [])

    def inspect_data_source(self, meta_type_id: str):
        url = f"{self._client.api_base}/inspect/data-source/{meta_type_id}"
        response = self._client._get_session().get(
            url, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "meta type data_source")
        return result.get("data", [])

    def inspect_basic(self, meta_type_id: str):
        url = f"{self._client.api_base}/inspect/basic/{meta_type_id}"
        response = self._client._get_session().get(
            url, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "meta type basic inspect")
        return result.get("data", [])


class EtcAPI:
    def tag_list(self):
        url = f"{self._client.api_base}/tag-list"
        response = self._client._get_session().get(
            url, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "get tag list")
        return result.get("status", [])


# ============================
# 최상위 진입점 (client.meta_type)
# ============================
class MetaTypeNamespace:
    """
    client.meta_type 네임스페이스.
    GraphioClient와 함께 사용: client = GraphioClient(); client.meta_type.data.list(...)
    """

    def __init__(self, client: "GraphioClient"):
        self._client = client
        self.meta_table_data = MetaTableAPI(client)
        self.meta_type_manage = MetaManageAPI(client)


__all__ = [
    "MetaTableAPI",
    "MetaManageAPI",
    "MetaTypeNamespace",
]
