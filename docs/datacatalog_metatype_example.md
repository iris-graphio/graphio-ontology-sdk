# 시나리오: MetaType으로 데이터 카탈로그 만들기

Graphio Ontology SDK의 `client.meta_type` API를 활용해 **데이터 카탈로그(Data Catalog)** 를
구성하는 예제입니다. 데이터 카탈로그는 조직이 보유한 데이터 자산(테이블/뷰/파일)을
한눈에 검색·탐색하고, 각 자산의 스키마·소유자·태그·데이터 출처(lineage)·품질 정보를
제공하는 시스템입니다.

이 문서에서는 SDK의 MetaType 기능이 데이터 카탈로그의 어떤 요구사항에 매핑되는지를
시나리오로 설명합니다.

---

## 0. MetaType이 곧 "카탈로그 항목"이다

GraphIO에서 **MetaType**은 하나의 데이터셋(테이블/뷰/파일)에 대한 메타데이터 단위입니다.
즉, 데이터 카탈로그 관점에서 보면 **MetaType 1개 = 카탈로그 엔트리 1개**입니다.

| 데이터 카탈로그 요구사항 | SDK MetaType API |
| --- | --- |
| 전체 자산 목록 (인벤토리) | `manage.list()` |
| 종류별(TABLE/VIEW/FILE) 분류 | `manage.kind_list(kind)` |
| 자산 상세 (개요) | `manage.inspect_basic(meta_type_id)` |
| 스키마 / 컬럼 정의 | `manage.inspect_property(meta_type_id)` |
| 데이터 출처(lineage) | `manage.inspect_data_source(meta_type_id)` |
| 데이터 품질 / 프로파일링 통계 | `manage.inspect_profiling(meta_type_id)` |
| 미리보기(샘플 데이터) | `table_data.sample_data_param(meta_type_id, page, size)` |
| 소유자(Owner) | `manage.owner()` |
| 태그(분류 체계) | `etc.tag_list()` |
| 이름 중복 검사 | `manage.duplicate_check(name)` |

---

## 1. 카탈로그 인벤토리 만들기 — 전체 자산 훑어보기

가장 먼저 필요한 것은 "우리가 어떤 데이터를 가지고 있는가?"입니다.
`manage.list()`로 등록된 모든 MetaType을 가져와 카탈로그의 첫 화면(목록)을 구성합니다.

```python
from graphio_sdk import GraphioClient

client = GraphioClient()

# 등록된 모든 데이터 자산(MetaType) 조회 → List[MetaTypeDto]
catalog = client.meta_type.manage.list()

print(f"총 {len(catalog)}개의 데이터 자산이 카탈로그에 등록되어 있습니다.\n")

for m in catalog:
    kind = m.meta_type_kind or "UNKNOWN"
    table = m.meta_type_table_name or "-"
    print(f"[{kind:5}] {m.name:30} (table={table}, id={m.id})")
```

`MetaTypeDto`는 카탈로그 카드에 그대로 쓸 수 있는 필드를 제공합니다:
`name`, `description`, `meta_type_kind`, `meta_type_schema_name`,
`meta_type_table_name`, `tag_ids`, `owner_id`, `created_at`, `updated_at`.

---

## 2. 종류별로 분류하기 — TABLE / VIEW / FILE 탭

카탈로그 UI는 보통 "테이블 / 뷰 / 파일" 같은 탭으로 자산을 나눕니다.
`MetaTypeKind` enum과 `kind_list()`를 사용합니다.

```python
from graphio_sdk import GraphioClient
from graphio_sdk.schema import MetaTypeKind

client = GraphioClient()

# 종류별로 카탈로그를 묶어서 보여주기
for kind in (MetaTypeKind.TABLE, MetaTypeKind.VIEW, MetaTypeKind.FILE):
    items = client.meta_type.manage.kind_list(kind.value)   # List[MetaTypeInspectDto]
    print(f"\n=== {kind.value} ({len(items)}개) ===")
    for it in items:
        print(f"  - {it.name}: {it.description or '설명 없음'}")
```

> `kind_list()`는 `MetaTypeInspectDto`를 돌려주므로 `properties`까지 함께 들어 있어
> 종류별 화면에서 바로 스키마 미리보기를 보여줄 수 있습니다.

---

## 3. 자산 상세 페이지 구성하기

