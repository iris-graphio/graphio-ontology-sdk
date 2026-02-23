# Graphio Ontology SDK

Python 클라이언트 for Graphio Ontology Service

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)

## 📋 목차

- [소개](#소개)
- [주요 특징](#주요-특징)
- [설치](#설치)
- [빠른 시작](#빠른-시작)
- [사용 방법](#사용-방법)
    - [환경 변수 설정](#환경-변수-설정)
    - [ObjectType 로드](#objecttype-로드)
    - [쿼리](#쿼리)
    - [편집](#편집)
- [API 문서](#api-문서)
- [예제](#예제)
- [고급 사용법](#고급-사용법)
- [문제 해결](#문제-해결)
- [기여](#기여)
- [라이선스](#라이선스)

## 소개

Graphio Ontology SDK는 GraphIO Ontology Service와 상호작용하기 위한 Python 클라이언트입니다.
직관적인 API를 제공하여 데이터 조회, 생성, 수정을 쉽게 수행할 수 있습니다.

### 주요 기능

- ✅ **Fluent API**: 체이닝 방식의 직관적인 쿼리 빌더
- ✅ **Lazy Loading**: 필요할 때만 ObjectType 자동 로드
- ✅ **환경 변수 지원**: 설정을 코드에서 분리
- ✅ **실제 데이터 조회**: 데이터베이스에서 실제 데이터 조회

## 주요 특징

### 🚀 간단한 사용법

```python
from graphio_sdk import GraphioClient

# 환경 변수에서 자동으로 base_url 읽기
client = GraphioClient()

# ObjectType 로드 및 쿼리
Employee = client.ontology.get_object_type("Employee")
employees = Employee.where(Employee.age > 30).select("name", "age").execute()

# MetaType list 출력 API 실행
meta_type_list = client.meta_type.manage.list()
```

### 🔄 자동 리소스 관리

```python
# with 문 없이도 안전하게 사용 가능
client = GraphioClient()
Employee = client.ontology.get_object_type("Employee")
result = Employee.select("name").execute()
# 자동으로 리소스 정리됨
```

## 설치

### pip로 설치 (TODO)

```bash
pip install graphio-sdk
```

### 소스에서 설치

```bash
# 최신 버전
git clone https://github.com/iris-graphio/graphio-ontology-sdk.git
# v0.1.0
git clone https://github.com/iris-graphio/graphio-ontology-sdk.git@v0.1.0
# v1.0.0
git clone https://github.com/iris-graphio/graphio-ontology-sdk.git@v1.0.0

cd graphio-sdk
pip install -e .
```

### 의존성

- Python 3.11+
- requests >= 2.25.0

## 빠른 시작

### 1. 환경 변수 설정 (선택적)

```bash
# Linux/Mac
export GRAPHIO_BASE_URL=http://localhost:8080

# Windows (PowerShell)
$env:GRAPHIO_BASE_URL="http://localhost:8080"
```

### 2. 기본 사용

```python
from graphio_sdk import GraphioClient

# 클라이언트 초기화
client = GraphioClient()

# ObjectType 로드
Employee = client.ontology.get_object_type("Employee")

# 쿼리 실행
employees = (Employee
    .where(Employee.age > 30)
    .select("name", "age", "email", "department")
    .limit(10)
    .execute())

# 결과 출력
for emp in employees:
    print(f"{emp['name']}: {emp['age']}세, {emp['department']}")
```

### 3. 편집

```python
# 편집 세션 시작
edits = client.ontology.edits()

# 새 객체 생성
new_emp = edits.objects.Employee.create({
    "name": "John Doe",
    "age": 35,
    "email": "john@example.com",
    "department": "Engineering"
})

# 커밋
edits.commit()
```

## 사용 방법

### 환경 변수 설정

#### Linux/Mac (bash/zsh)

```bash
# 임시 설정
export GRAPHIO_BASE_URL=http://localhost:8080

# 영구 설정 (~/.bashrc 또는 ~/.zshrc에 추가)
echo 'export GRAPHIO_BASE_URL=http://localhost:8080' >> ~/.bashrc
source ~/.bashrc
```

#### Windows (PowerShell)

```powershell
# 임시 설정
$env:GRAPHIO_BASE_URL="http://localhost:8080"

# 영구 설정
[System.Environment]::SetEnvironmentVariable("GRAPHIO_BASE_URL", "http://localhost:8080", "User")
```

#### Python 코드에서 설정

```python
import os
os.environ["GRAPHIO_BASE_URL"] = "http://localhost:8080"

from graphio_sdk import GraphioClient
client = GraphioClient()  # 자동으로 환경 변수 사용
```

#### .env 파일 사용 (python-dotenv)

```bash
# .env 파일
GRAPHIO_BASE_URL=http://localhost:8080
```

```python
from dotenv import load_dotenv
load_dotenv()

from graphio_sdk import GraphioClient
client = GraphioClient()  # .env에서 자동으로 읽음
```

### ObjectType 로드

#### 자동 로드 (Lazy Loading)

```python
client = GraphioClient()

# 처음 사용 시 자동으로 서버에서 로드
Employee = client.ontology.get_object_type("Employee")
```

#### 명시적 로드

```python
# 이름으로 로드
Employee = client.ontology.load_object_type(name="Employee")

# ID로 로드
Employee = client.ontology.load_object_type(
    object_type_id="123e4567-e89b-12d3-a456-426614174000"
)
```

#### 수동 등록

```python
# 서버 접근 없이 직접 등록
Employee = client.ontology.register_object_type(
    "Employee",
    "123e4567-e89b-12d3-a456-426614174000",
    properties=["name", "age", "email", "department"]
)
```

#### 한글 ObjectType 이름

```python
# 한글 이름도 지원
unit = client.ontology.get_object_type("유닛")
results = unit.where(unit.x > 650).select("*").execute()
```

### 쿼리

#### 기본 쿼리

```python
Employee = client.ontology.get_object_type("Employee")

# 단순 조건
result = Employee.where(Employee.age > 30).select("name", "age").execute()

# 모든 필드 선택
result = Employee.select("*").execute()

# 제한
result = Employee.select("name", "age").limit(10).execute()
```

#### 비교 연산자

```python
# 크기 비교
Employee.where(Employee.age > 30)
Employee.where(Employee.age >= 30)
Employee.where(Employee.age < 50)
Employee.where(Employee.age <= 50)

# 동등 비교
Employee.where(Employee.name == "John")
Employee.where(Employee.name != "Jane")
```

#### LIKE 검색

```python
# 패턴 매칭
Employee.where(Employee.name.like("John%"))
Employee.where(Employee.email.like("%@example.com"))
```

#### IN 조건

```python
# 여러 값 중 하나
Employee.where(Employee.department.is_in(["Sales", "Marketing", "HR"]))
```

#### NULL 체크

```python
# NULL 여부 확인
Employee.where(Employee.middle_name.is_null())
Employee.where(Employee.email.is_not_null())
```

#### 복잡한 조건 (AND/OR)

```python
from graphio_sdk import LogicalCondition

# AND 조건
result = (Employee
    .where(
        LogicalCondition("and", [
            Employee.age > 30,
            Employee.department == "Engineering"
        ])
    )
    .select("name", "age", "department")
    .execute())

# OR 조건
result = (Employee
    .where(
        LogicalCondition("or", [
            Employee.age < 25,
            Employee.age > 50
        ])
    )
    .select("name", "age")
    .execute())

# 중첩 조건
result = (Employee
    .where(
        LogicalCondition("and", [
            LogicalCondition("or", [
                Employee.age > 40,
                Employee.department == "Sales"
            ]),
            Employee.active == True
        ])
    )
    .select("name", "age", "department")
    .execute())
```

#### 유틸리티 메서드

```python
# 개수 세기
count = Employee.where(Employee.age > 30).select("name").count()

# 첫 번째 레코드
first = Employee.select("name", "age").first()

# 존재 여부 확인
exists = Employee.where(Employee.department == "Sales").select("name").exists()
```

### 편집

#### 객체 생성

```python
edits = client.ontology.edits()

# 딕셔너리로 생성
new_emp = edits.objects.Employee.create({
    "name": "Alice Johnson",
    "age": 32,
    "email": "alice@example.com",
    "department": "Marketing"
})

# 또는 kwargs 사용
new_emp = edits.objects.Employee.create(
    name="Bob Williams",
    age=45,
    email="bob@example.com"
)

# 커밋
edits.commit()
```

#### 객체 수정

```python
edits = client.ontology.edits()

# 기존 객체 편집
existing = {
    "elementId": "(0,13):713518e7-e1be-4b65-ab42-507d0a9b5085",
    "properties": {"name": "Jane Doe", "age": 28}
}

edited_emp = edits.objects.Employee.edit(existing)
edited_emp.age = 29
edited_emp.department = "Engineering"

# 커밋
edits.commit()
```

#### 편집 내역 확인

```python
edits = client.ontology.edits()

# 편집 추가
new_emp = edits.objects.Employee.create({"name": "John", "age": 30})

# 커밋 전 확인
edit_list = edits.get_edits()
print(f"커밋할 내역: {len(edit_list)}개")

# 커밋
edits.commit()
```

## API 문서

### GraphioClient

#### `__init__(base_url=None, timeout=30)`

클라이언트 초기화

**Parameters:**
- `base_url` (str, optional): API 서버의 base URL. None이면 환경 변수 `GRAPHIO_BASE_URL`을 확인하고, 없으면 기본값 `"http://localhost:8080"` 사용
- `timeout` (int, optional): 요청 타임아웃 시간(초), 기본값 30초

**Example:**
```python
# 환경 변수 사용
client = GraphioClient()

# 명시적 지정
client = GraphioClient(base_url="http://your-server:8080", timeout=60)
```

#### `close()`

세션 종료 (명시적 호출)

**Note:** 가비지 컬렉션 시 자동으로 호출되므로 대부분의 경우 명시적 호출 불필요

### OntologyNamespace

#### `get_object_type(name) -> Optional[type]`

ObjectType 클래스 가져오기 (Lazy Loading)

**Parameters:**
- `name` (str): ObjectType 이름

**Returns:**
- ObjectType 클래스 또는 None (로드 실패 시)

**Example:**
```python
Employee = client.ontology.get_object_type("Employee")
```

#### `load_object_type(object_type_id=None, name=None) -> type`

특정 ObjectType을 서버에서 가져와 등록

**Parameters:**
- `object_type_id` (str, optional): ObjectType UUID
- `name` (str, optional): ObjectType 이름

**Returns:**
- 등록된 ObjectType 클래스

**Example:**
```python
Employee = client.ontology.load_object_type(name="Employee")
```

#### `register_object_type(name, object_type_id, properties=None) -> type`

ObjectType 수동 등록

**Parameters:**
- `name` (str): ObjectType 이름
- `object_type_id` (str): ObjectType UUID
- `properties` (List[str], optional): 속성 이름 리스트

**Returns:**
- 생성된 ObjectType 클래스

#### `list_object_types() -> List[str]`

캐시된 ObjectType 이름 목록

**Returns:**
- ObjectType 이름 리스트

#### `edits() -> OntologyEditsBuilder`

편집 세션 시작

**Returns:**
- OntologyEditsBuilder 인스턴스

### ObjectSetQuery

#### `select(*fields) -> ObjectSetQuery`

조회할 필드 선택

**Parameters:**
- `*fields` (str): 조회할 필드명들. `'*'`를 사용하면 모든 필드 선택

**Returns:**
- 자기 자신 (메서드 체이닝용)

**Example:**
```python
query.select("name", "age")
query.select("*")  # 모든 필드
```

#### `where(*conditions) -> ObjectSetQuery`

조건 추가

**Parameters:**
- `*conditions`: 조건들 (Condition 또는 LogicalCondition)

**Returns:**
- 자기 자신 (메서드 체이닝용)

#### `limit(count) -> ObjectSetQuery`

결과 개수 제한

**Parameters:**
- `count` (int): 최대 개수

**Returns:**
- 자기 자신 (메서드 체이닝용)

#### `execute() -> List[Dict[str, Any]]`

쿼리 실행 - 실제 데이터베이스에서 데이터 조회

**Returns:**
- 조회된 데이터 리스트

**Raises:**
- `ValueError`: select 필드가 없을 때
- `Exception`: API 호출 실패 시

#### `count() -> int`

조건에 맞는 레코드 개수 반환

**Returns:**
- 레코드 개수

#### `first() -> Optional[Dict[str, Any]]`

첫 번째 레코드만 반환

**Returns:**
- 첫 번째 레코드 또는 None

#### `exists() -> bool`

조건에 맞는 레코드가 존재하는지 확인

**Returns:**
- 존재 여부

### OntologyEditsBuilder

#### `objects.<ObjectType>.create(properties=None, **kwargs) -> EditableObject`

새 객체 생성

**Parameters:**
- `properties` (dict, optional): 속성 딕셔너리
- `**kwargs`: 속성 키워드 인자

**Returns:**
- EditableObject 인스턴스

#### `objects.<ObjectType>.edit(existing_object) -> EditableObject`

기존 객체 편집

**Parameters:**
- `existing_object`: dict 또는 EditableObject

**Returns:**
- EditableObject 인스턴스

#### `get_edits() -> List[Dict[str, Any]]`

모든 편집 내용을 리스트로 반환 (커밋하지 않음)

**Returns:**
- 편집 내역 리스트

#### `commit() -> Dict[str, Any]`

변경사항을 서버에 커밋

**Returns:**
- 커밋 결과 딕셔너리

## 예제

### 예제 1: 기본 데이터 조회

```python
from graphio_sdk import GraphioClient

client = GraphioClient()

# ObjectType 로드
Employee = client.ontology.get_object_type("Employee")

# 쿼리 실행
employees = (Employee
    .where(Employee.age > 30)
    .select("name", "age", "email", "department")
    .limit(10)
    .execute())

# 결과 출력
for emp in employees:
    print(f"{emp['name']}: {emp['age']}세, {emp['department']}")
```

### 예제 2: 모든 필드 선택

```python
client = GraphioClient()
Employee = client.ontology.get_object_type("Employee")

# 모든 필드 선택
all_fields = Employee.where(Employee.age > 30).select("*").execute()

print(f"필드 목록: {list(all_fields[0].keys())}")
```

### 예제 3: 복잡한 조건

```python
from graphio_sdk import GraphioClient, LogicalCondition

client = GraphioClient()
Employee = client.ontology.get_object_type("Employee")

# AND/OR 조건
result = (Employee
    .where(
        LogicalCondition("and", [
            Employee.age > 30,
            LogicalCondition("or", [
                Employee.department == "Engineering",
                Employee.department == "Sales"
            ])
        ])
    )
    .select("name", "age", "department")
    .execute())
```

### 예제 4: 유틸리티 메서드

```python
client = GraphioClient()
Employee = client.ontology.get_object_type("Employee")

# 개수 세기
count = Employee.where(Employee.age > 30).select("name").count()
print(f"30세 이상: {count}명")

# 첫 번째 레코드
first = Employee.select("name", "age").first()
if first:
    print(f"첫 번째: {first['name']}")

# 존재 여부
exists = Employee.where(Employee.department == "Sales").select("name").exists()
print(f"Sales 부서 존재: {exists}")
```

### 예제 5: 편집

```python
client = GraphioClient()
edits = client.ontology.edits()

# 생성
new_emp = edits.objects.Employee.create({
    "name": "John Doe",
    "age": 35,
    "email": "john@example.com"
})

# 수정
existing = {"elementId": "...", "properties": {...}}
edited = edits.objects.Employee.edit(existing)
edited.age = 36

# 커밋
edits.commit()
```

### 예제 6: 한글 ObjectType

```python
client = GraphioClient()

# 한글 ObjectType 이름 사용
unit = client.ontology.get_object_type("유닛")

# 쿼리
results = (unit
    .where(unit.x > 650)
    .select("*")
    .limit(10)
    .execute())
```

## 고급 사용법

### Context Manager 사용

```python
# with 문을 사용해도 되고
with GraphioClient() as client:
    Employee = client.ontology.get_object_type("Employee")
    result = Employee.select("name").execute()

# 사용하지 않아도 됨 (자동 정리)
client = GraphioClient()
Employee = client.ontology.get_object_type("Employee")
result = Employee.select("name").execute()
```

### 여러 클라이언트 인스턴스

```python
# 여러 클라이언트를 동시에 사용 가능
client1 = GraphioClient(base_url="http://server1:8080")
client2 = GraphioClient(base_url="http://server2:8080")

Employee1 = client1.ontology.get_object_type("Employee")
Employee2 = client2.ontology.get_object_type("Employee")
```

### 캐시 관리

```python
client = GraphioClient()

# ObjectType 로드
Employee = client.ontology.get_object_type("Employee")

# 캐시된 ObjectType 목록
cached = client.ontology.list_object_types()
print(f"캐시된 ObjectType: {cached}")

# 캐시 클리어
client.ontology.clear_cache()
```

### 커스텀 타임아웃

```python
# 긴 작업을 위한 타임아웃 설정
client = GraphioClient(base_url="http://localhost:8080", timeout=120)
```

## 문제 해결

### ObjectType을 찾을 수 없습니다

```python
# ObjectType 이름 확인
Employee = client.ontology.get_object_type("Employee")
if not Employee:
    print("ObjectType을 찾을 수 없습니다.")
    # 서버에 등록되어 있는지 확인하세요
```

### 네트워크 에러

```python
# base_url 확인
client = GraphioClient()
print(f"Base URL: {client.base_url}")

# 타임아웃 증가
client = GraphioClient(timeout=60)
```

### select 필드 오류

```python
# select()를 먼저 호출해야 함
try:
    result = Employee.where(Employee.age > 30).execute()
except ValueError as e:
    print(f"에러: {e}")
    # 올바른 사용법
    result = Employee.where(Employee.age > 30).select("name").execute()
```

## 기여

기여를 환영합니다! 이슈를 등록하거나 Pull Request를 보내주세요.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 라이선스

이 프로젝트는 MIT License 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 지원

- **이슈**: [GitHub Issues](https://github.com/iris-graphio/graphio-ontology-sdk/issues)

## 변경 이력

### v0.1.0 (2025-01-XX)

- 초기 릴리스
- 기본 쿼리 기능
- 편집 기능
- 환경 변수 지원
- Lazy Loading
- 자동 리소스 관리

---

**Made with ❤️ by Graphio Team**
