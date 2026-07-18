#NOME: Remover Linhas Selecionadas Triangulo

#DESCRIÇÃO: REMOVER LINHAS SELECIONADAS POR MEDIDAS (TRIANGULO) 1) Selecione manualmente as linhas na camada alvo no QGIS. 2) Execute este script no console Python do QGIS. 3) O script remove APENAS as linhas selecionadas cujas medidas batem com os alvos.

#PRÉ-REQUISITO: Selecionar previamente as feicoes que serao processadas.


# REMOVER LINHAS SELECIONADAS POR MEDIDAS (TRIANGULO)
# Uso:
# 1) Selecione manualmente as linhas na camada alvo no QGIS.
# 2) Execute este script no console Python do QGIS.
# 3) O script remove APENAS as linhas selecionadas cujas medidas batem com os alvos.


def remover_linhas_selecionadas_triangulo():
    try:
        from qgis.core import QgsDistanceArea, QgsUnitTypes, QgsWkbTypes
        from qgis.utils import iface

        # Medidas alvo informadas (em metros)
        medidas_alvo_m = (5.182, 1.704)
        tolerancia_m = 0.08

        layer = iface.activeLayer()
        if not layer or not layer.isValid():
            print("Nenhuma camada ativa valida.")
            return False

        if QgsWkbTypes.geometryType(layer.wkbType()) != QgsWkbTypes.LineGeometry:
            print("A camada ativa nao e de linhas.")
            return False

        selecionadas = layer.selectedFeatures()
        if not selecionadas:
            print("Nenhuma linha selecionada. Selecione as linhas no mapa e rode novamente.")
            return False

        medidor = QgsDistanceArea()
        medidor.setSourceCrs(layer.crs(), layer.transformContext())
        medidor.setEllipsoid("WGS84")
        if hasattr(medidor, "setEllipsoidalMode"):
            medidor.setEllipsoidalMode(True)

        candidatos = []
        ignoradas = 0

        for feat in selecionadas:
            geom = feat.geometry()
            if not geom or geom.isEmpty():
                ignoradas += 1
                continue

            comp = medidor.measureLength(geom)
            comp_m = medidor.convertLengthMeasurement(comp, QgsUnitTypes.DistanceMeters)

            if any(abs(comp_m - alvo) <= tolerancia_m for alvo in medidas_alvo_m):
                candidatos.append((feat.id(), comp_m))

        if not candidatos:
            print("Nenhuma linha selecionada bateu com as medidas alvo.")
            return False

        if not layer.isEditable():
            if not layer.startEditing():
                print("Nao foi possivel iniciar edicao da camada.")
                return False

        removidas = 0
        for fid, _ in candidatos:
            if layer.deleteFeature(fid):
                removidas += 1

        if not layer.commitChanges():
            layer.rollBack()
            print("Falha ao salvar edicao. Alteracoes desfeitas.")
            return False

        layer.updateExtents()
        layer.triggerRepaint()

        print("Remocao concluida.")
        print(f"Selecionadas: {len(selecionadas)}")
        print(f"Removidas (medidas alvo): {removidas}")
        print(f"Ignoradas (geometria vazia): {ignoradas}")
        print(f"Medidas alvo (m): {medidas_alvo_m} | Tolerancia: {tolerancia_m}")
        return True

    except Exception as e:
        print(f"Erro: {e}")
        import traceback

        traceback.print_exc()
        return False


print("Executando removedor de linhas selecionadas por medidas...")
ok = remover_linhas_selecionadas_triangulo()
print("Finalizado com sucesso" if ok else "Finalizado com erro")
