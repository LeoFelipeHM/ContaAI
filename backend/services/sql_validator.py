import re

FORBIDDEN = re.compile(r"\b(drop|delete|truncate|alter)\b", re.I)

def validate_sql(sql: str):
    if FORBIDDEN.search(sql):
        raise ValueError("Forbidden SQL operation detected")

    if sql.count(";") > 1:
        raise ValueError("Multiple SQL statements detected")

    if "user_id" not in sql.lower():
        raise ValueError("user_id filter is mandatory")

    if sql.strip().lower().startswith("update") and "where" not in sql.lower():
        raise ValueError("UPDATE without WHERE is not allowed")
