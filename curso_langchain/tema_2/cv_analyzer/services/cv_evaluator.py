from langchain_openai import ChatOpenAI
from models.cv_model import AnalisisCV
from prompts.cv_prompts import crear_sistema_prompts

def crear_evaluador_cv():
  """Crea un evaluador de CVs basado en el modelo de datos AnalisisCV"""
  modelo_base = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

  modelo_estructurado = modelo_base.with_structured_output(AnalisisCV)
  chat_prompt = crear_sistema_prompts()

  # elaboro la cadena
  evaluador_cv = chat_prompt | modelo_estructurado

  return evaluador_cv


def evaluar_candidato(texto_cv: str, descripcion_puesto: str) -> AnalisisCV:
  """Evalua un candidato basado en su CV"""
  try:
    cadena_evaluacion = crear_evaluador_cv()
    resultado = cadena_evaluacion.invoke({
      "texto_cv": texto_cv,
      "descripcion_puesto": descripcion_puesto
    })

    return resultado
  
  except Exception as e:
    return AnalisisCV(
      nombre_candidato="Error al evaluar el candidato",
      experiencia_años=0,
      hablidades_clave=["Error al procesar CV"],
      educacion="Error al evaluar el candidato",
      experiencia_relevante="Error al evaluar el candidato",
      fortalezas=["Requiere revision manuel del CV"],
      areas_mejora=["Verifificar formato y legibilidad del PDF"],
      porcentaje_ajuste=0
    )
   