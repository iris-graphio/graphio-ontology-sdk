"""
GraphIO Ontology SDK - Palantir Foundry 스타일 Python 클라이언트

Example:
    from graphio_sdk import GraphioClient

    client = GraphioClient(base_url="http://localhost:8080")
    Employee = client.ontology.get_object_type("Employee")
    employees = (
        Employee.where(Employee.age > 30)
        .select("name", "age")
        .execute()
    )
"""

__version__ = "0.1.0"
__author__ = "GraphIO Team"

from graphio_sdk.client import GraphioClient
from graphio_sdk.ontology.operators import QueryOp, Condition, LogicalCondition
from graphio_sdk.ontology.object_type import ObjectTypeBase
from graphio_sdk.ontology.query import ObjectSetQuery
from graphio_sdk.ontology.edits import EditableObject, OntologyEditsBuilder
from graphio_sdk.ontology.ontology import OntologyNamespace
from graphio_sdk.meta_type import MetaTypeNamespace

__all__ = [
    "GraphioClient",
    "QueryOp",
    "Condition",
    "LogicalCondition",
    "ObjectTypeBase",
    "ObjectSetQuery",
    "EditableObject",
    "OntologyEditsBuilder",
    "OntologyNamespace",
    "MetaTypeNamespace",
]
