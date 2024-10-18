import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import inserir_imovel

df = pd.read_csv(inserir_imovel)
murilo()

for i in df.index:
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirInserirImovelAction.do?menu=sim")
    driver.find_element(By.NAME, "idLocalidade").send_keys(str(df['LOCALIDADE'][i]), Keys.ENTER)
    driver.find_element(By.NAME, "idSetorComercial").send_keys(str(df['SETOR'][i]), Keys.ENTER)
    driver.find_element(By.NAME, "idQuadra").send_keys(str(df['QUADRA'][i]), Keys.ENTER)
    driver.find_element(By.NAME, "lote").send_keys(str(df['SEQUENCIA'][i]), Keys.ENTER)
    driver.find_element(By.NAME, "subLote").send_keys(str(df['SUBLOTE'][i]), Keys.ENTER)
    driver.find_element(By.NAME, "testadaLote").send_keys(str(df['TESTADA'][i]), Keys.ENTER)
    driver.find_element(By.NAME, "sequencialRota").send_keys(str(df['SEQUENCIA'][i]), Keys.ENTER)
    driver.find_element(By.NAME, "avancar").click()
    try:
        driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
    except:
        pass
    driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()
    main_window_handle = driver.current_window_handle
    all_window_handles = driver.window_handles
    for handle in all_window_handles:
        if handle != main_window_handle:
            driver.switch_to.window(handle)
            driver.find_element(By.NAME, "logradouro").send_keys('11583', Keys.ENTER)
            driver.find_element(By.XPATH, "//input[@value='1']").click()
            driver.find_element(By.NAME, "bairro").send_keys('JD ELDORADO')
            # driver.find_element(By.NAME, "enderecoReferencia").send_keys('01 - NUMERO')
            driver.find_element(By.NAME, "numero").send_keys(str(df['NUMERO'][i]))
            driver.find_element(By.NAME, "complemento").send_keys(str(df['COMPLEMENTO'][i]))
            driver.find_element(By.XPATH, "//input[@value='Inserir']").click()
        driver.switch_to.window(main_window_handle)

    driver.find_element(By.XPATH, "//input[@value='Avançar']").click()

    driver.find_element(By.NAME, "idCliente").send_keys(str(df['ID_CLIENTE'][i]), Keys.ENTER)

    driver.find_element(By.NAME, "tipoClienteImovel").send_keys('02 - USUARIO')
    driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()

    driver.find_element(By.XPATH, "//input[@value='Avançar']").click()

    driver.find_element(By.NAME, "idCategoria").send_keys('01 - RESIDENCIAL')
    driver.find_element(By.NAME, "idSubCategoria").send_keys('01 - RESIDENCIAL')
    driver.find_element(By.NAME, "quantidadeEconomia").send_keys('1')
    driver.find_element(By.NAME, "botaoAdicionar").click()

    driver.find_element(By.XPATH, "//input[@value='Avançar']").click()

    driver.find_element(By.NAME, "areaConstruida").send_keys('6128')
    driver.find_element(By.NAME, "pavimentoCalcada").send_keys('02 - CIMENTO')
    driver.find_element(By.NAME, "pavimentoRua").send_keys('02 - ASFALTO')
    driver.find_element(By.NAME, "fonteAbastecimento").send_keys('01 - CAEMA')
    driver.find_element(By.NAME, "situacaoLigacaoAgua").send_keys('02 - FACTIVEL')
    driver.find_element(By.NAME, "situacaoLigacaoEsgoto").send_keys('01 - POTENCIAL')
    driver.find_element(By.NAME, "perfilImovel").send_keys('05 - NORMAL')
    driver.find_element(By.NAME, "tipoDespejo").send_keys('01 - RESIDENCIAL')
    driver.find_element(By.NAME, "imovelTipoHabitacao").send_keys('01 - HABITADO')
    driver.find_element(By.NAME, "imovelTipoPropriedade").send_keys('01 - PROPRIO')
    driver.find_element(By.NAME, "imovelTipoConstrucao").send_keys('03 - ALVENARIA')
    driver.find_element(By.NAME, "imovelTipoCobertura").send_keys('02 - TELHA CERAMICA')

    driver.find_element(By.XPATH, "//input[@value='Avançar']").click()

    driver.find_element(By.NAME, "numeroPontos").send_keys('10')
    driver.find_element(By.NAME, "numeroMoradores").send_keys('3')

    driver.find_element(By.XPATH, "//input[@value='Concluir']").click()

    msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span")
    print(msg_ok)