카탈로그에서 항목 하나를 클릭하면 상세 페이지가 열립니다.
상세 페이지는 보통 **개요 / 스키마 / 데이터 출처 / 품질 / 미리보기** 탭으로 구성됩니다.
각 탭을 하나의 함수로 만들어 봅니다.

```python
from graphio_sdk import GraphioClient


def describe_asset(client: GraphioClient, meta_type_id: str) -> None:
    """카탈로그 자산 1개의 상세 정보를 모두 출력한다."""

    # (1) 개요 ─ inspect_basic
    basic = client.meta_type.manage.inspect_basic(meta_type_id)
    print("=" * 60)
    print(f"📦 {basic.name}  ({basic.meta_type_kind})")
    print(f"   설명     : {basic.description or '-'}")
    print(f"   스키마   : {basic.meta_type_schema_name}")
    print(f"   테이블   : {basic.meta_type_table_name}")
    print(f"   소유자   : {basic.owner_id}")
    print(f"   태그     : {basic.tag_ids}")
    print(f"   생성/수정: {basic.created_at} / {basic.updated_at}")

    # (2) 스키마(컬럼 정의) ─ inspect_property
    print("\n📋 스키마(컬럼)")
    props = client.meta_type.manage.inspect_property(meta_type_id)
    for p in props:
        print(f"   - {p.name:25} {p.data_type:10} {p.description or ''}")

    # (3) 데이터 출처(lineage) ─ inspect_data_source
    print("\n🔗 데이터 출처(Lineage)")
    sources = client.meta_type.manage.inspect_data_source(meta_type_id)
    for s in sources:
        print(f"   - {s.resource_type}: {s.connection_name} "
              f"({s.file_name or ''}{s.file_extension or ''}) tags={s.tags}")

    # (4) 데이터 품질(프로파일링 통계) ─ inspect_profiling
    print("\n📊 프로파일링")
    profiling = client.meta_type.manage.inspect_profiling(meta_type_id)
    for col_stat in profiling:
        print(f"   - {col_stat}")

    # (5) 미리보기(샘플 데이터) ─ sample_data_param
    print("\n👀 샘플 데이터 (상위 5행)")
    sample = client.meta_type.table_data.sample_data_param(meta_type_id, page=0, size=5)
    for row in sample:
        print(f"   {row}")
    print("=" * 60)


if __name__ == "__main__":
    client = GraphioClient()
    try:
        # 카탈로그 목록에서 첫 번째 자산의 상세 정보 보기
        first = client.meta_type.manage.list()[0]
        describe_asset(client, first.id)
    finally:
        client.close()
```

이 한 함수가 곧 데이터 카탈로그의 "자산 상세 페이지"입니다.

---

## 4. 태그 기반 분류 체계(Taxonomy)

카탈로그에서 데이터를 주제별("재무", "고객", "센서" 등)로 찾으려면 태그를 활용합니다.
`etc.tag_list()`로 전체 태그를 가져오고, 각 MetaType의 `tag_ids`와 매칭합니다.

```python
from graphio_sdk import GraphioClient

client = GraphioClient()

# 전체 태그 사전 구성: tag_id -> tag_name
tags = {t.id: t.name for t in client.meta_type.etc.tag_list()}

# 태그별로 자산을 묶기
from collections import defaultdict
by_tag = defaultdict(list)

for m in client.meta_type.manage.list():
    for tid in m.tag_ids:
        by_tag[tags.get(tid, tid)].append(m.name)

for tag_name, assets in by_tag.items():
    print(f"#{tag_name} ({len(assets)})")
    for a in assets:
        print(f"   - {a}")
```

---

## 5. 소유자(Ownership) 기준 거버넌스 뷰

데이터 거버넌스 관점에서는 "이 데이터는 누가 책임지는가?"가 중요합니다.
`manage.owner()`로 소유자 목록을 가져오고, 자산을 소유자별로 묶습니다.

```python
from collections import defaultdict
from graphio_sdk import GraphioClient

client = GraphioClient()

owners = client.meta_type.manage.owner()   # List[str] (UUID)
print(f"데이터 소유자 수: {len(owners)}")

by_owner = defaultdict(list)
for m in client.meta_type.manage.list():
    by_owner[m.owner_id].append(m.name)

for owner_id, assets in by_owner.items():
    print(f"\n👤 {owner_id} — {len(assets)}개 자산 소유")
    for a in assets:
        print(f"   - {a}")
```

