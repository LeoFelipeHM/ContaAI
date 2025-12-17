from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from uuid import UUID

from services.chat_service import ChatService
from services.llm_client import LLMClient
from auth.security import get_current_user
from database.data_module import User

chat_router = APIRouter(prefix="/chat", tags=["chat"])

def get_llm_client() -> LLMClient:
    return LLMClient()  

def get_chat_service(llm_client: LLMClient = Depends(get_llm_client)) -> ChatService:
    return ChatService(llm_client)

class ChatSQLInput(BaseModel):
    message: str

class ChatSQLOutput(BaseModel):
    sql: str

@chat_router.post("/sql", response_model=ChatSQLOutput)
async def natural_language_to_sql(
    payload: ChatSQLInput,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    try:
        sql = await chat_service.generate_sql(
            user_id=current_user.id,
            message=payload.message
        )

        clean_sql = sql.replace("```sql", "").replace("```", "").strip()

        return {"sql": clean_sql}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate SQL: {str(e)}"
        )