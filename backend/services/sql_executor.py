from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

async def execute_sql(
    session: AsyncSession,
    sql: str
):
    result = await session.execute(text(sql))

    if sql.strip().lower().startswith("select"):
        rows = result.mappings().all()
        return {
            "type": "select",
            "rows": rows
        }

    await session.commit()

    return {
        "type": "mutation",
        "affected_rows": result.rowcount
    }
