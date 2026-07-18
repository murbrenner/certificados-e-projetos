import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from db_login import login, driver
from db_arquivos import *

# Carrega os dados do arquivo CSV em um DataFrame
df = pd.read_csv(databaseCSV1)

# Realiza login no sistema
login()

# Itera sobre cada linha do DataFrame
for i in df.index:
    # Navega para a página de filtro do sistema
    driver.get("https://gsan.caema.ma.gov.br/gsan/exibirFiltrarImovelAction.do?menu=sim")
    
    # Insere a matrícula no campo de filtro e clica em "Filtrar"
    driver.find_element(By.NAME, "matriculaFiltro").send_keys(str(df['MATRICULA'][i]))
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    
    # Acessa o segundo item na lista de resultados
    driver.find_element(By.ID, "2").click()
    
    # Tenta confirmar qualquer pop-up que possa aparecer
    try:
        driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
    except:
        pass  # Ignora exceções se o botão 'Confirmar' não estiver disponível
    
    # Aguarda um curto período para garantir que todas as ações tenham sido processadas
    time.sleep(0.5)
    
    # Clica no botão de erro (ocasionalmente necessário em algumas interfaces web)
    driver.find_element(By.XPATH, "//img[@src='/gsan/imagens/Error.gif']").click()
    alert = driver.switch_to.alert
    alert.accept()  # Aceita o alerta exibido
    
    # Clica em "Adicionar" para inserir novas informações
    driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
    
    # Navega para a nova janela pop-up
    janela = driver.window_handles[0]
    popup = driver.window_handles[1]
    driver.switch_to.window(popup)
    
    # Insere o código do logradouro e confirma
    driver.find_element(By.NAME, "logradouro").send_keys(int(df['COD_LOG'][i]), Keys.ENTER)
    #driver.find_element(By.XPATH, "//input[@value='5720']").click()
    
    # Preenche o campo do bairro com o valor do DataFrame
    driver.find_element(By.NAME, "bairro").send_keys(str(df['BAIRRO'][i]))
    
    # Preenche o número do imóvel
    driver.find_element(By.NAME, "numero").send_keys(str(df['NUMERO'][i]))
    
    # Preenche o campo de complemento, se existir
    complemento = int(df['COMPLEMENTO'][i])
    if complemento != 0:
        driver.find_element(By.NAME, "complemento").send_keys(str(df['COMPLEMENTO'][i]))
    
    # Clica em "Inserir" para adicionar o registro
    driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
    
    # Retorna à janela principal
    driver.switch_to.window(janela)
    
    # Finaliza o procedimento
    driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
    
    # Tenta capturar e imprimir a mensagem de sucesso ou erro
    try:
        msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
        print(msg_ok)
    except:
        msg_ero = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
        print(msg_ero)
