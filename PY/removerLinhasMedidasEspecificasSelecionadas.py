#NOME: Remover Linhas Medidas Especificas Selecionadas

#DESCRIÇÃO: Executa a rotina 'Remover Linhas Medidas Especificas Selecionadas', removendo feicoes ou inconsistencias de acordo com os criterios implementados.

#PRÉ-REQUISITO: Selecionar previamente as feicoes que serao processadas.


from qgis.PyQt.QtWidgets import QInputDialog, QMessageBox
from qgis.core import QgsProject, QgsWkbTypes, QgsPointXY


MEDIDAS_ALVO = (2.480, 0.815)
TOLERANCIA_MEDIDA = 0.01
TOLERANCIA_TOPOLOGICA = 0.02


def _chave_ponto(pt, tolerancia):
    return (int(round(pt.x() / tolerancia)), int(round(pt.y() / tolerancia)))


def _extremos_linha(geom):
    if not geom or geom.isEmpty():
        return None, None

    if geom.isMultipart():
        linhas = geom.asMultiPolyline()
        if not linhas:
            return None, None
        parte = max(linhas, key=lambda l: len(l))
    else:
        parte = geom.asPolyline()

    if not parte or len(parte) < 2:
        return None, None

    return QgsPointXY(parte[0]), QgsPointXY(parte[-1])


def _indice_medida_alvo(comprimento):
    for idx, medida in enumerate(MEDIDAS_ALVO):
        if abs(comprimento - medida) <= TOLERANCIA_MEDIDA:
            return idx
    return -1


def remover_linhas_medidas_conectadas():
    nome_camada, ok = QInputDialog.getText(
        None,
        "Remover Linhas por Medida",
        "Digite o nome da camada de linhas:",
        text="OVERLEY",
    )

    if not ok or not nome_camada.strip():
        print("Operacao cancelada.")
        return

    layers = QgsProject.instance().mapLayersByName(nome_camada.strip())
    if not layers:
        QMessageBox.warning(None, "Camada nao encontrada", f"Camada '{nome_camada}' nao encontrada.")
        print(f"Camada '{nome_camada}' nao encontrada.")
        return

    layer = layers[0]
    if QgsWkbTypes.geometryType(layer.wkbType()) != QgsWkbTypes.LineGeometry:
        QMessageBox.warning(None, "Tipo invalido", "A camada informada nao e de linhas.")
        print("A camada informada nao e de linhas.")
        return

    selecionadas = list(layer.selectedFeatures())
    if not selecionadas:
        QMessageBox.information(None, "Sem selecao", "Selecione as linhas antes de executar.")
        print("Nenhuma feicao selecionada.")
        return

    info = {}
    no_para_ids = {}

    for feat in selecionadas:
        geom = feat.geometry()
        if not geom or geom.isEmpty():
            continue

        p_ini, p_fim = _extremos_linha(geom)
        if not p_ini or not p_fim:
            continue

        comp = geom.length()
        n1 = _chave_ponto(p_ini, TOLERANCIA_TOPOLOGICA)
        n2 = _chave_ponto(p_fim, TOLERANCIA_TOPOLOGICA)

        info[feat.id()] = {
            "len": comp,
            "idx_alvo": _indice_medida_alvo(comp),
            "n1": n1,
            "n2": n2,
        }

        no_para_ids.setdefault(n1, set()).add(feat.id())
        no_para_ids.setdefault(n2, set()).add(feat.id())

    if not info:
        print("Nao foi possivel analisar as feicoes selecionadas.")
        return

    adj = {fid: set() for fid in info.keys()}
    for fids_no in no_para_ids.values():
        lista = list(fids_no)
        for i in range(len(lista)):
            a = lista[i]
            for j in range(i + 1, len(lista)):
                b = lista[j]
                adj[a].add(b)
                adj[b].add(a)

    remover = set()
    componentes_removidos = 0
    visitados = set()

    for fid_inicial in info.keys():
        if fid_inicial in visitados:
            continue

        fila = [fid_inicial]
        visitados.add(fid_inicial)
        componente = []

        while fila:
            atual = fila.pop()
            componente.append(atual)
            for viz in adj[atual]:
                if viz not in visitados:
                    visitados.add(viz)
                    fila.append(viz)

        idxs_alvo = {info[f]["idx_alvo"] for f in componente if info[f]["idx_alvo"] != -1}
        if len(idxs_alvo) < len(MEDIDAS_ALVO):
            continue

        if len(componente) <= 20:
            remover.update(componente)
            componentes_removidos += 1
            continue

        alvo_comp = {f for f in componente if info[f]["idx_alvo"] != -1}
        remover.update(alvo_comp)

        for f in componente:
            if f in alvo_comp:
                continue

            d = info[f]
            toca_alvo = False
            for no in (d["n1"], d["n2"]):
                if len(no_para_ids.get(no, set()) & alvo_comp) > 0:
                    toca_alvo = True
                    break

            if not toca_alvo:
                continue

            deg1 = len(no_para_ids.get(d["n1"], set()))
            deg2 = len(no_para_ids.get(d["n2"], set()))
            if deg1 == 1 or deg2 == 1:
                remover.add(f)

    if componentes_removidos:
        print(f"Componentes de seta removidos: {componentes_removidos}")

    if not remover:
        print("Nao foi identificado componente de seta com as medidas-alvo conectadas.")
        return

    iniciou_edicao = False
    if not layer.isEditable():
        if not layer.startEditing():
            print("Nao foi possivel iniciar edicao da camada.")
            return
        iniciou_edicao = True

    for fid in remover:
        layer.deleteFeature(fid)

    if iniciou_edicao:
        if not layer.commitChanges():
            layer.rollBack()
            print("Erro ao aplicar remocoes.")
            return
    else:
        layer.triggerRepaint()

    print(f"Camada: {layer.name()}")
    print(f"Selecionadas: {len(selecionadas)}")
    print(f"Linhas removidas (2.480m/0.815m conectadas): {len(remover)}")
    QMessageBox.information(
        None,
        "Remocao concluida",
        f"Linhas removidas: {len(remover)}\nCamada: {layer.name()}",
    )


remover_linhas_medidas_conectadas()
