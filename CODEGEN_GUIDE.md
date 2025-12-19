# Codegen 가이드

이 문서는 Ontology 기반 SDK의 Codegen 시스템 사용 방법을 설명합니다.

## 개요

SDK는 MQ로부터 Ontology 변경 이벤트를 수신하고, 이를 기반으로 Python class를 자동 생성합니다.

### 핵심 개념

1. **MQ 이벤트 소비**: OntologyChangeEvent를 MQ로부터 수신
2. **Schema 조회**: MQ payload만으로 codegen하지 않고, 항상 Service에서 schema를 다시 조회
3. **Python class 생성**: Schema를 기반으로 Python class 생성
4. **파일 생성**: `ontology_sdk/ontology/objects/*.py`, `ontology_sdk/ontology/links/*.py` 생성
5. **SDK 사용**: 생성된 class를 import하여 사용

## 구조

```
graphio_sdk/
├── codegen/              # Codegen 모듈
│   ├── mq_consumer.py    # MQ 이벤트 소비
│   ├── schema_fetcher.py # Schema 조회
│   ├── codegen_engine.py # Python class 생성
│   └── file_generator.py # 파일 생성 및 __init__.py 업데이트
└── ontology/             # 생성된 클래스들
    ├── base.py           # TypedObject, TypedLink base class
    ├── objects/          # ObjectType 클래스들
    │   ├── __init__.py
    │   ├── employee.py
    │   └── ticket.py
    └── links/            # LinkType 클래스들
        ├── __init__.py
        └── works_for.py
```

## MQ → Codegen 흐름

### 1. MQ 이벤트 수신

```python
from graphio_sdk.codegen import OntologyChangeEventConsumer, SchemaFetcher, CodegenEngine, FileGenerator
from graphio_sdk.codegen.example_mq_consumer import ExampleMQConsumer
from graphio_sdk import GraphioClient
import os

# 클라이언트 생성
client = GraphioClient(base_url="http://localhost:8080")

# MQ 설정
mq_config = {
    "type": "rabbitmq",
    "host": "localhost",
    "port": 5672,
    "queue": "ontology-changes"
}

# 컴포넌트 생성
mq_consumer = ExampleMQConsumer(mq_config)
schema_fetcher = SchemaFetcher(client)
codegen_engine = CodegenEngine()

# FileGenerator 경로 설정
sdk_base_path = os.path.dirname(os.path.dirname(__file__))
ontology_path = os.path.join(sdk_base_path, "graphio_sdk", "ontology")
file_generator = FileGenerator(ontology_path)

# Consumer 생성
consumer = OntologyChangeEventConsumer(
    mq_consumer=mq_consumer,
    schema_fetcher=schema_fetcher,
    codegen_engine=codegen_engine,
    file_generator=file_generator
)

# 시작
consumer.start()
```

### 2. 이벤트 처리

MQ에서 이벤트를 수신하면:

1. **이벤트 타입 확인**: ObjectType 또는 LinkType 이벤트인지 확인
2. **Schema 조회**: Ontology Service API를 호출하여 최신 schema 조회
3. **Class 생성**: Schema를 기반으로 Python class 코드 생성
4. **파일 작성**: `ontology/objects/` 또는 `ontology/links/` 디렉토리에 파일 생성
5. **__init__.py 업데이트**: import 문 추가

### 3. 생성된 파일 예시

**ontology/objects/employee.py**:
```python
"""
자동 생성된 ObjectType 클래스: Employee

이 파일은 codegen에 의해 자동 생성되었습니다. 수동으로 수정하지 마세요.
"""

from typing import Optional, Dict, Any
from ...ontology.base import TypedObject


class Employee(TypedObject):
    """
    Employee ObjectType
    
    ObjectType ID: 123e4567-e89b-12d3-a456-426614174000
    """
    
    _object_type_id = "123e4567-e89b-12d3-a456-426614174000"
    _object_type_name = "Employee"

    def __init__(
        self,
        element_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
        age: Optional[int] = None,
        email: Optional[str] = None,
    ):
        """
        Employee 객체 생성
        
        Args:
            element_id: Element ID (기존 객체인 경우)
            properties: 속성 딕셔너리
            name: STRING (nullable)
            age: INTEGER (nullable)
            email: STRING (nullable)
        """
        props = properties or {}
        
        kwargs_props = {
            "name": name,
            "age": age,
            "email": email,
        }
        props.update({k: v for k, v in kwargs_props.items() if v is not None})
        
        super().__init__(
            element_id=element_id,
            object_type_id=self._object_type_id,
            object_type_name=self._object_type_name,
            properties=props
        )
        
        for prop_name, prop_value in props.items():
            setattr(self, prop_name, prop_value)
```

