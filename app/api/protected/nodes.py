from typing import List, Optional
from fastapi import HTTPException, Depends, APIRouter
from app.ai.text_processing import get_update_node_chain
from app.db.session import get_neo4j
from neo4j import Session
from app.db.util.utilities import convert_neo4j_datetime
from app.dependencies import get_current_user
from app.schemas.ai import BaseNode, CreateNodeResponse, CreateSingleNode, NodeInDB, UpdateSingleNode
from app.schemas.auth import TokenData
from app.schemas.node import NodesWithRelationshipsResponse

router = APIRouter(prefix="/nodes", tags=["nodes"])

@router.get("/{label}", response_model=NodesWithRelationshipsResponse)
async def get_nodes_with_relationships(
    label: str,
    token_data: TokenData = Depends(get_current_user),
    session: Session = Depends(get_neo4j),
):
    """
    특정 라벨을 가진 노드들과 그 노드들 간의 관계를 가져옵니다.
    """
    # Cypher 쿼리 작성
    query = f"""
    MATCH (n:{label})
    OPTIONAL MATCH (n)-[r]-(m)
    WITH n, r, m
    WHERE r IS NULL OR elementId(n) < elementId(m)
    RETURN n, r, m
    LIMIT 100
    """
    
    result = session.run(query)
    
    nodes = {}
    relationships = []
    
    for record in result:
        source_node = record["n"]
        target_node = record["m"]
        relationship = record["r"]

        if source_node.id not in nodes:
            node_data = dict(source_node.items())
            nodes[source_node.id] = {
                "uuid": node_data.get("uuid"),
                "label": label,
                "title": node_data.get("title", ""),
                "summary": node_data.get("summary", []),
                "entities": node_data.get("entities", []),
                "createdAt": convert_neo4j_datetime(node_data.get("createdAt", "")),
                "updatedAt": convert_neo4j_datetime(node_data.get("updatedAt", ""))
            }

        if(target_node is None):
            continue
        
        if target_node.id not in nodes:
            node_data = dict(target_node.items())
            nodes[target_node.id] = {
                "uuid": node_data.get("uuid"),
                "label": label,
                "title": node_data.get("title", ""),
                "summary": node_data.get("summary", []),
                "entities": node_data.get("entities", []),
                "createdAt": convert_neo4j_datetime(node_data.get("createdAt", "")),
                "updatedAt": convert_neo4j_datetime(node_data.get("updatedAt", ""))
            }
        
        relationships.append({
            "id": relationship.id,
            "type": relationship.type,
            "properties": dict(relationship),
            "source": dict(source_node.items()).get("uuid"),
            "target": dict(target_node.items()).get("uuid")
        })
    
    return {
        "nodes": list(nodes.values()),
        "relations": relationships
    }


@router.get("/{label}/{title}", response_model=Optional[NodeInDB])
async def get_node(
    label: str,
    title: str,
    token_data: TokenData = Depends(get_current_user),
    session: Session = Depends(get_neo4j),
):
    """
    특정 label과 title을 가진 노드 1개를 가져옵니다.
    """
    # Cypher 쿼리 작성
    query = f"""
        MATCH (n:{label} {{title: $title}})
        RETURN n
        LIMIT 1
    """

    result = session.run(query, {"title": title})
    
    record = result.single()
    print(f"asdfasdfsd {record}")
    
    if not record:
        return {}
    if record["n"] is None:
        return {}

    return {
        "uuid": record["n"].get("uuid"),
        "label": label,
        "title": record["n"].get("title", ""),
        "summary": record["n"].get("summary", []),
        "entities": record["n"].get("entities", []),
        "createdAt": convert_neo4j_datetime(record["n"].get("createdAt", "")),
        "updatedAt": convert_neo4j_datetime(record["n"].get("updatedAt", ""))
    }


# delete node
@router.delete("/{label}/{uuid}")
async def delete_node(
    label: str,
    uuid: str,
    token_data: TokenData = Depends(get_current_user),
    session: Session = Depends(get_neo4j),
):
    """
    특정 label과 uuid를 가진 노드를 삭제합니다.
    """
    # Cypher 쿼리 작성
    query = f"""
        MATCH (n:{label} {{uuid: $uuid}})
        DETACH DELETE n
    """
    
    result = session.run(query, {"uuid": uuid})
    
    if not result:
        raise HTTPException(status_code=404, detail="Node not found")
    
    return {"detail": "Node and Relations deleted successfully"}


@router.post("/{label}", response_model=CreateNodeResponse)
async def create_node(
    label: str,
    node_data: CreateSingleNode,
    token_data: TokenData = Depends(get_current_user),
    session: Session = Depends(get_neo4j),
):
    """
    특정 label을 가진 노드를 생성합니다.
    """
    # Cypher 쿼리 작성
    query = f"""
        CREATE (n:{label} {{title: $title, summary: $summary, entities: $entities, createdAt: datetime(), updatedAt: datetime(), uuid: randomUUID()}})
        RETURN n
    """
    
    result = session.run(query, {"title": node_data.title, "summary": node_data.summary, "entities": node_data.entities})
    
    record = result.single()

    if not record:
        raise HTTPException(status_code=500, detail="Node creation failed")
    
    return {
        "uuid": record["n"].get("uuid"),
        "label": label,
        "title": record["n"].get("title", ""),
        "summary": record["n"].get("summary", ""),
        "entities": record["n"].get("entities", []),
        "createdAt": convert_neo4j_datetime(record["n"].get("createdAt", "")),
        "updatedAt": convert_neo4j_datetime(record["n"].get("updatedAt", ""))
    }
    

# update node
@router.put("/{label}", response_model=CreateNodeResponse)
async def update_node(
    label: str,
    node_data: UpdateSingleNode,
    token_data: TokenData = Depends(get_current_user),
    session: Session = Depends(get_neo4j),
):
    """
    특정 label을 가진 노드를 업데이트합니다.
    """

    update_node_chain = get_update_node_chain()
        
    result = update_node_chain.invoke({
        "title": node_data.node.title,
        "prev_summary": node_data.node.summary,
        "prev_entities": node_data.node.entities,
        "new_summary": node_data.summary,
        "new_entities": node_data.entities
    })

    new_summary = result.summary
    new_entities = result.entities

    query = f"""
        MATCH (n:{label} {{title: $title}})
        SET n.summary = $summary, n.entities = $entities, n.updatedAt = datetime()
        RETURN n
    """
    result = session.run(query, {"title": node_data.node.title, "summary": new_summary, "entities": new_entities})
    
    record = result.single()

    if not record:
        raise HTTPException(status_code=500, detail="Node update failed")
    
    return {
        "uuid": record["n"].get("uuid"),
        "label": label,
        "title": record["n"].get("title", ""),
        "summary": record["n"].get("summary", ""),
        "entities": record["n"].get("entities", []),
        "createdAt": convert_neo4j_datetime(record["n"].get("createdAt", "")),
        "updatedAt": convert_neo4j_datetime(record["n"].get("updatedAt", ""))
    }