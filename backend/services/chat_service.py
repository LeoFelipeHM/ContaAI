from uuid import UUID
from services.prompts import SYSTEM_PROMPT_SQL_AGENT
from services.sql_validator import validate_sql

class ChatService:
    def __init__(self, llm_client):
        self.llm = llm_client

    def _build_prompt(self, user_id: UUID, message: str):
        return [
            {
                "role": "system",
                "content": SYSTEM_PROMPT_SQL_AGENT
            },
            {
                "role": "user",
                "content": f"user_id = '{user_id}'\n\n{message}"
            }
        ]

    async def generate_sql(
        self,
        user_id: UUID,
        message: str
    ) -> str:
        messages = self._build_prompt(user_id, message)

        sql = await self.llm.chat(messages)
        sql = sql.strip()

        validate_sql(sql)

        return sql

