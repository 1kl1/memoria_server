from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import StrOutputParser
from app.ai.model import claude_llm
from app.schemas.ai import AnswerModel, SummarizedText



def get_text_extraction_chain():
    """메모에서 중요한 의미를 추출"""

    parser = PydanticOutputParser(pydantic_object=SummarizedText)
    
    template = """
    다음 메모를 분석하여 엔티티를 추출해 주시고, 메모의 주요 의미를 요약해 주세요.:
    
    메모제목: {title}
    메모: {text}
    
    주요 엔티티란 메모에 등장하는 사람, 조직, 장소, 제품, 개념 등의 구체적인 대상을 말합니다.
    주요 엔티티는 1~10개 이내로 추출해야 합니다.
    요약은 메모의 핵심 내용을 간결하게 정리한 것으로, 메모의 주제와 관련된 중요한 정보만 포함해야 합니다.

    {format_instructions}
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["text", "title"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    extraction_chain = prompt | claude_llm | StrOutputParser() | parser
    
    return extraction_chain


def get_update_node_chain():
    """이미 존재하는 노드와 새로운 데이터 업데이트"""

    parser = PydanticOutputParser(pydantic_object=SummarizedText)

    template = """
    기존의 summary와 entities를 바탕으로 추가되는 summary과 entities가 주어졌을 때,
    새로운 메모의 summary과 entities를 업데이트 해주세요.:

    메모 주제: {title}
    
    기존 summary: {prev_summary}
    기존 entities: {prev_entities}

    추가되는 summary: {new_summary}
    추가되는 entities: {new_entities}

    주요 엔티티란 메모에 등장하는 사람, 조직, 장소, 제품, 개념 등의 구체적인 대상을 말합니다.
    주요 엔티티는 1~10개 이내로 추출해야 합니다.
    요약은 메모의 핵심 내용을 간결하게 정리한 것으로, 메모의 주제와 관련된 중요한 정보만 포함해야 합니다.
    메모의 제목은 변경되지 않습니다.

    {format_instructions}
    """

    prompt = PromptTemplate(
        template=template,
        input_variables=["title", "prev_summary", "prev_entities", "new_summary", "new_entities"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    extraction_chain = prompt | claude_llm | StrOutputParser() | parser
    
    return extraction_chain




def get_answer_with_nodes_query_chain():
    """검색된 노드를 기반으로 사용자의 질문에 답변하는 쿼리"""

    parser = PydanticOutputParser(pydantic_object=AnswerModel)

    template = """
    사용자의 질문에 답변해주세요.
    주어진 노드들의 내용을 기반으로 답변을 작성해야 합니다.
    주어진 노드가 존재하지 않을 경우, 관련된 노드를 찾을 수 없었다고 명시해주세요.

    사용자의 질문:
    {question}
    주어진 노드들:
    {nodes}

    {format_instructions}
    """

    prompt = PromptTemplate(
        template=template,
        input_variables=["title", "prev_summary", "prev_entities", "new_summary", "new_entities"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    extraction_chain = prompt | claude_llm | StrOutputParser() | parser
    
    return extraction_chain
