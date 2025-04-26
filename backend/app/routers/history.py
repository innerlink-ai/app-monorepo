from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
#from data_models import ChatHistory
from database import get_chat_db

router = APIRouter()

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str, db: Session = Depends(get_chat_db)):
    """Retrieve chat history for a specific session."""
    return {"200":"okay"}
    #h#istory = db.query(ChatHistory).filter(ChatHistory.session_id == session_id).all()
    #return {"session_id": session_id, "history": [{"prompt": h.prompt, "response": h.response} for h in history]}
