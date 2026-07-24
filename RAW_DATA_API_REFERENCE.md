# RawDataNamespace API 함수 레퍼런스

## raw_data (RawDataNamespace)


### client.raw_data.list(*, page=0, size=10, ...)

- 원천 데이터(Raw Data) 목록 조회
- 사용 api : GET /graphio/v1/raw-data
- 반환 타입 : `list[RawDataListItemDto]` (`data` 배열만 파싱하여 반환)
- Query params (Python snake_case → API camelCase)

| Python | Query key | 기본값 | 설명 |
|---|---|---|---|
| `page` | `page` | `0` | 0-base 페이지 인덱스 |
| `size` | `size` | `10` | 페이지 크기 (v1 기본 10) |
| `connect_type` | `connectType` | — | `string[]` (반복 키). 예: `MINIO`, `POSTGRESQL` |
| `data_type` | `dataType` | — | `FILE` \| `TABLE` |
| `file_extensions` | `fileExtensions` | — | `string[]` (반복 키). 파일 확장자 |
| `processing_status` | `processingStatus` | — | `string[]` (반복 키). `PROCESSING` \| `COMPLETE` \| `ERROR` |
| `last_period` | `lastPeriod` | — | 기간. 예: `1d`, `2d`, `1m` |
| `query` | `query` | — | 검색어 |

- `None`인 필터는 query에서 생략됨
- 사용 예시

```
from graphio_sdk import GraphioClient

client = GraphioClient(base_url="http://your-server:8080")

items = client.raw_data.list(
    page=0,
    size=10,
    data_type="FILE",
    connect_type=["MINIO", "POSTGRESQL"],
    processing_status=["COMPLETE"],
)

for item in items:
    print(item.raw_data_id, item.name, item.status, item.data_type)
```

- 응답 항목 필드

| 필드 (Python) | 필드 (API) | 설명 |
|---|---|---|
| `raw_data_id` | `rawDataId` | 원천 데이터 ID |
| `connect_type` | `connectType` | 연결 타입 |
| `connection_instance_name` | `connectionInstanceName` | 연결 인스턴스명 |
| `name` | `name` | 이름 |
| `data_type` | `dataType` | 파일 확장자 문자열 (FILE/TABLE 아님) |
| `collected_at` | `collectedAt` | 수집 시각 |
| `owner_id` | `ownerId` | 소유자 ID |
| `status` | `status` | `PROCESSING` \| `COMPLETE` \| `ERROR` |

---

### client.raw_data.source_info(raw_data_id)

- 원천 데이터(Raw Data)의 연결 정보 조회
- 사용 api : GET /graphio/v1/raw-data/{raw_data_id}/source-info
- 반환 타입 : RawDataSourceInfoDto (`data` 필드만 파싱하여 반환)
- 사용 예시

```
from graphio_sdk import GraphioClient

client = GraphioClient(base_url="http://your-server:8080")

# raw_data_id는 meta_type.manage.raw_datas() 등으로 조회한 ID 사용
source = client.raw_data.source_info("f0666ad9-39bd-4259-b0c1-bfc3a1527028")

# 전체 응답 data 확인 (dict)
print(source.model_dump())

# API와 동일한 camelCase JSON
import json
print(json.dumps(source.model_dump(by_alias=True), indent=2, ensure_ascii=False))
```

---

## dataType별 응답 필드

API 응답의 `data.dataType` 값에 따라 채워지는 필드가 다릅니다.

### table

DB 테이블 원천 데이터인 경우 `location`에 스키마·테이블 정보가 포함됩니다.

| 필드 (Python) | 필드 (API) | 설명 |
|---|---|---|
| `data_type` | `dataType` | `"table"` |
| `connection.ip` | `connection.ip` | DB 호스트 IP |
| `connection.port` | `connection.port` | DB 포트 |
| `full_path` | `fullPath` | `null` |
| `bucket_name` | `bucketName` | `null` |
| `file_name` | `fileName` | `null` |
| `location.database_name` | `location.databaseName` | 데이터베이스명 |
| `location.schema_name` | `location.schemaName` | 스키마명 |
| `location.table_name` | `location.tableName` | 테이블명 |

- 출력 예시

```
source = client.raw_data.source_info("f0666ad9-39bd-4259-b0c1-bfc3a1527028")
source.model_dump()
```

```
{
  'data_type': 'table',
  'connection': {'ip': '192.168.109.254', 'port': 31032},
  'full_path': None,
  'bucket_name': None,
  'file_name': None,
  'location': {
    'database_name': 'suju',
    'schema_name': 'suju_v2',
    'table_name': 'VT_용역계약'
  }
}
```

- table 타입 사용 예시

```
source = client.raw_data.source_info(raw_data_id)

if source.data_type == "table" and source.location:
    print(source.connection.ip, source.connection.port)
    print(source.location.database_name)
    print(source.location.schema_name)
    print(source.location.table_name)
```

### file

파일(오브젝트 스토리지) 원천 데이터인 경우 `fullPath`, `bucketName`, `fileName`이 채워지고 `location`은 `null`입니다.

| 필드 (Python) | 필드 (API) | 설명 |
|---|---|---|
| `data_type` | `dataType` | `"file"` |
| `connection.ip` | `connection.ip` | 스토리지 호스트 |
| `connection.port` | `connection.port` | 스토리지 포트 |
| `full_path` | `fullPath` | 파일 전체 URL |
| `bucket_name` | `bucketName` | 버킷명 |
| `file_name` | `fileName` | 파일명 |
| `location` | `location` | `null` |

- 출력 예시

```
source = client.raw_data.source_info("092ffa48-7333-4c0a-a93d-ce7e895fec37")
source.model_dump()
```

```
{
  'data_type': 'file',
  'connection': {'ip': 'minio-svc', 'port': 9000},
  'full_path': 'http://minio-svc:9000/ontology-service/2026/0/092ffa48-7333-4c0a-a93d-ce7e895fec37/092ffa48-7333-4c0a-a93d-ce7e895fec37.pdf',
  'bucket_name': 'ontology-service',
  'file_name': '북적북적 회칙2.pdf',
  'location': None
}
```

- file 타입 사용 예시

```
source = client.raw_data.source_info(raw_data_id)

if source.data_type == "file":
    print(source.connection.ip, source.connection.port)
    print(source.full_path)
    print(source.bucket_name)
    print(source.file_name)
```

---

## raw_data_id 조회

`source_info` 호출 전에 원천 데이터 ID가 필요하면 `raw_data.list()` 또는 메타타입 API로 목록을 조회합니다.

```
items = client.raw_data.list(page=0, size=10)
for item in items:
    print(item.raw_data_id, item.name, item.status)
    source = client.raw_data.source_info(item.raw_data_id)
    print(source.model_dump())
```

```
raw_list = client.meta_type.manage.raw_datas(meta_type_id, page=0, size=20)
for raw in raw_list:
    print(raw.id, raw.name, raw.data_type)
    source = client.raw_data.source_info(raw.id)
    print(source.model_dump())
```
