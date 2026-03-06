"""
Ontology 네임스페이스 및 ObjectType 관리 (Lazy Loading Only)
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
import threading
import time
from datetime import datetime, timezone

import requests

from .object_type import ObjectTypeBase
from .operators import PropertyDescriptor
from .edits import OntologyEditsBuilder

if TYPE_CHECKING:
    from graphio_sdk.client import GraphioClient


class OntologyNamespace:
    """ontology 네임스페이스 - Lazy Loading 전용"""

    def __init__(self, client: 'GraphioClient'):
        self.client = client
        self._object_types: Dict[str, type] = {}
        self._object_type_id_to_name: Dict[str, str] = {}
        self._link_types: Dict[str, type] = {}
        self._link_type_id_to_name: Dict[str, str] = {}
        self._cache_lock = threading.Lock()  # 스레드 안전성

    # ========================================================================
    # ObjectType 관련 API 호출 (ontology 전용)
    # ========================================================================

    def _fetch_object_types(
            self,
            ontology_id: Optional[str] = None,
            name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """서버에서 ObjectType 목록 가져오기"""
        url = f"{self.client.api_base}/object-type"

        params = {}
        if ontology_id:
            params["ontology-id"] = ontology_id
        if name:
            params["name"] = name

        try:
            response = self.client._get_session().get(
                url, params=params, timeout=self.client.timeout
            )
            response.raise_for_status()

            result = response.json()
            self.client._check_response(result, "fetch object types")

            return result.get("data", [])

        except requests.exceptions.Timeout as e:
            raise Exception(
                f"ObjectType 목록 조회 타임아웃 "
                f"(timeout={self.client._format_timeout()}): {str(e)}"
            ) from e
        except requests.exceptions.RequestException as e:
            raise Exception(f"ObjectType 목록 조회 실패: {str(e)}") from e

    def fetch_object_types(
            self,
            ontology_id: Optional[str] = None,
            name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        ObjectType 목록 조회 (public).

        Args:
            ontology_id: ontology-id 필터(선택)
            name: ObjectType 이름 필터(선택)

        Returns:
            ObjectType 정보 목록
        """
        return self._fetch_object_types(ontology_id=ontology_id, name=name)

    def _fetch_object_type_by_id(self, object_type_id: str) -> Dict[str, Any]:
        """특정 ObjectType 상세 정보 가져오기"""
        url = f"{self.client.api_base}/object-type/{object_type_id}"

        try:
            response = self.client._get_session().get(url, timeout=self.client.timeout)
            response.raise_for_status()

            result = response.json()

            # CommonResponse 어노테이션이 있는 경우 data를 직접 반환
            if isinstance(result, dict) and "id" in result:
                return result

            self.client._check_response(result, "fetch object type")
            return result.get("data", {})

        except requests.exceptions.Timeout as e:
            raise Exception(
                f"ObjectType 조회 타임아웃 "
                f"(timeout={self.client._format_timeout()}): {str(e)}"
            ) from e
        except requests.exceptions.RequestException as e:
            raise Exception(f"ObjectType 조회 실패: {str(e)}") from e

    def _fetch_object_type_properties(
        self, object_type_id: str
    ) -> List[Dict[str, Any]]:
        """ObjectType의 Property 목록 가져오기"""
        url = f"{self.client.api_base}/object-type-property/{object_type_id}"

        try:
            response = self.client._get_session().get(url, timeout=self.client.timeout)
            response.raise_for_status()

            result = response.json()
            self.client._check_response(result, "fetch object type properties")

            return result.get("data", [])

        except requests.exceptions.Timeout as e:
            raise Exception(
                f"ObjectType Properties 조회 타임아웃 "
                f"(timeout={self.client._format_timeout()}): {str(e)}"
            ) from e
        except requests.exceptions.RequestException as e:
            raise Exception(f"ObjectType Properties 조회 실패: {str(e)}") from e

    def _execute_select(
        self, select_dto: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        실제 데이터 조회 (selectObjectSet 사용, ontology-workflow 전용)

        Args:
            select_dto: ObjectSetSelectDto 형식의 요청

        Returns:
            조회된 실제 데이터 리스트
        """
        url = f"{self.client.api_base}/ontology-workflow/objects/select"

        try:
            response = self.client._get_session().post(
                url,
                json=select_dto,
                headers={"Content-Type": "application/json"},
                timeout=self.client.timeout
            )
            response.raise_for_status()

            result = response.json()
            self.client._check_response(result, "select")

            return result.get("data", [])

        except requests.exceptions.Timeout as e:
            raise Exception(
                f"데이터 조회 타임아웃 "
                f"(timeout={self.client._format_timeout()}): {str(e)}"
            ) from e
        except requests.exceptions.RequestException as e:
            raise Exception(f"데이터 조회 실패: {str(e)}") from e

    # ========================================================================
    # ObjectSet 생성/수정 (HTTP API 호출, ontology 전용)
    # ========================================================================

    def _execute_create(
        self, messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """생성 실행 - HTTP API로 요청"""
        url = f"{self.client.api_base}/ontology-workflow/objects/insert"
        request_body = messages
        try:
            response = self.client._get_session().post(
                url,
                json=request_body,
                headers={"Content-Type": "application/json"},
                timeout=self.client.timeout
            )
            response.raise_for_status()
            result = response.json()
            self.client._check_response(result, "객체 생성")
            return result.get("data", result)
        except requests.exceptions.Timeout as e:
            raise Exception(
                f"객체 생성 타임아웃 "
                f"(timeout={self.client._format_timeout()}): {str(e)}"
            ) from e
        except requests.exceptions.RequestException as e:
            raise Exception(f"객체 생성 실패: {str(e)}") from e

    def _execute_update(
        self, messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """업데이트 실행 - HTTP API로 요청"""
        url = f"{self.client.api_base}/ontology-workflow/objects/update"
        request_body = messages
        try:
            response = self.client._get_session().post(
                url,
                json=request_body,
                headers={"Content-Type": "application/json"},
                timeout=self.client.timeout
            )
            response.raise_for_status()
            result = response.json()
            self.client._check_response(result, "객체 업데이트")
            return result.get("data", result)
        except requests.exceptions.Timeout as e:
            raise Exception(
                f"객체 업데이트 타임아웃 "
                f"(timeout={self.client._format_timeout()}): {str(e)}"
            ) from e
        except requests.exceptions.RequestException as e:
            raise Exception(f"객체 업데이트 실패: {str(e)}") from e

    def _execute_delete(
        self, messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """삭제 실행 - HTTP API로 요청"""
        url = f"{self.client.api_base}/ontology-workflow/objects/delete"
        request_body = messages
        try:
            response = self.client._get_session().post(
                url,
                json=request_body,
                headers={"Content-Type": "application/json"},
                timeout=self.client.timeout
            )
            response.raise_for_status()
            result = response.json()
            self.client._check_response(result, "객체 삭제")
            return result.get("data", result)
        except requests.exceptions.Timeout as e:
            raise Exception(
                f"객체 삭제 타임아웃 "
                f"(timeout={self.client._format_timeout()}): {str(e)}"
            ) from e
        except requests.exceptions.RequestException as e:
            raise Exception(f"객체 삭제 실패: {str(e)}") from e

    def _normalize_object_messages(
        self,
        objs,
        require_element_id: bool = False,
        method_name: str = "insert_batch"
    ) -> List[Dict[str, Any]]:
        """단건/배치 입력을 object message 형식으로 정규화."""
        if isinstance(objs, (list, tuple)):
            obj_list = list(objs)
        else:
            obj_list = [objs]

        if not obj_list:
            raise ValueError(f"{method_name}()의 입력 객체가 비어 있습니다.")

        messages: List[Dict[str, Any]] = []
        for obj in obj_list:
            message: Optional[Dict[str, Any]] = None
            if isinstance(obj, dict):
                message = obj
            elif hasattr(obj, "to_contract"):
                message = obj.to_contract()
            elif hasattr(obj, "to_message"):
                message = obj.to_message()
            else:
                raise ValueError(
                    f"{method_name}()의 각 항목은 dict 이거나 "
                    "to_contract()/to_message()를 지원해야 합니다."
                )

            if require_element_id and not message.get("elementId"):
                raise ValueError(
                    f"{method_name}()를 사용하려면 "
                    "모든 객체에 element_id(elementId)가 필요합니다."
                )
            messages.append(message)
        return messages

    def _resolve_object_type_id(self, object_type_name: Optional[str]) -> Optional[str]:
        """ObjectType 이름으로 objectTypeId 조회."""
        if not object_type_name:
            return None
        obj_type_cls = self.get_object_type(object_type_name)
        if not obj_type_cls:
            raise ValueError(f"ObjectType을 찾을 수 없습니다. name={object_type_name}")
        return obj_type_cls._object_type_id

    def _fill_missing_element_ids(
        self,
        messages: List[Dict[str, Any]],
        resolved_object_type_id: Optional[str],
        method_name: str,
        element_id_lookup_field: Optional[str]
    ) -> None:
        """elementId가 누락된 메시지에 대해 select API로 elementId를 채운다."""
        missing_element_id_messages = [
            message for message in messages if not message.get("elementId")
        ]

        if not missing_element_id_messages:
            return

        if not element_id_lookup_field:
            raise ValueError(
                f"{method_name}()에서 elementId가 없는 객체를 처리하려면 "
                "element_id_lookup_field 인자가 필요합니다. "
                "예: element_id_lookup_field='id'"
            )

        for message in missing_element_id_messages:
            object_type_id = message.get("objectTypeId") or resolved_object_type_id
            if not object_type_id:
                raise ValueError(
                    f"{method_name}()에서 objectTypeId를 찾을 수 없습니다. "
                    "object_type_name 또는 message.objectTypeId를 전달하세요."
                )

            properties = message.get("properties") or {}
            lookup_value = properties.get(element_id_lookup_field)
            if lookup_value is None:
                raise ValueError(
                    f"{method_name}()에서 elementId 조회를 위해 "
                    f"properties['{element_id_lookup_field}'] 값이 필요합니다."
                )

            select_dto = {
                "select": [element_id_lookup_field],
                "from": object_type_id,
                "where": {
                    "field": element_id_lookup_field,
                    "op": "eq",
                    "value": lookup_value
                },
                "limit": 2
            }
            selected_rows = self._execute_select(select_dto)
            if not selected_rows:
                raise ValueError(
                    f"{method_name}()에서 elementId를 찾을 수 없습니다. "
                    f"{element_id_lookup_field}={lookup_value}"
                )
            if len(selected_rows) > 1:
                raise ValueError(
                    f"{method_name}()에서 elementId가 여러 건 조회되었습니다. "
                    f"{element_id_lookup_field}={lookup_value}"
                )

            resolved_element_id = selected_rows[0].get("elementId")
            if not resolved_element_id:
                raise ValueError(
                    f"{method_name}()에서 조회 결과에 elementId가 없습니다. "
                    f"{element_id_lookup_field}={lookup_value}"
                )

            message["elementId"] = resolved_element_id
            if not message.get("objectTypeId"):
                message["objectTypeId"] = object_type_id

    def insert_batch(
        self,
        objs,
        object_type_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """여러 객체를 insert API로 한 번에 생성."""
        resolved_object_type_id = self._resolve_object_type_id(object_type_name)
        messages = self._normalize_object_messages(
            objs=objs,
            require_element_id=False,
            method_name="insert_batch"
        )
        if resolved_object_type_id:
            for message in messages:
                if "objectTypeId" not in message or not message.get("objectTypeId"):
                    message["objectTypeId"] = resolved_object_type_id
        return self._execute_create(messages)

    def update_batch(
        self,
        objs,
        object_type_name: Optional[str] = None,
        element_id_lookup_field: Optional[str] = None
    ) -> Dict[str, Any]:
        """여러 객체를 update API로 한 번에 수정."""
        resolved_object_type_id = self._resolve_object_type_id(object_type_name)
        messages = self._normalize_object_messages(
            objs=objs,
            require_element_id=False,
            method_name="update_batch"
        )
        self._fill_missing_element_ids(
            messages=messages,
            resolved_object_type_id=resolved_object_type_id,
            method_name="update_batch",
            element_id_lookup_field=element_id_lookup_field
        )
        if resolved_object_type_id:
            for message in messages:
                if "objectTypeId" not in message or not message.get("objectTypeId"):
                    message["objectTypeId"] = resolved_object_type_id
        return self._execute_update(messages)

    def delete_batch(
        self,
        objs,
        object_type_name: Optional[str] = None,
        element_id_lookup_field: Optional[str] = None
    ) -> Dict[str, Any]:
        """여러 객체를 delete API로 한 번에 삭제."""
        resolved_object_type_id = self._resolve_object_type_id(object_type_name)
        messages = self._normalize_object_messages(
            objs=objs,
            require_element_id=False,
            method_name="delete_batch"
        )
        self._fill_missing_element_ids(
            messages=messages,
            resolved_object_type_id=resolved_object_type_id,
            method_name="delete_batch",
            element_id_lookup_field=element_id_lookup_field
        )
        if resolved_object_type_id:
            for message in messages:
                if "objectTypeId" not in message or not message.get("objectTypeId"):
                    message["objectTypeId"] = resolved_object_type_id
        return self._execute_delete(messages)

    # ========================================================================
    # Typed Object/Link API (insert, update, delete)
    # ========================================================================

    def insert(self, obj):
        """
        Typed Object 또는 Link를 생성

        Args:
            obj: TypedObject 또는 TypedLink 인스턴스

        Returns:
            생성 결과

        Example:
            Employee = client.ontology.get_object_type("Employee")
            emp = Employee(
                element_id="e-1",
                properties={"name": "John", "age": 30}
            )
            client.ontology.insert(emp)
        """
        contract = obj.to_contract()
        messages = [contract]
        return self._execute_create(messages)

    def update(self, obj):
        """
        Typed Object 또는 Link를 업데이트

        Args:
            obj: TypedObject 또는 TypedLink 인스턴스 (element_id 필수)

        Returns:
            업데이트 결과

        Example:
            Employee = client.ontology.get_object_type("Employee")
            emp = Employee(
                element_id="e-1",
                properties={"name": "John", "age": 31}
            )
            client.ontology.update(emp)
        """
        if not obj.element_id:
            raise ValueError(
                "update()를 사용하려면 element_id가 필요합니다."
            )
        contract = obj.to_contract()
        messages = [contract]
        return self._execute_update(messages)

    def delete(self, obj):
        """
        Typed Object 또는 Link를 삭제

        Args:
            obj: TypedObject 또는 TypedLink 인스턴스 (element_id 필수)

        Returns:
            삭제 결과

        Example:
            Employee = client.ontology.get_object_type("Employee")
            emp = Employee(element_id="e-1")
            client.ontology.delete(emp)
        """
        if not obj.element_id:
            raise ValueError(
                "delete()를 사용하려면 element_id가 필요합니다."
            )
        contract = obj.to_contract()
        messages = [contract]
        return self._execute_delete(messages)

    def register_object_type(
            self,
            name: str,
            object_type_id: str,
            properties: Optional[List[str]] = None
    ) -> type:
        """
        ObjectType 수동 등록

        Args:
            name: ObjectType 이름 (예: "Employee", "Ticket")
            object_type_id: ObjectType UUID
            properties: 속성 이름 리스트 (선택적)

        Returns:
            생성된 ObjectType 클래스
        """
        with self._cache_lock:
            # 이미 등록된 경우 기존 클래스 반환
            if name in self._object_types:
                return self._object_types[name]

            # 동적으로 클래스 생성 (query에서 _execute_select 호출을 위해 _ontology_namespace 전달)
            cls = type(name, (ObjectTypeBase,), {
                "_object_type_id": object_type_id,
                "_object_type_name": name,
                "_client": self.client,
                "_ontology_namespace": self,
                "_properties": properties or []
            })

            # 속성 디스크립터 동적 생성
            if properties:
                for prop_name in properties:
                    setattr(cls, prop_name, PropertyDescriptor(prop_name))

            self._object_types[name] = cls
            self._object_type_id_to_name[object_type_id] = name

            # objects 네임스페이스에 등록
            setattr(self.objects, name, cls)

            return cls

    def add_property(self, object_type_name: str, property_name: str):
        """ObjectType에 속성 추가"""
        if object_type_name not in self._object_types:
            raise ValueError(f"ObjectType '{object_type_name}'이 등록되지 않았습니다.")

        cls = self._object_types[object_type_name]
        setattr(cls, property_name, PropertyDescriptor(property_name))
        cls._properties.append(property_name)

    def load_object_type(
            self,
            object_type_id: Optional[str] = None,
            name: Optional[str] = None
    ) -> type:
        """
        특정 ObjectType을 서버에서 가져와 등록

        Args:
            object_type_id: ObjectType UUID (id 또는 name 중 하나 필수)
            name: ObjectType 이름 (id 또는 name 중 하나 필수)

        Returns:
            등록된 ObjectType 클래스
        """
        # name으로 이미 로드된 경우
        if name and name in self._object_types:
            return self._object_types[name]

        # id로 이미 로드된 경우
        if object_type_id and object_type_id in self._object_type_id_to_name:
            cached_name = self._object_type_id_to_name[object_type_id]
            return self._object_types[cached_name]

        # 서버에서 로드
        if object_type_id:
            ot_data = self._fetch_object_type_by_id(object_type_id)
        elif name:
            # name으로 검색
            results = self._fetch_object_types(name=name)
            if not results:
                raise ValueError(f"ObjectType '{name}'을 찾을 수 없습니다.")
            ot_data = results[0]  # 첫 번째 결과 사용
        else:
            raise ValueError("object_type_id 또는 name 중 하나는 필수입니다.")

        object_type_id = ot_data.get("id")
        name = ot_data.get("name")

        if not object_type_id or not name:
            raise ValueError(f"유효하지 않은 ObjectType 데이터: {ot_data}")

        # Properties 가져오기
        properties = self._fetch_object_type_properties(object_type_id)
        property_names = [prop["name"] for prop in properties]

        # ObjectType 등록
        return self.register_object_type(name, object_type_id, property_names)

    def get_object_type(self, name: str) -> Optional[type]:
        """
        ObjectType 클래스 가져오기 (Lazy Loading)

        캐시에 없으면 자동으로 서버에서 로드합니다.

        Args:
            name: ObjectType 이름

        Returns:
            ObjectType 클래스 또는 None (로드 실패 시)
        """
        # 캐시에서 찾기
        if name in self._object_types:
            return self._object_types[name]

        # 자동 로드
        try:
            return self.load_object_type(name=name)
        except Exception:
            # 로드 실패 시 None 반환
            return None

    def list_object_types(self) -> List[str]:
        """
        캐시된 ObjectType 이름 목록

        Returns:
            ObjectType 이름 리스트
        """
        return list(self._object_types.keys())

    def get_link_type(self, name: str) -> Optional[type]:
        """
        LinkType 클래스 가져오기 (Lazy Loading)

        캐시에 없으면 자동으로 서버에서 로드합니다.

        Args:
            name: LinkType 이름

        Returns:
            LinkType 클래스 또는 None (로드 실패 시)
        """
        # 캐시에서 찾기
        if name in self._link_types:
            return self._link_types[name]

        # 자동 로드
        try:
            return self.load_link_type(name=name)
        except Exception:
            # 로드 실패 시 None 반환
            return None

    def load_link_type(
            self,
            link_type_id: Optional[str] = None,
            name: Optional[str] = None
    ) -> type:
        """
        특정 LinkType을 서버에서 가져와 등록

        Args:
            link_type_id: LinkType UUID (id 또는 name 중 하나 필수)
            name: LinkType 이름 (id 또는 name 중 하나 필수)

        Returns:
            등록된 LinkType 클래스
        """
        # name으로 이미 로드된 경우
        if name and name in self._link_types:
            return self._link_types[name]

        # id로 이미 로드된 경우
        if link_type_id and link_type_id in self._link_type_id_to_name:
            cached_name = self._link_type_id_to_name[link_type_id]
            return self._link_types[cached_name]

        # 서버에서 로드 (LinkType API가 구현되면 사용)
        # 현재는 ObjectType과 동일한 구조로 구현
        if link_type_id:
            # TODO: LinkType API 구현 시 사용
            raise NotImplementedError("LinkType API가 아직 구현되지 않았습니다.")
        elif name:
            # TODO: LinkType API 구현 시 사용
            raise NotImplementedError("LinkType API가 아직 구현되지 않았습니다.")
        else:
            raise ValueError("link_type_id 또는 name 중 하나는 필수입니다.")

    def register_link_type(
            self,
            name: str,
            link_type_id: str,
            properties: Optional[List[str]] = None
    ) -> type:
        """
        LinkType 수동 등록

        Args:
            name: LinkType 이름
            link_type_id: LinkType UUID
            properties: 속성 이름 리스트 (선택적)

        Returns:
            생성된 LinkType 클래스
        """
        with self._cache_lock:
            # 이미 등록된 경우 기존 클래스 반환
            if name in self._link_types:
                return self._link_types[name]

            # 동적으로 클래스 생성 (ObjectType과 동일한 구조)
            cls = type(name, (ObjectTypeBase,), {
                "_object_type_id": link_type_id,  # LinkType도 동일한 구조 사용
                "_object_type_name": name,
                "_client": self.client,
                "_properties": properties or []
            })

            # 속성 디스크립터 동적 생성
            if properties:
                for prop_name in properties:
                    setattr(cls, prop_name, PropertyDescriptor(prop_name))

            self._link_types[name] = cls
            self._link_type_id_to_name[link_type_id] = name

            # links 네임스페이스에 등록
            setattr(self.links, name, cls)

            return cls

    def list_link_types(self) -> List[str]:
        """
        캐시된 LinkType 이름 목록

        Returns:
            LinkType 이름 리스트
        """
        return list(self._link_types.keys())

    def clear_cache(self):
        """캐시된 ObjectType과 LinkType 모두 제거"""
        with self._cache_lock:
            self._object_types.clear()
            self._object_type_id_to_name.clear()
            self._link_types.clear()
            self._link_type_id_to_name.clear()
            self._objects_namespace = type('ObjectsNamespace', (), {})()
            self._links_namespace = type('LinksNamespace', (), {})()

    @property
    def objects(self):
        """objects 네임스페이스 - 동적 속성 접근용"""
        if not hasattr(self, '_objects_namespace'):
            self._objects_namespace = type('ObjectsNamespace', (), {})()
        return self._objects_namespace

    @property
    def links(self):
        """links 네임스페이스 - 동적 속성 접근용"""
        if not hasattr(self, '_links_namespace'):
            self._links_namespace = type('LinksNamespace', (), {})()
        return self._links_namespace

    def edits(self) -> OntologyEditsBuilder:
        """편집 세션 시작"""
        return OntologyEditsBuilder(self.client, self._object_types)
