import json
from app.data.duckdb import DuckDBManager
from app.llm.provider import LLMProvider
from app.agent.sql_validator import validate_sql


async def process_question(
    question: str,
    dataset_id: str,
    llm: LLMProvider,
    db_manager: DuckDBManager,
) -> dict:
    """
    Full orchestration flow:
      question → schema → LLM.generate_sql → validate → DuckDB.execute → LLM.explain_result → response
    """
    schema_info = db_manager.get_dataset_schema(dataset_id)
    schema_str = json.dumps(schema_info, indent=2)

    sql = await llm.generate_sql(question=question, schema=schema_str)

    validated_sql = validate_sql(sql)

    columns, rows = db_manager.execute_query(validated_sql, dataset_id=dataset_id)

    result_str = f"Colunas: {columns}\nLinhas: {rows}"

    answer = await llm.explain_result(
        question=question,
        sql=validated_sql,
        result=result_str,
    )

    return {
        "answer": answer,
        "sql": validated_sql,
        "columns": columns,
        "rows": rows,
    }
