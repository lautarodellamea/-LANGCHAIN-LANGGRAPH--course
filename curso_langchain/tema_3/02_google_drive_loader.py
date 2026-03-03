# pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

from langchain_community.document_loaders import GoogleDriveLoader

credentials_path = "C:\\LAUTARO\\LANGCHAIN\\curso_langchain\\tema_3\\credentials.json"
token_path = "C:\\LAUTARO\\LANGCHAIN\\curso_langchain\\tema_3\\token.json" # este se creara automaticamente al ejecutar el codigo



loader = GoogleDriveLoader(
  folder_id="1DqJ46y_GmsVEOKdS-Hs9fd7I2dIEm8YW", # carpeta de google drive, lo sacamos de la url de la carpeta en google drive
  credentials_path=credentials_path,
  token_path=token_path,
  recursive=True, # si queremos cargar todos los archivos de la carpeta y sus subcarpetas

)

documents = loader.load()

# print((documents))
print(f"Metadatos: {documents[0].metadata}")
print(f"Contenido: {documents[0].page_content}")








