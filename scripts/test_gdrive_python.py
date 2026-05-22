import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

def test_gdrive_access():
    print("--- Testando Acesso Direto ao Google Drive via Python ---")
    creds_path = r"C:\Users\victor.bernardi\.credentials\google-service-account.json"
    
    if not os.path.exists(creds_path):
        print(f"ERRO: Arquivo não encontrado em {creds_path}")
        return

    try:
        creds = service_account.Credentials.from_service_account_file(
            creds_path, scopes=['https://www.googleapis.com/auth/drive']
        )
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(pageSize=5, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('Nenhum arquivo encontrado.')
        else:
            print('Arquivos encontrados:')
            for item in items:
                print(f"{item['name']} ({item['id']})")
        print("SUCESSO: Conectividade básica OK.")
    except Exception as e:
        print(f"FALHA: {str(e)}")

if __name__ == "__main__":
    test_gdrive_access()