## SDK 사용 흐름

### 1. 생성된 class import

```python
from graphio_sdk.ontology.objects import Employee
```

### 2. Object 생성

```python
# 방법 1: properties 딕셔너리 사용
emp = Employee(
    element_id="e-1",
    properties={
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com"
    }
)

# 방법 2: kwargs 사용
emp = Employee(
    element_id="e-1",
    name="John Doe",
    age=30,
    email="john@example.com"
)
```

### 3. Service API 호출

```python
from graphio_sdk import GraphioClient

client = GraphioClient(base_url="http://localhost:8080")

# 생성
client.insert(emp)

# 수정
emp.age = 31
client.update(emp)

# 삭제
client.delete(emp)
```

## SDK → Service 전달 규칙

SDK는 class를 Service로 그대로 전달하지 않고, Contract 형태로 변환합니다:

```python
# TypedObject.to_contract() 호출
contract = emp.to_contract()
# {
#     "objectType": "Employee",
#     "elementId": "e-1",
#     "properties": {
#         "name": "John Doe",
#         "age": 30,
#         "email": "john@example.com"
#     }
# }
```

## MQ 이벤트 형식

MQ에서 수신하는 이벤트는 다음 형식입니다:

```json
{
    "eventType": "OBJECT_TYPE_CREATED",
    "objectTypeId": "123e4567-e89b-12d3-a456-426614174000",
    "timestamp": "2025-01-01T00:00:00Z"
}
```

지원하는 이벤트 타입:
- `OBJECT_TYPE_CREATED`
- `OBJECT_TYPE_UPDATED`
- `OBJECT_TYPE_DELETED`
- `LINK_TYPE_CREATED`
- `LINK_TYPE_UPDATED`
- `LINK_TYPE_DELETED`

## 실제 MQ 구현

`example_mq_consumer.py`는 예제입니다. 실제 환경에서는 다음 중 하나를 사용하세요:

- **RabbitMQ**: `pika` 라이브러리
- **Kafka**: `kafka-python` 또는 `confluent-kafka`
- **Redis Streams**: `redis` 라이브러리
- **AWS SQS**: `boto3` 라이브러리

예제 (RabbitMQ):

```python
import pika
from graphio_sdk.codegen.mq_consumer import MQConsumer, OntologyChangeEvent

class RabbitMQConsumer(MQConsumer):
    def __init__(self, host, port, queue):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, port=port)
        )
        self.channel = self.connection.channel()
        self.queue = queue
        self._callback = None

    def start(self, callback):
        self._callback = callback
        self.channel.queue_declare(queue=self.queue)
        self.channel.basic_consume(
            queue=self.queue,
            on_message_callback=self._on_message,
            auto_ack=True
        )
        self.channel.start_consuming()

    def stop(self):
        self.channel.stop_consuming()
        self.connection.close()

    def _on_message(self, ch, method, properties, body):
        import json
        message = json.loads(body)
        event = OntologyChangeEvent.from_mq_message(message)
        if self._callback:
            self._callback(event)
```

## 주의사항

1. **수동 수정 금지**: 생성된 파일은 codegen에 의해 자동 생성되므로 수동으로 수정하지 마세요.
2. **Schema 조회**: MQ payload만으로 codegen하지 않고, 항상 Service에서 schema를 다시 조회합니다.
3. **타입 안정성**: SDK는 타입 안정성을 제공하지만, 최종 validation 책임은 Service에 있습니다.
4. **파일 구조**: `ontology/objects/`와 `ontology/links/` 디렉토리 구조를 유지하세요.

## 문제 해결

### 생성된 파일이 import되지 않음

- `__init__.py`가 올바르게 업데이트되었는지 확인
- Python 경로에 SDK가 포함되어 있는지 확인

### MQ 이벤트가 처리되지 않음

- MQ 연결 상태 확인
- 이벤트 형식이 올바른지 확인
- 로그 확인

### Schema 조회 실패

- Ontology Service 연결 상태 확인
- ObjectType/LinkType ID가 올바른지 확인
- API 권한 확인

