# En google console crear la API key modo OAuth, agregar el usuario de prueba en publico y habilitar el API de Gmail

from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model

# https://reference.langchain.com/python/langchain-community/agent_toolkits
from langchain_community.tools.gmail.utils import get_gmail_credentials, build_resource_service, clean_email_body
from langchain_community.tools.gmail import (
    GmailCreateDraft,
    GmailGetMessage,
    GmailGetThread,
    GmailSearch,
    GmailSendMessage,
)
import base64
import email
import os
from typing import Any, Dict, List, Optional

from langchain_core.callbacks import CallbackManagerForToolRun


def _safe_decode(data: bytes | None) -> str:
    """Decodificación con tolerancia a errores (Santiago: decode con errors='replace')."""
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

# Configurar el directorio de trabajo
original_dir = os.getcwd()
os.chdir(r"C:\LAUTARO\LANGCHAIN\curso_langchain\tema_6\agentes")

# Credenciales con tu archivo (por defecto Gmail busca credentials.json)
credentials = get_gmail_credentials(client_secrets_file="credential-agentes.json")
api_resource = build_resource_service(credentials=credentials)

# Configurar el toolkit de Gmail (herramientas con decode(..., errors='replace') para evitar fallos de encoding)
tools = [
    GmailCreateDraft(api_resource=api_resource),
    GmailSendMessage(api_resource=api_resource),
    GmailSearchSafe(api_resource=api_resource),
    GmailGetMessageSafe(api_resource=api_resource),
    GmailGetThread(api_resource=api_resource),
]

# Configurar modelo del agente que soporte tool calling
model = init_chat_model("openai:gpt-4o", temperature=0)

# Prompt de agente que define su comportamiento
prompt = ChatPromptTemplate.from_messages([
  # prompt de sistema que define el comportamiento del agente
    ("system", """Eres un asistente de email profesional. Para procesar emails sigue EXACTAMENTE estos pasos:

    1. PRIMERO: Usa 'search_gmail' con query 'in:inbox' para obtener la lista de mensajes en la bandeja de entrada.
    
    2. SEGUNDO: De la lista obtenida, identifica el message_id del email más reciente (el primer resultado).
    
    3. TERCERO: Usa 'get_gmail_message' con el message_id real obtenido en el paso anterior para obtener el contenido completo.
    
    4. CUARTO: Analiza el email y EXTRAE esta información crítica:
       - Thread ID (busca "Thread ID:" en el contenido)
       - Remitente original (busca "From:" y extrae el email)
       - Asunto original (busca "Subject:")
       - Contenido principal del mensaje
    
    5. QUINTO: Genera una respuesta profesional y apropiada en español.
    
    6. SEXTO: Usa 'create_gmail_draft' para crear un borrador de RESPUESTA (no email nuevo) con:
       - "message": tu respuesta generada
       - "subject": "Re: [asunto original]" (si no empieza ya con "Re:")
       - "to": email del remitente original
       - "thread_id": el Thread ID extraído del paso 4 (MUY IMPORTANTE para que sea una respuesta)

    CRÍTICO PARA RESPUESTAS:
    - SIEMPRE incluye "thread_id" en create_gmail_draft para que sea una respuesta, no un email nuevo
    - El "to" debe ser el email del remitente original
    - El "subject" debe empezar con "Re:" si no lo tiene ya

    IMPORTANTE: 
    - NUNCA uses message_id hardcodeados como '1' o '2' 
    - SIEMPRE obtén los IDs reales de los mensajes primero
    - Sin thread_id, el borrador será un email nuevo, no una respuesta
    - Si no encuentras thread_id, informa el problema pero intenta crear el borrador igual
    
    Si encuentras errores, explica qué información falta y por qué."""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])
# ("human", "{input}"), Es el mensaje que representa lo que escribe el usuario.
# ("placeholder", "{agent_scratchpad}") es un espacio reservado para que el agente piense y registre pasos intermedios.

# En agentes con tools (como tu caso con Gmail):
# El LLM no resuelve todo de una, sino que hace esto:
# Pensamiento → acción (tool) → resultado → pensamiento → acción...

# Crear agente
agent = create_tool_calling_agent(model, tools, prompt)

# Crear executor del agente
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools,
    verbose=True, # para ver todos los logs a medida que se van ejecutando las herramientas
    handle_parsing_errors=True, # para que los herrores que puedan ocurrir el agente ejecutara otra herramienta uo la misma pero con diferentes argumentos
    max_iterations=10 # Limitar iteraciones para evitar bucles *loops (MUY IMPORTANTE PARA NO CONSUMIR TODOS NUESTROS RECURSOS)
)

# Funcion para procesar el email mas reciente
def process_latest_email():
    try:
        response = agent_executor.invoke({
            "input": "Procesa el email más reciente en la bandeja de entrada y genera un borrador de respuesta profesional."
        })
        return response['output'] # devuelve la respuesta del agente
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