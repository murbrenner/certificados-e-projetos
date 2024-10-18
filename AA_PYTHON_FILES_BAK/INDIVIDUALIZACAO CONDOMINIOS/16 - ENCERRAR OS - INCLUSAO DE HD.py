from datetime import date, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
from arquivos import elaboration, teste, abrir_ra
from login import murilo, driver

df = pd.read_csv(abrir_ra)
murilo()

hoje = date.today()
ontem = date.today() + timedelta(days= -1)
ontem = ontem.strftime("%d/%m/%Y")
hoje = hoje.strftime("%d/%m/%Y")
data_atv = hoje.replace("/", "")
motivo = "CONCLUSAO DO SERVIÇO"

for i in df.index:
    driver.get("https://gsan.caema.ma.gov.br/gsan/exibirFiltrarOrdemServicoAction.do?menu=sim")
    os = driver.find_element(By.NAME, "numeroOS").send_keys(str(df['OS'][i]), Keys.ENTER)
    driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()
    sit_os = driver.find_element(By.NAME, "situacaoOS").get_attribute('value')
    if sit_os == 'Encerrada':
        print(i + 1, str(df['MATRICULA'][i]),  "ORDEM DE SERVIÇO ENCERRADA", sep=';')
    elif sit_os == 'Pendente':
        driver.find_element(By.XPATH, "//input[@value='Encerrar']").click()
        driver.find_element(By.NAME, "dataEncerramento").send_keys(hoje)
        driver.find_element(By.NAME, "idMotivoEncerramento").send_keys(motivo)
        driver.find_element(By.NAME, "observacaoEncerramento").send_keys(str(df['OBSERVACAO'][i]))
        driver.find_element(By.NAME, "ButtonAtividade").click()
        popup = driver.window_handles[1]
        janela = driver.window_handles[0]
        driver.switch_to.window(popup)
        time.sleep(0.5)
        driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr/td/table[3]/tbody/tr[9]/td/table[2]/tbody/tr/td/table/tbody/tr[2]/td/div/table/tbody/tr/td[4]/a/img').click()

        driver.find_element(By.NAME, "dataExecucao").clear()
        driver.find_element(By.NAME, "dataExecucao").send_keys(data_atv)
        driver.find_element(By.NAME, 'horaInicioExecucao').send_keys("0800")
        driver.find_element(By.NAME, 'horaFimExecucao').send_keys("1800")
        driver.find_element(By.NAME, "idEquipeNaoProgramada").send_keys("CADASTRO")
        driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
        driver.find_element(By.XPATH, "//input[@value='Voltar']").click()
        driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
        driver.switch_to.window(janela)
        driver.find_element(By.NAME, "ButtonEncerrar").click()
        time.sleep(0.3)
        driver.find_element(By.XPATH, "//input[@value='Voltar']").click()
        driver.find_element(By.NAME, "dataEncerramento").clear()
        driver.find_element(By.NAME, "dataEncerramento").send_keys(ontem)
        driver.find_element(By.NAME, "ButtonEncerrar").click()
        time.sleep(0.3)
        try:
            leitura = int(df['LEITURA'][i])
            if leitura == 0:
                driver.find_element(By.NAME, "leituraInstalacao").send_keys(str(df['LEITURA'][i])).clear()
            else:
                driver.find_element(By.NAME, "leituraInstalacao").send_keys(str(df['LEITURA'][i]))
            driver.find_element(By.NAME, "numeroHidrometro").send_keys(str(df['HIDROMETRO'][i]))
            driver.find_element(By.NAME, "localInstalacao").send_keys('INTERNO')
            driver.find_element(By.NAME, "protecao").send_keys('OUTROS')
            driver.find_element(By.XPATH, "/html/body/form/table[3]/tbody/tr/td[2]/table[3]/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[10]/td[2]/input[1]").click()
            driver.find_element(By.XPATH, "//input[@value='Efetuar']").click()

            try:
                driver.find_element(By.XPATH, "//input[@value='Sim']").click()
                msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
                print(i + 1, msg_ok, sep=';')
            except:
                msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                print(i + 1, str(df['MATRICULA'][i]), msg_er, sep=';')
                pass
            try:
                driver.find_element(By.XPATH, "//input[@value='Cancelar']").click()
                driver.find_element(By.XPATH, "//input[@value='Voltar']").click()
                driver.find_element(By.XPATH, "//input[@value='ButtonCancelar']").click()
                driver.find_element(By.XPATH, "//input[@value='ButtonVoltar']").click()
            except:
                pass
        except:
            try:
                msg_er = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                print(i + 1, str(df['MATRICULA'][i]), msg_er, sep=';')
            except:
                pass