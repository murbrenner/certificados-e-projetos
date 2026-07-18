import unicodedata
import time, csv, os, subprocess
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import *

allOkText = '0'
errorText = '0'
writer = '0'

def cpf_ok(cpf):
    ncpf = len(cpf)
    while ncpf < 11:
        cpf = "0" + cpf
        ncpf = ncpf + 1
    return cpf

def cnpj_ok(cpf):
    ncpf = len(cpf)
    while ncpf < 14:
        cpf = "0" + cpf
        ncpf = ncpf + 1
    return cpf

def rg_ok(rg):
    nrg = len(rg)
    while nrg < 13:
        cpf = "0" + rg
        nrg = nrg + 1
    return rg

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
        

def checkErroPadrao(allOkText, errorText, i, writer):
    try:
        allOkText = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text        
        row = i+1, allOkText
        writer.writerow(row)
        time.sleep(0.3)
    except:
        errorText = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
        row = i+1, errorText
        writer.writerow(row)
        time.sleep(0.3)

def calculoPorcentagem(contador, totalRow):
    percent1 = ((contador-1)*100)/totalRow
    percent1 = int(percent1)
    percent2 = (contador*100)/totalRow
    percent2 = int(percent2)
    if percent1 != percent2:            
        if percent2 != 100:
            comando = 'cls' if os.name == 'nt' else 'clear'
            subprocess.run(comando, shell=True)
            print(f'EXECUTANDO...\n{percent2}% CONCLUÍDO!')
            if percent2 % 10 == 0:
                os.system('cls') if os.name == 'nt' else os.system('clear')            
        else:
            comando = 'cls' if os.name == 'nt' else 'clear'
            subprocess.run(comando, shell=True)
            print(f'EXECUTANDO...\n{percent2}% CONCLUÍDO!')

def exit(alterar):
    if alterar == 0:
        return
    
tipoLogFunc = {'1': 'AL',
           '2': 'AV',
           '3': 'BC',
           '4': 'BL',
           '5': 'BR',
           '6': 'CA',
           '7': 'CJ',
           '8': 'CT',
           '9': 'ET',
           '10': 'LT',
           '11': 'LG',
           '12': 'LT',
           '13': 'PC',
           '22': 'PQ',
           '14': 'Q',
           '15': 'R',
           '16': 'RC',
           '17': 'RD',
           '18': 'RI',
           '19': 'TT',
           '20': 'TV',
           '21': 'V'
        }

titLogFunc = {

    "1": '101',
    "2": 'ALF',
    "3": 'ALM',
    "4": 'AVD',
    "5": 'BR',
    "6": 'BRIG',
    "7": 'CAP',
    "8": 'CAP.',
    "9": 'CB',
    "10": 'CEL',
    "11": 'CEL.',
    "12": 'COM',
    "13": 'D',
    "14": 'DEP',
    "15": 'DR',
    "16": 'DR.',
    "17": 'DRA',
    "18": 'DRA.',
    "19": 'DUQUE',
    "20": 'ENG',
    "21": 'EXP',
    "22": 'GAL',
    "23": 'GOV',
    "24": 'HAB',
    "25": 'JORN',
    "26": 'MAJOR',
    "27": 'MAL',
    "28": 'MARQU',
    "29": 'NSA',
    "30": 'PE',
    "31": 'PREF',
    "32": 'PREF.',
    "33": 'PRES',
    "34": 'PRIN',
    "35": 'PROF',
    "36": 'RES',
    "37": 'RIO',
    "38": 'S',
    "39": 'SAO',
    "40": 'SEN',
    "41": 'STA',
    "42": 'STO',
    "43": 'TEN',
    "44": 'VER',
}

        