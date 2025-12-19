# SDK 아키텍처 문서

## 개요

이 SDK는 Ontology 기반 시스템의 Typed Facade이며, Python 개발자 경험(DX)을 책임집니다.

## 핵심 개념

1. **SDK는 ObjectType, LinkType을 Python class로 제공**
   - 런타임 동적 생성이 아니라 codegen 결과물
   - `graphio_sdk/ontology/objects/` - ObjectType classes
   - `graphio_sdk/ontology/links/` - LinkType classes

2. **SDK는 Ontology Service를 Source of Truth로 봄**
   - MQ payload만으로 codegen하지 않음
   - 항상 Service에서 schema를 다시 조회

3. **SDK는 ObjectType / LinkType 변경 이벤트를 MQ로부터 수신**
   - `OntologyChangeEvent` 수신
   - 이벤트를 트리거로 codegen 실행

## 아키텍처 구조

```
graphio_sdk/
├── codegen/                    # Codegen 모듈
│   ├── __init__.py
│   ├── mq_consumer.py          # MQ 이벤트 소비
│   ├── schema_fetcher.py      # Schema 조회
│   ├── codegen_engine.py      # Python class 생성
│   ├── file_generator.py      # 파일 생성 및 __init__.py 업데이트
│   └── example_mq_consumer.py # 예제 MQ Consumer 구현
├── ontology/                   # 생성된 클래스들
│   ├── __init__.py
│   ├── base.py                # TypedObject, TypedLink base class
│   ├── objects/               # ObjectType 클래스들 (codegen)
│   │   ├── __init__.py
│   │   ├── employee.py
│   │   └── ticket.py
│   └── links/                 # LinkType 클래스들 (codegen)
│       ├── __init__.py
│       └── works_for.py
├── client.py                  # GraphioClient (insert, update, delete)
├── ontology.py                # OntologyNamespace (기존 런타임 로딩)
└── ...
```

## MQ → Codegen 흐름

### 1. MQ 이벤트 수신

```python
# MQ에서 OntologyChangeEvent 수신
event = OntologyChangeEvent.from_mq_message(mq_message)
# {
#     "eventType": "OBJECT_TYPE_CREATED",
#     "objectTypeId": "123e4567-...",
#     ...
# }
```

### 2. Schema 조회

```python
# Ontology Service API 호출
schema = schema_fetcher.fetch_object_type_schema(object_type_id)
# {
#     "id": "123e4567-...",
#     "name": "Employee",
#     "properties": [
#         {"name": "name", "type": "STRING", "nullable": True},
#         {"name": "age", "type": "INTEGER", "nullable": True},
#         ...
#     ]
# }
```

### 3. Python Class 생성

```python
# Schema를 기반으로 Python class 코드 생성
class_code = codegen_engine.generate_object_type_class(schema)
```

생성된 코드 예시:
```python
class Employee(TypedObject):
    _object_type_id = "123e4567-..."
    _object_type_name = "Employee"
    
    def __init__(self, element_id=None, properties=None, name=None, age=None, ...):
        ...
```

### 4. 파일 생성

```python
# ontology/objects/employee.py 생성
file_generator.write_object_type_file(
    class_name="Employee",
    object_type_id="123e4567-...",
    class_code=class_code
)

# ontology/objects/__init__.py 업데이트
# from .employee import Employee
# __all__ = ["Employee"]
```

### 5. SDK 패키지 재생성/갱신

생성된 파일들이 Python 패키지에 포함되어 사용 가능해집니다.

## SDK 사용 흐름

### 1. 생성된 class import

```python
from graphio_sdk.ontology.objects import Employee
```

### 2. Object 생성

```python
emp = Employee(
    element_id="e-1",
    properties={
        "name": "John",
        "age": 30
    }
)
# 또는
emp = Employee(
    element_id="e-1",
    name="John",
    age=30
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
#         "name": "John",
#         "age": 30
#     }
# }
```

이 Contract가 Service API로 전달됩니다.

## 책임 분리

### SDK 책임

- ✅ MQ 이벤트 소비
- ✅ Ontology schema 조회
- ✅ Python class codegen
- ✅ Typed Object 제공
- ✅ Ontology Service API Client 제공

### SDK가 하지 않는 것

- ❌ Ontology의 실제 변경 (Service 책임)
- ❌ 데이터 저장 (Service 책임)
- ❌ 최종 validation (Service 책임)

## 컴포넌트 상세

### 1. OntologyChangeEventConsumer

MQ 이벤트를 수신하고 codegen을 트리거합니다.

- `start()`: 이벤트 소비 시작
- `stop()`: 이벤트 소비 중지
- `_handle_event()`: 이벤트 처리

### 2. SchemaFetcher

Ontology Service에서 Schema를 조회합니다.

- `fetch_object_type_schema()`: ObjectType Schema 조회
- `fetch_link_type_schema()`: LinkType Schema 조회

### 3. CodegenEngine

Schema를 Python class 코드로 변환합니다.

- `generate_object_type_class()`: ObjectType class 생성
- `generate_link_type_class()`: LinkType class 생성

### 4. FileGenerator

Python 파일을 생성하고 `__init__.py`를 업데이트합니다.

- `write_object_type_file()`: ObjectType 파일 생성
- `write_link_type_file()`: LinkType 파일 생성
- `_update_objects_init()`: objects/__init__.py 업데이트
- `_update_links_init()`: links/__init__.py 업데이트

### 5. TypedObject / TypedLink

생성된 class들이 상속하는 base class입니다.

- `to_contract()`: Service Contract 형태로 변환
- `_get_all_properties()`: 모든 속성을 딕셔너리로 반환

### 6. GraphioClient

Ontology Service API Client입니다.

- `insert(obj)`: Typed Object/Link 생성
- `update(obj)`: Typed Object/Link 업데이트
- `delete(obj)`: Typed Object/Link 삭제

## 타입 안정성

SDK는 타입 안정성을 제공합니다:

- 생성된 class에 타입 힌트 포함
- IDE 자동완성 지원
- 런타임 타입 체크 (선택적)

하지만 최종 validation 책임은 Service에 있습니다.

## 확장성

### 새로운 MQ 구현

`MQConsumer` 추상 클래스를 상속하여 구현:

```python
class MyMQConsumer(MQConsumer):
    def start(self, callback):
        # MQ 소비 시작
        pass
    
    def stop(self):
        # MQ 소비 중지
        pass
```

### 커스텀 Codegen

`CodegenEngine`을 상속하여 커스텀 로직 추가 가능:

```python
class CustomCodegenEngine(CodegenEngine):
    def generate_object_type_class(self, schema):
        # 커스텀 로직
        code = super().generate_object_type_class(schema)
        # 추가 처리
        return code
```

## 참고 문서

- [CODEGEN_GUIDE.md](./CODEGEN_GUIDE.md): Codegen 사용 가이드
- [README.md](./README.md): SDK 사용 가이드

