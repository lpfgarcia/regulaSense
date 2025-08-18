import chromadb
import os
import PyPDF2
import io


def get_chromadb_client(folder_path: str):
    """
    Initializes and returns a ChromaDB client using the specified folder path as the persist directory.

    Args:
        folder_path (str): Path to the folder for ChromaDB persistence.

    Returns:
        chromadb.api.Client: An instance of the ChromaDB client.
    """
    # Initialize ChromaDB client
    chroma_client = chromadb.Client()
    # Initialize collection
    collection = chroma_client.create_collection(name="regulacoes")
    # Read all pdf files in the specified folder to a Dict
    files_content = read_all_files_in_folder(folder_path)

    print(files_content)  # Debugging line to check the extracted text

    return chroma_client

    
def read_all_files_in_folder(folder_path):
    """
    Lê todos os arquivos de uma pasta e retorna um dicionário com o nome do arquivo como chave e o conteúdo como valor.
    Args:
        folder_path (str): Caminho para a pasta que contém os arquivos a serem lidos.
    Returns:
        dict: Dicionário com nomes dos arquivos como chaves e conteúdos dos arquivos como valores.
    """
    files_content = {}
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        # Verifica se é um arquivo (ignora subpastas)
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                files_content[filename] = PyPDF2.PdfReader(f).pages[0].extract_text()
    return files_content
