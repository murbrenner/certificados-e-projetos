import unicodedata
import time, csv, os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_arquivos import *

def remover_acentos(texto):
    """
    Remove acentos e caracteres diacríticos de uma string.
    """
    try:
        # Normaliza o texto para separar a letra do acento
        normalizado = unicodedata.normalize('NFKD', texto)
        # Filtra apenas os caracteres que não são diacríticos (Mn)
        apenas_letras = "".join([c for c in normalizado if not unicodedata.combining(c)])
        return apenas_letras
    except:
        # Retorna o original se houver algum erro (ex: valor não é string)
        return texto
    
def calculoPorcentagem(contador, totalRow):
    percent1 = ((contador-1)*100)/totalRow
    percent1 = int(percent1)
    percent2 = (contador*100)/totalRow
    percent2 = int(percent2)
    if percent1 != percent2:            
        if percent2 != 100:
            print(f'{percent2}% CONCLUÍDO...')
            if percent2 % 10 == 0:
                os.system('cls') if os.name == 'nt' else os.system('clear')            
        else:
            print(f'{percent2}% CONCLUÍDO!')