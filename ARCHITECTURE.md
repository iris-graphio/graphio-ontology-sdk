# SDK 아키텍처 문서

## 개요

이 SDK는 Ontology 기반 시스템의 Typed Facade이며, Python 개발자 경험(DX)을 책임집니다.

## 핵심 개념

1. **SDK는 ObjectType, LinkType을 Python class로 제공**
   - 런타임 동적 생성 방식
   - 필요할 때 서버에서 schema를 조회하여 동적으로 클래스 생성

2. **SDK는 Ontology Service를 Source of Truth로 봄**
   - 항상 Service에서 schema를 조회
   - Lazy Loading 방식으로 필요할 때만 로드

## 아키텍처 구조

```
graphio_sdk/
├── client.py                  # GraphioClient (insert, update, delete)
├── ontology.py                # OntologyNamespace (런타임 동적 로딩)
├── object_type.py             # ObjectTypeBase (동적 클래스 생성)
├── query.py                   # ObjectSetQuery (쿼리 빌더)
├── operators.py               # 연산자 및 조건
├── edits.py                   # 편집 기능
└── ...
```

## SDK 사용 흐름

### 1. ObjectType 동적 로드

```python
from graphio_sdk import GraphioClient

client = GraphioClient()
# 서버에서 schema를 조회하여 동적으로 클래스 생성
Employee = client.ontology.get_object_type("Employee")
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

- ✅ Ontology schema 조회
- ✅ 런타임 동적 클래스 생성
- ✅ Typed Object 제공
- ✅ Ontology Service API Client 제공
- ✅ 쿼리 빌더 및 편집 기능

### SDK가 하지 않는 것

- ❌ Ontology의 실제 변경 (Service 책임)
- ❌ 데이터 저장 (Service 책임)
- ❌ 최종 validation (Service 책임)

## 컴포넌트 상세

### 1. GraphioClient

Ontology Service API Client입니다.

- `insert(obj)`: Typed Object/Link 생성
- `update(obj)`: Typed Object/Link 업데이트
- `delete(obj)`: Typed Object/Link 삭제

### 2. OntologyNamespace

런타임에 ObjectType을 동적으로 로드하고 관리합니다.

- `get_object_type(name)`: ObjectType 클래스 가져오기 (Lazy Loading)
- `load_object_type(object_type_id, name)`: 서버에서 ObjectType 로드
- `register_object_type(name, object_type_id, properties)`: 수동 등록
- `list_object_types()`: 캐시된 ObjectType 목록
- `clear_cache()`: 캐시 클리어

### 3. ObjectTypeBase

동적으로 생성되는 ObjectType 클래스의 베이스 클래스입니다.

- 쿼리 빌더 메서드 제공 (`where`, `select`, `execute` 등)
- 속성 디스크립터를 통한 동적 속성 접근

### 4. ObjectSetQuery

쿼리 빌더 클래스입니다.

- `select(*fields)`: 조회할 필드 선택
- `where(*conditions)`: 조건 추가
- `limit(count)`: 결과 개수 제한
- `execute()`: 쿼리 실행
- `count()`, `first()`, `exists()`: 유틸리티 메서드

## 타입 안정성

SDK는 런타임 동적 생성 방식을 사용하지만, 다음과 같은 기능을 제공합니다:

- 동적으로 생성된 속성 디스크립터를 통한 타입 안전한 접근
- IDE 자동완성 지원 (동적 속성)
- 런타임 타입 체크 (선택적)

하지만 최종 validation 책임은 Service에 있습니다.

## 참고 문서

- [README.md](./README.md): SDK 사용 가이드

