"""
MQ Consumer 예제 구현

실제 MQ 구현체에 맞게 수정하여 사용하세요.
"""

import json
import logging
from typing import Callable
from .mq_consumer import MQConsumer, OntologyChangeEvent

logger = logging.getLogger(__name__)


class ExampleMQConsumer(MQConsumer):
    """
    예제 MQ Consumer 구현
    
    실제 환경에서는 RabbitMQ, Kafka, Redis Streams 등을 사용합니다.
    """

    def __init__(self, mq_config: dict):
        """
        Args:
            mq_config: MQ 설정 딕셔너리
                예: {
                    "type": "rabbitmq",
                    "host": "localhost",
                    "port": 5672,
                    "queue": "ontology-changes"
                }
        """
        self.mq_config = mq_config
        self._running = False
        self._callback = None

    def start(self, callback: Callable[[OntologyChangeEvent], None]):
        """MQ 소비 시작"""
        self._callback = callback
        self._running = True
        
        logger.info(f"MQ Consumer 시작: {self.mq_config}")
        
        # TODO: 실제 MQ 라이브러리를 사용하여 메시지 소비
        # 예시:
        # import pika  # RabbitMQ
        # connection = pika.BlockingConnection(...)
        # channel = connection.channel()
        # channel.basic_consume(
        #     queue=self.mq_config["queue"],
        #     on_message_callback=self._on_message
        # )
        # channel.start_consuming()
        
        logger.warning("예제 구현입니다. 실제 MQ 라이브러리를 사용하세요.")

    def stop(self):
        """MQ 소비 중지"""
        self._running = False
        logger.info("MQ Consumer 중지")

    def _on_message(self, channel, method, properties, body):
        """메시지 수신 핸들러"""
        try:
            message = json.loads(body)
            event = OntologyChangeEvent.from_mq_message(message)
            if self._callback:
                self._callback(event)
        except Exception as e:
            logger.error(f"메시지 처리 실패: {e}", exc_info=True)


def create_codegen_consumer(client, mq_config: dict):
    """
    Codegen Consumer 생성 헬퍼 함수
    
    Args:
        client: GraphioClient 인스턴스
        mq_config: MQ 설정
        
    Returns:
        OntologyChangeEventConsumer 인스턴스
    """
    from .mq_consumer import OntologyChangeEventConsumer
    from .schema_fetcher import SchemaFetcher
    from .codegen_engine import CodegenEngine
    from .file_generator import FileGenerator
    import os
    
    # FileGenerator 경로 설정
    sdk_base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    ontology_path = os.path.join(sdk_base_path, "ontology")
    
    # 컴포넌트 생성
    mq_consumer = ExampleMQConsumer(mq_config)
    schema_fetcher = SchemaFetcher(client)
    codegen_engine = CodegenEngine()
    file_generator = FileGenerator(ontology_path)
    
    # Consumer 생성
    consumer = OntologyChangeEventConsumer(
        mq_consumer=mq_consumer,
        schema_fetcher=schema_fetcher,
        codegen_engine=codegen_engine,
        file_generator=file_generator
    )
    
    return consumer


# 사용 예제
if __name__ == "__main__":
    from graphio_sdk import GraphioClient
    
    # 클라이언트 생성
    client = GraphioClient(base_url="http://localhost:8080")
    
    # MQ 설정
    mq_config = {
        "type": "rabbitmq",
        "host": "localhost",
        "port": 5672,
        "queue": "ontology-changes"
    }
    
    # Consumer 생성 및 시작
    consumer = create_codegen_consumer(client, mq_config)
    consumer.start()
    
    # 실행 중...
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        consumer.stop()

