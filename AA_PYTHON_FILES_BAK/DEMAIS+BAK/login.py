from selenium.webdriver.common.by import By
from selenium import webdriver
from arquivos import down_path

driver = webdriver.Edge()


def murilo():
    driver.get("https://gsan.caema.ma.gov.br/gsan/")
    #driver.get("http://10.39.192.23:8080/gsan/")
    driver.find_element(By.NAME, 'login').send_keys('BRENNER')
    driver.find_element(By.NAME, 'senha').send_keys('dram128@')
    driver.find_element(By.NAME, 'buttonLogin').click()

def login():
    driver.get("https://gsan.caema.ma.gov.br/gsan/")
    driver.find_element(By.NAME, 'login').send_keys('LUCIANAVERA')
    driver.find_element(By.NAME, 'senha').send_keys('theo)04')
    driver.find_element(By.NAME, 'buttonLogin').click()