---

## 6. 새 데이터 자산 등록 전 — 이름 중복 검사

카탈로그에 새 자산을 등록하기 전, 이름 충돌을 막기 위해 중복 검사를 합니다.

```python
from graphio_sdk import GraphioClient

client = GraphioClient()

name = "customer_master"
result = client.meta_type.manage.duplicate_check(name)
# {"meta_type_id": <기존 id 또는 None>, "status": <bool>}

if result["meta_type_id"]:
    print(f"⚠️ '{name}' 은 이미 카탈로그에 존재합니다 (id={result['meta_type_id']}).")
else:
    print(f"✅ '{name}' 사용 가능 — 신규 등록을 진행하세요.")
```

---

## 7. 한 데이터 소스에 연결된 원천 데이터(Raw Data) 추적

하나의 MetaType이 어떤 원천 파일/테이블에서 만들어졌는지를 추적합니다 (페이지네이션 지원).

```python
from graphio_sdk import GraphioClient

client = GraphioClient()

meta_type_id = client.meta_type.manage.list()[0].id

raw_datas = client.meta_type.manage.raw_datas(meta_type_id, page=0, size=20)
print(f"이 자산은 {len(raw_datas)}개의 원천 데이터에서 매핑되었습니다:")
for rd in raw_datas:
    print(f"   - {rd.name} (type={rd.data_type}, id={rd.id})")
```

---

## 부록 A. 전체 카탈로그를 한 번에 덤프하는 스크립트

위 조각들을 합쳐, 카탈로그 전체를 구조화된 딕셔너리(예: JSON 내보내기용)로 만드는 예시입니다.

```python
"""build_catalog.py — MetaType 기반 데이터 카탈로그 전체 덤프"""
import json
from graphio_sdk import GraphioClient


def build_catalog() -> list[dict]:
    client = GraphioClient()
    try:
        tags = {t.id: t.name for t in client.meta_type.etc.tag_list()}
        catalog = []

        for m in client.meta_type.manage.list():
            props = client.meta_type.manage.inspect_property(m.id)
            sources = client.meta_type.manage.inspect_data_source(m.id)

            catalog.append({
                "id": m.id,
                "name": m.name,
                "description": m.description,
                "kind": m.meta_type_kind,
                "schema": m.meta_type_schema_name,
                "table": m.meta_type_table_name,
                "owner": m.owner_id,
                "tags": [tags.get(tid, tid) for tid in m.tag_ids],
                "columns": [
                    {"name": p.name, "type": p.data_type, "desc": p.description}
                    for p in props
                ],
                "lineage": [
                    {"source": s.connection_name, "type": s.resource_type}
                    for s in sources
                ],
            })
        return catalog
    finally:
        client.close()


if __name__ == "__main__":
    data = build_catalog()
    print(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"\n✅ {len(data)}개의 자산을 카탈로그로 내보냈습니다.")
```

---

## 부록 B. 사용한 API 한눈에 보기

```python
client.meta_type.manage.list()                          # 전체 자산 목록
client.meta_type.manage.kind_list("TABLE")              # 종류별 목록
client.meta_type.manage.inspect_basic(id)               # 개요
client.meta_type.manage.inspect_property(id)            # 컬럼/스키마
client.meta_type.manage.inspect_data_source(id)         # 데이터 출처
client.meta_type.manage.inspect_profiling(id)           # 프로파일링 통계
client.meta_type.manage.raw_datas(id, page, size)       # 원천 데이터
client.meta_type.manage.owner()                         # 소유자 목록
client.meta_type.manage.duplicate_check(name)           # 이름 중복 검사
client.meta_type.table_data.sample_data_param(id, 0, 5) # 샘플 데이터
client.meta_type.table_data.all_data(id)                # 전체 데이터
client.meta_type.table_data.table_list(conn, schema, kind)     # 물리 테이블 목록
client.meta_type.table_data.table_columns(conn, schema, table) # 물리 컬럼 목록
client.meta_type.etc.tag_list()                         # 태그 목록
```

관련 DTO는 `graphio_sdk.schema`에서 가져옵니다:
`MetaTypeDto`, `MetaTypeInspectDto`, `MetaTypePropertyResponseDto`,
`RawDataInfoResponseDto`, `TagDto`, `MetaTypeKind`, `PropertyDataType` 등.
