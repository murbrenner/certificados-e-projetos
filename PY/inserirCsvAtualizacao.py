import csv
import os
from urllib.parse import quote

from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox
from qgis.core import (
    Qgis,
    QgsMarkerSymbol,
    QgsPalLayerSettings,
    QgsProject,
    QgsTextBufferSettings,
    QgsTextFormat,
    QgsVectorFileWriter,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
)


def avisar(texto, nivel=Qgis.Info):
    if "iface" in globals() and iface is not None:
        iface.messageBar().pushMessage("Inserir CSV", texto, level=nivel, duration=6)
    else:
        print(texto)


def detectar_xy(headers):
    normalizados = {h.strip().lower(): h for h in headers}
    candidatos = [
        ("x", "y"),
        ("lon", "lat"),
        ("lng", "lat"),
        ("longitude", "latitude"),
        ("long", "lat"),
        ("coord_x", "coord_y"),
        ("easting", "northing"),
    ]
    for x_key, y_key in candidatos:
        if x_key in normalizados and y_key in normalizados:
            return normalizados[x_key], normalizados[y_key]
    return None, None


def aplicar_estilo_rotulo(camada, campo_rotulo):
    simbolo = QgsMarkerSymbol.createSimple(
        {
            "name": "circle",
            "color": "127,255,0",  # verde cana
            "outline_color": "40,90,40",
            "outline_width": "0.2",
            "size": "2.8",
        }
    )
    camada.renderer().setSymbol(simbolo)

    if campo_rotulo:
        conf_rotulo = QgsPalLayerSettings()
        conf_rotulo.enabled = True
        conf_rotulo.fieldName = campo_rotulo

        formato = QgsTextFormat()
        formato.setSize(9)
        formato.setColor(QColor("white"))

        buffer = QgsTextBufferSettings()
        buffer.setEnabled(True)
        buffer.setSize(1.2)
        buffer.setColor(QColor("blue"))
        formato.setBuffer(buffer)

        conf_rotulo.setFormat(formato)
        camada.setLabelsEnabled(True)
        camada.setLabeling(QgsVectorLayerSimpleLabeling(conf_rotulo))
    else:
        camada.setLabelsEnabled(False)

    camada.triggerRepaint()


def salvar_shp(camada, caminho_saida):
    opcoes = QgsVectorFileWriter.SaveVectorOptions()
    opcoes.driverName = "ESRI Shapefile"
    opcoes.fileEncoding = "UTF-8"
    opcoes.layerName = os.path.splitext(os.path.basename(caminho_saida))[0]

    erro, msg_erro, _, _ = QgsVectorFileWriter.writeAsVectorFormatV3(
        camada,
        caminho_saida,
        QgsProject.instance().transformContext(),
        opcoes,
    )
    return erro, msg_erro


def executar():
    csv_path, _ = QFileDialog.getOpenFileName(
        None,
        "Selecione o CSV",
        "",
        "CSV (*.csv);;Todos os arquivos (*.*)",
    )
    if not csv_path:
        avisar("Operação cancelada pelo usuário.", Qgis.Warning)
        return

    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        leitor = csv.reader(f)
        headers = next(leitor, [])

    if not headers:
        avisar("Não foi possível ler o cabeçalho do CSV.", Qgis.Critical)
        return

    x_field, y_field = detectar_xy(headers)
    if not x_field or not y_field:
        avisar(
            "Não foi possível detectar campos X/Y automaticamente. "
            "Use nomes como x/y, lon/lat ou longitude/latitude.",
            Qgis.Critical,
        )
        return

    epsg = "4326"

    base_name = os.path.splitext(os.path.basename(csv_path))[0]
    pasta_origem = os.path.dirname(csv_path)
    pasta_shp = os.path.join(pasta_origem, "SHP")
    os.makedirs(pasta_shp, exist_ok=True)
    shp_path = os.path.join(pasta_shp, f"{base_name}.shp")

    if os.path.exists(shp_path):
        resp = QMessageBox.question(
            None,
            "Inserir CSV",
            f"O arquivo já existe:\n{shp_path}\n\nDeseja sobrescrever?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            avisar("Salvamento cancelado. SHP existente não foi sobrescrito.", Qgis.Warning)
            return

    uri = (
        f"file:///{csv_path.replace(os.sep, '/')}"
        f"?delimiter=,&detectTypes=yes&xField={quote(x_field)}&yField={quote(y_field)}"
        f"&crs=EPSG:{quote(epsg)}&geomType=point&decimalPoint=."
    )

    camada_csv = QgsVectorLayer(uri, f"{base_name}_tmp_csv", "delimitedtext")
    if not camada_csv.isValid():
        avisar("Falha ao carregar CSV como camada temporária.", Qgis.Critical)
        return

    QgsProject.instance().addMapLayer(camada_csv)

    campo_rotulo = "seq_id"
    if camada_csv.fields().indexOf(campo_rotulo) < 0:
        avisar(
            "Campo de rótulo 'seq_id' não existe no CSV. Continuando sem rótulo.",
            Qgis.Warning,
        )
        campo_rotulo = None

    aplicar_estilo_rotulo(camada_csv, campo_rotulo)

    erro, msg_erro = salvar_shp(camada_csv, shp_path)
    if erro != QgsVectorFileWriter.NoError:
        avisar(f"Erro ao salvar SHP: {msg_erro}", Qgis.Critical)
        return

    QgsProject.instance().removeMapLayer(camada_csv.id())

    camada_shp = QgsVectorLayer(shp_path, base_name, "ogr")
    if not camada_shp.isValid():
        avisar("SHP foi salvo, mas falhou ao carregar no QGIS.", Qgis.Critical)
        return

    QgsProject.instance().addMapLayer(camada_shp)
    aplicar_estilo_rotulo(camada_shp, campo_rotulo)

    if not camada_shp.startEditing():
        avisar("SHP carregado, mas não foi possível entrar em modo de edição.", Qgis.Warning)
    else:
        avisar("SHP criado e aberto em modo de edição com sucesso.", Qgis.Success)

    if "iface" in globals() and iface is not None:
        iface.setActiveLayer(camada_shp)
        iface.mapCanvas().refresh()


executar()
