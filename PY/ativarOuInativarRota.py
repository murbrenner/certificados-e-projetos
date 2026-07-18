import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from db_login import login, driver

login()

rota = 100
rotas = 112

while rota <= rotas:      
    idLocalidade = 830
    codigoSetorComercial = 800
    codigoRota = rota    

    time.sleep(0.2)  
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarRotaAction.do?menu=sim")
    
    switch = 0

    if switch == 0:
        switch = 2 # Inativar rota
    elif switch == 1:
        switch = 1 # Ativar rota    
    
    driver.find_element(By.NAME, "idLocalidade").send_keys(idLocalidade)
    time.sleep(0.2)  
    driver.find_element(By.NAME, "codigoSetorComercial").send_keys(codigoSetorComercial)
    time.sleep(0.2)
    driver.find_element(By.NAME, "codigoRota").send_keys(codigoRota)
    time.sleep(0.2) 
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    time.sleep(0.5) 

    driver.find_element(By.XPATH, f"//input[@name='indicadorUso' and @value={switch}]").click()    
    
    driver.find_element(By.XPATH, "//input[@value='Atualizar']").click()

    try:
        time.sleep(0.5)  
        msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text  
        time.sleep(0.5)    
        print(rota, msg_ok)
    except:
        time.sleep(0.5)  
        msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
        time.sleep(0.5)  
        print(rota, msg_er)        

    rota = rota + 1