#NOME: Inserir Rotas com pontos de referência no DXF

#DESCRIÇÃO: Importa um arquivo DXF georreferenciado utilizando pontos de referência PR1 e PR2. O script identifica os pontos PR1 e PR2 no DXF, solicita ao usuário que clique nos pontos correspondentes no mapa, e aplica uma

#PRÉ-REQUISITO: Inserir camadas PR1 e PR2 no DXF marcando os pontos de referência.


# IMPORTADOR DXF COM GEOREFERENCIAMENTO POR PR1/PR2 (LINHAS QUADRAS)
# Seleciona DXF, identifica PR1/PR2 e gera camada de linhas da layer QUADRAS
# Data: Mar/2026


def processar_dxf_quadras_linhas():
    """
    Fluxo:
    1) Seleciona arquivo DXF
    2) Carrega camada DXF (entities)
    3) Encontra pontos de referencia no DXF (Layer = PR1 e PR2)
    4) Filtra Layer = QUADRAS e prepara geometrias de linha
    5) Solicita 2 cliques no mapa (destino PR1 e PR2)
    6) Aplica transformacao com translacao + rotacao + escala livre
    7) Salva shapefile de linhas ajustadas na pasta SHAPES e adiciona ao projeto
    """

    print("INICIANDO GEOREFERENCIADOR DXF (PR1/PR2) - LINHAS QUADRAS")
    print("=" * 70)

    try:
        import math
        from datetime import datetime
        from pathlib import Path

        from qgis.PyQt.QtCore import Qt, QEventLoop, pyqtSignal
        from qgis.PyQt.QtGui import QTransform, QColor
        from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox
        from qgis.gui import QgsMapToolEmitPoint
        from qgis.core import (
            Qgis,
            QgsFeature,
            QgsField,
            QgsGeometry,
            QgsPointXY,
            QgsProject,
            QgsVectorFileWriter,
            QgsVectorLayer,
            QgsCoordinateReferenceSystem,
            QgsWkbTypes,
            QgsPalLayerSettings,
            QgsTextFormat,
            QgsTextBufferSettings,
            QgsVectorLayerSimpleLabeling,
        )
        from qgis.utils import iface

        class CapturarUmPontoTool(QgsMapToolEmitPoint):
            pontoClicado = pyqtSignal(QgsPointXY)
            cancelado = pyqtSignal()

            def canvasReleaseEvent(self, event):
                if event.button() == Qt.RightButton:
                    self.cancelado.emit()
                    return

                ponto = self.toMapCoordinates(event.pos())
                self.pontoClicado.emit(QgsPointXY(ponto))

            def keyPressEvent(self, event):
                if event.key() == Qt.Key_Escape:
                    self.cancelado.emit()
                else:
                    super().keyPressEvent(event)

        def _normalizar(valor):
            if valor is None:
                return ""
            return str(valor).strip().upper()

        def _carregar_dxf(dxf_file, nome_base):
            uris_teste = [
                f"{dxf_file}|layername=entities",
                dxf_file,
                f"{dxf_file}|layername=entities|geometrytype=LineString",
                f"{dxf_file}|geometrytype=LineString",
                f"{dxf_file}|layername=entities|geometrytype=MultiLineString",
                f"{dxf_file}|geometrytype=MultiLineString",
                f"{dxf_file}|layername=entities|geometrytype=Polygon",
                f"{dxf_file}|geometrytype=Polygon",
                f"{dxf_file}|layername=entities|geometrytype=Point",
            ]

            for i, uri in enumerate(uris_teste, 1):
                print(f"   Tentativa {i}: {uri}")
                camada_teste = QgsVectorLayer(uri, f"DXF_{nome_base}", "ogr")
                if camada_teste.isValid() and camada_teste.featureCount() > 0:
                    print(f"   DXF carregado ({camada_teste.featureCount()} feicoes)")
                    return camada_teste

            return None

        def _campo_layer(camada):
            campos = [f.name() for f in camada.fields()]
            for nome in ["Layer", "layer", "LAYER", "LayerName", "layername"]:
                if nome in campos:
                    return nome
            return None

        def _ponto_da_geometria(geom):
            if not geom or geom.isEmpty():
                return None

            if QgsWkbTypes.geometryType(geom.wkbType()) == QgsWkbTypes.PointGeometry:
                if geom.isMultipart():
                    pontos = geom.asMultiPoint()
                    return QgsPointXY(pontos[0]) if pontos else None
                return QgsPointXY(geom.asPoint())

            centroide = geom.centroid()
            if not centroide or centroide.isEmpty():
                return None
            return QgsPointXY(centroide.asPoint())

        def _obter_ponto_referencia(camada, nome_ref, campo_layer):
            pontos = []
            alvo = _normalizar(nome_ref)

            for feat in camada.getFeatures():
                valor_layer = _normalizar(feat.attribute(campo_layer)) if campo_layer else ""
                if valor_layer != alvo:
                    continue

                ponto = _ponto_da_geometria(feat.geometry())
                if ponto:
                    pontos.append(ponto)

            if not pontos:
                return None, 0

            media_x = sum(p.x() for p in pontos) / len(pontos)
            media_y = sum(p.y() for p in pontos) / len(pontos)
            return QgsPointXY(media_x, media_y), len(pontos)

        def _montar_campos_destino(camada_origem):
            campos_destino = []
            mapa_origem_destino = {}

            for field in camada_origem.fields():
                nome_origem = field.name()

                if nome_origem.lower() == "text":
                    if "seq_id" not in mapa_origem_destino:
                        campo_seq_id = QgsField(
                            "seq_id",
                            field.type(),
                            field.typeName(),
                            field.length(),
                            field.precision(),
                        )
                        campos_destino.append(campo_seq_id)
                        mapa_origem_destino["seq_id"] = nome_origem
                    continue

                campos_destino.append(field)
                mapa_origem_destino[nome_origem] = nome_origem

            return campos_destino, mapa_origem_destino

        def _poligono_para_linha(geom):
            if not geom or geom.isEmpty():
                return None

            linhas = []

            if geom.isMultipart():
                multipoligono = geom.asMultiPolygon()
                for poligono in multipoligono:
                    for anel in poligono:
                        if len(anel) >= 2:
                            linhas.append([QgsPointXY(pt) for pt in anel])
            else:
                poligono = geom.asPolygon()
                for anel in poligono:
                    if len(anel) >= 2:
                        linhas.append([QgsPointXY(pt) for pt in anel])

            if not linhas:
                return None

            if len(linhas) == 1:
                return QgsGeometry.fromPolylineXY(linhas[0])

            return QgsGeometry.fromMultiPolylineXY(linhas)

        def _quebrar_em_linhas_simples(geom):
            if not geom or geom.isEmpty():
                return []

            linhas = []
            if geom.isMultipart():
                for parte in geom.asMultiPolyline():
                    if len(parte) >= 2:
                        linhas.append(QgsGeometry.fromPolylineXY(parte))
            else:
                parte = geom.asPolyline()
                if len(parte) >= 2:
                    linhas.append(QgsGeometry.fromPolylineXY(parte))

            return [g for g in linhas if g and not g.isEmpty()]

        def _chave_ponto(pt, tolerancia):
            return (int(round(pt.x() / tolerancia)), int(round(pt.y() / tolerancia)))

        def _extremos_linha(geom):
            if not geom or geom.isEmpty():
                return None, None

            if geom.isMultipart():
                linhas = geom.asMultiPolyline()
                if not linhas:
                    return None, None
                parte = max(linhas, key=lambda linha: len(linha))
            else:
                parte = geom.asPolyline()

            if not parte or len(parte) < 2:
                return None, None

            return QgsPointXY(parte[0]), QgsPointXY(parte[-1])

        def _inverter_geometria_linha(geom):
            if not geom or geom.isEmpty():
                return None

            if geom.isMultipart():
                linhas = geom.asMultiPolyline()
                invertidas = []
                for linha in linhas:
                    if len(linha) >= 2:
                        invertidas.append(list(reversed(linha)))
                if not invertidas:
                    return None
                return QgsGeometry.fromMultiPolylineXY(invertidas)

            linha = geom.asPolyline()
            if not linha or len(linha) < 2:
                return None
            return QgsGeometry.fromPolylineXY(list(reversed(linha)))

        def _limpar_linhas_curtas_em_componentes(camada, tolerancia):
            if not camada or not camada.isValid():
                return 0

            info = {}
            no_para_fids = {}

            for feat in camada.getFeatures():
                geom = feat.geometry()
                if not geom or geom.isEmpty():
                    continue

                p_ini, p_fim = _extremos_linha(geom)
                if not p_ini or not p_fim:
                    continue

                chave_ini = _chave_ponto(p_ini, tolerancia)
                chave_fim = _chave_ponto(p_fim, tolerancia)
                comprimento = geom.length()

                info[feat.id()] = {
                    "len": comprimento,
                    "n1": chave_ini,
                    "n2": chave_fim,
                }

                no_para_fids.setdefault(chave_ini, set()).add(feat.id())
                no_para_fids.setdefault(chave_fim, set()).add(feat.id())

            if not info:
                return 0

            comprimentos_globais = sorted(v["len"] for v in info.values())
            mediana_global = comprimentos_globais[len(comprimentos_globais) // 2]
            limite_curta_global = max(0.30, mediana_global * 0.22)
            limite_tri_global = max(0.40, mediana_global * 0.45)

            adj = {fid: set() for fid in info.keys()}
            for fids in no_para_fids.values():
                fids_lista = list(fids)
                for i in range(len(fids_lista)):
                    fid_a = fids_lista[i]
                    for j in range(i + 1, len(fids_lista)):
                        fid_b = fids_lista[j]
                        adj[fid_a].add(fid_b)
                        adj[fid_b].add(fid_a)

            visitados = set()
            remover = set()

            # Detecta triangulos de seta (3 segmentos) ligados a uma linha maior.
            candidatos_triangulo = {
                fid
                for fid, d in info.items()
                if d["len"] <= (limite_tri_global * 2.5)
            }

            pares_para_fids = {}
            incidentes_candidatos = {}
            for fid in candidatos_triangulo:
                n1 = info[fid]["n1"]
                n2 = info[fid]["n2"]
                chave_par = frozenset((n1, n2))
                pares_para_fids.setdefault(chave_par, []).append(fid)
                incidentes_candidatos.setdefault(n1, set()).add(fid)
                incidentes_candidatos.setdefault(n2, set()).add(fid)

            triangulos_detectados = set()
            for fid_ab in candidatos_triangulo:
                a = info[fid_ab]["n1"]
                b = info[fid_ab]["n2"]

                for fid_bc in incidentes_candidatos.get(b, set()):
                    if fid_bc == fid_ab:
                        continue

                    c = info[fid_bc]["n2"] if info[fid_bc]["n1"] == b else info[fid_bc]["n1"]
                    if c == a or c == b:
                        continue

                    chave_ca = frozenset((c, a))
                    if chave_ca not in pares_para_fids:
                        continue

                    fid_ca = min(pares_para_fids[chave_ca], key=lambda f: info[f]["len"])
                    tri = tuple(sorted((fid_ab, fid_bc, fid_ca)))
                    if len(set(tri)) == 3:
                        triangulos_detectados.add(tri)

            triagens_seta = 0
            for tri in triangulos_detectados:
                tri_set = set(tri)
                tri_nos = set()
                tri_lens = []

                for f in tri:
                    tri_nos.add(info[f]["n1"])
                    tri_nos.add(info[f]["n2"])
                    tri_lens.append(info[f]["len"])

                maior_tri = max(tri_lens)
                longas_externas = []

                for no in tri_nos:
                    externos = no_para_fids.get(no, set()) - tri_set
                    for fe in externos:
                        if fe in info:
                            longas_externas.append(info[fe]["len"])

                if not longas_externas:
                    continue

                maior_externa = max(longas_externas)

                # Assinatura de seta: triangulo menor conectado a linha mais longa.
                if maior_tri <= max(limite_tri_global, maior_externa * 0.70):
                    remover.update(tri_set)
                    triagens_seta += 1

            for fid in info.keys():
                if fid in visitados:
                    continue

                fila = [fid]
                visitados.add(fid)
                componente = []

                while fila:
                    atual = fila.pop()
                    componente.append(atual)
                    for viz in adj[atual]:
                        if viz not in visitados:
                            visitados.add(viz)
                            fila.append(viz)

                if len(componente) <= 3:
                    continue

                comprimentos = sorted(info[f]["len"] for f in componente)
                mediana = comprimentos[len(comprimentos) // 2]
                limite_curta = max(limite_curta_global, mediana * 0.22)
                limite_curta_trinca = max(0.40, mediana * 0.40)

                componente_set = set(componente)
                nos_componente = set()
                for f in componente:
                    nos_componente.add(info[f]["n1"])
                    nos_componente.add(info[f]["n2"])

                # Regra explicita para ponta de seta:
                # se existir um no com linha principal + pelo menos 3 linhas curtas,
                # remove as 3 linhas curtas dessa extremidade.
                for no in nos_componente:
                    incidentes = [
                        f
                        for f in no_para_fids.get(no, set())
                        if f in componente_set and f not in remover
                    ]
                    if len(incidentes) < 4:
                        continue

                    curtas = [f for f in incidentes if info[f]["len"] <= limite_curta_trinca]
                    longas = [f for f in incidentes if info[f]["len"] > limite_curta_trinca]
                    if len(curtas) < 3 or not longas:
                        continue

                    candidatos = []
                    for f in curtas:
                        outro_no = info[f]["n2"] if info[f]["n1"] == no else info[f]["n1"]
                        grau_outro_no = len(no_para_fids.get(outro_no, set()))
                        candidatos.append((grau_outro_no, info[f]["len"], f))

                    candidatos.sort(key=lambda x: (x[0], x[1]))
                    preferenciais = [f for grau, _, f in candidatos if grau <= 2]

                    if len(preferenciais) >= 3:
                        remover.update(preferenciais[:3])
                    else:
                        remover.update([f for _, _, f in candidatos[:3]])

                for f in componente:
                    if f in remover:
                        continue

                    comp = info[f]["len"]
                    if comp > limite_curta:
                        continue

                    deg1 = len(no_para_fids.get(info[f]["n1"], set()))
                    deg2 = len(no_para_fids.get(info[f]["n2"], set()))

                    if deg1 >= 3 or deg2 >= 3 or (deg1 >= 2 and deg2 >= 2):
                        remover.add(f)

            if not remover:
                return 0

            if not camada.startEditing():
                return 0

            for fid in remover:
                camada.deleteFeature(fid)

            if not camada.commitChanges():
                camada.rollBack()
                return 0

            camada.updateExtents()
            if triagens_seta:
                print(f"Triangulos de seta removidos: {triagens_seta}")
            return len(remover)

        def _inverter_sentido_de_todas_as_linhas(camada):
            if not camada or not camada.isValid():
                return 0

            if not camada.startEditing():
                return 0

            invertidas = 0
            for feat in camada.getFeatures():
                geom = feat.geometry()
                nova_geom = _inverter_geometria_linha(geom)
                if not nova_geom or nova_geom.isEmpty():
                    continue

                if camada.changeGeometry(feat.id(), nova_geom):
                    invertidas += 1

            if not camada.commitChanges():
                camada.rollBack()
                return 0

            camada.updateExtents()
            return invertidas

        def _remover_linhas_menores_que(camada, comprimento_minimo):
            if not camada or not camada.isValid():
                return 0

            candidatos = []
            for feat in camada.getFeatures():
                geom = feat.geometry()
                if not geom or geom.isEmpty():
                    continue
                if geom.length() < comprimento_minimo:
                    candidatos.append(feat.id())

            if not candidatos:
                return 0

            if not camada.startEditing():
                return 0

            for fid in candidatos:
                camada.deleteFeature(fid)

            if not camada.commitChanges():
                camada.rollBack()
                return 0

            camada.updateExtents()
            return len(candidatos)

        def _remover_linhas_medidas_conectadas(camada, medidas_alvo, tolerancia_medida, tolerancia_topologica):
            if not camada or not camada.isValid():
                return 0

            def _indice_medida_alvo(comp):
                for idx, medida in enumerate(medidas_alvo):
                    if abs(comp - medida) <= tolerancia_medida:
                        return idx
                return -1

            info = {}
            no_para_fids = {}

            for feat in camada.getFeatures():
                geom = feat.geometry()
                if not geom or geom.isEmpty():
                    continue

                p_ini, p_fim = _extremos_linha(geom)
                if not p_ini or not p_fim:
                    continue

                comp = geom.length()
                n1 = _chave_ponto(p_ini, tolerancia_topologica)
                n2 = _chave_ponto(p_fim, tolerancia_topologica)

                info[feat.id()] = {
                    "len": comp,
                    "n1": n1,
                    "n2": n2,
                    "idx_alvo": _indice_medida_alvo(comp),
                }

                no_para_fids.setdefault(n1, set()).add(feat.id())
                no_para_fids.setdefault(n2, set()).add(feat.id())

            if not info:
                return 0

            adj = {fid: set() for fid in info.keys()}
            for fids_no in no_para_fids.values():
                fids_lista = list(fids_no)
                for i in range(len(fids_lista)):
                    fid_a = fids_lista[i]
                    for j in range(i + 1, len(fids_lista)):
                        fid_b = fids_lista[j]
                        adj[fid_a].add(fid_b)
                        adj[fid_b].add(fid_a)

            remover = set()
            componentes_removidos = 0
            visitados = set()

            for fid_inicial in info.keys():
                if fid_inicial in visitados:
                    continue

                fila_comp = [fid_inicial]
                visitados.add(fid_inicial)
                componente = []

                while fila_comp:
                    atual = fila_comp.pop()
                    componente.append(atual)
                    for viz in adj[atual]:
                        if viz not in visitados:
                            visitados.add(viz)
                            fila_comp.append(viz)

                if not componente:
                    continue

                idxs_alvo = {info[f]["idx_alvo"] for f in componente if info[f]["idx_alvo"] != -1}
                if len(idxs_alvo) < len(medidas_alvo):
                    continue

                # Se a componente e pequena e contem as duas medidas-alvo,
                # remove tudo para eliminar tambem a linha fina (rabo da seta).
                if len(componente) <= 20:
                    remover.update(componente)
                    componentes_removidos += 1
                    continue

                # Componente grande: remove ao menos as linhas-alvo e ramais pendurados conectados a elas.
                alvo_comp = {f for f in componente if info[f]["idx_alvo"] != -1}
                remover.update(alvo_comp)

                for f in componente:
                    if f in alvo_comp:
                        continue

                    d = info[f]
                    toca_alvo = False
                    for no in (d["n1"], d["n2"]):
                        if len(no_para_fids.get(no, set()) & alvo_comp) > 0:
                            toca_alvo = True
                            break

                    if not toca_alvo:
                        continue

                    deg1 = len(no_para_fids.get(d["n1"], set()))
                    deg2 = len(no_para_fids.get(d["n2"], set()))
                    if deg1 == 1 or deg2 == 1:
                        remover.add(f)

            # Expande dentro da vizinhanca de removidos para pegar cadeias de linha fina coladas.
            fila = list(remover)
            while fila:
                atual = fila.pop()
                d = info.get(atual)
                if not d:
                    continue
                for no in (d["n1"], d["n2"]):
                    for viz in no_para_fids.get(no, set()):
                        if viz not in remover and info[viz]["len"] <= max(medidas_alvo) * 2.0:
                            remover.add(viz)
                            fila.append(viz)

            if not remover:
                return 0

            if not camada.startEditing():
                return 0

            for fid in remover:
                camada.deleteFeature(fid)

            if not camada.commitChanges():
                camada.rollBack()
                return 0

            camada.updateExtents()
            if componentes_removidos:
                print(f"Componentes de seta removidos: {componentes_removidos}")
            return len(remover)

        def _criar_camada_linhas_quadras(camada, campo_layer, crs_saida, nome_camada):
            authid = crs_saida.authid() if crs_saida and crs_saida.isValid() else "EPSG:31983"
            camada_linhas = QgsVectorLayer(f"MultiLineString?crs={authid}", nome_camada, "memory")

            if not camada_linhas.isValid():
                return None, 0, 0, 0

            prov = camada_linhas.dataProvider()
            campos_destino, mapa_origem_destino = _montar_campos_destino(camada)
            prov.addAttributes(campos_destino)
            camada_linhas.updateFields()

            total_quadras = 0
            convertidas = 0
            ignoradas_tipo = 0

            for feat in camada.getFeatures():
                if _normalizar(feat.attribute(campo_layer)) != "ROTAS":
                    continue

                total_quadras += 1
                geom = feat.geometry()

                if not geom or geom.isEmpty():
                    continue

                tipo = QgsWkbTypes.geometryType(geom.wkbType())

                if tipo == QgsWkbTypes.LineGeometry:
                    geom_linha = QgsGeometry(geom)
                elif tipo == QgsWkbTypes.PolygonGeometry:
                    # Se vier poligono no DXF, usa o contorno para manter saida em linhas.
                    geom_linha = _poligono_para_linha(geom)
                else:
                    ignoradas_tipo += 1
                    continue

                if not geom_linha or geom_linha.isEmpty():
                    continue

                partes_linha = _quebrar_em_linhas_simples(geom_linha)
                if not partes_linha:
                    continue

                for parte_geom in partes_linha:
                    nova = QgsFeature(camada_linhas.fields())
                    nova.setGeometry(parte_geom)

                    for field in camada_linhas.fields():
                        nome_destino = field.name()
                        nome_origem = mapa_origem_destino.get(nome_destino, nome_destino)
                        if feat.fieldNameIndex(nome_origem) != -1:
                            nova.setAttribute(nome_destino, feat.attribute(nome_origem))

                    prov.addFeature(nova)
                    convertidas += 1

            camada_linhas.updateExtents()
            return camada_linhas, total_quadras, convertidas, ignoradas_tipo

        def _capturar_ponto(canvas, titulo, instrucao):
            loop = QEventLoop()
            resultado = {"ponto": None, "cancelado": False}

            tool = CapturarUmPontoTool(canvas)

            def _on_ponto(pt):
                resultado["ponto"] = pt
                loop.quit()

            def _on_cancelado():
                resultado["cancelado"] = True
                loop.quit()

            tool.pontoClicado.connect(_on_ponto)
            tool.cancelado.connect(_on_cancelado)

            ferramenta_anterior = canvas.mapTool()
            canvas.setMapTool(tool)

            iface.messageBar().pushMessage(
                "Georreferenciar DXF",
                instrucao,
                level=Qgis.Info,
                duration=8,
            )

            QMessageBox.information(
                None,
                titulo,
                f"{instrucao}\n\nClique ESQUERDO para confirmar.\nClique DIREITO ou ESC para cancelar.",
            )

            loop.exec_()

            canvas.unsetMapTool(tool)
            if ferramenta_anterior and ferramenta_anterior != tool:
                canvas.setMapTool(ferramenta_anterior)

            if resultado["cancelado"]:
                return None

            return resultado["ponto"]

        print("PASSO 1: Selecionar arquivo DXF")
        dxf_file, _ = QFileDialog.getOpenFileName(
            None,
            "Selecionar arquivo DXF",
            "",
            "Arquivos DXF (*.dxf);;Todos os Arquivos (*)",
        )

        if not dxf_file:
            print("Processo cancelado: nenhum arquivo selecionado")
            return False

        dxf_path = Path(dxf_file)
        print(f"Arquivo: {dxf_path.name}")

        print("\nPASSO 2: Carregar DXF e filtrar Layer = QUADRAS")
        dxf_layer = _carregar_dxf(dxf_file, dxf_path.stem)
        if not dxf_layer:
            print("Nao foi possivel carregar o DXF")
            return False

        project = QgsProject.instance()
        crs_projeto = project.crs()
        if not crs_projeto.isValid():
            crs_projeto = QgsCoordinateReferenceSystem("EPSG:31983")
        dxf_layer.setCrs(crs_projeto)

        campo_layer = _campo_layer(dxf_layer)
        if not campo_layer:
            print("Campo de layer nao encontrado no DXF (esperado: Layer)")
            return False

        print(f"Campo layer detectado: {campo_layer}")

        camada_linhas_quadras, total_quadras, convertidas, ignoradas_tipo = _criar_camada_linhas_quadras(
            dxf_layer,
            campo_layer,
            crs_projeto,
            f"{dxf_path.stem}_QUADRAS_LINHAS",
        )

        if total_quadras == 0:
            print("Nenhuma feicao encontrada com Layer = 'QUADRAS' no DXF")
            return False

        if convertidas == 0 or not camada_linhas_quadras:
            print("Foram encontradas feicoes 'QUADRAS', mas nenhuma geometria valida para linhas")
            return False

        print(f"Feicoes Layer 'QUADRAS' encontradas: {total_quadras}")
        print(f"Geometrias QUADRAS convertidas para linha: {convertidas}")
        if ignoradas_tipo:
            print(f"Geometrias ignoradas por tipo nao suportado: {ignoradas_tipo}")

        origem_pr1, qtd_pr1 = _obter_ponto_referencia(dxf_layer, "PR1", campo_layer)
        origem_pr2, qtd_pr2 = _obter_ponto_referencia(dxf_layer, "PR2", campo_layer)

        if not origem_pr1 or not origem_pr2:
            print("Nao foi possivel localizar PR1 e PR2 no DXF")
            print("Verifique se ha feicoes com Layer = 'PR1' e Layer = 'PR2'")
            return False

        print(f"PR1 no DXF: {qtd_pr1} feicao(oes) | ponto medio ({origem_pr1.x():.3f}, {origem_pr1.y():.3f})")
        print(f"PR2 no DXF: {qtd_pr2} feicao(oes) | ponto medio ({origem_pr2.x():.3f}, {origem_pr2.y():.3f})")

        print("\nPASSO 3: Capturar referencias no mapa")
        canvas = iface.mapCanvas()

        destino_pr1 = _capturar_ponto(
            canvas,
            "Referencia PR1",
            "Clique no ponto do mapa que representa o PR1.",
        )
        if not destino_pr1:
            print("Processo cancelado na captura do PR1")
            return False

        print(f"PR1 destino: ({destino_pr1.x():.3f}, {destino_pr1.y():.3f})")

        destino_pr2 = _capturar_ponto(
            canvas,
            "Referencia PR2",
            "Clique no ponto do mapa que representa o PR2.",
        )
        if not destino_pr2:
            print("Processo cancelado na captura do PR2")
            return False

        print(f"PR2 destino: ({destino_pr2.x():.3f}, {destino_pr2.y():.3f})")

        print("\nPASSO 4: Calcular transformacao (translacao + rotacao + escala livre)")
        dx_origem = origem_pr2.x() - origem_pr1.x()
        dy_origem = origem_pr2.y() - origem_pr1.y()
        dx_destino = destino_pr2.x() - destino_pr1.x()
        dy_destino = destino_pr2.y() - destino_pr1.y()

        dist_origem = math.hypot(dx_origem, dy_origem)
        dist_destino = math.hypot(dx_destino, dy_destino)

        if dist_origem == 0 or dist_destino == 0:
            print("Distancia invalida entre PR1 e PR2 para calcular transformacao")
            return False

        escala = dist_destino / dist_origem
        angulo = math.atan2(dy_destino, dx_destino) - math.atan2(dy_origem, dx_origem)

        cos_a = math.cos(angulo)
        sin_a = math.sin(angulo)

        a = escala * cos_a
        b = -escala * sin_a
        d = escala * sin_a
        e = escala * cos_a

        tx = destino_pr1.x() - (a * origem_pr1.x() + b * origem_pr1.y())
        ty = destino_pr1.y() - (d * origem_pr1.x() + e * origem_pr1.y())

        matriz = QTransform(a, d, b, e, tx, ty)

        print(f"Escala aplicada (livre): {escala:.6f}")
        print(f"Rotacao aplicada: {math.degrees(angulo):.4f} graus")

        print("\nPASSO 5: Aplicar transformacao nas linhas QUADRAS")
        if not camada_linhas_quadras.startEditing():
            print("Nao foi possivel iniciar edicao da camada de linhas")
            return False

        erros_transformacao = 0
        total_transformadas = 0

        for feat in camada_linhas_quadras.getFeatures():
            total_transformadas += 1
            geom = feat.geometry()
            if not geom or geom.isEmpty():
                continue

            retorno = geom.transform(matriz)
            if retorno != 0:
                erros_transformacao += 1
                continue

            camada_linhas_quadras.changeGeometry(feat.id(), geom)

        if not camada_linhas_quadras.commitChanges():
            camada_linhas_quadras.rollBack()
            print("Erro ao salvar geometrias transformadas")
            return False

        print(f"Linhas processadas: {total_transformadas}")
        if erros_transformacao:
            print(f"Linhas com erro de transformacao: {erros_transformacao}")

        print("\nPASSO 6: Limpar linhas curtas conectadas (pontas de seta)")
        ext = camada_linhas_quadras.extent()
        diag = math.hypot(ext.width(), ext.height()) if ext else 0
        tolerancia_topologica = max(0.01, diag * 1e-6)
        removidas_curtas = _limpar_linhas_curtas_em_componentes(camada_linhas_quadras, tolerancia_topologica)
        print(f"Linhas curtas removidas: {removidas_curtas}")

        print("\nPASSO 7: Inverter sentido das linhas")
        total_invertidas = _inverter_sentido_de_todas_as_linhas(camada_linhas_quadras)
        print(f"Linhas com sentido invertido: {total_invertidas}")

        print("\nPASSO 8: Remover linhas conectadas com medidas 2.480m e 0.815m")
        ext = camada_linhas_quadras.extent()
        diag = math.hypot(ext.width(), ext.height()) if ext else 0
        tolerancia_topologica = max(0.01, diag * 1e-6)
        removidas_medidas = _remover_linhas_medidas_conectadas(
            camada_linhas_quadras,
            medidas_alvo=(2.480, 0.815),
            tolerancia_medida=0.02,
            tolerancia_topologica=tolerancia_topologica,
        )
        print(f"Linhas removidas por medida conectada: {removidas_medidas}")

        print("\nPASSO 9: Remover linhas finais com menos de 1 metro")
        removidas_menor_1m = _remover_linhas_menores_que(camada_linhas_quadras, 1.0)
        print(f"Linhas removidas (< 1m): {removidas_menor_1m}")

        print("\nPASSO 10: Salvar shapefile ajustado")
        nome_saida = f"{dxf_path.stem}_QUADRAS_LINHAS_AJUSTADO_PR1_PR2"
        camada_linhas_quadras.setName(nome_saida)

        output_dir = dxf_path.parent / "SHAPES"
        output_dir.mkdir(exist_ok=True)

        shp_path = output_dir / f"{nome_saida}.shp"
        if shp_path.exists():
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            shp_path = output_dir / f"{nome_saida}_{stamp}.shp"

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        options.fileEncoding = "UTF-8"

        erro = QgsVectorFileWriter.writeAsVectorFormatV3(
            camada_linhas_quadras,
            str(shp_path),
            project.transformContext(),
            options,
        )

        if erro[0] != QgsVectorFileWriter.NoError:
            print(f"Erro ao salvar shapefile: {erro[1]}")
            return False

        camada_final = QgsVectorLayer(str(shp_path), nome_saida, "ogr")
        if not camada_final.isValid():
            print("Shapefile salvo, mas falhou ao recarregar no QGIS")
            return False

        camada_final.setCrs(crs_projeto)
        project.addMapLayer(camada_final)

        if camada_final.fields().indexFromName("seq_id") != -1:
            settings = QgsPalLayerSettings()
            settings.enabled = True
            settings.fieldName = "seq_id"

            text_format = QgsTextFormat()
            text_format.setColor(QColor("#FFFFFF"))

            buffer_settings = QgsTextBufferSettings()
            buffer_settings.setEnabled(True)
            buffer_settings.setColor(QColor("#0000FF"))
            buffer_settings.setSize(1.0)
            text_format.setBuffer(buffer_settings)

            settings.setFormat(text_format)
            camada_final.setLabeling(QgsVectorLayerSimpleLabeling(settings))
            camada_final.setLabelsEnabled(True)
            camada_final.triggerRepaint()
            print("Rotulagem aplicada: campo 'seq_id' | texto branco | buffer azul")
        else:
            print("Campo 'seq_id' nao encontrado apos exportacao")

        canvas.setExtent(camada_final.extent())
        canvas.refresh()

        print("\nPROCESSO CONCLUIDO COM SUCESSO")
        print("=" * 70)
        print(f"Arquivo processado: {dxf_path.name}")
        print(f"Camada final: {camada_final.name()}")
        print(f"Linhas exibidas (Layer QUADRAS): {camada_final.featureCount()}")
        print(f"Shapefile: {shp_path}")
        print("A camada exibida foi filtrada para Layer = 'QUADRAS'")
        print("Campo 'Text' foi renomeado para 'seq_id' quando existente")
        print("Rotulos: seq_id com texto branco e buffer azul")
        print("A escala foi aplicada de forma livre para encaixar PR1/PR2")
        print("O sentido das linhas foi invertido ao final do processo")
        print("Linhas muito curtas em grupos conectados grandes foram removidas")
        print("Linhas conectadas com medidas 2.480m e 0.815m foram removidas")
        print("Linhas com comprimento menor que 1 metro foram removidas ao final")

        return True

    except Exception as e:
        print(f"ERRO NO PROCESSO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


print("INICIANDO GEOREFERENCIADOR DXF PR1/PR2 PARA QUADRAS (LINHAS)...")
resultado = processar_dxf_quadras_linhas()

if resultado:
    print("Finalizado com sucesso")
else:
    print("Finalizado com erro")
