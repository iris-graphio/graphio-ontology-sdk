"""
Raw Data 네임스페이스 - GraphIOClient와 함께 사용
"""

from typing import TYPE_CHECKING, List, Optional

from graphio_sdk.schema.raw_data_schema import RawDataListItemDto, RawDataSourceInfoDto

if TYPE_CHECKING:
    from graphio_sdk.client import GraphioClient


class RawDataNamespace:
    """
    client.raw_data 네임스페이스.

    Example:
        items = client.raw_data.list(page=0, size=10, data_type="FILE")
        source = client.raw_data.source_info("raw-data-uuid")
        if source.data_type == "file":
            print(source.full_path)
        elif source.data_type == "table":
            print(source.location.table_name)
    """

    def __init__(self, client: "GraphioClient"):
        self._client = client
        self._url = f"{self._client.api_base}/raw-data"

    def list(
        self,
        *,
        page: int = 0,
        size: int = 10,
        connect_type: Optional[List[str]] = None,
        data_type: Optional[str] = None,
        file_extensions: Optional[List[str]] = None,
        processing_status: Optional[List[str]] = None,
        last_period: Optional[str] = None,
        query: Optional[str] = None,
    ) -> List[RawDataListItemDto]:
        """
        원천 데이터 목록 조회.

        GET /graphio/v1/raw-data

        Args:
            page: 페이지 인덱스 (0-base)
            size: 페이지 크기 (v1 기본값 10)
            connect_type: 연결 타입 필터 (예: MINIO, POSTGRESQL). 반복 키로 전송
            data_type: 데이터 타입 필터 (FILE | TABLE)
            file_extensions: 파일 확장자 필터. 반복 키로 전송
            processing_status: 처리 상태 필터 (PROCESSING | COMPLETE | ERROR). 반복 키로 전송
            last_period: 기간 필터 (예: 1d, 2d, 1m)
            query: 검색어

        Returns:
            list[RawDataListItemDto]: 원천 데이터 목록
        """
        params = {
            "page": page,
            "size": size,
            "connectType": connect_type,
            "dataType": data_type,
            "fileExtensions": file_extensions,
            "processingStatus": processing_status,
            "lastPeriod": last_period,
            "query": query,
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = self._client._get_session().get(
            self._url, params=params, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "list raw data")
        data = result.get("data", [])
        return (
            [RawDataListItemDto.model_validate(item) for item in data]
            if isinstance(data, list)
            else []
        )

    def source_info(self, raw_data_id: str) -> RawDataSourceInfoDto:
        """
        원천 데이터의 연결 정보 조회.

        GET /graphio/v1/raw-data/{raw_data_id}/source-info

        Args:
            raw_data_id: 원천 데이터 ID

        Returns:
            RawDataSourceInfoDto: dataType이 file이면 fullPath/bucketName/fileName,
                table이면 location(databaseName, schemaName, tableName) 포함
        """
        url = f"{self._url}/{raw_data_id}/source-info"
        response = self._client._get_session().get(
            url, timeout=self._client.timeout
        )
        response.raise_for_status()
        result = response.json()
        self._client._check_response(result, "get raw data source info")
        data = result.get("data", {})
        return RawDataSourceInfoDto.model_validate(data) if isinstance(data, dict) else RawDataSourceInfoDto()


__all__ = ["RawDataNamespace"]
