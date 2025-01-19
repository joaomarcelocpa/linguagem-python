import pyautogui
import time
import pandas as pd
from django.contrib.admin import display

pyautogui.PAUSE = 1

# Passo 1: Abrir o navegador

pyautogui.press("win")
pyautogui.write("chrome")
pyautogui.press("enter")

# Passo 2: Abrir o site

pyautogui.write("https://dlp.hashtagtreinamentos.com/python/intensivao/login")
pyautogui.press("enter")

time.sleep(4)

# Passo 3: Logar no site

pyautogui.click(x=741, y=379)
pyautogui.write("joao@gmail.com")
pyautogui.press("tab")
pyautogui.write("joao123456")
pyautogui.press("tab")
pyautogui.press("enter")

# Passo 4: Importar a base de dados

tabela = pd.read_csv("produtos.csv")
display(tabela)

# Passo 5: Cadastrar os produtos

for linha in tabela.index:
    pyautogui.click(x=707, y=254)

    pyautogui.write(str(tabela.loc[linha, "codigo"]))
    pyautogui.press("tab")

    pyautogui.write(str(tabela.loc[linha, "marca"]))
    pyautogui.press("tab")

    pyautogui.write(str(tabela.loc[linha, "tipo"]))
    pyautogui.press("tab")

    pyautogui.write(str(tabela.loc[linha, "categoria"]))
    pyautogui.press("tab")

    pyautogui.write(str(tabela.loc[linha, "preco_unitario"]))
    pyautogui.press("tab")

    pyautogui.write(str(tabela.loc[linha, "custo"]))
    pyautogui.press("tab")

    pyautogui.write(str(tabela.loc[linha, "obs"]))
    pyautogui.press("tab")



    pyautogui.press("enter")
    pyautogui.scroll(5000)
