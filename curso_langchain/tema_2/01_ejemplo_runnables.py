from langchain_core.runnables import RunnableLambda


# usando la clase RunnableLambda dentro de langchain convierto una funcion en un objeto runnable que puedo invocar y como consecuencia tambien podemos concatenar dentro de una cadena
# usamos una funcion lambda y una tradicional
paso1 = RunnableLambda(lambda x: f"Numero {x}")

def duplicar_texto(texto):
  return [texto] * 2

paso2 = RunnableLambda(duplicar_texto)


# ahora las introducimos al ecosistema langchain
# resultado = paso2(paso1(input)) significa eso
cadena = paso1 | paso2

resultado = cadena.invoke(5)
print(resultado)