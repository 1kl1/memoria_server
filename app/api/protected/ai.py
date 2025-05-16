import base64
import io
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Any, List
from app.ai.image_process import  get_image_description_chain
from app.ai.query_generation import get_create_relation_query_chain, get_find_related_graph_chain, get_search_question_query_chain
from app.ai.text_processing import get_answer_with_nodes_query_chain, get_text_extraction_chain
from app.db.util.utilities import compress_image_to_base64, convert_neo4j_datetime
from app.schemas.ai import CreateNodeRelationRequest, CreateNodeRelationResponse, CreateNodeRequest, GetRelatedNodesRequest, QueryRequest, SummarizedText, TextProcessRequest
from app.schemas.note import *
from app.db.session import get_neo4j
from app.db.session import get_db
from app.dependencies import get_current_user
from app.schemas.auth import TokenData
from app.core.exceptions import NotFound
from PIL import Image


router = APIRouter(prefix="/ai", tags=["Ai"])

@router.post("/analyze_image")
async def analyze_image(
    image: UploadFile = File(...),
    label: str = Form(...),
    token_data: TokenData = Depends(get_current_user),
) -> Any:
    """
    image에서 유의미한 정보 추출하여 리턴하는 api
    """
    try:
        image_content = await image.read()
        image_data = await compress_image_to_base64(image_content)
        description_chain = get_image_description_chain()
        
        result = description_chain({
            "topic": label,
            "image_data": image_data
        })
        
        return JSONResponse(content={
            "description": result.description
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

    

@router.post("/summarize", response_model=SummarizedText)
async def summarize_text(
    request: TextProcessRequest,
    token_data: TokenData = Depends(get_current_user),
) -> Any:
    """
    note에서 유의미한 정보 추출하여 리턴하는 api
    """
    chain = get_text_extraction_chain()
    try:
        extraction_result = chain.invoke({"text": request.text,"title":request.title})
        
        return extraction_result

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"처리 중 오류 발생: {str(e)}")


@router.post("/get_related_nodes")
async def get_related_nodes(
    request: GetRelatedNodesRequest,
    neo4j: Session = Depends(get_neo4j),
    token_data: TokenData = Depends(get_current_user),
) -> Any:
    """
    요약 정보로부터 cipher query를 생성하고,
    db로부터 노드와 relation을 가져와서 리턴하는 api
    """
    chain = get_find_related_graph_chain()
    max_retries = 3
    retry_count = 0
    previous_query_error = ""

    while retry_count < max_retries:
        try:
            cipher_query = chain.invoke({
                "label": request.label,
                "title": request.node.title,
                "summary": request.node.summary,
                "entities": request.node.entities,
                "previous_query_error": previous_query_error,
            })
            
            result = neo4j.run(cipher_query.query, cipher_query.query_params)
            nodes = []
            unique_uuids = set()
            for record in result:
                node = record["n"]
                node_data = dict(node.items())
                uuid = node_data.get("uuid", "")

                if uuid in unique_uuids:
                    continue

                unique_uuids.add(uuid)

                nodes.append({
                    "uuid": uuid, 
                    "label": request.label,
                    "title": node_data.get("title", ""),
                    "summary": node_data.get("summary", []),
                    "entities": node_data.get("entities", []),
                    "createdAt": convert_neo4j_datetime(node_data.get("createdAt", "")),
                    "updatedAt": convert_neo4j_datetime(node_data.get("updatedAt", ""))
                })
            return {"nodes": nodes}
        
        except Exception as e:
            print(f"쿼리 실행 중 오류 발생: {str(e)}")
            previous_query_error = str(e)
            retry_count += 1
            if retry_count < max_retries:
                print(f"AI에게 수정된 쿼리를 요청합니다. 재시도 횟수: {retry_count}")
            else:
                return {"nodes": []}
    

@router.post("/create_node_relation", response_model=CreateNodeRelationResponse)
async def create_node_relation(
    node_data: CreateNodeRelationRequest,
    neo4j: Session = Depends(get_neo4j),
    token_data: TokenData = Depends(get_current_user),
) -> Any:
    """
    node와 관련된 노드들을 받아서 relation을 생성.
    """
    chain = get_create_relation_query_chain()
    max_retries = 3
    retry_count = 0
    previous_query_error = ""

    while retry_count < max_retries:
        try:
            cipher_query = chain.invoke({
                "label": node_data.label,
                "target_node": node_data.node,
                "existing_nodes": node_data.related_nodes,
                "previous_query_error": previous_query_error,
            })
            result = neo4j.run(cipher_query.query)
            if not result:
                raise NotFound("관계 생성 실패")
            
            get_relation_query = f"""
                MATCH (target_node:{node_data.label} {{uuid: $target_uuid}})
                MATCH (related_node:{node_data.label})
                WHERE related_node.uuid IN $related_uuids_list
                MATCH (target_node)-[relation]-(related_node)
                RETURN target_node, related_node, relation
            """

            related_uuids_list = [node.uuid for node in node_data.related_nodes]
            result = neo4j.run(get_relation_query, {
                "target_uuid": node_data.node.uuid,
                "related_uuids_list": related_uuids_list
            })
            
            relations = []
            for record in result:
                relation = record["relation"]
                relations.append({
                    "type": relation.type,
                    "properties": dict(relation.items()),
                    "source": record["target_node"].get("uuid"),
                    "target": record["related_node"].get("uuid")
                })
            
            return {"relations": relations}

            
        except Exception as e:
            print(f"쿼리 실행 중 오류 발생: {str(e)}")
            previous_query_error = str(e)
            retry_count += 1
            if retry_count < max_retries:
                print(f"AI에게 수정된 쿼리를 요청합니다. 재시도 횟수: {retry_count}")
            else:
                raise HTTPException(status_code=500, detail=f"처리 중 오류 발생: {str(e)}")
            



@router.post("/query")
async def get_related_nodes(
    request: QueryRequest,
    neo4j: Session = Depends(get_neo4j),
    token_data: TokenData = Depends(get_current_user),
) -> Any:
    """
    질문을 분석해서 graph db를 검색하고, 그에 대한 답변을 하는 api
    """
    chain = get_search_question_query_chain()
    question_chain = get_answer_with_nodes_query_chain()
    max_retries = 3
    retry_count = 0
    previous_query_error = ""

    while retry_count < max_retries:
        try:
            cipher_query = chain.invoke({
                "label": request.label,
                "question": request.question,
                "previous_query_error": previous_query_error,
            })
            print(cipher_query)
            result = neo4j.run(cipher_query.query, cipher_query.query_params)
            referred_nodes = []
            referred_nodes_for_answer = []

            for record in result:
                node = record["n"]
                node_data = dict(node.items())
                
                referred_nodes.append({
                    "uuid": node_data.get("uuid", ""), 
                    "label": request.label,
                    "title": node_data.get("title", ""),
                    "summary": node_data.get("summary", []),
                    "entities": node_data.get("entities", []),
                    "createdAt": convert_neo4j_datetime(node_data.get("createdAt", "")),
                    "updatedAt": convert_neo4j_datetime(node_data.get("updatedAt", ""))
                })
                referred_nodes_for_answer.append({
                    "title": node_data.get("title", ""),
                    "summary": node_data.get("summary", []),
                    "entities": node_data.get("entities", []),
                })

            answer = question_chain.invoke({
                "question": request.question,
                "nodes": referred_nodes_for_answer,
            })
            
            return {"referred_nodes": referred_nodes, "answer": answer.answer}
        
        except Exception as e:
            print(f"쿼리 실행 중 오류 발생: {str(e)}")
            previous_query_error = str(e)
            retry_count += 1
            if retry_count < max_retries:
                print(f"AI에게 수정된 쿼리를 요청합니다. 재시도 횟수: {retry_count}")
            else:
                return {"nodes": [], "answer": "질문 처리 중 에러가 발생했습니다."}