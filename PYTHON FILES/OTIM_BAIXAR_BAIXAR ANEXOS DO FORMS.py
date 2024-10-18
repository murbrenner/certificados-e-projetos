import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import enc, enc2, driver
from db_arquivos import inserir_imovel, elaboration
import pyautogui
from db_fiscais import abrev_nomes_joined

df = pd.read_csv(elaboration)
enc2()

j = 1
for i in df.index:    
    while j < 6:    
        try:
            link_foto = str(df['DOC{}'.format(j)][j]) 
            driver.get(link_foto)
        except:
            pass       
        
        j = j+1