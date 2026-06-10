# MetaType 테이블 데이터 가져오기

MetaType(데이터 자산)의 **실제 테이블 데이터**와 **테이블 메타 정보**를 조회하는 방법을
정리한 문서입니다. 관련 API는 모두 `client.meta_type.table_data`
(`MetaTableAPI`) 네임스페이스에 모여 있습니다.

> 모든 메서드는 `meta_type_id`를 인자로 받습니다. `meta_type_id`는
> `client.meta_type.manage.list()`로 얻은 `MetaTypeDto`의 `.id` 값을 사용하세요.

---

## 한눈에 보기

| 목적 | 메서드 | 반환 타입 |
| --- | --- | --- |
| 테이블 전체 행 데이터 | `table_data.all_data(meta_type_id)` | `{"data": List[Dict], "totalCount": int}` |
| 미리보기(상위 N행) | `table_data.sample_data_param(meta_type_id, page, size)` | `List[Dict]` |
| 테이블 메타 정보 | `table_data.meta_type_table(meta_type_id)` | `Dict[str, Any]` |
| 물리 테이블 목록 | `table_data.table_list(connection_instance_id, schema_name, meta_type_kind)` | `List[str]` |
| 물리 컬럼 목록 | `table_data.table_columns(connection_instance_id, schema_name, table_name)` | `List[Dict]` |

---

## 1. 전체 데이터 가져오기 — `all_data`

MetaType 테이블의 모든 행을 가져옵니다. 전체 건수(`totalCount`)도 함께 반환합니다.

```python
from graphio_sdk import GraphioClient

client = GraphioClient()

result = client.meta_type.table_data.all_data(meta_type_id="<META_TYPE_ID>")
# {"data": [ {...}, {...} ], "totalCount": 1234}

print(f"총 {result['totalCount']}건")
for row in result["data"]:
    print(row)
```

- **HTTP**: `GET /graphio/v1/meta-type/all-data?metaTypeId=<id>`
- **반환**: `{"data": <행 리스트>, "totalCount": <전체 건수>}`
- **용도**: 테이블 데이터를 통째로 내려받아 처리할 때 (기본 선택지)

---

## 2. 미리보기(샘플) 가져오기 — `sample_data_param`

전체가 아니라 상위 몇 건만 빠르게 확인할 때 사용합니다. 페이지네이션을 지원하므로
대용량 테이블을 페이지 단위로 끊어 가져올 수도 있습니다.

```python
sample = client.meta_type.table_data.sample_data_param(
    meta_type_id="<META_TYPE_ID>",
    page=0,    # 0부터 시작
    size=10,   # 페이지 크기
)

for row in sample:
    print(row)
```

- **HTTP**: `GET /graphio/v1/meta-type/inspect/sample-data-param?metaTypeId=<id>&page=0&size=10`
- **반환**: `List[Dict]` (행 리스트)
- **용도**: 카탈로그 미리보기, 데이터 형태 확인, 페이지 단위 조회

### 페이지를 끝까지 순회하기

```python
def iter_all_rows(client, meta_type_id, page_size=100):
    """sample_data_param을 페이지 단위로 끝까지 순회하는 제너레이터."""
    page = 0
    while True:
        rows = client.meta_type.table_data.sample_data_param(
            meta_type_id, page=page, size=page_size
        )
        if not rows:
            break
        yield from rows
        if len(rows) < page_size:   # 마지막 페이지
            break
        page += 1


for row in iter_all_rows(client, "<META_TYPE_ID>", page_size=100):
    print(row)
```

---

## 3. 테이블 메타 정보 — `meta_type_table`

행 데이터가 아니라 **테이블 자체의 메타 정보**(`Map<String, Object>`)를 가져옵니다.

```python
table_meta = client.meta_type.table_data.meta_type_table(meta_type_id="<META_TYPE_ID>")
print(table_meta)
```

- **HTTP**: `GET /graphio/v1/meta-type/meta-type-table/{meta-type-id}`
- **반환**: `Dict[str, Any]`

---

## 4. 물리 스키마 탐색 — `table_list` / `table_columns`

MetaType을 만들기 **전에**, 연결된 데이터 소스(DB)의 실제 스키마를 탐색할 때 사용합니다.

```python
# (1) 스키마 안의 테이블 목록
tables = client.meta_type.table_data.table_list(
    connection_instance_id="<CONN_ID>",
    schema_name="public",
    meta_type_kind="TABLE",   # TABLE / VIEW / FILE
)
print(tables)   # ["customer", "orders", ...]

# (2) 특정 테이블의 컬럼 목록
columns = client.meta_type.table_data.table_columns(
    connection_instance_id="<CONN_ID>",
    schema_name="public",
    table_name="customer",
)
for col in columns:
    print(col)
```

- **HTTP**:
  - `GET /graphio/v1/meta-type/table-list?connectionInstanceId=...&schemaName=...&metaTypeKind=...`
  - `GET /graphio/v1/meta-type/table-columns?connectionInstanceId=...&schemaName=...&tableName=...`
- **반환**: 각각 `List[str]`, `List[Dict]`

---

## 어떤 메서드를 써야 할까?

```
테이블 데이터를 가져오고 싶다
├─ 전체 행이 필요하다 ............................ all_data(id)
├─ 상위 N행 미리보기면 충분하다 ................... sample_data_param(id, 0, N)
├─ 대용량을 페이지 단위로 끊어서 받고 싶다 ........ sample_data_param(id, page, size) 반복
├─ 데이터가 아니라 테이블 메타 정보가 필요하다 .... meta_type_table(id)
└─ 아직 MetaType이 없고 원본 DB 스키마를 탐색 중이다
   ├─ 테이블 목록 .............................. table_list(conn, schema, kind)
   └─ 컬럼 목록 ................................ table_columns(conn, schema, table)
```

---

## 전체 예제

```python
"""fetch_metatype_table.py — MetaType 테이블 데이터 조회 예제"""
from graphio_sdk import GraphioClient


def main():
    client = GraphioClient()
    try:
        # 1) 카탈로그에서 첫 번째 자산의 id 얻기
        catalog = client.meta_type.manage.list()
        if not catalog:
            print("등록된 MetaType이 없습니다.")
            return
        meta_type_id = catalog[0].id
        print(f"대상 자산: {catalog[0].name} (id={meta_type_id})\n")

        # 2) 미리보기 5건
        print("── 미리보기 (상위 5행) ──")
        for row in client.meta_type.table_data.sample_data_param(meta_type_id, 0, 5):
            print(row)

        # 3) 전체 데이터
        print("\n── 전체 데이터 ──")
        result = client.meta_type.table_data.all_data(meta_type_id)
        print(f"총 {result['totalCount']}건")
        for row in result["data"][:3]:
            print(row)

    finally:
        client.close()


if __name__ == "__main__":
    main()
```

---

## 참고

- 관련 소스: [graphio_sdk/data_pipline/meta_type.py](../graphio_sdk/data_pipline/meta_type.py) (`MetaTableAPI`)
- MetaType을 데이터 카탈로그로 활용하는 더 넓은 시나리오는
  [datacatalog_metatype_example.md](datacatalog_metatype_example.md)를 참고하세요.
