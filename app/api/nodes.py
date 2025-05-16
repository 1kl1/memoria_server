from fastapi import HTTPException, Depends, APIRouter
from app.db.session import get_neo4j
from neo4j import Session

from app.db.util.utilities import convert_neo4j_datetime

router = APIRouter(prefix="/test-nodes", tags=["test-nodes"])

@router.get("/")
def get_all_nodes(
    neo4j: Session = Depends(get_neo4j),
):
    query = """
    MATCH (n)
    RETURN n, labels(n) AS labels
    LIMIT 100
    """
    
    result = neo4j.run(query)
    nodes = []
    for record in result:
        node = record["n"]
        node_labels = record["labels"]
        
        node_data = dict(node.items())
        
        nodes.append({
            "uuid": node_data.get("uuid"), 
            "labels": node_labels,
            "title": node_data.get("title", ""),
            "summary": node_data.get("summary", []),
            "entities": node_data.get("entities", []),
            "createdAt": convert_neo4j_datetime(node_data.get("createdAt", "")),
            "updatedAt": convert_neo4j_datetime(node_data.get("updatedAt", ""))
        })
    
    return {"nodes": nodes, "count": len(nodes)}
    