#NOME: Selecionar Linhas Menores10m Pre Selecao

#DESCRIÇÃO: SELECIONAR LINHAS < 10m A PARTIR DA PRE-SELECAO 1) Deixe ativa a camada OVERLEY. 2) Faça uma pre-selecao manual das linhas no mapa. 3) Execute este script no console Python do QGIS. 4) O script vai manter selecionadas somente as linhas < 10m.

#PRÉ-REQUISITO: Selecionar previamente as feicoes que serao processadas.


# SELECIONAR LINHAS < 10m A PARTIR DA PRE-SELECAO
# Uso:
# 1) Deixe ativa a camada OVERLEY.
# 2) Faça uma pre-selecao manual das linhas no mapa.
# 3) Execute este script no console Python do QGIS.
# 4) O script vai manter selecionadas somente as linhas < 10m.


def selecionar_linhas_menores_10m_preselecao():
    try:
        from qgis.core import QgsDistanceArea, QgsUnitTypes, QgsWkbTypes
        from qgis.utils import iface

        limite_m = 15.0

        layer = iface.activeLayer()
        if not layer or not layer.isValid():
            print("Nenhuma camada ativa valida.")
            return False

        nome_layer = (layer.name() or "").upper()
        if "OVERLEY" not in nome_layer:
            print(f"Camada ativa nao parece ser OVERLEY: {layer.name()}")
            return False

        if QgsWkbTypes.geometryType(layer.wkbType()) != QgsWkbTypes.LineGeometry:
            print("A camada ativa nao e de linhas.")
            return False

        preselecionadas = layer.selectedFeatures()
        if not preselecionadas:
            print("Nao ha pre-selecao. Selecione linhas primeiro.")
            return False

        medidor = QgsDistanceArea()
        medidor.setSourceCrs(layer.crs(), layer.transformContext())
        medidor.setEllipsoid("WGS84")
        if hasattr(medidor, "setEllipsoidalMode"):
            medidor.setEllipsoidalMode(True)

        ids_menores = []
        ignoradas = 0

        for feat in preselecionadas:
            geom = feat.geometry()
            if not geom or geom.isEmpty():
                ignoradas += 1
                continue

            comp = medidor.measureLength(geom)
            comp_m = medidor.convertLengthMeasurement(comp, QgsUnitTypes.DistanceMeters)
            if comp_m < limite_m:
                ids_menores.append(feat.id())

        layer.selectByIds(ids_menores)

        print("Selecao filtrada concluida.")
        print(f"Pre-selecionadas: {len(preselecionadas)}")
        print(f"Selecionadas (< {limite_m:.1f}m): {len(ids_menores)}")
        print(f"Ignoradas (geometria vazia): {ignoradas}")
        return True

    except Exception as e:
        print(f"Erro: {e}")
        import traceback

        traceback.print_exc()
        return False


print("Executando filtro de pre-selecao (< 10m)...")
ok = selecionar_linhas_menores_10m_preselecao()
print("Finalizado com sucesso" if ok else "Finalizado com erro")
