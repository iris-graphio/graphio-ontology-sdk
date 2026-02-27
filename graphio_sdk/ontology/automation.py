"""
Automation 네임스페이스 - GraphioClient와 함께 사용
"""

from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from graphio_sdk.client import GraphioClient


class AutomationNamespace:
    """
    client.automation 네임스페이스.

    이름 기반 상세 조회, 활성화, 수동 실행 API를 제공합니다.
    """

    def __init__(self, client: "GraphioClient"):
        self._client = client
        self._url = f"{self._client.api_base}/ontology-workflow/automation"

    def detail(self, name: str) -> Dict[str, Any]:
        """
        Automation 상세 조회 (이름 기반).

        Args:
            name: Automation 이름

        Returns:
            Automation 상세 정보(dict)
        """
        params = {"name": name}
        url = f"{self._url}/detail"
        response = self._client._get_session().get(
            url, params=params, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "automation detail")
        return result.get("data", {})

    def set_active(self, automation_id: str, active: bool = True) -> Dict[str, Optional[Any]]:
        """
        Automation 활성/비활성 (ID 기반).

        Args:
            automation_id: Automation ID(UUID)
            active: 활성화 여부

        Returns:
            {"status": bool, "active": bool | None}
        """
        url = f"{self._url}/{automation_id}/active"
        response = self._client._get_session().post(
            url,
            json={"active": active},
            headers={"Content-Type": "application/json"},
            timeout=self._client.timeout,
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "set automation active")
        return {
            "status": result.get("status"),
            "active": result.get("data"),
        }

    def set_active_by_name(self, name: str, active: bool = True) -> Dict[str, Optional[Any]]:
        """
        Automation 활성/비활성 (이름 기반).

        내부적으로 detail(name) -> set_active(automation_id) 순서로 호출합니다.

        Args:
            name: Automation 이름
            active: 활성화 여부

        Returns:
            {"status": bool, "active": bool | None}
        """
        automation = self.detail(name)
        automation_id = automation.get("id")
        if not automation_id:
            raise ValueError(f"Automation id를 찾을 수 없습니다. name={name}")
        return self.set_active(automation_id, active=active)

    def execute(self, automation_id: str) -> Dict[str, Optional[Any]]:
        """
        Automation 수동 실행 (ID 기반).

        Args:
            automation_id: Automation ID(UUID)

        Returns:
            {"status": bool, "execution_id": str | None}
        """
        url = f"{self._url}/{automation_id}/execute"
        response = self._client._get_session().post(url, timeout=self._client.timeout)
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "execute automation")
        return {
            "status": result.get("status"),
            "execution_id": result.get("data"),
        }

    def execute_by_name(self, name: str) -> Dict[str, Optional[Any]]:
        """
        Automation 수동 실행 (이름 기반).

        내부적으로 detail(name) -> execute(automation_id) 순서로 호출합니다.

        Args:
            name: Automation 이름

        Returns:
            {"status": bool, "execution_id": str | None}
        """
        automation = self.detail(name)
        automation_id = automation.get("id")
        if not automation_id:
            raise ValueError(f"Automation id를 찾을 수 없습니다. name={name}")
        return self.execute(automation_id)


__all__ = ["AutomationNamespace"]
