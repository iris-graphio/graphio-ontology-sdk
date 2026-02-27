"""
ActionType 네임스페이스 - GraphioClient와 함께 사용
"""

from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from graphio_sdk.client import GraphioClient


class ActionTypeNamespace:
    """
    client.action_type 네임스페이스.

    이름 기반 상세 조회와 수동 실행 API를 제공합니다.
    """

    def __init__(self, client: "GraphioClient"):
        self._client = client
        self._url = f"{self._client.api_base}/ontology-workflow/action-type"

    def detail(self, name: str) -> Dict[str, Any]:
        """
        ActionType 상세 조회 (이름 기반).

        Args:
            name: ActionType 이름

        Returns:
            ActionType 상세 정보(dict)
        """
        params = {"name": name}
        url = f"{self._url}/detail"
        response = self._client._get_session().get(
            url, params=params, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "action type detail")
        return result.get("data", {})

    def execute(self, action_type_id: str) -> Dict[str, Optional[Any]]:
        """
        ActionType 수동 실행 (ID 기반).

        Args:
            action_type_id: ActionType ID(UUID)

        Returns:
            {"status": bool, "execution_id": str | None}
        """
        url = f"{self._url}/{action_type_id}/execute"
        response = self._client._get_session().post(url, timeout=self._client.timeout)
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "execute action type")
        return {
            "status": result.get("status"),
            "execution_id": result.get("data"),
        }

    def execute_by_name(self, name: str) -> Dict[str, Optional[Any]]:
        """
        ActionType 수동 실행 (이름 기반).

        내부적으로 detail(name) -> execute(action_type_id) 순서로 호출합니다.

        Args:
            name: ActionType 이름

        Returns:
            {"status": bool, "execution_id": str | None}
        """
        action_type = self.detail(name)
        action_type_id = action_type.get("id")
        if not action_type_id:
            raise ValueError(f"ActionType id를 찾을 수 없습니다. name={name}")
        return self.execute(action_type_id)


__all__ = ["ActionTypeNamespace"]
