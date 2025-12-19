"""
Schema Fetcher - Ontology Service에서 Schema 조회
"""

import logging
from typing import Dict, Any, Optional, List
from .mq_consumer import OntologyChangeEvent

logger = logging.getLogger(__name__)


class SchemaFetcher:
    """
    Ontology Service에서 Schema를 조회하는 클래스
    
    MQ payload만으로 codegen하지 않고, 항상 Service에서 schema를 다시 조회합니다.
    """

    def __init__(self, client):
        """
        Args:
            client: GraphioClient 인스턴스
        """
        self.client = client

    def fetch_object_type_schema(self, object_type_id: str) -> Optional[Dict[str, Any]]:
        """
        ObjectType Schema 조회
        
        Args:
            object_type_id: ObjectType ID
            
        Returns:
            ObjectType Schema 또는 None (조회 실패 시)
        """
        try:
            # ObjectType 정보 조회
            object_type = self.client._fetch_object_type_by_id(object_type_id)
            if not object_type:
                logger.error(f"ObjectType을 찾을 수 없습니다: {object_type_id}")
                return None

            # Properties 조회
            properties = self.client._fetch_object_type_properties(object_type_id)
            
            # Schema 구성
            schema = {
                "id": object_type.get("id"),
                "name": object_type.get("name"),
                "properties": [
                    {
                        "name": prop.get("name"),
                        "type": prop.get("type"),  # 예: "STRING", "INTEGER", "DOUBLE", etc.
                        "nullable": prop.get("nullable", True),
                        "defaultValue": prop.get("defaultValue"),
                    }
                    for prop in properties
                ]
            }
            
            logger.info(f"ObjectType Schema 조회 성공: {schema['name']} ({object_type_id})")
            return schema
            
        except Exception as e:
            logger.error(f"ObjectType Schema 조회 실패: {e}", exc_info=True)
            return None

    def fetch_link_type_schema(self, link_type_id: str) -> Optional[Dict[str, Any]]:
        """
        LinkType Schema 조회
        
        Args:
            link_type_id: LinkType ID
            
        Returns:
            LinkType Schema 또는 None (조회 실패 시)
        """
        try:
            # TODO: LinkType 조회 API가 구현되면 사용
            # 현재는 placeholder
            logger.warning(f"LinkType Schema 조회는 아직 구현되지 않았습니다: {link_type_id}")
            return None
            
        except Exception as e:
            logger.error(f"LinkType Schema 조회 실패: {e}", exc_info=True)
            return None

