from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import io
import base64
from typing import Optional
from PIL import Image
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnablePassthrough
from app.ai.model import claude_llm
from app.schemas.ai import ImageDescription


def get_image_description_chain():
    """이미지로부터 설명을 생성하는 체인"""
    
    parser = PydanticOutputParser(pydantic_object=ImageDescription)
    format_instructions = parser.get_format_instructions()
    
    def generate_description(inputs):
        topic = inputs["topic"]
        base64_image = inputs["image_data"]["base64_image"]
        mime_type = inputs["image_data"]["mime_type"]
        
        
        prompt_text = f"""
        다음 이미지를 자세히 분석해 주세요. 이미지는 다음과 같은 주제 컨텍스트에서 제안되었습니다. {topic}

        1. 이미지에 포함된 주요 요소를 모두 설명해 주세요.
        2. 이미지에 텍스트가 있다면 모든 텍스트를 정확히 옮겨 적어주세요.
        3. 이미지에 있는 중요한 세부 사항(로고, 색상, 배치, 표현 등)을 설명해 주세요.
        4. 이미지의 전체적인 맥락과 목적이 무엇으로 보이는지 분석해 주세요.
        5. 이미지에 포함된 모든 데이터, 차트, 그래프가 있다면 그 내용을 자세히 설명해 주세요.
        6. 이미지에 사람이 있다면, 인원수와 일반적인 상황만 설명하고 특정 인물을 식별하지 마세요.

        가능한 한 자세하고 객관적으로 이미지를 설명해 주세요. 중요한 정보가 누락되지 않도록 이미지의 모든 부분을 검토해 주세요.
        
        {format_instructions}
        """
        
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt_text},
                {
                    "type": "image",
                    "source": {
                        "type": "base64", 
                        "media_type": mime_type,
                        "data": base64_image
                    }
                }
            ]
        )
        
        response = claude_llm.invoke([message])
        
        try:
            parsed_response = parser.parse(response.content)
            return parsed_response
        except Exception as e:
        
            return ImageDescription(description=response.content)
    
    return generate_description
