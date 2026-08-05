"""
ActionType 네임스페이스 - GraphioClient와 함께 사용
"""

from typing import List, Any, Dict, Optional, Tuple, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from graphio_sdk.client import GraphioClient

# ActionType 수동 실행 전용 읽기 타임아웃(초) — 서버 대기 10분 + 여유 20초.
# 서버가 실행 종료까지 응답을 붙잡는다(ontology-service dispatch.wait-timeout-seconds =
# dag-service RUN_WAIT_* = 600초). 여유 없이 600초로 맞추면 서버가 대기 상한에 도달해 응답을
# 만드는 순간 클라이언트가 먼저 끊는다 — requests의 read timeout은 "바이트 간 무응답 시간"이라
# 600초 침묵 후 응답하는 이 패턴에 정확히 걸린다. 그래서 서버보다 길게 잡는다.
EXECUTE_READ_TIMEOUT_SECONDS = 620


class ActionTypeNamespace:
    """
    client.action_type 네임스페이스.

    이름 기반 상세 조회와 수동 실행 API를 제공합니다.
    """

    def __init__(self, client: "GraphioClient"):
        self._client = client
        self._url = f"{self._client.api_base}/ontology-workflow/action-type"

    def _execute_timeout(self) -> Union[int, Tuple[int, int]]:
        """수동 실행 호출용 타임아웃. 연결 타임아웃은 클라이언트 설정을 그대로 쓴다."""
        client_timeout = self._client.timeout
        if isinstance(client_timeout, tuple):
            connect, _read = client_timeout
            return (connect, EXECUTE_READ_TIMEOUT_SECONDS)
        return EXECUTE_READ_TIMEOUT_SECONDS

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

    def execute_by_name(
        self, name: str, messages: List[Dict[str, Any]]
    ) -> Dict[str, Optional[Any]]:
        """
        ActionType 수동 실행 (이름 기반).

        서버가 **실행 종료까지 대기**한 뒤 응답하므로 반환 시점에는 실행이 끝나 있다.
        이 호출만 `EXECUTE_READ_TIMEOUT_SECONDS`를 쓰고 다른 API는 클라이언트 기본 타임아웃을 쓴다.

        Args:
            name: ActionType 이름
            messages: 실행 입력 Object 목록

        Returns:
            {"status": bool, "run_id": str | None, "run_status": str | None, "completed": bool}

            - `run_id`: 서버가 발급한 실행 식별자(실행 이력의 `dagRunId`)
            - `run_status`: `SUCCESS` / `FAILED` / `PARTIAL_FAILED` / `TIMEOUT`.
              rule이 실패해도 예외가 아니라 `FAILED`로 온다.
              `TIMEOUT`은 실패가 아니라 서버 대기 시간 내 미종료이며 실행은 계속 진행된다.
            - `completed`: 종료 여부. false면 `run_status`가 `TIMEOUT`이다.
            - `status`: HTTP 응답 래퍼의 API 성공 플래그(실행 결과가 아님)
        """
        action_type = self.detail(name)
        action_type_id = action_type.get("id")
        if not action_type_id:
            raise ValueError(f"ActionType id를 찾을 수 없습니다. name={name}")
        url = f"{self._url}/{action_type_id}/execute"
        response = self._client._get_session().post(
            url, json=messages, timeout=self._execute_timeout()
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "execute action type")
        return self._to_run_result(result)

    def get_run_status(self, run_id: str) -> Dict[str, Optional[Any]]:
        """
        runId로 실행 상태를 조회한다 (대기 없음).

        `execute_by_name`이 `run_status="TIMEOUT"`으로 돌아온 뒤 결과를 확인하는 경로다.

        Args:
            run_id: `execute_by_name`이 반환한 `run_id`

        Returns:
            `execute_by_name`과 같은 형태
            {"status": bool, "run_id": str | None, "run_status": str | None, "completed": bool}
        """
        url = f"{self._url}/execute/info"
        response = self._client._get_session().get(
            url, params={"run-id": run_id}, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "action type run status")
        return self._to_run_result(result)

    @staticmethod
    def _to_run_result(result: Dict[str, Any]) -> Dict[str, Optional[Any]]:
        """서버 응답 → 실행 결과 dict. data = ActionTypeExecutionResultView {runId, runStatus, completed}.

        래퍼의 `status`(API 성공 여부, boolean)와 실행 결과(`runStatus`, 문자열)를 구분해 담는다.
        """
        data = result.get("data") or {}
        return {
            "status": result.get("status"),
            "run_id": data.get("runId"),
            "run_status": data.get("runStatus"),
            "completed": bool(data.get("completed")),
        }


__all__ = ["ActionTypeNamespace"]
