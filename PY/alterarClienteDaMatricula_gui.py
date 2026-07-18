import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pandas as pd
import csv
import os
import sys
import threading
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Importações locais - driver será importado apenas ao iniciar
try:
    from db_arquivos import *
except ImportError:
    pass


class AlterarClienteGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ALTERAR CLIENTE DA MATRÍCULA")
        self.root.geometry("700x750")
        self.root.resizable(False, False)
        
        # Cores do tema
        self.bg_color = "#2b2b2b"
        self.fg_color = "#ffffff"
        self.entry_bg = "#3c3c3c"
        self.entry_fg = "#ffffff"
        
        # Configurar cor de fundo da janela
        self.root.configure(bg=self.bg_color)
        
        # Variável para armazenar o caminho do arquivo
        self.planilha_var = tk.StringVar()
        self.usuario_var = tk.StringVar()
        self.senha_var = tk.StringVar()
        self.is_running = False
        
        self.criar_widgets()
        
    def criar_widgets(self):
        # Título com linha cinza
        titulo_frame = tk.Frame(self.root, bg=self.bg_color)
        titulo_frame.pack(pady=(20, 0))
        
        titulo = tk.Label(titulo_frame, text="ALTERAR CLIENTE DA MATRÍCULA", 
                         font=("Arial", 14, "bold"),
                         bg=self.bg_color, fg="#ff6600")
        titulo.pack(padx=20)
        
        titulo_line = tk.Frame(self.root, bg="#666666", height=1)
        titulo_line.pack(fill="x", padx=20, pady=(5, 20))
        
        # Frame para o campo de planilha
        frame_planilha = tk.Frame(self.root, bg=self.bg_color)
        frame_planilha.pack(padx=20, pady=(0, 10), fill="x")
        
        # Label
        label1 = tk.Label(frame_planilha, text="PLANILHA BASE PARA ATUALIZAÇÃO:", 
                         font=("Arial", 9, "bold"),
                         bg=self.bg_color, fg="#999999")
        label1.pack(anchor="w", pady=(0, 8))
        
        # Entry sem linha embaixo - OCUPA A LINHA INTEIRA
        entry1 = tk.Entry(frame_planilha, textvariable=self.planilha_var,
                         bg=self.entry_bg, fg=self.entry_fg, 
                         insertbackground=self.fg_color, relief="flat", bd=0,
                         highlightthickness=0, font=("Arial", 9))
        entry1.pack(fill="x", ipady=5, pady=(0, 10))
        
        # Frame para os botões - NOVA LINHA ABAIXO DO ENTRY
        buttons_frame = tk.Frame(frame_planilha, bg=self.bg_color)
        buttons_frame.pack(fill="x")
        
        # Botão PROCURAR
        btn_procurar = self.criar_botao_acao(buttons_frame, "PROCURAR", 
                                             self.procurar_planilha, "#ffd700")
        btn_procurar.pack(side="left", padx=(0, 5))
        
        # Botão MODELO
        btn_modelo = self.criar_botao_acao(buttons_frame, "MODELO", 
                                           self.criar_modelo, "#00ff00")
        btn_modelo.pack(side="left")
        
        # Seção de Login GSAN
        login_frame = tk.Frame(self.root, bg=self.bg_color)
        login_frame.pack(padx=20, pady=(15, 10), fill="x")
        
        # Label "DADOS DE LOGIN GSAN:"
        label_login = tk.Label(login_frame, text="DADOS DE LOGIN GSAN:", 
                              font=("Arial", 9, "bold"),
                              bg=self.bg_color, fg="#00bfff")
        label_login.pack(anchor="w", pady=(0, 8))
        
        # Frame para os campos de usuário e senha (lado a lado)
        credentials_frame = tk.Frame(login_frame, bg=self.bg_color)
        credentials_frame.pack(fill="x")
        
        # Campo USUÁRIO
        usuario_container = tk.Frame(credentials_frame, bg=self.bg_color)
        usuario_container.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        label_usuario = tk.Label(usuario_container, text="USUÁRIO:", 
                                font=("Arial", 9, "bold"),
                                bg=self.bg_color, fg="#999999")
        label_usuario.pack(anchor="w", pady=(0, 5))
        
        entry_usuario = tk.Entry(usuario_container, textvariable=self.usuario_var,
                                bg=self.entry_bg, fg=self.entry_fg,
                                insertbackground=self.fg_color, relief="flat", bd=0,
                                highlightthickness=0, font=("Arial", 9))
        entry_usuario.pack(fill="x", ipady=5)
        
        # Campo SENHA
        senha_container = tk.Frame(credentials_frame, bg=self.bg_color)
        senha_container.pack(side="left", fill="x", expand=True)
        
        label_senha = tk.Label(senha_container, text="SENHA:", 
                              font=("Arial", 9, "bold"),
                              bg=self.bg_color, fg="#999999")
        label_senha.pack(anchor="w", pady=(0, 5))
        
        entry_senha = tk.Entry(senha_container, textvariable=self.senha_var,
                              bg=self.entry_bg, fg=self.entry_fg, show="*",
                              insertbackground=self.fg_color, relief="flat", bd=0,
                              highlightthickness=0, font=("Arial", 9))
        entry_senha.pack(fill="x", ipady=5)
        
        # Label CONSOLE:
        label_console = tk.Label(self.root, text="CONSOLE:", 
                                font=("Arial", 9, "bold"),
                                bg=self.bg_color, fg="#999999")
        label_console.pack(anchor="w", padx=20, pady=(10, 8))
        
        # Console text area com borda cinza
        console_outer = tk.Frame(self.root, bg="#4a4a4a", padx=2, pady=2)
        console_outer.pack(padx=20, fill="both", expand=True, pady=(0, 10))
        
        self.console = scrolledtext.ScrolledText(console_outer, 
                                                 bg="#1a1a1a", 
                                                 fg="#00ff00",
                                                 font=("Consolas", 9),
                                                 relief="flat",
                                                 bd=0,
                                                 insertbackground="#00ff00")
        self.console.pack(fill="both", expand=True)
        self.console.config(state="disabled")
        
        # Frame para os botões de ação
        frame_botoes = tk.Frame(self.root, bg=self.bg_color)
        frame_botoes.pack(pady=(0, 20))
        
        # Botão INICIAR
        btn_iniciar_outer = tk.Frame(frame_botoes, bg="#666666", padx=2, pady=2)
        btn_iniciar_outer.grid(row=0, column=0, padx=20)
        
        btn_iniciar_container = tk.Frame(btn_iniciar_outer, bg=self.bg_color)
        btn_iniciar_container.pack()
        
        self.btn_iniciar = tk.Button(btn_iniciar_container, text="INICIAR", 
                                     command=self.iniciar_processamento,
                                     width=15, height=2, font=("Arial", 10, "bold"),
                                     bg=self.bg_color, fg=self.fg_color,
                                     relief="flat", bd=0, cursor="hand2",
                                     activebackground="#3c3c3c", activeforeground=self.fg_color,
                                     highlightthickness=0)
        self.btn_iniciar.pack()
        
        linha_azul = tk.Frame(btn_iniciar_container, bg="#0078d4", height=3)
        linha_azul.pack(fill="x")
        
        # Botão CANCELAR
        btn_cancelar_outer = tk.Frame(frame_botoes, bg="#666666", padx=2, pady=2)
        btn_cancelar_outer.grid(row=0, column=1, padx=20)
        
        btn_cancelar_container = tk.Frame(btn_cancelar_outer, bg=self.bg_color)
        btn_cancelar_container.pack()
        
        btn_cancelar = tk.Button(btn_cancelar_container, text="CANCELAR", 
                                command=self.root.quit,
                                width=15, height=2, font=("Arial", 10, "bold"),
                                bg=self.bg_color, fg=self.fg_color,
                                relief="flat", bd=0, cursor="hand2",
                                activebackground="#3c3c3c", activeforeground=self.fg_color,
                                highlightthickness=0)
        btn_cancelar.pack()
        
        linha_vermelha = tk.Frame(btn_cancelar_container, bg="#ff0000", height=3)
        linha_vermelha.pack(fill="x")
    
    def criar_botao_acao(self, parent, texto, command, cor_linha):
        """Cria um botão com borda cinza e linha colorida na base"""
        outer = tk.Frame(parent, bg="#666666", padx=2, pady=2)
        
        container = tk.Frame(outer, bg=self.bg_color)
        container.pack()
        
        btn = tk.Button(container, text=texto, command=command,
                       width=10, height=1, font=("Arial", 9, "bold"),
                       bg=self.bg_color, fg=self.fg_color,
                       relief="flat", bd=0, cursor="hand2",
                       activebackground="#3c3c3c", activeforeground=self.fg_color,
                       highlightthickness=0)
        btn.pack(padx=5, pady=3)
        
        linha = tk.Frame(container, bg=cor_linha, height=3)
        linha.pack(fill="x")
        
        return outer
    
    def log_console(self, mensagem):
        """Adiciona mensagem ao console"""
        self.console.config(state="normal")
        self.console.insert(tk.END, mensagem + "\n")
        self.console.see(tk.END)
        self.console.config(state="disabled")
        self.root.update()
    
    def procurar_planilha(self):
        arquivo = filedialog.askopenfilename(
            title="Selecione a Planilha CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if arquivo:
            self.planilha_var.set(arquivo)
            self.log_console(f"Planilha carregada: {arquivo}")
    
    def criar_modelo(self):
        arquivo = filedialog.asksaveasfilename(
            title="Salvar Modelo CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if arquivo:
            try:
                # Criar CSV com o cabeçalho correto
                with open(arquivo, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(['imv_id', 'alterar', 'codigo'])
                
                self.log_console(f"Modelo criado com sucesso: {arquivo}")
                self.log_console("Cabeçalho: imv_id,alterar,codigo")
                messagebox.showinfo("Sucesso", f"Modelo CSV criado com sucesso!\n\n{arquivo}")
            except Exception as e:
                self.log_console(f"ERRO ao criar modelo: {str(e)}")
                messagebox.showerror("Erro", f"Erro ao criar modelo:\n\n{str(e)}")
    
    def iniciar_processamento(self):
        """Inicia o processamento em uma thread separada"""
        planilha = self.planilha_var.get()
        usuario = self.usuario_var.get()
        senha = self.senha_var.get()
        
        if not planilha:
            messagebox.showerror("Erro", "Por favor, selecione uma planilha!")
            return
        
        if not os.path.exists(planilha):
            messagebox.showerror("Erro", "Arquivo não encontrado!")
            return
        
        if not usuario or not senha:
            messagebox.showerror("Erro", "Por favor, preencha usuário e senha!")
            return
        
        if self.is_running:
            messagebox.showwarning("Aviso", "Processamento já está em execução!")
            return
        
        # Desabilitar botão
        self.btn_iniciar.config(state="disabled")
        self.is_running = True
        
        # Limpar console
        self.console.config(state="normal")
        self.console.delete(1.0, tk.END)
        self.console.config(state="disabled")
        
        # Iniciar thread
        thread = threading.Thread(target=self.processar_planilha, args=(planilha, usuario, senha))
        thread.daemon = True
        thread.start()
    
    def processar_planilha(self, planilha, usuario, senha):
        """Processa a planilha - código original do script"""
        try:
            self.log_console("="*60)
            self.log_console("INICIANDO PROCESSAMENTO...")
            self.log_console("="*60)
            
            df = pd.read_csv(planilha)
            self.log_console(f"Planilha carregada: {len(df)} registros encontrados")
            
            # Criar driver e fazer login com as credenciais fornecidas
            self.log_console("Realizando login no sistema...")
            self.log_console(f"Usuário: {usuario}")
            
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            
            # Login no GSAN com as credenciais fornecidas
            driver.get("http://gsan.caema.ma.gov.br:8080/gsan/")
            time.sleep(2)
            
            self.log_console("Preenchendo campos de login...")
            campo_usuario = driver.find_element(By.NAME, "login")
            campo_usuario.clear()
            campo_usuario.send_keys(usuario)
            
            campo_senha = driver.find_element(By.NAME, "senha")
            campo_senha.clear()
            campo_senha.send_keys(senha)
            
            time.sleep(0.5)
            driver.find_element(By.NAME, "buttonLogin").click()
            time.sleep(2)
            
            self.log_console("Login realizado com sucesso!")
            
            for i in df.index:    
                driver.get("http://gsan.caema.ma.gov.br:8080/gsan/exibirFiltrarImovelAction.do?menu=sim")    
                
                matricula = str(df['imv_id'][i])
                alterar = int(df['alterar'][i])  
                codigo = str(df['codigo'][i])
                
                self.log_console(f"\n[{i+1}/{len(df)}] Processando matrícula: {matricula}")
                
                driver.find_element(By.NAME, 'matriculaFiltro').send_keys(matricula)
                driver.find_element(By.XPATH, "//input[@value='Filtrar']").click()    
                time.sleep(0.5)
                driver.find_element(By.ID, "3").click()
                time.sleep(0.2)
                
                if alterar == 1:      
                    try:
                        driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()
                    except:
                        pass               
                    user_cod = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr/td[3]/div").text
                        
                    if user_cod != codigo:
                        try:          
                            tipo_cliente = driver.find_element(By.XPATH,"//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr/td[5]/div").text
                            if tipo_cliente == "USUARIO":
                                date_inicio_rel = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr/td[6]").text
                        except:
                            pass           
                        j = 1
                        while j < 4:
                            try:
                                tipo_cliente = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[5]/div".format(j)).text
                                if tipo_cliente == "USUARIO":
                                    date_inicio_rel = driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[6]".format(j)).text
                                    
                                    driver.find_element(By.XPATH, "//*[@id='formDiv']/form/table[3]/tbody/tr/td[2]/table[4]/tbody/tr[7]/td/table/tbody/tr[2]/td/div/table/tbody/tr[{}]/td[1]/div/input".format(j)).click()
                            except:
                                break
                            j = j + 1

                        time.sleep(0.2)            
                        driver.find_element(By.XPATH, "//input[@value='Remover']").click()
                        alert = driver.switch_to.alert
                        alert = alert.accept()
                        try:
                            driver.find_element(By.XPATH, "//input[@value='Prosseguir']").click()
                        except:
                            pass            
                        time.sleep(1) 
                        janela = driver.window_handles[0]
                        popup = driver.window_handles[1]
                        driver.switch_to.window(popup)        
                        date_inicio_rel = date_inicio_rel.replace('/', '')     
                        driver.find_element(By.NAME, 'dataTerminoRelacao').clear()
                        driver.find_element(By.NAME, 'dataTerminoRelacao').send_keys(date_inicio_rel)
                        driver.find_element(By.NAME, 'idMotivo').send_keys('ATUALIZ. CADASTRAL')
                        driver.find_element(By.XPATH, "//input[@value='Confirmar']").click()           
                        
                        try:
                            time.sleep(0.2)
                            msg_err0 = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span")
                            self.log_console(f"ERRO: {msg_err0.text}")
                            msg_er1 = bool(msg_err0)                
                        
                            driver.find_element(By.XPATH, "//input[@value='Voltar']").click()
                            driver.close()
                            time.sleep(0.5)
                            driver.switch_to.window(janela)               
                            driver.find_element(By.XPATH, "//input[@value='Cancelar']").click()
                        except:
                            time.sleep(0.2)
                            driver.switch_to.window(janela)
                            janela = driver.window_handles[0]               
                            driver.switch_to.window(janela)
                            time.sleep(0.5)                
                            
                            driver.find_element(By.NAME, "idCliente").send_keys(codigo, Keys.ENTER)
                            time.sleep(0.5)
                            driver.find_element(By.NAME, "tipoClienteImovel").send_keys('02 - USUARIO')
                            time.sleep(0.5)
                            driver.find_element(By.XPATH, "//input[@value='Adicionar']").click()               
                        
                            try:
                                time.sleep(0.3)
                                driver.find_element(By.XPATH, "//input[@value='Sim']").click()
                                time.sleep(0.3)
                                driver.find_element(By.XPATH, "//input[@value='Concluir']").click()    
                                time.sleep(0.3)                
                                msg_ok = driver.find_element(By.XPATH, "/html/body/table[2]/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/div/span").text
                                self.log_console(f"SUCESSO: {msg_ok}")
                            except:                   
                                msg_err = driver.find_element(By.XPATH, "/html/body/table/tbody/tr/td/table[3]/tbody/tr[1]/td[2]/span").text
                                self.log_console(f"ERRO: {msg_err}")
                    else:           
                        self.log_console(f"INFO: Cliente com o mesmo código já inserido na matrícula: {matricula}")
            
            self.log_console("\n" + "="*60)
            self.log_console("PROCESSAMENTO CONCLUÍDO!")
            self.log_console("="*60)
            
        except Exception as e:
            self.log_console(f"\nERRO CRÍTICO: {str(e)}")
            messagebox.showerror("Erro", f"Erro durante o processamento:\n\n{str(e)}")
        
        finally:
            self.is_running = False
            self.btn_iniciar.config(state="normal")


def main():
    root = tk.Tk()
    app = AlterarClienteGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
