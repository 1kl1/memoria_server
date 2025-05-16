from datetime import datetime
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from neo4j import Session

class RelationshipModel(BaseModel):
    type: Optional[str]
    properties: Dict[str, Any]
    source: str
    target: str
class BaseNode(BaseModel):
    uuid: str
    label: str
    title: str
    summary: str
    entities: List[str]

class NodeInDB(BaseNode):
    createdAt: Optional[datetime] = Field(description="노드 생성일")
    updatedAt: Optional[datetime] = Field(description="노드 수정일")

class NodesWithRelationshipsResponse(BaseModel):
    nodes: List[NodeInDB]
    relations: List[RelationshipModel]