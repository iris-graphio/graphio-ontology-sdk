"""
Ontology 네임스페이스 - Codegen으로 생성된 ObjectType/LinkType 클래스들
"""

# objects와 links는 codegen으로 자동 생성됩니다
try:
    from .objects import *
except ImportError:
    pass

try:
    from .links import *
except ImportError:
    pass

__all__ = []

