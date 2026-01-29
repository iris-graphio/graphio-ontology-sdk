"""
MetaType 네임스페이스 - GraphIOClient와 함께 사용
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from graphio_sdk.ontology.client import GraphioClient


# ============================
# 리소스별 래퍼
# ============================
class MetaTableDataAPI:
    """메타타입 테이블의 데이터를 조작하는 래퍼 (GraphioClient 세션 사용)"""

    def __init__(self, client: "GraphioClient"):
        self._client = client

    def list(self, meta_type_id: str) -> List[Dict[str, Any]]:
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
        url = f"{self._client.api_base}/{meta_type_name}"
        response = self._client._get_session().get(
            url, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "check meta_type name duplicate")
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
        self.meta_table_data = MetaTableDataAPI(client)
        self.meta_type_manage = MetaManageAPI(client)


__all__ = [
    "MetaTableDataAPI",
    "MetaManageAPI",
    "MetaTypeNamespace",
]
