import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tkinter import messagebox
import sys
import os

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SAMPLE_SPREADSHEET_ID = "1b_pkZIbi_hHoIq2XyxQ9qsS3GDziH3nTPQeFxwEif3c"
SHEET_NAME = "Página1"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_credentials():
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
    result = service.spreadsheets().values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=f"{SHEET_NAME}!F2:F").execute()
    values = result.get("values", [])
    if values:
        value_str = values[-1][0].replace("R$", "").replace(".", "").replace(",", ".")
        return float(value_str)
    return 0.0

def initialize_sheet():
    creds = get_credentials()
    try:
        service = build("sheets", "v4", credentials=creds)
        result = service.spreadsheets().values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                                     range=f"{SHEET_NAME}!G2:G").execute()
        checkbox_values = result.get("values", [])
        checkbox_values = [row[0] == "TRUE" if row else False for row in checkbox_values]

        values = [["Data", "Tipo", "Descrição", "Débito", "Crédito", "Saldo Atual", "Lançado"]]
        body = {"values": values}
        service.spreadsheets().values().update(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A1:G1",
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()

        result = service.spreadsheets().values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                                     range=f"{SHEET_NAME}!A:A").execute()
        num_rows = len(result.get("values", []))
        requests = []
        for i in range(num_rows - 1):
            requests.append({
                "updateCells": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": i + 1,
                        "endRowIndex": i + 2,
                        "startColumnIndex": 6,
                        "endColumnIndex": 7
                    },
                    "rows": [{
                        "values": [{
                            "userEnteredValue": {
                                "boolValue": checkbox_values[i] if i < len(checkbox_values) else False
                            },
                            "dataValidation": {
                                "condition": {
                                    "type": "BOOLEAN"
                                },
                                "strict": True,
                                "showCustomUi": True
                            }
                        }]
                    }],
                    "fields": "userEnteredValue,dataValidation"
                }
            })

        requests.append({
            "updateBorders": {
                "range": {
                    "sheetId": 0,
                    "startRowIndex": 0,
                    "endRowIndex": num_rows,
                    "startColumnIndex": 0,
                    "endColumnIndex": 7
                },
                "top": {
                    "style": "SOLID",
                    "width": 1,
                    "color": {
                        "red": 0,
                        "green": 0,
                        "blue": 0
                    }
                },
                "bottom": {
                    "style": "SOLID",
                    "width": 1,
                    "color": {
                        "red": 0,
                        "green": 0,
                        "blue": 0
                    }
                },
                "left": {
                    "style": "SOLID",
                    "width": 1,
                    "color": {
                        "red": 0,
                        "green": 0,
                        "blue": 0
                    }
                },
                "right": {
                    "style": "SOLID",
                    "width": 1,
                    "color": {
                        "red": 0,
                        "green": 0,
                        "blue": 0
                    }
                },
                "innerHorizontal": {
                    "style": "SOLID",
                    "width": 1,
                    "color": {
                        "red": 0,
                        "green": 0,
                        "blue": 0
                    }
                },
                "innerVertical": {
                    "style": "SOLID",
                    "width": 1,
                    "color": {
                        "red": 0,
                        "green": 0,
                        "blue": 0
                    }
                }
            }
        })

        body = {"requests": requests}
        service.spreadsheets().batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=body).execute()
    except HttpError as err:
        messagebox.showerror("Erro", f"Ocorreu um erro ao inicializar a planilha: {err}")

def update_sheet(data):
    creds = get_credentials()
    try:
        service = build("sheets", "v4", credentials=creds)
        current_balance = get_current_balance(service)
        if data["Tipo"] in ["PIX", "Stone", "Depósito"]:
            debito = data["Valor"]
            credito = ""
            new_balance = current_balance + debito
        else:
            debito = ""
            credito = data["Valor"]
            new_balance = current_balance - credito
        formatted_debito = f"R${debito:.2f}".replace(".", ",") if debito != "" else ""
        formatted_credito = f"R${credito:.2f}".replace(".", ",") if credito != "" else ""
        formatted_balance = f"R${new_balance:.2f}".replace(".", ",")
        values = [[data["Data"], data["Tipo"], data["Detalhes"], formatted_debito, formatted_credito, formatted_balance, False]]
        body = {"values": values}
        service.spreadsheets().values().append(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:G",
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()

        # Add checkbox to the new row
        result = service.spreadsheets().values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=f"{SHEET_NAME}!A:G").execute()
        num_rows = len(result.get("values", []))
        requests = [{
            "updateCells": {
                "range": {
                    "sheetId": 0,
                    "startRowIndex": num_rows - 1,
                    "endRowIndex": num_rows,
                    "startColumnIndex": 6,
                    "endColumnIndex": 7
                },
                "rows": [{
                    "values": [{
                        "userEnteredValue": {
                            "boolValue": False
                        },
                        "dataValidation": {
                            "condition": {
                                "type": "BOOLEAN"
                            },
                            "strict": True,
                            "showCustomUi": True
                        }
                    }]
                }],
                "fields": "userEnteredValue,dataValidation"
            }
        }, {
            "updateBorders": {
                "range": {
                    "sheetId": 0,
                    "startRowIndex": num_rows - 1,
                    "endRowIndex": num_rows,
                    "startColumnIndex": 0,
                    "endColumnIndex": 7
                },
                "top": {
                    "style": "SOLID",
                    "width": 1,
                    "color": {
                        "red": 0,
                        "green": 0,
                        "blue": 0
                    }
                },
                "bottom": {
                    "style": "SOLID",
                    "width": 1,
                    "color": {
                        "red": 0,
                        "green": 0,
                        "blue": 0
                    }
                },
                "left": {
                    "style": "SOLID",
                    "width": 1,
                    "color": {
                        "red": 0,
                        "green": 0,
                        "blue": 0
                    }
                },
                "right": {
                    "style": "SOLID",
                    "width": 1,
                    "color": {
                        "red": 0,
                        "green": 0,
                        "blue": 0
                    }
                }
            }
        }]
        body = {"requests": requests}
        service.spreadsheets().batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=body).execute()
    except HttpError as err:
        messagebox.showerror("Erro", f"Ocorreu um erro: {err}")