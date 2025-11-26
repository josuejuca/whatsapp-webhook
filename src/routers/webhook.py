from fastapi import APIRouter, Request
from fastapi import Query, HTTPException
from fastapi.responses import PlainTextResponse
from src.db.storage import db
from src.utils.filter import process_webhook_payload

WEBHOOK_VERIFY_TOKEN = "7b5a67574d8b1d77d2803b24946950f0"

router = APIRouter(
    tags=["Webhook"]
)

"""
Tipos de Webhook que podem ser recebidos:
1. Mensagens de texto
2. Mensagens de mídia (imagens, vídeos, áudios)
3. Atualizações de status (entregue, lido)
4. Eventos de contato (novo contato, bloqueio)
"""

@router.get("/webhook")
def verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """Verifica o webhook do WhatsApp"""
    if hub_mode == "subscribe" and hub_verify_token == WEBHOOK_VERIFY_TOKEN:        
        return PlainTextResponse(hub_challenge or "", status_code=200)
    raise HTTPException(status_code=403, detail="Invalid verify token")


@router.post("/webhook")
async def receive_webhook(request: Request):
    """
    Recebe qualquer payload enviado para o webhook e processa
    """
    data = await request.json()
    
    # Salva o webhook completo no banco
    webhook_id = db.save_webhook(data)
    if webhook_id:
        print(f"\n✓ Webhook #{webhook_id} salvo no banco de dados\n")

    # Processa o payload
    process_webhook_payload(data)

    return {"status": "ok", "webhook_id": webhook_id}
