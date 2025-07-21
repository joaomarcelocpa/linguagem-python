import os.path
import time
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_ID = "1NR6hPSGMiBc2fmWhTDOZzvvQlJ75ielUwiKbn8dojAk"
RANGE = "Julho-25"

def resource_path(relative_path):
    """Retorna o caminho absoluto do recurso, compatível com PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_credentials():
    """Obtém as credenciais de autenticação do Google Sheets."""
    creds = None
    if os.path.exists(resource_path("token.json")):
        creds = Credentials.from_authorized_user_file(resource_path("token.json"), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(resource_path("client_secret.json"), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(resource_path("token.json"), "w") as token:
            token.write(creds.to_json())

    return creds

def get_current_balance(service):
    """Obtém o saldo atual da planilha, garantindo que valores negativos sejam considerados corretamente."""
    try:
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE).execute()
        values = result.get("values", [])

        if values and len(values) > 1:
            try:
                saldo_str = values[-1][5].replace("R$", "").replace(".", "").replace(",", ".").strip()
                saldo_atual = float(saldo_str) if saldo_str else 0.0
            except ValueError:
                saldo_atual = 0.0
        else:
            saldo_atual = 0.0

        return saldo_atual
    except HttpError as err:
        print(f"Erro ao obter saldo: {err}")
        return 0.0

def update_sheet(data):
    """Atualiza a planilha do Google Sheets com os novos dados inseridos."""
    try:
        creds = get_credentials()
        service = build("sheets", "v4", credentials=creds)

        # Obtendo saldo atual
        saldo_atual = get_current_balance(service)

        valor = float(data["Valor"])
        if data["Tipo"] in ["PIX", "Depósito", "Stone"]:
            saldo_atual += valor  # Aumenta o saldo
            debito = f"R$ {valor:.2f}".replace(".", ",")
            credito = ""
        else:
            saldo_atual -= valor  # Diminui o saldo
            debito = ""
            credito = f"R$ {valor:.2f}".replace(".", ",")

        # Estruturando a linha de dados a ser inserida
        new_row = [
            data["Data"],        # Data
            data["Tipo"],        # Tipo
            data["Detalhes"],    # Descrição
            debito,              # Débito
            credito,             # Crédito
            f"R$ {saldo_atual:.2f}".replace(".", ","),  # Saldo Atual
            "FALSE"              # Lançado
        ]

        # Obtendo o número de linhas atuais na planilha
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE).execute()
        values = result.get("values", [])
        next_row = len(values) + 1 if values else 2

        # Adicionando a nova linha na próxima linha disponível
        sheet.values().update(
            spreadsheetId=SHEET_ID,
            range=f"{RANGE}!A{next_row}:G{next_row}",
            valueInputOption="USER_ENTERED",
            body={"values": [new_row]}
        ).execute()

        time.sleep(1)

        # Adicionando validação de dados para a checkbox
        requests = [{
            "updateCells": {
                "range": {
                    "sheetId": 0,
                    "startRowIndex": next_row - 1,
                    "endRowIndex": next_row,
                    "startColumnIndex": 6,
                    "endColumnIndex": 7
                },
                "rows": [{
                    "values": [{
                        "userEnteredValue": {"boolValue": False},
                        "dataValidation": {
                            "condition": {
                                "type": "BOOLEAN"
                            },
                            "showCustomUi": True
                        }
                    }]
                }],
                "fields": "userEnteredValue,dataValidation"
            }
        }]

        body = {
            "requests": requests
        }
        service.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body=body).execute()

    except HttpError as err:
        print(f"Erro ao atualizar a planilha: {err}")