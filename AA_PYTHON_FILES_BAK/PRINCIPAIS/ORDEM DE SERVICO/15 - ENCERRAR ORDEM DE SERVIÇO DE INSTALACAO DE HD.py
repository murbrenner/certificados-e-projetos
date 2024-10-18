from datetime import date
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
from arquivos import elaboration, abrir_ra
from login import murilo, driver, murilo2

df = pd.read_csv(abrir_ra)
murilo2()

hoje = date.today()
hoje = hoje.strftime("%d/%m/%Y")
motivo = "CONCLUSAO DO SERVIÇO"


for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
    os = driver.find_element(By.NAME, "numeroOS").send_keys(str(df['OS'][i]), Keys.ENTER)
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    sit_os = driver.find_element(By.NAME, "situacaoOS").get_attribute('value')
    if sit_os == 'Encerrada':
        print("Ordem de Serviço {} JÁ ENCERRADA".format(str(df['OS'][i])))
        pass
    else:
        driver.find_element(By.XPATH, "//input[@value='Encerrar']").click()
        driver.find_element(By.NAME, "dataEncerramento").send_keys(hoje)
        driver.find_element(By.NAME, "idMotivoEncerramento").send_keys(motivo)
        driver.find_element(By.NAME, "observacaoEncerramento").send_keys(str(df['OBSERVACAO'][i]), ". HD INSTALADO: ", str(df['HIDROMETRO'][i]), ". LEITURA: ", str(df['LEITURA'][i]))
        driver.find_element(By.NAME, "ButtonAtividade").click()
        jan_princ = driver.window_handles[0]
        jan_ativ = driver.window_handles[1]
        driver.switch_to.window(jan_ativ)
        driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr/td/table[3]/tbody/tr[9]/td/table[2]/tbody/tr/td/table/tbody/tr[2]/td/div/table/tbody/tr/td[4]/a/img').click()
        time.sleep(0.3)
        data_corrida = hoje.replace('/', '')
        driver.find_element(By.NAME, "dataExecucao").send_keys(data_corrida)
        driver.find_element(By.NAME, 'horaInicioExecucao').send_keys("0800")
        driver.find_element(By.NAME, 'horaFimExecucao').send_keys("1800")
        driver.find_element(By.NAME, "idEquipeNaoProgramada").send_keys("CADASTRO")
        driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
        driver.find_element(By.XPATH, "//input[@value='Voltar']").click()
        driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
        driver.switch_to.window(jan_princ)

        driver.find_element(By.NAME, "ButtonEncerrar").click()
        
        driver.find_element(By.NAME, "numeroHidrometro").send_keys(str(df['HIDROMETRO'][i]))
        
        driver.find_element(By.NAME, "localInstalacao").send_keys('MURETA FRONTAL')
        driver.find_element(By.NAME, "protecao").send_keys('OUTROS')
        driver.find_element(By.NAME, "leituraInstalacao").send_keys(str(df['LEITURA'][i]))
        driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[10]/td[2]/input[1]").click()
        
        driver.find_element(By.XPATH, "//input[@value='Efetuar']").click()


        try:
            driver.find_element(By.XPATH, "//input[@value='Sim']").click()
            print("Ordem de Serviço {} ENCERRADA. HD {} INSTALADO COM SUCESSO".format(str(df['OS'][i]), str(df['HIDROMETRO'][i])))
        except:
            msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
            print("Ordem de Serviço {} NAO DEU CERTO. HD {} NÃO INSTALADO".format(str(df['OS'][i]), str(df['HIDROMETRO'][i])), msg_er)

            pass