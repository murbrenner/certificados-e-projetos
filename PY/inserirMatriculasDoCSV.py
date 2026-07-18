#NOME: Inserir Matriculas do CSV

#DESCRIÇÃO: Executa a rotina 'Inserir Matriculas do CSV', inserindo dados, geometrias ou atributos conforme a logica definida no script. Inclui leitura e/ou escrita de dados em CSV.

#PRÉ-REQUISITO: Selecionar previamente as feicoes que serao processadas; garantir arquivo CSV valido e no layout esperado.


import re

import pandas as pd
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


def normalizar_texto(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()
    if not texto or texto.lower() == "nan":
        return ""

    if re.match(r"^\d+\.0$", texto):
        return texto[:-2]

    return texto


def mesmo_codigo(valor_a, valor_b):
    a = normalizar_texto(valor_a)
    b = normalizar_texto(valor_b)

    if not a or not b:
        return False

    if a.isdigit() and b.isdigit():
        a_num = a.lstrip("0") or "0"
        b_num = b.lstrip("0") or "0"
        return a_num == b_num

    return a.lower() == b.lower()


def obter_camada(nome_camada):
    camadas = QgsProject.instance().mapLayersByName(nome_camada)
    if not camadas:
        raise Exception("Camada '{}' não encontrada no projeto.".format(nome_camada))
    return camadas[0]


def obter_rota_preselecionada(layer_rotas):
    rotas_selecionadas = layer_rotas.selectedFeatures()
    if not rotas_selecionadas:
        raise Exception("Selecione ao menos uma feição na camada 'ROTAS DE LEITURA'.")

    campos_rota = ["ROTA", "rota", "rot_id", "ROT_ID", "cd_rota", "CD_ROTA", "id_rota", "ID_ROTA"]

    for campo in campos_rota:
        if campo in layer_rotas.fields().names():
            rota = normalizar_texto(rotas_selecionadas[0][campo])
            if rota:
                return rota

    raise Exception(
        "Não foi possível identificar o campo da rota na camada 'ROTAS DE LEITURA'. "
        "Use um campo como ROTA ou rot_id."
    )


def selecionar_imoveis_por_localizacao_da_rota(layer_rotas, layer_imovel, rota_preselecionada):
    rotas_selecionadas = layer_rotas.selectedFeatures()
    if not rotas_selecionadas:
        raise Exception("Selecione ao menos uma feição na camada 'ROTAS DE LEITURA'.")

    # Primeiro tenta selecionar por atributo de rota no IMÓVEL.
    campos_rota_imovel = ["rot_id", "ROT_ID", "ROTA", "rota", "cd_rota", "CD_ROTA", "id_rota", "ID_ROTA"]
    campos_imovel = layer_imovel.fields().names()
    for campo in campos_rota_imovel:
        if campo not in campos_imovel:
            continue

        ids_por_atributo = []
        for imovel in layer_imovel.getFeatures():
            if mesmo_codigo(imovel[campo], rota_preselecionada):
                ids_por_atributo.append(imovel.id())

        if ids_por_atributo:
            layer_imovel.removeSelection()
            layer_imovel.selectByIds(ids_por_atributo)
            print("Imóveis selecionados por atributo de rota ({}): {}".format(campo, len(ids_por_atributo)))
            return len(ids_por_atributo)

    geometria_rotas = None
    for rota_feature in rotas_selecionadas:
        geom = rota_feature.geometry()
        if not geom or geom.isEmpty():
            continue
        if geometria_rotas is None:
            geometria_rotas = geom
        else:
            geometria_rotas = geometria_rotas.combine(geom)

    if geometria_rotas is None or geometria_rotas.isEmpty():
        raise Exception("As feições selecionadas em 'ROTAS DE LEITURA' não possuem geometria válida.")

    ids_imoveis = []
    for imovel in layer_imovel.getFeatures():
        geom_imovel = imovel.geometry()
        if not geom_imovel or geom_imovel.isEmpty():
            continue
        if geom_imovel.intersects(geometria_rotas):
            ids_imoveis.append(imovel.id())

    layer_imovel.removeSelection()
    if ids_imoveis:
        layer_imovel.selectByIds(ids_imoveis)

    return len(ids_imoveis)


class SeletorCsvDialog(QDialog):
    def __init__(self, rota):
        super().__init__()
        self.setWindowTitle("Selecionar CSV e rota")
        self.setFixedSize(560, 130)

        layout_principal = QVBoxLayout(self)

        linha_arquivo = QHBoxLayout()
        linha_arquivo.addWidget(QLabel("CSV:"))
        self.input_arquivo = QLineEdit()
        self.input_arquivo.setPlaceholderText("Selecione o arquivo CSV...")
        linha_arquivo.addWidget(self.input_arquivo)

        botao_procurar = QPushButton("Procurar")
        botao_procurar.clicked.connect(self.selecionar_arquivo)
        linha_arquivo.addWidget(botao_procurar)
        layout_principal.addLayout(linha_arquivo)

        linha_rota = QHBoxLayout()
        linha_rota.addWidget(QLabel("Rota selecionada:"))
        self.input_rota = QLineEdit(rota)
        self.input_rota.setReadOnly(True)
        linha_rota.addWidget(self.input_rota)
        layout_principal.addLayout(linha_rota)

        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botoes.accepted.connect(self.validar)
        botoes.rejected.connect(self.reject)
        layout_principal.addWidget(botoes)

    def selecionar_arquivo(self):
        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecione o arquivo CSV",
            "C:/CSV",
            "Arquivos CSV (*.csv);;Todos os arquivos (*)",
        )
        if arquivo:
            self.input_arquivo.setText(arquivo)

    def validar(self):
        if not self.input_arquivo.text().strip():
            QMessageBox.warning(self, "Atenção", "Selecione um arquivo CSV.")
            return
        self.accept()


