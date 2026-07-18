import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from db_login import login, driver

login()

rota = 34
rotas = 34

while rota <= rotas:

    idLocalidade = '301'
    codigoSetorComercial = '300'
    codigoRota = rota
    faturamentoGrupo = codigoSetorComercial
    cobrancaGrupo = codigoSetorComercial
    leituraTipo = 'MICROCOLETOR'    
    empresaLeituristica = 'CAEMA'
    empresaCobranca = 'CAEMA'
    empresaEntregaContas = 'CAEMA'   
    idLeiturista = '1'

    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirInserirRotaAction.do?menu=sim")
    
    time.sleep(0.5)
    driver.find_element(By.NAME, "idLocalidade").send_keys(idLocalidade, Keys.ENTER)
    time.sleep(0.5)  
    driver.find_element(By.NAME, "codigoSetorComercial").send_keys(codigoSetorComercial, Keys.ENTER)
    time.sleep(0.5)
    driver.find_element(By.NAME, "idLeiturista").send_keys(idLeiturista, Keys.ENTER)
    time.sleep(0.5)    
    driver.find_element(By.NAME, "codigoRota").clear()
    driver.find_element(By.NAME, "codigoRota").send_keys(codigoRota)
    time.sleep(0.5)

    driver.find_element(By.NAME, "faturamentoGrupo").send_keys(faturamentoGrupo)     
    driver.find_element(By.NAME, "cobrancaGrupo").send_keys(cobrancaGrupo)      
    driver.find_element(By.NAME, "leituraTipo").send_keys(leituraTipo)    
    driver.find_element(By.NAME, "empresaLeituristica").send_keys(empresaLeituristica)      
    driver.find_element(By.NAME, "empresaCobranca").send_keys(empresaCobranca)    
    driver.find_element(By.NAME, "empresaEntregaContas").send_keys(empresaEntregaContas)     
    driver.find_element(By.XPATH, "//input[@name='indicadorFiscalizarCortado' and @value='2']").click()      
    driver.find_element(By.XPATH, "//input[@name='indicadorFiscalizarSuprimido' and @value='2']").click()      
    driver.find_element(By.XPATH, "//input[@name='indicadorArmazenarCoordenadas' and @value='1']").click()        
    driver.find_element(By.XPATH, "//input[@name='indicadorGerarFalsaFaixa' and @value='2']").click()      
    driver.find_element(By.XPATH, "//input[@name='indicadorGerarFiscalizacao' and @value='2']").click()      
    driver.find_element(By.XPATH, "//input[@value='Inserir']").click()

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