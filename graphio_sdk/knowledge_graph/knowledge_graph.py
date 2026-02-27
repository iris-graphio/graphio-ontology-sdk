"""
KnowledgeGraph 네임스페이스 - GraphioClient와 함께 사용
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from graphio_sdk.client import GraphioClient


class KnowledgeGraphNamespace:
    """
    client.knowledge_graph 네임스페이스.

    - 특정 ObjectType 기준 hop 탐색
    - ObjectType/LinkType 목록 기준 연결관계 조회
    """

    _MIN_HOP = 0
    _MAX_HOP = 10

    def __init__(self, client: "GraphioClient"):
        self._client = client
        self._ontology_url = f"{self._client.api_base}/ontology"

    def _validate_hop(self, hop: int) -> None:
        if not isinstance(hop, int):
            raise ValueError("hop은 int 타입이어야 합니다.")
        if hop < self._MIN_HOP or hop > self._MAX_HOP:
            raise ValueError(
                f"hop은 {self._MIN_HOP} 이상 {self._MAX_HOP} 이하만 허용됩니다. 입력값={hop}"
            )

    def _resolve_object_type_id_by_name(self, object_type_name: str) -> str:
        """
        기존 ObjectType 이름 조회 API(/object-type?name=...)를 사용해 id를 찾습니다.
        """
        results = self._client.ontology._fetch_object_types(name=object_type_name)
        if not results:
            raise ValueError(f"ObjectType '{object_type_name}'을 찾을 수 없습니다.")

        exact_match = next(
            (item for item in results if item.get("name") == object_type_name), None
        )
        object_type = exact_match if exact_match else results[0]

        object_type_id = object_type.get("id")
        if not object_type_id:
            raise ValueError(
                f"ObjectType id를 찾을 수 없습니다. object_type_name={object_type_name}"
            )
        return object_type_id

    def graph_by_object_type_id(self, object_type_id: str, hop: int) -> Dict[str, Any]:
        """
        특정 ObjectType(id) 기준 hop 범위 내 연결 graph 조회.

        Args:
            object_type_id: ObjectType UUID
            hop: 탐색 hop(0~10)

        Returns:
            {"nodes": [...], "edges": [...]} 형태의 graph 데이터
        """
        self._validate_hop(hop)

        url = f"{self._ontology_url}/{object_type_id}"
        response = self._client._get_session().get(
            url, params={"hop": hop}, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "knowledge graph by object type id")
        return result.get("data", {})

    def graph_by_object_type_name(self, object_type_name: str, hop: int) -> Dict[str, Any]:
        """
        특정 ObjectType(name) 기준 hop 범위 내 연결 graph 조회.

        내부적으로 name -> object_type_id 조회 후 graph_by_object_type_id를 호출합니다.
        """
        object_type_id = self._resolve_object_type_id_by_name(object_type_name)
        return self.graph_by_object_type_id(object_type_id, hop)

    def graph_by_object_and_link_types(
        self,
        object_type_id_list: List[str],
        link_type_id_list: List[str],
        element_id_list: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        특정 ObjectType 목록 + LinkType 목록으로 연결관계 graph 조회.

        Args:
            object_type_id_list: 조회 대상 ObjectType ID 목록
            link_type_id_list: 필터링할 LinkType ID 목록
            element_id_list: element ID 목록(옵션, 기본값 [])

        Returns:
            {"nodes": [...], "edges": [...]} 형태의 graph 데이터
        """
        url = f"{self._ontology_url}/list"
        request_body = {
            "elementIdList": element_id_list or [],
            "objectTypeIdList": object_type_id_list,
            "linkTypeIdList": link_type_id_list,
        }
        response = self._client._get_session().post(
            url,
            json=request_body,
            headers={"Content-Type": "application/json"},
            timeout=self._client.timeout,
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "knowledge graph by object/link type list")
        return result.get("data", {})


__all__ = ["KnowledgeGraphNamespace"]
