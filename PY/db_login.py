from selenium.webdriver.common.by import By
from selenium import webdriver
import time

driver = webdriver.Edge()
#driver.maximize_window()

def login():
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/")
    driver.find_element(By.NAME, 'login').send_keys('BRENNER')
    driver.find_element(By.NAME, 'senha').send_keys('Dram512@')
    driver.find_element(By.NAME, 'buttonLogin').click()

def enc():
    driver.get("https://docs.google.com/spreadsheets/d/1HhG9YARARX16EkQybElZ2HvC8IlR8QY-qSFL8fFphN4/edit?pli=1#gid=1805539427")
    driver.find_element(By.NAME, "identifier").send_keys("enc.cadastrocomercial@caema.ma.gov.br")
    driver.find_element(By.XPATH, "//*[@id='identifierNext']/div/button/span").click()
    time.sleep(6)
    driver.find_element(By.NAME, "Passwd").send_keys('Dram128@')
    driver.find_element(By.XPATH, "//*[@id='passwordNext']/div/button/span").click()
    time.sleep(10)

def enc2():
    driver.get("https://docs.google.com/spreadsheets/d/1oK_9fFdMDJDzpXJiqT22uDPSw-QIGvLR15nChz4khOw/edit?usp=drive_link")
    driver.find_element(By.NAME, "identifier").send_keys("enc.cadastrocomercial@caema.ma.gov.br")
    driver.find_element(By.XPATH, "//*[@id='identifierNext']/div/button/span").click()
    time.sleep(6)
    driver.find_element(By.NAME, "Passwd").send_keys('Dram128@')
    driver.find_element(By.XPATH, "//*[@id='passwordNext']/div/button/span").click()
    time.sleep(10)

def sei_login():
    driver.get("https://sip.sei.ma.gov.br/sip/login.php?sigla_orgao_sistema=GOVMA&sigla_sistema=SEI&infra_url=L3NlaS8=")
    driver.find_element(By.ID, "txtUsuario").send_keys('07890072902')
    driver.find_element(By.ID, "pwdSenha").send_keys('Murbs$30')
    driver.find_element(By.ID, "selOrgao").send_keys('CAEMA')
    driver.find_element(By.ID, "Acessar").click()