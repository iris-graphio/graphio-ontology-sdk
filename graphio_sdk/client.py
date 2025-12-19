"""
GraphIO Ontology Service 메인 클라이언트 (자동 리소스 관리)
"""
import os

import requests
import weakref
from typing import List, Dict, Any, Optional

from .ontology import OntologyNamespace


class GraphioClient:
    """
    GraphIO Ontology Service 클라이언트

    자동으로 리소스를 관리하므로 with 문 없이도 사용 가능합니다.

    Example:
        from graphio_sdk import GraphIOClient

        client = GraphIOClient()
        Employee = client.ontology.get_object_type("Employee")
        employees = Employee.where(Employee.age > 30).select("name", "age").execute()

        # 또는 편집
        edits = client.ontology.edits()
        new_emp = edits.objects.Employee.create({"name": "John", "age": 30})
        edits.commit()
    """

    def __init__(self, base_url: str = os.getenv("GRAPHIO_BASE_URL", "http://localhost:8080"), timeout: int = 30):
        """
        클라이언트 초기화

        Args:
            base_url: API 서버의 base URL (기본값: http://localhost:8080)
            timeout: 요청 타임아웃 시간(초), 기본값 30초
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/graphio/v1"
        self.timeout = timeout
        self._session: Optional[requests.Session] = None
        self._closed = False
        self.ontology = OntologyNamespace(self)

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
    # ObjectType 관련 API 호출
    # ========================================================================

    def _fetch_object_types(
            self,
            ontology_id: Optional[str] = None,
            name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """서버에서 ObjectType 목록 가져오기"""
        url = f"{self.api_base}/object-type"

        params = {}
        if ontology_id:
            params["ontology-id"] = ontology_id
        if name:
            params["name"] = name

        try:
            response = self._get_session().get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            result = response.json()
            self._check_response(result, "fetch object types")

            return result.get("data", [])

        except requests.exceptions.RequestException as e:
            raise Exception(f"ObjectType 목록 조회 실패: {str(e)}") from e

    def _fetch_object_type_by_id(self, object_type_id: str) -> Dict[str, Any]:
        """특정 ObjectType 상세 정보 가져오기"""
        url = f"{self.api_base}/object-type/{object_type_id}"

        try:
            response = self._get_session().get(url, timeout=self.timeout)
            response.raise_for_status()

            result = response.json()

            # CommonResponse 어노테이션이 있는 경우 data를 직접 반환
            if isinstance(result, dict) and "id" in result:
                return result

            self._check_response(result, "fetch object type")
            return result.get("data", {})

        except requests.exceptions.RequestException as e:
            raise Exception(f"ObjectType 조회 실패: {str(e)}") from e

    def _fetch_object_type_properties(self, object_type_id: str) -> List[Dict[str, Any]]:
        """ObjectType의 Property 목록 가져오기"""
        url = f"{self.api_base}/object-type-property/{object_type_id}"

        try:
            response = self._get_session().get(url, timeout=self.timeout)
            response.raise_for_status()

            result = response.json()
            self._check_response(result, "fetch object type properties")

            return result.get("data", [])

        except requests.exceptions.RequestException as e:
            raise Exception(f"ObjectType Properties 조회 실패: {str(e)}") from e

    # ========================================================================
    # ObjectSet 관련 API 호출 (실제 데이터 조회)
    # ========================================================================

    def _execute_select(self, select_dto: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        실제 데이터 조회 (selectObjectSet 사용)

        Args:
            select_dto: ObjectSetSelectDto 형식의 요청

        Returns:
            조회된 실제 데이터 리스트
        """
        url = f"{self.api_base}/ontology-workflow/object-set/select"

        try:
            response = self._get_session().post(
                url,
                json=select_dto,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            self._check_response(result, "select")

            return result.get("data", [])

        except requests.exceptions.RequestException as e:
            raise Exception(f"데이터 조회 실패: {str(e)}") from e

    # ========================================================================
    # ObjectSet 생성/수정 API 호출
    # ========================================================================

    def _execute_create(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """생성 실행"""
        url = f"{self.api_base}/ontology-workflow/object-set/insert"

        try:
            response = self._get_session().post(
                url,
                json=messages,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            self._check_response(result, "create")

            return result

        except requests.exceptions.RequestException as e:
            raise Exception(f"객체 생성 실패: {str(e)}") from e

    def _execute_update(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """업데이트 실행"""
        url = f"{self.api_base}/ontology-workflow/object-set/update"

        try:
            response = self._get_session().post(
                url,
                json=messages,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            self._check_response(result, "update")

            return result

        except requests.exceptions.RequestException as e:
            raise Exception(f"객체 업데이트 실패: {str(e)}") from e

    # ========================================================================
    # 유틸리티
    # ========================================================================

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
        if not self._closed and self._session:
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