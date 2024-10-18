import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver, login
from arquivos import elaboration
from funcoes import cpf_ok

df = pd.read_csv(elaboration)

for i in df.index:
    driver.get("https://www.4devs.com.br/validador_cpf")
    cpf_cru = str(df['CPF'][i])
    cpf = cpf_ok(cpf_cru)
    driver.find_element(By.ID, "txt_cpf").send_keys(cpf)
    driver.find_element(By.ID, "bt_validar_cpf").click()    
    resposta = driver.find_element(By.XPATH, "div#area_resposta.app-output::after").get_attribute('value')
    time.sleep(3)
    #resposta = driver.execute_script("return window.getComputedStyle(arguments[0], '::after').getPropertyValue('content');", resposta_0)
    print(resposta)
    time.sleep(11111)