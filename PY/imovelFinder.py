# -*- coding: utf-8 -*-
from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox
from qgis.PyQt.QtCore import Qt, QTimer
from qgis.core import QgsProject, QgsFeatureRequest, QgsGeometry, QgsCoordinateTransform, QgsCoordinateReferenceSystem

class BuscadorEspacialSRC(QDialog):
    def __init__(self, parent=None):
        super(BuscadorEspacialSRC, self).__init__(parent, Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Buscador Espacial - Filtro por Localização")
        self.resize(350, 320)
        
        self.layout = QVBoxLayout()
        
        self.layout.addWidget(QLabel("Selecione a Camada Alvo:"))
        self.combo_camadas = QComboBox()
        self.layout.addWidget(self.combo_camadas)
        
        self.layout.addWidget(QLabel("Selecione o Campo (Coluna):"))
        self.combo_campos = QComboBox()
        self.layout.addWidget(self.combo_campos)
        
        self.layout.addWidget(QLabel("Termo para buscar:"))
        self.txt_busca = QLineEdit()
        self.layout.addWidget(self.txt_busca)
        
        self.layout.addWidget(QLabel("<br><b>Limitar busca à área selecionada de:</b>"))
        self.combo_limite = QComboBox()
        self.layout.addWidget(self.combo_limite)
        
        self.btn_buscar = QPushButton("🔍 Filtrar Localização e Buscar")
        self.btn_buscar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; font-size: 14px; padding: 6px;")
        self.layout.addWidget(self.btn_buscar)
        
        self.setLayout(self.layout)
        
        self.combo_camadas.currentIndexChanged.connect(self.atualizar_campos)
        self.btn_buscar.clicked.connect(self.executar_busca)
        
        self.carregar_camadas()

    def carregar_camadas(self):
        self.combo_camadas.clear()
        self.combo_limite.clear()
        self.combo_limite.addItem("Não limitar (Buscar em tudo)", None)
        
        camadas = QgsProject.instance().mapLayers().values()
        camadas_vetoriais = [c for c in camadas if c.type() == 0]
        
        for c in camadas_vetoriais:
            self.combo_camadas.addItem(c.name(), c)
            if c.geometryType() == 2:
                self.combo_limite.addItem(f"Área: {c.name()}", c)
        self.atualizar_campos()

    def atualizar_campos(self):
        self.combo_campos.clear()
        camada = self.combo_camadas.currentData()
        if camada:
            for campo in camada.fields():
                self.combo_campos.addItem(campo.name())

    def ejecutar_busca(self): # Mantido o nome interno estável
        pass

    def executar_busca(self):
        camada_alvo = self.combo_camadas.currentData()
        campo_nome = self.combo_campos.currentText()
        termo = self.txt_busca.text().strip().lower()
        camada_limite = self.combo_limite.currentData()
        
        if not camada_alvo or not campo_nome or not termo:
            QMessageBox.warning(self, "Aviso", "Preencha todos os campos!")
            return
            
        camada_alvo.removeSelection()
        ids_finais = []
        
        geometria_limite = None
        if camada_limite and self.combo_limite.currentIndex() > 0:
            selecionados = camada_limite.selectedFeatures()
            if not selecionados:
                QMessageBox.warning(self, "Aviso", f"Selecione o polígono na camada '{camada_limite.name()}' antes de buscar.")
                return
            
            # Une as áreas selecionadas
            geometria_limite = QgsGeometry.unaryUnion([f.geometry() for f in selecionados])
            
            # SOLUÇÃO DO BUG: Se os SRCs forem diferentes, reprojeta o polígono limite para o SRC da camada alvo
            src_alvo = camada_alvo.crs()
            src_limite = camada_limite.crs()
            if src_alvo != src_limite:
                transformacao = QgsCoordinateTransform(src_limite, src_alvo, QgsProject.instance())
                geometria_limite.transform(transformacao)

        # Varredura direta dos dados
        for feature in camada_alvo.getFeatures():
            valor_string = str(feature[campo_nome]).strip().lower()
            if termo in valor_string:
                if geometria_limite:
                    # Filtro simples por localização espacial (Interseção real corrigida por SRC)
                    if feature.geometry() and feature.geometry().intersects(geometria_limite):
                        ids_finais.append(feature.id())
                else:
                    ids_finais.append(feature.id())
        
        contagem = len(ids_finais)
        
        if contagem > 0:
            camada_alvo.selectByIds(ids_finais)
            canvas = iface.mapCanvas()
            canvas.zoomToSelected(camada_alvo)
            canvas.zoomScale(350)
            canvas.refresh()
            
            # Pisca por 5 segundos
            self.contador_piscas = 0
            def piscar_elemento():
                if self.contador_piscas < 10:
                    canvas.flashFeatureIds(camada_alvo, ids_finais)
                    self.contador_piscas += 1
                else:
                    self.timer_pisca.stop()
            
            self.timer_pisca = QTimer()
            self.timer_pisca.timeout.connect(piscar_elemento)
            self.timer_pisca.start(500)
            
            iface.showAttributeTable(camada_alvo)
            iface.messageBar().pushMessage("Sucesso", f"{contagem} feições encontradas!", level=0, duration=3)
        else:
            QMessageBox.information(self, "Sem resultados", f"O termo '{termo}' não foi localizado dentro do polígono selecionado.")

# Inicialização
if 'janela_busca' in globals():
    try: janela_busca.close()
    except: pass

janela_busca = BuscadorEspacialSRC(iface.mainWindow())
janela_busca.show()