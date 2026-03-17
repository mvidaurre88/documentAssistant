import win32com.client

# ------------------
# FUNCION PARA CERRAR ARCHIVO DE WORD ABIERTO
# ------------------
def close_file(fileName: str):
    try:
        wordFiles = win32com.client.GetActiveObject("Word.Application")

        for doc in wordFiles.Documents:
            if fileName.lower() in doc.FullName.lower():
                doc.Save()
                doc.Close()

    except Exception as e:
        print("Error:", e)