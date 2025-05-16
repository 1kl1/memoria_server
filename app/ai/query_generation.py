from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import StrOutputParser
from app.ai.model import claude_llm
from app.schemas.ai import Neo4jCipherQuery, RawNeo4jCipherQuery

def get_find_related_graph_chain():
    """추출된 의미와 관련된 노드를 찾기 위한 Cypher 쿼리"""
    
    parser = PydanticOutputParser(pydantic_object=Neo4jCipherQuery)
    
    template = """
    추출된 의미와 엔티티를 기반으로 Neo4j 데이터베이스에서 관련 노드를 검색하기 위한 Cypher 쿼리를 작성하세요.
    Cypher 쿼리는 주어진 label을 가진 노드만을 검색해야 합니다.
    이전에 생성했던 쿼리가 실패했을 경우 에러 메시지가 previous_query_error에 포함되어 있습니다.
    
    주어진 label: {label}
    노드의 title: {title}
    노드의 주요 내용 summary: {summary}
    추출된 entities: {entities}

    노드의 속성 목록:
    title: String
    summary: String
    entities: String Array
    
    쿼리 작성 시 유의사항:
    1. 노드의 주요 summary와 추출된 entitiy의 키워드를 활용하여 노드를 검색합니다. 
    2. 의미론적으로 관련된 노드를 찾기 위해 CONTAINS 또는 유사성 검색을 사용합니다.
    3. 결과는 최대 100개로 제한합니다.
    4. apoc.text.sorensenDiceSimilarity() 함수를 사용하여 유사성을 계산합니다.

    previous_query_error:
    {previous_query_error}

    {format_instructions}
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["title", "label", "summary", "entities", "previous_query_error"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    query_chain = prompt | claude_llm | StrOutputParser() | parser
    
    return query_chain




def get_create_relation_query_chain():
    """생성된 노드와, 기존 노드 간의 관계를 생성하기 위한 Cypher 쿼리"""
    
    parser = PydanticOutputParser(pydantic_object=RawNeo4jCipherQuery)
    
    template = """
    타겟 노드와 연관 노드들 사이의 관계를 생성하는 Neo4j 쿼리를 작성하세요.

    주어진 라벨: {label}
    타겟 노드: {target_node}
    연관 노드들: {existing_nodes}

    
    쿼리 작성 시 유의사항:
    1. 모든 노드는 동일한 label을 가지고 있습니다.
    2. 타겟 노드와 연관 노드들 간의 관계를 생성합니다.
    3. 관계 유형은 다음 5가지 중 하나여야 합니다. [(REFERS_TO, REFERENCED_BY), RELATED_TO, (PARENT_OF, CHILD_OF)].
    4. MERGE 구문을 사용하여 중복 노드/관계 생성을 방지합니다.
    

    previous_query_error:
    {previous_query_error}

    {format_instructions}
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["label", "target_node", "existing_nodes", "previous_query_error"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    relationship_chain = prompt | claude_llm | StrOutputParser() | parser
    
    return relationship_chain


def get_search_question_query_chain():
    """사용자의 질문과 관련한 노드를 검색하기 위한 Cypher 쿼리"""
    
    parser = PydanticOutputParser(pydantic_object=Neo4jCipherQuery)
    
    template = """
    사용자의 질문과 관련된 노드들을 neo4j 데이터베이스에서 검색하기 위한 Cypher 쿼리를 작성하세요.
    
    사용자의 질문: {question}
    주어진 라벨: {label}

    노드의 속성 목록:
    title: String
    summary: String
    entities: String Array

    쿼리 작성 시 유의사항:
    1. 주어진 라벨을 가진 노드들 중에서 사용자의 질문과 관련된 노드를 검색합니다.
    2. 질문의 주요한 키워드를 추출한 뒤 의미론적으로 관련된 노드를 찾기 위해 CONTAINS 또는 유사성 검색을 사용합니다. 
    3. 유사성 검색 시 apoc.text.sorensenDiceSimilarity() 함수를 사용하여 유사성을 계산합니다.
    4. 노드의 title, summary, entities 속성을 사용하여 질문과 관련된 노드를 찾습니다.
    5. 결과는 최대 100개로 제한합니다.

    previous_query_error:
    {previous_query_error}

    {format_instructions}
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["label", "question", "previous_query_error"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    relationship_chain = prompt | claude_llm | StrOutputParser() | parser
    
    return relationship_chain
