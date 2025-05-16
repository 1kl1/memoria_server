from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel, Field, Json
from typing import List, Optional,Dict, Any

from app.schemas.node import BaseNode, NodeInDB, RelationshipModel

class TextProcessRequest(BaseModel):
    text: str
    title: str

class GetRelatedNodesRequest(BaseModel):
    label: str
    node: BaseNode

class CreateSingleNode(BaseModel):
    title: str
    summary: str
    entities: List[str]

class UpdateSingleNode(BaseModel):
    node: BaseNode
    summary: str = Field(description="노드 요약")
    entities: List[str] = Field(description="노드에 포함된 엔티티 목록")
class CreateNodeResponse(NodeInDB):
    pass


class CreateNodeRelationRequest(BaseModel):
    label: str
    node: BaseNode
    related_nodes: List[BaseNode]

class CreateNodeRelationResponse(BaseModel):
    relations: List[RelationshipModel]

class CreateNodeRequest(BaseModel):
    label: str
    title: str
    summary: str
    entities: List[str]
    related_nodes: List[BaseNode]

class SummarizedText(BaseModel): 
    summary: str = Field(description="메모 내용 요약")
    entities: List[str] = Field(description="메모에서 확인된 주요 엔티티들의 목록과 그 속성")
    

class Neo4jCipherQuery(BaseModel):
    query: str  = Field(description="Neo4j Cypher 쿼리 문자열")
    query_params: Json = Field(description="쿼리 파라미터를 포함하는 JSON 객체")

class RawNeo4jCipherQuery(BaseModel):
    query: str= Field(description="Neo4j Cypher 쿼리 문자열")


class ImageDescription(BaseModel):
    """이미지에 대한 설명 클래스"""
    description: str = Field(description="이미지에 대한 3줄 이내의 설명")


class QueryRequest(BaseModel):
    label: str
    question: str
    # language_tag: str

class AnswerModel(BaseModel):
    """질문에 대한 답변 클래스"""
    answer: str = Field(description="질문에 대한 답변")