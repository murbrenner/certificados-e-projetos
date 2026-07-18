from selenium.webdriver.common.by import By
from selenium import webdriver
import time, os


driver = webdriver.Edge()

user = os.environ.get('USR')
senha = os.environ.get('PWD')

user2 = os.environ.get('USR2')
senha2 = os.environ.get('PWD2')

def login():
    #driver.get("http://177.66.194.131:8080/gsan/")
    #driver.get("http://gsan.caema.ma.gov.br:8080/gsan/")
    driver.get("http://g1.caema.ma.gov.br/gsan/")
    #"http://177.66.194.131:8080/gsan/"
    driver.find_element(By.NAME, 'login').send_keys(user)
    driver.find_element(By.NAME, 'senha').send_keys(senha)
    driver.find_element(By.NAME, 'buttonLogin').click() 
    time.sleep(0.5)
   

def login2():
    driver.get("http://g1.caema.ma.gov.br/gsan/")
    driver.find_element(By.NAME, 'login').send_keys(user2)
    driver.find_element(By.NAME, 'senha').send_keys(senha2)
    driver.find_element(By.NAME, 'buttonLogin').click()
    driver.get("http://g1.caema.ma.gov.br:8080/gsan/")
