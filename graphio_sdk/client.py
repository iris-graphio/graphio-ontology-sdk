"""
GraphIO Ontology Service 메인 클라이언트 (자동 리소스 관리)
"""
import os

import requests
import weakref
from typing import Dict, Any, Optional, Union, Tuple

from graphio_sdk.ontology.ontology import OntologyNamespace
from graphio_sdk.data_pipline.meta_type import MetaTypeNamespace


class GraphioClient:
    """
    GraphIO Ontology Service 클라이언트

    자동으로 리소스를 관리하므로 with 문 없이도 사용 가능합니다.

    Example:
        from graphio_sdk import GraphIOClient

        client = GraphIOClient()
        Employee = client.ontology.get_object_type("Employee")
        employees = (Employee
                     .where(Employee.age > 30)
                     .select("name", "age")
                     .execute())

        # 또는 편집
        edits = client.ontology.edits()
        new_emp = edits.objects.Employee.create({"name": "John", "age": 30})
        edits.commit()
    """

    def __init__(
            self,
            base_url: Optional[str] = None,
            timeout: Union[int, Tuple[int, int]] = 30,
    ):
        """
        클라이언트 초기화

        Args:
            base_url: API 서버의 base URL (기본값: http://localhost:8080)
            timeout: 요청 타임아웃 시간(초) 또는 (연결 타임아웃, 읽기 타임아웃)
                    튜플. 기본값 30초. int인 경우 (5초, timeout초)로 설정되어
                    서버가 죽어있을 때 빠르게 실패합니다.
        """
        # base_url이 None이면 환경변수에서 가져오기
        if base_url is None:
            base_url = os.getenv("ONTOLOGY_SERVICE", "http://ontology-svc:8080")
        
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/graphio/v1"

        # timeout 처리: int면 (connect_timeout, read_timeout) 튜플로 변환
        if isinstance(timeout, int):
            # 연결 타임아웃 5초, 읽기 타임아웃은 사용자 지정값
            self.timeout: Tuple[int, int] = (5, timeout)
        else:
            self.timeout = timeout
        self._session: Optional[requests.Session] = None
        self._closed = False
        self.ontology = OntologyNamespace(self)
        self.meta_type = MetaTypeNamespace(self)

        # 가비지 컬렉션 시 자동 정리 등록
        self._register_cleanup()

    def _register_cleanup(self):
        """가비지 컬렉션 시 자동 정리 등록"""
        # weakref를 사용하여 순환 참조 방지
        try:
            weakref.finalize(self, self._cleanup)
        except Exception:
            pass  # finalize가 실패해도 계속 진행

    def _cleanup(self):
        """리소스 정리 (가비지 컬렉션 시 자동 호출)"""
        if not self._closed:
            self.close()

    def _get_session(self) -> requests.Session:
        """
        세션 가져오기 (Lazy 초기화)

        Returns:
            requests.Session 인스턴스
        """
        if self._closed:
            raise RuntimeError("클라이언트가 이미 닫혔습니다.")

        if self._session is None:
            self._session = requests.Session()

        return self._session

    # ========================================================================
    # 유틸리티
    # ========================================================================

    def _format_timeout(self) -> str:
        """timeout 값을 문자열로 포맷팅"""
        if isinstance(self.timeout, tuple):
            connect, read = self.timeout
            return f"연결={connect}초, 읽기={read}초"
        return f"{self.timeout}초"

    def _check_response(self, response: Dict[str, Any], operation: str):
        """응답 검증"""
        if response.get("status") is False or "error" in response:
            error_info = response.get("error", {})
            error_msg = f"{operation} 실패"

            if error_info:
                error_code = error_info.get("code", "UNKNOWN")
                error_desc = error_info.get("description", "")
                error_message = error_info.get("errorMessage", "")
                error_msg += f": [{error_code}] {error_desc} - {error_message}"

            raise Exception(error_msg)

    def close(self):
        """
        세션 종료 (명시적 호출)

        Note: 가비지 컬렉션 시 자동으로 호출되므로 대부분의 경우 명시적 호출 불필요
        """
        if not self._closed:
            if self._session:
                self._session.close()
                self._session = None
            self._closed = True

    def __enter__(self):
        """Context manager 진입 (선택적 사용)"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.close()

    def __del__(self):
        """소멸자 - 가비지 컬렉션 시 자동 정리"""
        try:
            if not self._closed:
                self.close()
        except Exception:
            pass  # 소멸자에서는 예외를 무시


# Palantir Foundry 스타일 별칭 (선택적)
FoundryClient = GraphioClient
