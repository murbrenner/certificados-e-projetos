from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import pyautogui
import time

dataframe = pd.read_csv("C:\\Users\\ocmvc45555\\Desktop\\PYTHON\\CSV\\dataframe.csv")
driver = webdriver.Edge()

driver.get("http://gsan.caema.ma.gov.br:8080/gsan/")


driver.find_element(By.NAME, "buttonLogin").click()
time.sleep(1111)
# driver.find_element(By.NAME, "NOME").click()
# driver.find_element(By.ID, "ID")