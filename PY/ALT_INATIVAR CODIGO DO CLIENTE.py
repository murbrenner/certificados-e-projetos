from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from db_arquivos import teste, elaboration
from db_login import login, driver
import pandas as pd

df = pd.read_csv(elaboration)
login()

header = ['#', 'COD_CLIENTE', 'MSG']


for i in df.index:
    cod_cliente = int(df['COD_CLIENTE'][i])
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/ExibirConsultarRelacaoClienteImovelAction.do?menu=sim")    
    driver.find_element(By.NAME, "idCliente").send_keys(cod_cliente, Keys.ENTER)
    
    try:
        inex = driver.find_element(By.NAME, "nomeCliente").get_attribute("value")              
        if inex == "Cliente Inexistente.":
            print(i+1, cod_cliente, "Cliente Inexistente")
        
        elif inex != "Cliente Inexistente.":
            driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()  
            try:                                
                msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                print(i+1, cod_cliente, msg_er)
                v_msg_er = 1
                driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarClienteAction.do?menu=sim")        
                driver.find_element(By.NAME, "codigoClienteFiltro").send_keys(cod_cliente)
                driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
                driver.find_element(By.XPATH, "//input[@name='indicadorUso' and @value='2']").click()
                try:
                    driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
                    msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
                    print(i+1, cod_cliente, msg_ok)
                except:
                    v_cpf = driver.find_element(By.NAME, "indicadorPessoaFisicaJuridica").get_attribute('value')
                    if v_cpf == '1':
                        driver.find_element(By.NAME, "tipoPessoa").send_keys('100 - RESIDENCIA')
                        driver.find_element(By.ID, "2").click()
                        driver.find_element(By.NAME, "idPessoaSexo").send_keys("01 - MASCULINO")
                        driver.find_element(By.XPATH, "//input[@value='Concluir']").click()
                        msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
                        print(i+1, cod_cliente, msg_ok)
                
            except:
                print(i+1, cod_cliente, "ALGUM ERRO")
                pass


    except:
        print(i+1, cod_cliente, "Cliente possui vínculo com imóvel no sistema")        
        pass