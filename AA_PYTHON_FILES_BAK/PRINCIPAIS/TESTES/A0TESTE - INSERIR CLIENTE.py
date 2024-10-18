import time, os, glob, subprocess
import pyautogui
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
from login import murilo, driver
from arquivos import listagem, down_path, elaboration
from funcoes import cpf_ok, documento

df = pd.read_csv(elaboration)

tdoc = '0'

doc = '123321000112'
doc = cpf_ok(doc)
doc = documento(doc)
tdoc = documento(tdoc)

print(doc)