def executar_fluxo():
    layer_rotas = obter_camada("ROTAS DE LEITURA")
    layer_imovel = obter_camada("IMÓVEL")

    rota_preselecionada = obter_rota_preselecionada(layer_rotas)

    dialogo = SeletorCsvDialog(rota_preselecionada)
    if dialogo.exec_() != QDialog.Accepted:
        print("Operação cancelada pelo usuário.")
        return

    arquivo_csv = dialogo.input_arquivo.text().strip()
    db = pd.read_csv(arquivo_csv, dtype=str)

    if "SEQUENCIA" not in db.columns or "MATRICULA" not in db.columns:
        raise Exception("CSV deve conter as colunas SEQUENCIA e MATRICULA.")

    total_imoveis_selecionados = selecionar_imoveis_por_localizacao_da_rota(
        layer_rotas,
        layer_imovel,
        rota_preselecionada,
    )
    if total_imoveis_selecionados == 0:
        raise Exception("Nenhum imóvel foi encontrado na localização da(s) rota(s) selecionada(s).")

    print("Imóveis selecionados por localização:", total_imoveis_selecionados)

    layer_imovel.startEditing()
    atualizados = 0
    imoveis_selecionados = layer_imovel.selectedFeatures()

    for i in db.index:
        sequencia = normalizar_texto(db["SEQUENCIA"][i])
        matricula = normalizar_texto(db["MATRICULA"][i])

        if not sequencia or not matricula:
            continue

        for imovel in imoveis_selecionados:
            seq_id = normalizar_texto(imovel["seq_id"])
            rot_id = normalizar_texto(imovel["rot_id"])

            if mesmo_codigo(seq_id, sequencia) and mesmo_codigo(rot_id, rota_preselecionada):
                imovel.setAttribute("imv_id", matricula)
                layer_imovel.updateFeature(imovel)
                atualizados += 1
                print(sequencia, matricula, rota_preselecionada, ",", seq_id, imovel["imv_id"], imovel["rot_id"])

    QMessageBox.information(
        None,
        "Sucesso",
        (
            "Processo concluído com sucesso.\n"
            "Rota utilizada: {}\n"
            "Imóveis selecionados: {}\n"
            "Atributos imv_id atualizados: {}"
        ).format(rota_preselecionada, total_imoveis_selecionados, atualizados),
    )


try:
    executar_fluxo()
except Exception as erro:
    QMessageBox.critical(None, "Erro no processo", str(erro))
    print("Erro:", erro)
