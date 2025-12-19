"""
MQ Consumer - OntologyChangeEvent 수신
"""

import json
import logging
from typing import Callable, Optional, Dict, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class OntologyChangeEvent:
    """Ontology 변경 이벤트"""

    def __init__(self, event_type: str, object_type_id: Optional[str] = None, 
                 link_type_id: Optional[str] = None, payload: Optional[Dict[str, Any]] = None):
        """
        Args:
            event_type: 이벤트 타입 ("OBJECT_TYPE_CREATED", "OBJECT_TYPE_UPDATED", 
                       "OBJECT_TYPE_DELETED", "LINK_TYPE_CREATED", "LINK_TYPE_UPDATED", 
                       "LINK_TYPE_DELETED")
            object_type_id: ObjectType ID (ObjectType 이벤트인 경우)
            link_type_id: LinkType ID (LinkType 이벤트인 경우)
            payload: 원본 이벤트 payload
        """
        self.event_type = event_type
        self.object_type_id = object_type_id
        self.link_type_id = link_type_id
        self.payload = payload or {}

    @classmethod
    def from_mq_message(cls, message: Dict[str, Any]) -> 'OntologyChangeEvent':
        """MQ 메시지로부터 이벤트 생성"""
        event_type = message.get("eventType", "")
        object_type_id = message.get("objectTypeId")
        link_type_id = message.get("linkTypeId")
        
        return cls(
            event_type=event_type,
            object_type_id=object_type_id,
            link_type_id=link_type_id,
            payload=message
        )

    def is_object_type_event(self) -> bool:
        """ObjectType 관련 이벤트인지 확인"""
        return self.object_type_id is not None

    def is_link_type_event(self) -> bool:
        """LinkType 관련 이벤트인지 확인"""
        return self.link_type_id is not None


class MQConsumer(ABC):
    """MQ Consumer 추상 클래스"""

    @abstractmethod
    def start(self, callback: Callable[[OntologyChangeEvent], None]):
        """MQ 소비 시작"""
        pass

    @abstractmethod
    def stop(self):
        """MQ 소비 중지"""
        pass


class OntologyChangeEventConsumer:
    """
    OntologyChangeEvent 소비자
    
    MQ로부터 이벤트를 수신하고 codegen을 트리거합니다.
    """

    def __init__(self, mq_consumer: MQConsumer, schema_fetcher: 'SchemaFetcher', 
                 codegen_engine: 'CodegenEngine', file_generator: 'FileGenerator'):
        """
        Args:
            mq_consumer: MQ Consumer 구현체
            schema_fetcher: Schema 조회기
            codegen_engine: Codegen 엔진
            file_generator: 파일 생성기
        """
        self.mq_consumer = mq_consumer
        self.schema_fetcher = schema_fetcher
        self.codegen_engine = codegen_engine
        self.file_generator = file_generator
        self._running = False

    def _handle_event(self, event: OntologyChangeEvent):
        """이벤트 처리"""
        try:
            logger.info(f"Ontology 변경 이벤트 수신: {event.event_type}")
            
            if event.is_object_type_event():
                self._handle_object_type_event(event)
            elif event.is_link_type_event():
                self._handle_link_type_event(event)
            else:
                logger.warning(f"알 수 없는 이벤트 타입: {event.event_type}")
                
        except Exception as e:
            logger.error(f"이벤트 처리 실패: {e}", exc_info=True)

    def _handle_object_type_event(self, event: OntologyChangeEvent):
        """ObjectType 이벤트 처리"""
        if event.event_type.endswith("_DELETED"):
            # 삭제 이벤트: 파일 삭제
            self.file_generator.delete_object_type_file(event.object_type_id)
        else:
            # 생성/수정 이벤트: Schema 조회 후 codegen
            schema = self.schema_fetcher.fetch_object_type_schema(event.object_type_id)
            if schema:
                class_code = self.codegen_engine.generate_object_type_class(schema)
                self.file_generator.write_object_type_file(
                    schema["name"], 
                    event.object_type_id,
                    class_code
                )

    def _handle_link_type_event(self, event: OntologyChangeEvent):
        """LinkType 이벤트 처리"""
        if event.event_type.endswith("_DELETED"):
            # 삭제 이벤트: 파일 삭제
            self.file_generator.delete_link_type_file(event.link_type_id)
        else:
            # 생성/수정 이벤트: Schema 조회 후 codegen
            schema = self.schema_fetcher.fetch_link_type_schema(event.link_type_id)
            if schema:
                class_code = self.codegen_engine.generate_link_type_class(schema)
                self.file_generator.write_link_type_file(
                    schema["name"],
                    event.link_type_id,
                    class_code
                )

    def start(self):
        """이벤트 소비 시작"""
        if self._running:
            logger.warning("이미 실행 중입니다.")
            return

        self._running = True
        logger.info("OntologyChangeEvent 소비 시작")
        self.mq_consumer.start(self._handle_event)

    def stop(self):
        """이벤트 소비 중지"""
        if not self._running:
            return

        self._running = False
        logger.info("OntologyChangeEvent 소비 중지")
        self.mq_consumer.stop()

