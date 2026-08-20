from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse
from app.llm.provider_impl import get_llm_provider
from app.data.duckdb import DuckDBManager
from app.agent.orchestrator import process_question

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        llm = get_llm_provider()
        db_manager = DuckDBManager()

        result = await process_question(
            question=request.question,
            dataset_id=request.dataset_id,
            llm=llm,
            db_manager=db_manager,
        )

        return ChatResponse(
            answer=result["answer"],
            sql=result["sql"],
            columns=result["columns"],
            rows=result["rows"],
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao processar pergunta: {str(exc)}")
