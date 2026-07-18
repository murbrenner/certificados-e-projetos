from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
import time
import os

# Variáveis de ambiente
user = os.environ.get('USR')
senha = os.environ.get('PWD')

user2 = os.environ.get('USR2')
senha2 = os.environ.get('PWD2')

# Variáveis globais para o Playwright
playwright = None
browser = None
context = None
page = None

def inicializar_browser():
    """Inicializa o browser Playwright"""
    global playwright, browser, context, page
    
    playwright = sync_playwright().start()
    browser = playwright.firefox.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    return page

def fechar_browser():
    """Fecha o browser Playwright"""
    global playwright, browser, context, page
    
    if browser:
        browser.close()
    if playwright:
        playwright.stop()

def login():
    """Faz login no sistema GSAN com o primeiro usuário"""
    global page
    
    if page is None:
        inicializar_browser()
    
    page.goto("http://gsan.caema.ma.gov.br:8080/gsan/")
    page.locator('[name="login"]').fill(user)
    page.locator('[name="senha"]').fill(senha)
    page.locator('[name="buttonLogin"]').click()
    time.sleep(0.5)

def login2():
    """Faz login no sistema GSAN com o segundo usuário"""
    global page
    
    if page is None:
        inicializar_browser()
    
    page.goto("http://gsan.caema.ma.gov.br:8080/gsan/")
    page.locator('[name="login"]').fill(user2)
    page.locator('[name="senha"]').fill(senha2)
    page.locator('[name="buttonLogin"]').click()
    page.goto("http://gsan.caema.ma.gov.br:8080/gsan/")
