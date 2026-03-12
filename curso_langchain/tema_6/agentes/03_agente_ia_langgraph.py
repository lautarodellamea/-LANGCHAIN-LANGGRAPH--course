# mecanismo ams recomendado en la actualidad

from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain.chat_models import init_chat_model
from langchain_community.tools.gmail.utils import get_gmail_credentials, build_resource_service, clean_email_body
from langchain_community.tools.gmail import (
    GmailCreateDraft,
    GmailGetMessage,
    GmailGetThread,
    GmailSearch,
    GmailSendMessage,
)
from langchain_core.tools import tool
import base64
import email
import os
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

from langchain_core.callbacks import CallbackManagerForToolRun

# Configurar el directorio de trabajo (carpeta agentes para credential-agentes.json y token.json)
original_dir = os.getcwd()
os.chdir(r"C:\LAUTARO\LANGCHAIN\curso_langchain\tema_6\agentes")

# Credenciales con tu archivo
credentials = get_gmail_credentials(client_secrets_file="credential-agentes.json")
api_resource = build_resource_service(credentials=credentials)


def _safe_decode(data: bytes | None) -> str:
    """Decodificación con tolerancia a errores (decode con errors='replace')."""
    if data is None:
        return ""
    return data.decode("utf-8", errors="replace")


class GmailGetMessageSafe(GmailGetMessage):
    """get_gmail_message usando decode(..., errors='replace') para evitar fallos por encoding."""

    def _run(
        self,
        message_id: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Dict:
        query = (
            self.api_resource.users()
            .messages()
            .get(userId="me", format="raw", id=message_id)
        )
        message_data = query.execute()
        raw_message = base64.urlsafe_b64decode(message_data["raw"])
        email_msg = email.message_from_bytes(raw_message)
        subject = email_msg["Subject"]
        sender = email_msg["From"]
        message_body = ""
        if email_msg.is_multipart():
            for part in email_msg.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get("Content-Disposition"))
                if ctype == "text/plain" and "attachment" not in cdispo:
                    message_body = _safe_decode(part.get_payload(decode=True))
                    break
        else:
            message_body = _safe_decode(email_msg.get_payload(decode=True))
        body = clean_email_body(message_body)
        return {
            "id": message_id,
            "threadId": message_data["threadId"],
            "snippet": message_data["snippet"],
            "body": body,
            "subject": subject,
            "sender": sender,
        }


class GmailSearchSafe(GmailSearch):
    """search_gmail con decode(..., errors='replace') al leer el cuerpo de cada mensaje."""

    def _parse_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for message in messages:
            message_id = message["id"]
            message_data = (
                self.api_resource.users()
                .messages()
                .get(userId="me", format="raw", id=message_id)
                .execute()
            )
            raw_message = base64.urlsafe_b64decode(message_data["raw"])
            email_msg = email.message_from_bytes(raw_message)
            subject = email_msg["Subject"]
            sender = email_msg["From"]
            message_body = ""
            if email_msg.is_multipart():
                for part in email_msg.walk():
                    ctype = part.get_content_type()
                    cdispo = str(part.get("Content-Disposition"))
                    if ctype == "text/plain" and "attachment" not in cdispo:
                        message_body = _safe_decode(part.get_payload(decode=True))
                        break
            else:
                message_body = _safe_decode(email_msg.get_payload(decode=True))
            body = clean_email_body(message_body)
            results.append({
                "id": message["id"],
                "threadId": message_data["threadId"],
                "snippet": message_data["snippet"],
                "body": body,
                "subject": subject,
                "sender": sender,
                "from": email_msg["From"],
                "date": email_msg["Date"],
                "to": email_msg["To"],
                "cc": email_msg["Cc"],
            })
        return results


