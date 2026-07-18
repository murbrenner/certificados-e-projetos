#NOME: Gerar Pdf da Rota Selecionada

#DESCRIÇÃO: gerarPdfDaRotaSelecionada.py Exporta PDFs e arquivos QPT para varias rotas selecionadas na camada 'ROTAS DE LEITURA'. O script abre uma unica janela para informar: - template QPT base - pasta de saida dos QPTs - pasta de saida dos PDFs - localidade, setor e municipio Para cada feicao selecionada, o valor da rota e lido. O resultado final e adicionado ao projeto.

#PRÉ-REQUISITO: Selecionar previamente as feicoes que serao processadas.


# -*- coding: utf-8 -*-
"""
gerarPdfDaRotaSelecionada.py

Exporta PDFs e arquivos QPT para varias rotas selecionadas na camada
'ROTAS DE LEITURA'. O script abre uma unica janela para informar:
- template QPT base
- pasta de saida dos QPTs
- pasta de saida dos PDFs
- localidade, setor e municipio

Para cada feicao selecionada, o valor da rota e lido do atributo 'rota'
da camada de rotas, o layout e preenchido automaticamente e os arquivos
finais sao gerados nas pastas informadas.
"""

import math
import os
import shutil
import time
import unicodedata
import csv

from qgis.core import (
    QgsCoordinateTransform,
    QgsFeature,
    QgsField,
    QgsFillSymbol,
    QgsGeometry,
    QgsLayoutExporter,
    QgsLayoutItemLabel,
    QgsLayoutItemMap,
    QgsLayoutItemPolygon,
    QgsLayoutItemPicture,
    QgsLineSymbol,
    QgsMapLayerStyle,
    QgsMarkerSymbol,
    QgsProject,
    QgsPrintLayout,
    QgsReadWriteContext,
    QgsRectangle,
    QgsSymbol,
    QgsVectorLayer,
)
from qgis.gui import QgsFileWidget
from qgis.PyQt.QtCore import QEventLoop, QSize, Qt
from qgis.PyQt.QtXml import QDomDocument
from qgis.PyQt.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QCheckBox,
)


class InterfaceExportacao(QDialog):
    def __init__(self, parent=None):
        super(InterfaceExportacao, self).__init__(parent)
        self.setWindowTitle("Configurar Exportação de Rotas")
        self.setMinimumWidth(500)
        
        self.layout_principal = QVBoxLayout()
        self.form_layout = QFormLayout()
        
        # Campo Template QPT
        self.txt_template = QLineEdit()
        self.btn_template = QPushButton("Buscar...")
        self.btn_template.clicked.connect(self._selecionar_template)
        layout_tmp = QHBoxLayout()
        layout_tmp.addWidget(self.txt_template)
        layout_tmp.addWidget(self.btn_template)
        self.form_layout.addRow("Template QPT Base:", layout_tmp)
        
        # Campo Pasta Saída QPT
        self.txt_out_qpt = QLineEdit()
        self.btn_out_qpt = QPushButton("Buscar...")
        self.btn_out_qpt.clicked.connect(lambda: self._selecionar_diretorio(self.txt_out_qpt))
        layout_qpt = QHBoxLayout()
        layout_qpt.addWidget(self.txt_out_qpt)
        layout_qpt.addWidget(self.btn_out_qpt)
        self.form_layout.addRow("Pasta Saída QPTs:", layout_qpt)
        
        # Campo Pasta Saída PDF
        self.txt_out_pdf = QLineEdit()
        self.btn_out_pdf = QPushButton("Buscar...")
        self.btn_out_pdf.clicked.connect(lambda: self._selecionar_diretorio(self.txt_out_pdf))
        layout_pdf = QHBoxLayout()
        layout_pdf.addWidget(self.txt_out_pdf)
        layout_pdf.addWidget(self.btn_out_pdf)
        self.form_layout.addRow("Pasta Saída PDFs:", layout_pdf)
        
        # Filtros de Texto
        self.txt_municipio = QLineEdit()
        self.form_layout.addRow("Município:", self.txt_municipio)
        
        self.txt_localidade = QLineEdit()
        self.form_layout.addRow("Localidade:", self.txt_localidade)
        
        self.txt_setor = QLineEdit()
        self.form_layout.addRow("Setor:", self.txt_setor)

        # --- ADICIONE ESTAS LINHAS JUNTO AOS OUTROS CAMPOS DO FORMULÁRIO ---
        self.chk_exibir_quadras = QCheckBox("Exibir polígonos da camada QUADRAS")
        self.chk_exibir_quadras.setChecked(True)  # Deixa marcado por padrão
        self.form_layout.addRow("", self.chk_exibir_quadras)
        
        # --- CAIXA DE SELEÇÃO PARA EXIBIR POLÍGONOS DAS QUADRAS ---
        self.chk_exibir_quadras = QCheckBox("Exibir polígonos da camada QUADRAS")
        self.chk_exibir_quadras.setChecked(True)  # Marcado como padrão (visível)
        self.form_layout.addRow("", self.chk_exibir_quadras)
        
        # Botões da Janela
        self.btn_ok = QPushButton("Iniciar Exportação")
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancelar.clicked.connect(self.reject)
        
        layout_botoes = QHBoxLayout()
        layout_botoes.addStretch()
        layout_botoes.addWidget(self.btn_ok)
        layout_botoes.addWidget(self.btn_cancelar)
        
        self.layout_principal.addLayout(self.form_layout)
        self.layout_principal.addLayout(layout_botoes)
        self.setLayout(self.layout_principal)

    def _selecionar_template(self):
        arquivo, _ = QFileDialog.getOpenFileName(self, "Selecionar Template QPT", "", "Templates QGIS (*.qpt)")
        if arquivo:
            self.txt_template.setText(arquivo)

    def _selecionar_diretorio(self, campo_texto):
        diretorio = QFileDialog.getExistingDirectory(self, "Selecionar Pasta")
        if diretorio:
            campo_texto.setText(diretorio)

    def obter_configuracoes(self):
        return {
            "template_path": self.txt_template.text().strip(),
            "qpt_output_dir": self.txt_out_qpt.text().strip(),
            "pdf_output_dir": self.txt_out_pdf.text().strip(),
            "municipio": self.txt_municipio.text().strip(),
            "localidade": self.txt_localidade.text().strip(),
            "setor": self.txt_setor.text().strip(),
            "exibir_poligonos_quadras": self.chk_exibir_quadras.isChecked()
        }


