from datetime import date
from selenium.webdriver.common.by import By
import pandas as pd
from login import murilo, driver
from arquivos import prog_fisc

df = pd.read_csv(prog_fisc)
murilo()

#fiscal = '258' # inserir numero do fiscal em string
today = date.today()
today = today.strftime("%d/%m/%Y")
today = '12/12/2023'

driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirElaborarOrdemServicoRoteiroCriteriosAction.do?menu=sim&filtro=0&dataRoteiro={}".format(today))
driver.find_element(By.XPATH, "//option[@value='613']").click()
driver.find_element(By.XPATH, "//option[@value='890']").click()
driver.find_element(By.XPATH, "//option[@value='9125']").click()
driver.find_element(By.XPATH, "//input[@value='  >  ']").click()
driver.find_element(By.XPATH, "//input[@value='Pesquisar']").click()

for i in df.index:
    driver.find_element(By.XPATH, "//option[@value='{}']".format(str(df['FISCAL'][i]))).click() #.format(str(df['FISCAL'][i]))).click()
    driver.find_element(By.XPATH, "//input[@value='  >  ']").click()

    try:
        driver.find_element(By.XPATH, "//input[@value='{}']".format(str(df['OS'][i]))).click()
        driver.find_element(By.XPATH, "//input[@value='Programar']").click()
        j = i + 1
        print(j, "Ordem de serviço {} programada com sucesso!".format(str(df['OS'][i])))
    except:
        j = i + 1
        print(j, "Ordem de serviço {} não localizada. Falha na programação.".format(str(df['OS'][i])))
        driver.find_element(By.XPATH, "//input[@value=' << ']").click()
        pass

driver.find_element(By.XPATH, "//input[@value='Concluir']").click()

#REFERÊNCIAS
'''
230 ABIR DE R MESQUITA
244	ALEXSANDRO A MENDES
263	ANSELMO R MARQUES
245	ARCELINO JOSE DA SIL
239	ARMANDO H ABREU
325	ATALIBA SANTOS FILHO
246	AURELIO M F FILHO
247	BRASILIANO ALMEIDA
11	CAEMA-CADASTRO SEDE
231	CELSO H M RODRIGUES
248	CESAR L A FONSECA
249	CLEITON ABREU MORAES
250	DIMAS DIAS COSTA
309	DOMINGOS LOPES DA SI
251	ELIANE CONDE SANTOS
223	EQUIPE ALLSAN/CAD
222	EQUIPE ESAC/CAD
253	FRANCISCO ARNOBIO
254	JADIEL RIBEIRO REIS
255	JOAO CARLOS R FONSEC
234	JOHNNY FRAN C SANTOS
308	JOSE BENEDITO PINTO
235	JOSE DE RIBAMAR NUNE
264	JOSE DOMINGOS S FILH
256	JOSENILTON D DIAS
242	JOSE PATRICIO S SILV
243	JOSE R DINIZ MARANHA
267	JOSINALDO BARBOSA
257	LEONARDO C SANTIAGO
258	LUIS ANTONIO A MOURA
236	LUIZ CARLOS FRAZAO
237	LUIZITO GEMA LIMA
259	MARCELO C PEREIRA
260	MAURO HENRIQUE LIMA
326	OMAR MARQUES RIBEIRO
238	PEDRO SODRE COSTA F
240	RAIMUNDO N SANTOS
241	RAIMUNDO N S GONCALV
261	RAMES MARTINS GARCIA
272	THIAGO CHRISTOPHER

'''