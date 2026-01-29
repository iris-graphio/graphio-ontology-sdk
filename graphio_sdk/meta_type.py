"""
MetaType 네임스페이스 - GraphIOClient와 함께 사용
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import GraphioClient


# ============================
# 리소스별 래퍼
# ============================
class DataAPI:
    """GET /all-data list 전용 래퍼 (GraphioClient 세션 사용)"""

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
        self.data = DataAPI(client)


__all__ = [
    "DataAPI",
    "MetaTypeNamespace",
]
