from selenium.webdriver.common.by import By
from selenium import webdriver
import time, pyautogui

driver = webdriver.Edge()

def murilo():
    driver.get("https://gsan.caema.ma.gov.br/gsan/")
    driver.find_element(By.XPATH, "/html/body/div/div[2]/button[3]").click()
    driver.find_element(By.XPATH, "/html/body/div/div[3]/p[2]/a").click()    
    driver.find_element(By.NAME, 'login').send_keys('BRENNER')
    driver.find_element(By.NAME, 'senha').send_keys('Dram@512')
    driver.find_element(By.NAME, 'buttonLogin').click()

def login():
    driver.get("https://gsan.caema.ma.gov.br/gsan/")
    driver.find_element(By.NAME, 'login').send_keys('LUCIANAVERA')
    driver.find_element(By.NAME, 'senha').send_keys('lu0408%')
    driver.find_element(By.NAME, 'buttonLogin').click()

def murilo2():
    driver.get("http://gsan.caema.ma.gov.br:8080/gsan/")
    driver.find_element(By.NAME, 'login').send_keys('BRENNER')
    driver.find_element(By.NAME, 'senha').send_keys('Dram@512')
    driver.find_element(By.NAME, 'buttonLogin').click()

def enc():
    driver.get("https://docs.google.com/spreadsheets/d/1HhG9YARARX16EkQybElZ2HvC8IlR8QY-qSFL8fFphN4/edit?pli=1#gid=1805539427")
    driver.find_element(By.NAME, "identifier").send_keys("enc.cadastrocomercial@caema.ma.gov.br")
    driver.find_element(By.XPATH, "//*[@id='identifierNext']/div/button/span").click()
    time.sleep(6)
    driver.find_element(By.NAME, "Passwd").send_keys('Dram128@')
    driver.find_element(By.XPATH, "//*[@id='passwordNext']/div/button/span").click()
    time.sleep(10)

def login2():
    pyautogui.press('super')
    pyautogui.typewrite('Google Chrome')
    pyautogui.press('enter')
    pyautogui.typewrite("https://gsan.caema.ma.gov.br/gsan/")
    driver.find_element(By.NAME, 'login').send_keys('BRENNER')
    driver.find_element(By.NAME, 'senha').send_keys('ram1024@')
    driver.find_element(By.NAME, 'buttonLogin').click()