def _processar_eventos_ui():
    QApplication.processEvents(QEventLoop.ExcludeUserInputEvents | QEventLoop.WaitForMoreEvents, 10)


def remover_acentos(texto):
    if not texto:
        return ""
    nfkd = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)])


def configurar_layout(layout, feicao_rota, config):
    substituicoes = {
        "txt_municipio": config.get("municipio", ""),
        "txt_localidade": config.get("localidade", ""),
        "txt_setor": config.get("setor", ""),
        "txt_rota": str(feicao_rota.attribute("rota") or "")
    }
    
    for item in layout.items():
        if isinstance(item, QgsLayoutItemLabel):
            id_item = item.id()
            if id_item in substituicoes:
                item.setText(substituicoes[id_item])
        
        if isinstance(item, QgsLayoutItemMap):
            geometria = feicao_rota.geometry()
            if not geometria.isEmpty():
                item.zoomToExtent(geometria.boundingBox())
                item.setExtent(item.extent().buffered(item.extent().width() * 0.15))


def exportar_rota(feicao_rota, config):
    projeto = QgsProject.instance()
    layout = QgsPrintLayout(projeto)
    
    with open(config["template_path"], "r", encoding="utf-8") as f:
        conteudo_xml = f.read()
        
    documento = QDomDocument()
    documento.setContent(conteudo_xml)
    
    contexto = QgsReadWriteContext()
    if not layout.loadFromTemplate(documento, contexto):
        raise RuntimeError("Falha ao carregar a estrutura do arquivo QPT base.")
        
    configurar_layout(layout, feicao_rota, config)
    
    rota_id = str(feicao_rota.attribute("rota") or "Sem_Nome")
    nome_arquivo = f"Rota_{remover_acentos(rota_id)}"
    
    path_qpt_final = os.path.join(config["qpt_output_dir"], f"{nome_arquivo}.qpt")
    path_pdf_final = os.path.join(config["pdf_output_dir"], f"{nome_arquivo}.pdf")
    
    layout.saveAsTemplate(path_qpt_final, contexto)
    
    exportador = QgsLayoutExporter(layout)
    config_pdf = QgsLayoutExporter.PdfExportSettings()
    config_pdf.dpi = 150
    
    status = exportador.exportToPdf(path_pdf_final, config_pdf)
    if status != QgsLayoutExporter.Success:
        raise RuntimeError(f"Erro do QGIS (Código {status}) ao gerar arquivo PDF.")
        
    return path_pdf_final


