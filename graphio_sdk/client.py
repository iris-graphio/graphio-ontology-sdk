"""
GraphIO Ontology Service 메인 클라이언트 (자동 리소스 관리)
"""
import os
import time
import json

import requests
import weakref
from typing import List, Dict, Any, Optional, Union, Tuple

from .ontology import OntologyNamespace

# pika는 optional dependency이므로 import 시도
try:
    import pika
    PIKA_AVAILABLE = True
except ImportError:
    PIKA_AVAILABLE = False
    pika = None


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
            rabbitmq_host: Optional[str] = None,
            rabbitmq_port: Optional[int] = None,
            rabbitmq_username: Optional[str] = None,
            rabbitmq_password: Optional[str] = None,
            rabbitmq_vhost: Optional[str] = None,
            rabbitmq_exchange: Optional[str] = None,
            rabbitmq_routing_key: Optional[str] = None
    ):
        """
        클라이언트 초기화

        Args:
            base_url: API 서버의 base URL (기본값: http://localhost:8080)
            timeout: 요청 타임아웃 시간(초) 또는 (연결 타임아웃, 읽기 타임아웃)
                    튜플. 기본값 30초. int인 경우 (5초, timeout초)로 설정되어
                    서버가 죽어있을 때 빠르게 실패합니다.
            rabbitmq_host: RabbitMQ 호스트 (환경변수: RABBIT_MQ_HOST)
            rabbitmq_port: RabbitMQ 포트 (환경변수: RABBIT_MQ_PORT,
                    기본값: 5672)
            rabbitmq_username: RabbitMQ 사용자명
                    (환경변수: RABBIT_MQ_USERNAME)
            rabbitmq_password: RabbitMQ 비밀번호
                    (환경변수: RABBIT_MQ_PASSWORD)
            rabbitmq_vhost: RabbitMQ Virtual Host
                    (환경변수: RABBIT_MQ_VHOST, 기본값: "/")
            rabbitmq_exchange: RabbitMQ Exchange 이름
                    (환경변수: RABBIT_MQ_EXCHANGE)
            rabbitmq_routing_key: RabbitMQ Routing Key
                    (환경변수: RABBIT_MQ_ROUTING_KEY)
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

        # RabbitMQ 설정
        self.rabbitmq_host = (
            rabbitmq_host or os.getenv("RABBIT_MQ_HOST", "rabbitmq")
        )
        if rabbitmq_port is not None:
            self.rabbitmq_port = rabbitmq_port
        else:
            port_str = os.getenv("RABBIT_MQ_PORT", "5672")
            self.rabbitmq_port = int(port_str)
        self.rabbitmq_username = (
            rabbitmq_username or os.getenv("RABBIT_MQ_USERNAME", "guest")
        )
        self.rabbitmq_password = (
            rabbitmq_password or os.getenv("RABBIT_MQ_PASSWORD", "guest")
        )
        self.rabbitmq_vhost = (
            rabbitmq_vhost or os.getenv("RABBIT_MQ_VHOST", "/")
        )
        self.rabbitmq_exchange = (
            rabbitmq_exchange
            or os.getenv("RABBIT_MQ_EXCHANGE", "ontology.direct")
        )
        self.rabbitmq_routing_key = (
            rabbitmq_routing_key
            or os.getenv("RABBIT_MQ_ROUTING_KEY", "ontology")
        )
        self._rabbitmq_connection: Optional[Any] = None
        self._rabbitmq_channel: Optional[Any] = None

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

    def _get_rabbitmq_channel(self):
        """
        RabbitMQ 채널 가져오기 (Lazy 초기화)

        Returns:
            pika.channel.Channel 인스턴스
        """
        if not PIKA_AVAILABLE:
            raise ImportError(
                "pika가 설치되지 않았습니다. RabbitMQ를 사용하려면 "
                "다음을 실행하세요: "
                "pip install 'graphio-sdk[mq]' 또는 "
                "pip install pika>=1.3.0"
            )

        if self._closed:
            raise RuntimeError("클라이언트가 이미 닫혔습니다.")

        conn = self._rabbitmq_connection
        if conn is None or conn.is_closed:
            credentials = pika.PlainCredentials(
                self.rabbitmq_username, self.rabbitmq_password
            )
            parameters = pika.ConnectionParameters(
                host=self.rabbitmq_host,
                port=self.rabbitmq_port,
                virtual_host=self.rabbitmq_vhost,
                credentials=credentials
            )
            self._rabbitmq_connection = pika.BlockingConnection(parameters)
            self._rabbitmq_channel = self._rabbitmq_connection.channel()

        return self._rabbitmq_channel

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
            response = self._get_session().get(
                url, params=params, timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            self._check_response(result, "fetch object types")

            return result.get("data", [])

        except requests.exceptions.Timeout as e:
            raise Exception(
                f"ObjectType 목록 조회 타임아웃 "
                f"(timeout={self._format_timeout()}): {str(e)}"
            ) from e
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

        except requests.exceptions.Timeout as e:
            raise Exception(
                f"ObjectType 조회 타임아웃 "
                f"(timeout={self._format_timeout()}): {str(e)}"
            ) from e
        except requests.exceptions.RequestException as e:
            raise Exception(f"ObjectType 조회 실패: {str(e)}") from e

    def _fetch_object_type_properties(
        self, object_type_id: str
    ) -> List[Dict[str, Any]]:
        """ObjectType의 Property 목록 가져오기"""
        url = f"{self.api_base}/object-type-property/{object_type_id}"

        try:
            response = self._get_session().get(url, timeout=self.timeout)
            response.raise_for_status()

            result = response.json()
            self._check_response(result, "fetch object type properties")

            return result.get("data", [])

        except requests.exceptions.Timeout as e:
            raise Exception(
                f"ObjectType Properties 조회 타임아웃 "
                f"(timeout={self._format_timeout()}): {str(e)}"
            ) from e
        except requests.exceptions.RequestException as e:
            raise Exception(f"ObjectType Properties 조회 실패: {str(e)}") from e

    # ========================================================================
    # ObjectSet 관련 API 호출 (실제 데이터 조회)
    # ========================================================================

    def _execute_select(
        self, select_dto: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        실제 데이터 조회 (selectObjectSet 사용)

        Args:
            select_dto: ObjectSetSelectDto 형식의 요청

        Returns:
            조회된 실제 데이터 리스트
        """
        url = f"{self.api_base}/ontology-workflow/objects/select"

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

        except requests.exceptions.Timeout as e:
            raise Exception(
                f"데이터 조회 타임아웃 "
                f"(timeout={self._format_timeout()}): {str(e)}"
            ) from e
        except requests.exceptions.RequestException as e:
            raise Exception(f"데이터 조회 실패: {str(e)}") from e

    # ========================================================================
    # Typed Object/Link API (insert, update, delete)
    # ========================================================================

    def insert(self, obj):
        """
        Typed Object 또는 Link를 생성

        Args:
            obj: TypedObject 또는 TypedLink 인스턴스

        Returns:
            생성 결과

        Example:
            Employee = client.ontology.get_object_type("Employee")

            emp = Employee(
                element_id="e-1",
                properties={"name": "John", "age": 30}
            )
            client.insert(emp)
        """
        contract = obj.to_contract()
        messages = [contract]
        return self._execute_create(messages)

    def update(self, obj):
        """
        Typed Object 또는 Link를 업데이트

        Args:
            obj: TypedObject 또는 TypedLink 인스턴스 (element_id 필수)

        Returns:
            업데이트 결과

        Example:
            Employee = client.ontology.get_object_type("Employee")

            emp = Employee(
                element_id="e-1",
                properties={"name": "John", "age": 31}
            )
            client.update(emp)
        """
        if not obj.element_id:
            raise ValueError(
                "update()를 사용하려면 element_id가 필요합니다."
            )

        contract = obj.to_contract()
        messages = [contract]
        return self._execute_update(messages)

    def delete(self, obj):
        """
        Typed Object 또는 Link를 삭제

        Args:
            obj: TypedObject 또는 TypedLink 인스턴스 (element_id 필수)

        Returns:
            삭제 결과

        Example:
            Employee = client.ontology.get_object_type("Employee")

            emp = Employee(element_id="e-1")
            client.delete(emp)
        """
        if not obj.element_id:
            raise ValueError(
                "delete()를 사용하려면 element_id가 필요합니다."
            )

        contract = obj.to_contract()
        messages = [contract]
        return self._execute_delete(messages)

    def _execute_delete(
        self, messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """삭제 실행 - RabbitMQ로 메시지 발행"""
        # DTO 형식으로 요청 본문 구성
        request_body = {
            "eventType": "DELETE",
            "timestamp": int(time.time() * 1000),  # 밀리초 단위 timestamp
            "objectInputs": messages
        }

        try:
            channel = self._get_rabbitmq_channel()
            message_body = json.dumps(request_body).encode('utf-8')

            channel.basic_publish(
                exchange=self.rabbitmq_exchange,
                routing_key=self.rabbitmq_routing_key,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 메시지 영속성
                    content_type='application/json'
                )
            )

            return {
                "status": True,
                "message": "메시지가 RabbitMQ로 발행되었습니다"
            }

        except Exception as e:
            raise Exception(
                f"객체 삭제 실패 (RabbitMQ 발행 오류): {str(e)}"
            ) from e

    # ========================================================================
    # ObjectSet 생성/수정 API 호출
    # ========================================================================

    def _execute_create(
        self, messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """생성 실행 - RabbitMQ로 메시지 발행"""
        # DTO 형식으로 요청 본문 구성
        request_body = {
            "eventType": "INSERT",
            "timestamp": int(time.time() * 1000),  # 밀리초 단위 timestamp
            "objectInputs": messages
        }

        try:
            channel = self._get_rabbitmq_channel()
            message_body = json.dumps(request_body).encode('utf-8')

            channel.basic_publish(
                exchange=self.rabbitmq_exchange,
                routing_key=self.rabbitmq_routing_key,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 메시지 영속성
                    content_type='application/json'
                )
            )

            return {
                "status": True,
                "message": "메시지가 RabbitMQ로 발행되었습니다"
            }

        except Exception as e:
            raise Exception(
                f"객체 생성 실패 (RabbitMQ 발행 오류): {str(e)}"
            ) from e

    def _execute_update(
        self, messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """업데이트 실행 - RabbitMQ로 메시지 발행"""
        # DTO 형식으로 요청 본문 구성
        request_body = {
            "eventType": "UPDATE",
            "timestamp": int(time.time() * 1000),  # 밀리초 단위 timestamp
            "objectInputs": messages
        }

        try:
            channel = self._get_rabbitmq_channel()
            message_body = json.dumps(request_body).encode('utf-8')

            channel.basic_publish(
                exchange=self.rabbitmq_exchange,
                routing_key=self.rabbitmq_routing_key,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 메시지 영속성
                    content_type='application/json'
                )
            )

            return {
                "status": True,
                "message": "메시지가 RabbitMQ로 발행되었습니다"
            }

        except Exception as e:
            raise Exception(
                f"객체 업데이트 실패 (RabbitMQ 발행 오류): {str(e)}"
            ) from e

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

            # RabbitMQ 연결 종료
            conn = self._rabbitmq_connection
            if conn and not conn.is_closed:
                try:
                    self._rabbitmq_connection.close()
                except Exception:
                    pass  # 연결 종료 중 오류는 무시
                self._rabbitmq_connection = None
                self._rabbitmq_channel = None

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