@tool
def create_gmail_reply_draft(
    message: str,
    to: str,
    subject: str,
    thread_id: str,
    in_reply_to: str | None = None,
) -> str:
    """
    Crea un borrador de respuesta en Gmail que SÍ funciona como respuesta en el hilo.
    Usa esta herramienta cuando quieras crear una RESPUESTA a un email existente.

    Args:
        message: Contenido del mensaje de respuesta
        to: Email del destinatario
        subject: Asunto (debería empezar con Re:)
        thread_id: ID del hilo para que sea una respuesta (OBLIGATORIO)
        in_reply_to: Message-ID del email original (opcional)
    """
    try:
        service = api_resource
        mime_message = MIMEText(message, "plain", "utf-8")
        mime_message["To"] = to
        mime_message["Subject"] = subject
        if in_reply_to:
            mime_message["In-Reply-To"] = in_reply_to
            mime_message["References"] = in_reply_to
        encoded_message = base64.urlsafe_b64encode(
            mime_message.as_bytes()
        ).decode("utf-8")
        draft_body = {
            "message": {
                "raw": encoded_message,
                "threadId": thread_id,
            }
        }
        draft = service.users().drafts().create(
            userId="me",
            body=draft_body,
        ).execute()
        return f"Borrador de RESPUESTA creado exitosamente. Draft ID: {draft['id']}, Thread ID: {thread_id}"
    except Exception as e:
        return f"Error creando borrador de respuesta: {str(e)}"


# Herramientas Gmail con decode seguro + herramienta custom de borrador de respuesta
tools = [
    GmailCreateDraft(api_resource=api_resource),
    GmailSendMessage(api_resource=api_resource),
    GmailSearchSafe(api_resource=api_resource),
    GmailGetMessageSafe(api_resource=api_resource),
    GmailGetThread(api_resource=api_resource),
    create_gmail_reply_draft,
]

# Configurar modelo del agente que soporte tool calling
model = init_chat_model("openai:gpt-4o", temperature=0)

# Prompt de agente que define su comportamiento
system_prompt = """Eres un asistente de email profesional. Para procesar emails sigue EXACTAMENTE estos pasos:

    1. PRIMERO: Usa 'search_gmail' con query 'in:inbox' para obtener la lista de mensajes en la bandeja de entrada.
    
    2. SEGUNDO: De la lista obtenida, identifica el message_id del email más reciente (el primer resultado).
    
    3. TERCERO: Usa 'get_gmail_message' con el message_id real obtenido en el paso anterior para obtener el contenido completo.
    
    4. CUARTO: Analiza el email y EXTRAE esta información crítica:
       - Thread ID (busca "Thread ID:" en el contenido)
       - Remitente original (busca "From:" y extrae el email)
       - Asunto original (busca "Subject:")
       - Contenido principal del mensaje
    
    5. QUINTO: Genera una respuesta profesional y apropiada en español.
    
    6. SEXTO: Usa 'create_gmail_draft' o 'create_gmail_reply_draft' para crear un borrador de RESPUESTA (no email nuevo) con:
       - "message": tu respuesta generada
       - "subject": "Re: [asunto original]" (si no empieza ya con "Re:")
       - "to": email del remitente original
       - "thread_id": el Thread ID extraído del paso 4 (MUY IMPORTANTE para que sea una respuesta)

    CRÍTICO PARA RESPUESTAS:
    - SIEMPRE incluye "thread_id" en create_gmail_draft/create_gmail_reply_draft para que sea una respuesta, no un email nuevo
    - El "to" debe ser el email del remitente original
    - El "subject" debe empezar con "Re:" si no lo tiene ya

    IMPORTANTE: 
    - NUNCA uses message_id hardcodeados como '1' o '2' 
    - SIEMPRE obtén los IDs reales de los mensajes primero
    - Sin thread_id, el borrador será un email nuevo, no una respuesta
    - Si no encuentras thread_id, informa el problema pero intenta crear el borrador igual
    
    Si encuentras errores, explica qué información falta y por qué."""

# Crear agente (create_react_agent deprecado → create_agent desde langchain.agents)
memory = MemorySaver()
agent_executor = create_agent(
    model,
    tools,
    system_prompt=system_prompt,
    checkpointer=memory,
)

def process_latest_email():
    try:
        # Configurar el estado inicial
        # podriamos usar una memoria persistente con sqlLite, postgresql, etc y nos permitiria persisitir el estado, para despues reanudar donde quedamos, ahora le damos uno por defecto
        config = {"configurable": {"thread_id": "gmail-processing"}}
        
        response = agent_executor.invoke(
            {"messages": [("human", "Procesa el email más reciente en la bandeja de entrada y genera un borrador de respuesta profesional.")]},
            config=config,
        )
        return response['messages'][-1].content
    except Exception as e:
        print(f"Error al procesar email: {str(e)}")
        return f"Error {str(e)}"
    
# Ejecutar
if __name__ == "__main__":
    result = process_latest_email()
    print("\n" + "="*50)
    print("RESULTADO:")
    print("="*50)
    print(result)