def main():
    camadas_rotas = QgsProject.instance().mapLayersByName('ROTAS DE LEITURA')
    if not camadas_rotas:
        QMessageBox.critical(None, "Erro", "A camada obrigatória 'ROTAS DE LEITURA' não foi encontrada no projeto.")
        return
        
    camada_rotas = camadas_rotas[0]
    feicoes_selecionadas = list(camada_rotas.selectedFeatures())
    
    if not feicoes_selecionadas:
        QMessageBox.warning(None, "Aviso", "Por favor, selecione ao menos uma rota na camada 'ROTAS DE LEITURA' antes de rodar o script.")
        return
        
    janela = InterfaceExportacao()
    if janela.exec_() != QDialog.Accepted:
        print("Exportação cancelada pelo usuário.")
        return
        
    config_exportacao = janela.obter_configuracoes()
    
    if not config_exportacao["template_path"] or not config_exportacao["pdf_output_dir"] or not config_exportacao["qpt_output_dir"]:
        QMessageBox.critical(None, "Campos Obrigatórios", "Você precisa preencher o Template Base e as Pastas de Saída para continuar.")
        return

    # --- CONTROLE DINÂMICO DA OPACIDADE DA CAMADA QUADRAS ---
    camadas_quadras = QgsProject.instance().mapLayersByName('QUADRAS')
    camada_quadras = camadas_quadras[0] if camadas_quadras else None
    
    original_opacity = 1.0
    alterou_estilo = False
    
    # Se a camada 'QUADRAS' existir e o usuário desmarcou o checkbox
    if camada_quadras and not config_exportacao["exibir_poligonos_quadras"]:
        if camada_quadras.renderer():
            original_opacity = camada_quadras.renderer().opacity()
            # Define opacidade do preenchimento/linhas para 0. Rótulos continuam 100% visíveis
            camada_quadras.renderer().setOpacity(0.0)
            camada_quadras.triggerRepaint()
            alterou_estilo = True

    progresso = QProgressBar()
    progresso.setWindowTitle("Exportando PDFs das Rotas")
    progresso.setRange(0, len(feicoes_selecionadas))
    progresso.setValue(0)
    progresso.show()
    
    resultados = []
    erros = []
    total = len(feicoes_selecionadas)

    try:
        for indice, feicao in enumerate(feicoes_selecionadas, start=1):
            rota_label = str(feicao.attribute("rota") or "Ignorada")
            try:
                print(f"[{indice}/{total}] Exportando Rota: {rota_label}...")
                pdf_gerado = exportar_rota(feicao, config_exportacao)
                resultados.append(pdf_gerado)
            except Exception as exc:
                erros.append(f"Rota {rota_label}: {exc}")
                print(f"[{indice}/{total}] Erro na rota {rota_label}: {exc}")
            finally:
                progresso.setValue(indice)
                _processar_eventos_ui()

    finally:
        # --- BLOCO DE SEGURANÇA: RESTAURA O DESIGN ORIGINAL NO SEU QGIS ---
        if alterou_estilo and camada_quadras and camada_quadras.renderer():
            camada_quadras.renderer().setOpacity(original_opacity)
            camada_quadras.triggerRepaint()
            
        progresso.close()

    if resultados and not erros:
        QMessageBox.information(
            None,
            'Exportação concluída',
            f'{len(resultados)} rota(s) exportada(s) com sucesso.\n\nPDFs: {config_exportacao["pdf_output_dir"]}\nQPTs: {config_exportacao["qpt_output_dir"]}',
        )
        return

    if resultados and erros:
        QMessageBox.warning(
            None,
            'Exportação concluída com ressalvas',
            f'{len(resultados)} rota(s) exportada(s) com sucesso e {len(erros)} falha(s).\n\n' + '\n'.join(erros[:10]),
        )
        return

    raise RuntimeError('Nenhuma rota foi exportada.\n' + '\n'.join(erros[:10]))


def _run_with_ui_feedback():
    try:
        print('Iniciando geracao de PDFs das rotas selecionadas...')
        main()
    except Exception as exc:
        msg = f'Erro: {exc}'
        print(msg)
        QMessageBox.critical(None, 'Erro na exportacao do PDF', msg)


def run():
    _run_with_ui_feedback()


if __name__ in ('__main__', '__qgis_main__'):
    run()