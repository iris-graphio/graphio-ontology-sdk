"""
RabbitMQ 메시지 발행 관련 클래스 및 함수
"""
import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from enum import Enum as EnumType

try:
    import pika

    PIKA_AVAILABLE = True
except ImportError:
    PIKA_AVAILABLE = False
    pika = None

logger = logging.getLogger(__name__)

# RabbitMQ 기본 설정 (환경 변수로 오버라이드 가능)
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq-svc")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "admin123")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "ontology.workflow")

# 전역 커넥션/채널
_connection: Optional[Any] = None
_channel: Optional[Any] = None


def _get_channel() -> Any:
    """
    전역 RabbitMQ 채널 반환 (없으면 생성)
    
    Returns:
        pika.channel.Channel: RabbitMQ 채널 인스턴스
        
    Raises:
        ImportError: pika가 설치되지 않은 경우
        Exception: RabbitMQ 연결 실패 시
    """
    global _connection, _channel

    if not PIKA_AVAILABLE:
        raise ImportError(
            "pika가 설치되지 않았습니다. "
            "RabbitMQ 기능을 사용하려면 'pip install pika'를 실행하세요."
        )

    if _channel and _channel.is_open:
        return _channel

    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    _connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials
        )
    )
    _channel = _connection.channel()
    logger.info("✅ RabbitMQ channel initialized (singleton)")
    return _channel


def _close_connection():
    """
    RabbitMQ 연결 종료
    
    전역 커넥션과 채널을 닫습니다.
    """
    global _connection, _channel

    if _channel and _channel.is_open:
        try:
            _channel.close()
        except Exception:
            pass
        _channel = None

    if _connection and not _connection.is_closed:
        try:
            _connection.close()
        except Exception:
            pass
        _connection = None

    logger.info("RabbitMQ connection closed")


def _serializer(o: Any) -> Any:
    """
    JSON 직렬화를 위한 커스텀 serializer
    
    Args:
        o: 직렬화할 객체
        
    Returns:
        직렬화 가능한 객체
    """
    # Enum 인스턴스 처리
    if isinstance(o, EnumType):
        return o.value

    # 객체의 __dict__ 속성이 있는 경우
    if hasattr(o, "__dict__"):
        return o.__dict__

    # datetime 인스턴스 처리
    if isinstance(o, datetime):
        return o.isoformat()

    return str(o)


def __publish(
        queue_name: str,
        exchange: str,
        routing_key: str,
        body: Dict[str, Any]
) -> None:
    """
    RabbitMQ에 메시지 발행
    
    Args:
        queue_name: 큐 이름
        exchange: Exchange 이름
        routing_key: 라우팅 키
        body: 발행할 메시지 본문 (딕셔너리)
        
    Raises:
        ImportError: pika가 설치되지 않은 경우
        Exception: 메시지 발행 실패 시
    """
    channel = _get_channel()
    channel.queue_declare(queue=queue_name, durable=True)

    channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=json.dumps(body, default=_serializer).encode('utf-8'),
        properties=pika.BasicProperties(
            delivery_mode=2  # 메시지 영속화
        )
    )

    logger.debug(
        f"[PUBLISH] queue={queue_name}, "
        f"routing_key={routing_key}, body={body}"
    )


def _publish(
        dag_id: str,
        automation_id: str,
        step: str,
        message: str,
        status: str
) -> None:
    """
    워크플로우 로그 이벤트를 RabbitMQ에 발행
    
    Args:
        dag_id: DAG ID
        automation_id: 자동화 ID
        step: 단계 (condition, action, notification_effects 등)
        message: 메시지
        status: 상태 (SUCCESS, FAILED 등)
    """
    logger.debug(
        f"[LOG] dag_id: {dag_id}, step: {step}, "
        f"message: {message}, status: {status}"
    )

    log_event = {
        "automationId": automation_id,
        "step": step,
        "message": message,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # step에 따라 큐와 라우팅 키 결정
    match step:
        case "automation":
            queue_name = "automation.executed.queue"
            routing_key = "automation"
        case _:
            queue_name = "observation.queue"
            routing_key = "observation"

    # 메시지 발행
    __publish(queue_name, RABBITMQ_EXCHANGE, routing_key, log_event)
    logger.debug(f"[LOG] Sent to queue={queue_name}: {log_event}")


def _on_task_success(
        context: Dict[str, Any],
        dag_id: str,
        automation_id: str,
        step: str
) -> None:
    """
    Airflow 태스크 성공 콜백 함수
    
    Args:
        context: Airflow 태스크 컨텍스트
        dag_id: DAG ID
        automation_id: 자동화 ID
        step: 단계
    """
    task_id = context["task_instance"].task_id
    result = context['task_instance'].xcom_pull(task_ids=task_id)
    message = result.get('message', '') if result else ''
    status = result.get('status', 'SUCCESS') if result else 'SUCCESS'

    _publish(
        dag_id=dag_id,
        automation_id=automation_id,
        step=step,
        message=message,
        status=status
    )


def _on_task_failure(
        context: Dict[str, Any],
        dag_id: str,
        automation_id: str,
        step: str
) -> None:
    """
    Airflow 태스크 실패 콜백 함수
    
    Args:
        context: Airflow 태스크 컨텍스트
        dag_id: DAG ID
        automation_id: 자동화 ID
        step: 단계
    """
    _publish(
        dag_id=dag_id,
        automation_id=automation_id,
        step=step,
        message="",
        status="FAILED"
    )


def _on_dag_run_success(
        context: Dict[str, Any],
        automation_id: str,
        message: str = ""
) -> None:
    """
    Airflow DAG 실행 성공 콜백 함수

    DAG가 성공적으로 완료되었을 때 로그를 발행합니다.

    Args:
        context: Airflow DAG run 컨텍스트
        automation_id: 자동화 ID
        message: 추가 메시지 (선택적)

    Example:
        from airflow import DAG
        from graphio_sdk.mq_publisher import _on_dag_run_success

        def on_success_callback(context):
            _on_dag_run_success(
                context,
                automation_id="auto_123",
                message="DAG 완료"
            )

        dag = DAG(
            dag_id="my_dag",
            on_success_callback=on_success_callback
        )
    """
    dag_obj = context.get("dag")
    if dag_obj and hasattr(dag_obj, "dag_id"):
        dag_id = dag_obj.dag_id
    else:
        dag_id = context.get("dag_id", "")

    _publish(
        dag_id=dag_id,
        automation_id=automation_id,
        step="automation",
        message=message or "DAG 실행 완료",
        status="SUCCESS"
    )


def _on_dag_run_failure(
        context: Dict[str, Any],
        automation_id: str,
        message: str = ""
) -> None:
    """
    Airflow DAG 실행 실패 콜백 함수

    DAG가 실패했을 때 로그를 발행합니다.

    Args:
        context: Airflow DAG run 컨텍스트
        automation_id: 자동화 ID
        message: 추가 메시지 (선택적)

    Example:
        from airflow import DAG
        from graphio_sdk.mq_publisher import _on_dag_run_failure

        def on_failure_callback(context):
            _on_dag_run_failure(
                context,
                automation_id="auto_123",
                message="DAG 실패"
            )

        dag = DAG(
            dag_id="my_dag",
            on_failure_callback=on_failure_callback
        )
    """
    dag_obj = context.get("dag")
    if dag_obj and hasattr(dag_obj, "dag_id"):
        dag_id = dag_obj.dag_id
    else:
        dag_id = context.get("dag_id", "")

    _publish(
        dag_id=dag_id,
        automation_id=automation_id,
        step="automation",
        message=message or "DAG 실행 실패",
        status="FAILED"
    )
