"""
File Generator - Python 파일 생성 및 __init__.py 업데이트
"""

import os
import logging
from typing import Dict, Set
from pathlib import Path

logger = logging.getLogger(__name__)


class FileGenerator:
    """
    Python 파일 생성 및 __init__.py 업데이트를 담당하는 클래스
    """

    def __init__(self, base_path: str):
        """
        Args:
            base_path: SDK base 경로 (예: graphio_sdk/ontology)
        """
        self.base_path = Path(base_path)
        self.objects_path = self.base_path / "objects"
        self.links_path = self.base_path / "links"
        
        # 디렉토리 생성
        self.objects_path.mkdir(parents=True, exist_ok=True)
        self.links_path.mkdir(parents=True, exist_ok=True)
        
        # __init__.py 파일 생성
        self._ensure_init_files()

    def _ensure_init_files(self):
        """__init__.py 파일이 존재하는지 확인하고 없으면 생성"""
        objects_init = self.objects_path / "__init__.py"
        links_init = self.links_path / "__init__.py"
        
        if not objects_init.exists():
            objects_init.write_text('"""자동 생성된 ObjectType 클래스들"""\n')
        
        if not links_init.exists():
            links_init.write_text('"""자동 생성된 LinkType 클래스들"""\n')

    def write_object_type_file(self, class_name: str, object_type_id: str, class_code: str):
        """
        ObjectType 파일 생성
        
        Args:
            class_name: 클래스 이름
            object_type_id: ObjectType ID
            class_code: 생성된 클래스 코드
        """
        # 파일명: 클래스명을 snake_case로 변환
        file_name = self._to_snake_case(class_name) + ".py"
        file_path = self.objects_path / file_name
        
        try:
            # 파일 작성
            file_path.write_text(class_code, encoding="utf-8")
            logger.info(f"ObjectType 파일 생성: {file_path}")
            
            # __init__.py 업데이트
            self._update_objects_init(class_name, file_name)
            
        except Exception as e:
            logger.error(f"ObjectType 파일 생성 실패: {e}", exc_info=True)
            raise

    def write_link_type_file(self, class_name: str, link_type_id: str, class_code: str):
        """
        LinkType 파일 생성
        
        Args:
            class_name: 클래스 이름
            link_type_id: LinkType ID
            class_code: 생성된 클래스 코드
        """
        file_name = self._to_snake_case(class_name) + ".py"
        file_path = self.links_path / file_name
        
        try:
            file_path.write_text(class_code, encoding="utf-8")
            logger.info(f"LinkType 파일 생성: {file_path}")
            
            # __init__.py 업데이트
            self._update_links_init(class_name, file_name)
            
        except Exception as e:
            logger.error(f"LinkType 파일 생성 실패: {e}", exc_info=True)
            raise

    def delete_object_type_file(self, object_type_id: str):
        """
        ObjectType 파일 삭제
        
        Args:
            object_type_id: ObjectType ID
        """
        # TODO: object_type_id로 파일 찾기 (파일 내용에서 _object_type_id 확인)
        # 현재는 간단히 로그만 남김
        logger.info(f"ObjectType 파일 삭제 요청: {object_type_id}")

    def delete_link_type_file(self, link_type_id: str):
        """
        LinkType 파일 삭제
        
        Args:
            link_type_id: LinkType ID
        """
        logger.info(f"LinkType 파일 삭제 요청: {link_type_id}")

    def _update_objects_init(self, class_name: str, file_name: str):
        """objects/__init__.py 업데이트"""
        init_file = self.objects_path / "__init__.py"
        
        # 기존 내용 읽기
        existing_content = init_file.read_text(encoding="utf-8") if init_file.exists() else ""
        
        # import 문 확인
        import_line = f"from .{file_name[:-3]} import {class_name}"
        
        if import_line not in existing_content:
            # import 추가
            if existing_content.strip():
                new_content = existing_content.rstrip() + f"\n{import_line}\n"
            else:
                new_content = f'"""자동 생성된 ObjectType 클래스들"""\n\n{import_line}\n'
            
            # __all__ 업데이트
            if "__all__" in existing_content:
                # 기존 __all__ 찾아서 업데이트
                import re
                pattern = r'__all__\s*=\s*\[(.*?)\]'
                match = re.search(pattern, existing_content, re.DOTALL)
                if match:
                    existing_all = match.group(1).strip()
                    if class_name not in existing_all:
                        new_all = f"__all__ = [{existing_all}, \"{class_name}\"]"
                        new_content = re.sub(pattern, new_all, new_content, flags=re.DOTALL)
                else:
                    new_content += f'\n__all__ = ["{class_name}"]\n'
            else:
                new_content += f'\n__all__ = ["{class_name}"]\n'
            
            init_file.write_text(new_content, encoding="utf-8")
            logger.info(f"objects/__init__.py 업데이트: {class_name} 추가")

    def _update_links_init(self, class_name: str, file_name: str):
        """links/__init__.py 업데이트"""
        init_file = self.links_path / "__init__.py"
        
        existing_content = init_file.read_text(encoding="utf-8") if init_file.exists() else ""
        import_line = f"from .{file_name[:-3]} import {class_name}"
        
        if import_line not in existing_content:
            if existing_content.strip():
                new_content = existing_content.rstrip() + f"\n{import_line}\n"
            else:
                new_content = f'"""자동 생성된 LinkType 클래스들"""\n\n{import_line}\n'
            
            if "__all__" in existing_content:
                import re
                pattern = r'__all__\s*=\s*\[(.*?)\]'
                match = re.search(pattern, existing_content, re.DOTALL)
                if match:
                    existing_all = match.group(1).strip()
                    if class_name not in existing_all:
                        new_all = f"__all__ = [{existing_all}, \"{class_name}\"]"
                        new_content = re.sub(pattern, new_all, new_content, flags=re.DOTALL)
                else:
                    new_content += f'\n__all__ = ["{class_name}"]\n'
            else:
                new_content += f'\n__all__ = ["{class_name}"]\n'
            
            init_file.write_text(new_content, encoding="utf-8")
            logger.info(f"links/__init__.py 업데이트: {class_name} 추가")

    def _to_snake_case(self, name: str) -> str:
        """클래스명을 snake_case로 변환"""
        import re
        # CamelCase를 snake_case로 변환
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

