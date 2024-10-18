from selenium.webdriver.common.by import By
from selenium import webdriver
from arquivos import down_path

driver = webdriver.Chrome()


def murilo():
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan")
    driver.find_element(By.NAME, 'login').send_keys('BRENNER')
    driver.find_element(By.NAME, 'senha').send_keys('dram512@')
    driver.find_element(By.NAME, 'buttonLogin').click()

def login():
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan")
    driver.find_element(By.NAME, 'login').send_keys('LUCIANAVERA')
    driver.find_element(By.NAME, 'senha').send_keys('theo)04')
    driver.find_element(By.NAME, 'buttonLogin').click()

