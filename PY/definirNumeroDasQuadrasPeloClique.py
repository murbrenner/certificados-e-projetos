#NOME: Definir Numero das Quadras Pelo Clique

#DESCRIÇÃO: Define valores e atualiza atributos das feicoes conforme a regra estabelecida. Requer interacao do operador por clique no mapa. Camadas envolvidas: 'QUADRAS'.

#PRÉ-REQUISITO: Carregar a camada 'QUADRAS' no projeto QGIS; manter ativa a ferramenta/interacao por clique durante a execucao.


from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QHBoxLayout
from qgis.gui import QgsMapTool
from qgis.core import (
    QgsProject,
    QgsPointXY,
    QgsField,
)
from PyQt5.QtCore import QVariant
from qgis.utils import iface

layer_name = 'QUADRAS'
layer = QgsProject.instance().mapLayersByName(layer_name)[0]

# Ferramenta de clique
class ClickTool(QgsMapTool):
    def __init__(self, canvas, layer, quadra_inicial, setor, gerencia, janela):
        super().__init__(canvas)
        self.canvas = canvas
        self.layer = layer
        self.quadra = quadra_inicial
        self.setor = setor
        self.gerencia = gerencia
        self.janela = janela  # Referência à janela

    def canvasReleaseEvent(self, event):
        point = self.canvas.getCoordinateTransform().toMapCoordinates(event.pos().x(), event.pos().y())
        clicked_point = QgsPointXY(point)

        for feat in self.layer.getFeatures():
            if feat.geometry().contains(clicked_point):
                if not self.layer.isEditable():
                    if not self.layer.startEditing():
                        print("Erro ao ativar edição.")
                        return
                feat['quadra'] = self.quadra
                feat['setor'] = self.setor
                feat['gerencia'] = self.gerencia
                self.layer.updateFeature(feat)
                print(f"Feição atualizada: Quadra {self.quadra}")
                self.quadra += 1
                break

# Janela com botões
class QuadraDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Definir Quadra, Setor e Gerência")
        self.layout = QVBoxLayout()
        self.form = QFormLayout()

        self.quadra_input = QLineEdit()
        self.setor_input = QLineEdit()
        self.gerencia_input = QLineEdit()

        self.form.addRow("Quadra inicial:", self.quadra_input)
        self.form.addRow("Setor:", self.setor_input)
        self.form.addRow("Gerência:", self.gerencia_input)

        self.layout.addLayout(self.form)

        self.btn_iniciar = QPushButton("Iniciar")
        self.btn_cancelar = QPushButton("Cancelar")

        self.btn_iniciar.clicked.connect(self.ativar_ferramenta)
        self.btn_cancelar.clicked.connect(self.encerrar)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_iniciar)
        btn_layout.addWidget(self.btn_cancelar)

        self.layout.addLayout(btn_layout)
        self.setLayout(self.layout)

        self.tool = None

    def ativar_ferramenta(self):
        try:
            quadra = int(self.quadra_input.text())
            setor = self.setor_input.text()
            gerencia = self.gerencia_input.text()
        except:
            print("Valores inválidos.")
            return

        if not layer.isEditable():
            if not layer.startEditing():
                print("Erro ao ativar modo de edição.")
                return

        self.tool = ClickTool(iface.mapCanvas(), layer, quadra, setor, gerencia, self)
        iface.mapCanvas().setMapTool(self.tool)
        print("Ferramenta ativada. Clique nas feições para atualizar.")

    def encerrar(self):
        iface.mapCanvas().unsetMapTool(self.tool)
        print("Ferramenta desativada. Operação finalizada.")
        self.close()

# Garante campos
def garantir_campos(cam, campos):
    existente = [f.name() for f in cam.fields()]
    novos = []
    for nome, tipo in campos:
        if nome not in existente:
            novos.append(QgsField(nome, tipo))
    if novos:
        cam.startEditing()
        for campo in novos:
            cam.addAttribute(campo)
        cam.updateFields()
        cam.commitChanges()
        print(f"Campos criados: {[c.name() for c in novos]}")

# Início do processo
def iniciar():
    if not layer:
        print(f"Camada '{layer_name}' não encontrada.")
        return

    garantir_campos(layer, [
        ('quadra', QVariant.Int),
        ('setor', QVariant.String),
        ('gerencia', QVariant.String)
    ])

    dlg = QuadraDialog()
    iface._janela_quadra = dlg  # <- MANTÉM A JANELA VIVA
    dlg.show()

iniciar()
