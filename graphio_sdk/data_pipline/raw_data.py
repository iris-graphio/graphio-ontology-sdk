"""
Raw Data 네임스페이스 - GraphIOClient와 함께 사용
"""

from typing import TYPE_CHECKING

from graphio_sdk.schema.raw_data_schema import RawDataSourceInfoDto

if TYPE_CHECKING:
    from graphio_sdk.client import GraphioClient


class RawDataNamespace:
    """
    client.raw_data 네임스페이스.

    Example:
        source = client.raw_data.source_info("raw-data-uuid")
        if source.data_type == "file":
            print(source.full_path)
        elif source.data_type == "table":
            print(source.location.table_name)
    """

    def __init__(self, client: "GraphioClient"):
        self._client = client
        self._url = f"{self._client.api_base}/raw-data"

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
