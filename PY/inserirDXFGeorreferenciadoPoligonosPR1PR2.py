#NOME: Inserir Poligonos com pontos de referência no DXF

#DESCRIÇÃO: Importa um arquivo DXF georreferenciado utilizando pontos de referência PR1 e PR2. O script identifica os pontos PR1 e PR2 no DXF, solicita ao usuário que clique nos pontos correspondentes no mapa, e aplica uma

#PRÉ-REQUISITO: Inserir camadas PR1 e PR2 no DXF marcando os pontos de referência.


# IMPORTADOR DXF COM GEOREFERENCIAMENTO POR PR1/PR2 (POLIGONOS)
# Seleciona DXF, identifica PR1/PR2 e gera poligonos da layer LIMITE_ROTA
# Data: Mar/2026


def processar_dxf_limite_rota():
    """
    Fluxo:
    1) Seleciona arquivo DXF
    2) Carrega camada DXF (entities)
    3) Encontra pontos de referencia no DXF (Layer = PR1 e PR2)
    4) Filtra Layer = LIMITE_ROTA (linha/poligono) e prepara linhas de limite
    5) Solicita 2 cliques no mapa (destino PR1 e PR2)
    6) Aplica transformacao com translacao + rotacao + escala livre
    7) Polygoniza as linhas ajustadas, salva shapefile e adiciona ao projeto
    """

    print("INICIANDO GEOREFERENCIADOR DXF (PR1/PR2) - LIMITE_ROTA EM POLIGONOS")
    print("=" * 75)

    try:
        import math
        from datetime import datetime
        from pathlib import Path

        import processing
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

        def _criar_camada_linhas_limite(camada, campo_layer, crs_saida, nome_camada):
            authid = crs_saida.authid() if crs_saida and crs_saida.isValid() else "EPSG:31983"
            camada_linhas = QgsVectorLayer(f"MultiLineString?crs={authid}", nome_camada, "memory")

            if not camada_linhas.isValid():
                return None, 0, 0, 0

            prov = camada_linhas.dataProvider()
            campos_destino, mapa_origem_destino = _montar_campos_destino(camada)
            prov.addAttributes(campos_destino)
            camada_linhas.updateFields()

            total_limite = 0
            convertidas = 0
            ignoradas_tipo = 0

            for feat in camada.getFeatures():
                if _normalizar(feat.attribute(campo_layer)) != "LIMITE_ROTA":
                    continue

                total_limite += 1
                geom = feat.geometry()

                if not geom or geom.isEmpty():
                    continue

                tipo = QgsWkbTypes.geometryType(geom.wkbType())

                if tipo == QgsWkbTypes.LineGeometry:
                    geom_linha = QgsGeometry(geom)
                elif tipo == QgsWkbTypes.PolygonGeometry:
                    geom_linha = _poligono_para_linha(geom)
                else:
                    ignoradas_tipo += 1
                    continue

                if not geom_linha or geom_linha.isEmpty():
                    continue

                nova = QgsFeature(camada_linhas.fields())
                nova.setGeometry(geom_linha)

                for field in camada_linhas.fields():
                    nome_destino = field.name()
                    nome_origem = mapa_origem_destino.get(nome_destino, nome_destino)
                    if feat.fieldNameIndex(nome_origem) != -1:
                        nova.setAttribute(nome_destino, feat.attribute(nome_origem))

                prov.addFeature(nova)
                convertidas += 1

            camada_linhas.updateExtents()
            return camada_linhas, total_limite, convertidas, ignoradas_tipo

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

        print("\nPASSO 2: Carregar DXF e filtrar Layer = LIMITE_ROTA")
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

        camada_linhas_limite, total_limite, convertidas, ignoradas_tipo = _criar_camada_linhas_limite(
            dxf_layer,
            campo_layer,
            crs_projeto,
            f"{dxf_path.stem}_LIMITE_ROTA_LINHAS",
        )

        if total_limite == 0:
            print("Nenhuma feicao encontrada com Layer = 'LIMITE_ROTA' no DXF")
            return False

        if convertidas == 0 or not camada_linhas_limite:
            print("Foram encontradas feicoes 'LIMITE_ROTA', mas nenhuma geometria valida para linhas")
            return False

        print(f"Feicoes Layer 'LIMITE_ROTA' encontradas: {total_limite}")
        print(f"Geometrias de limite convertidas para linha: {convertidas}")
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

        print("\nPASSO 5: Aplicar transformacao nas linhas LIMITE_ROTA")
        if not camada_linhas_limite.startEditing():
            print("Nao foi possivel iniciar edicao da camada de linhas")
            return False

        erros_transformacao = 0
        total_transformadas = 0

        for feat in camada_linhas_limite.getFeatures():
            total_transformadas += 1
            geom = feat.geometry()
            if not geom or geom.isEmpty():
                continue

            retorno = geom.transform(matriz)
            if retorno != 0:
                erros_transformacao += 1
                continue

            camada_linhas_limite.changeGeometry(feat.id(), geom)

        if not camada_linhas_limite.commitChanges():
            camada_linhas_limite.rollBack()
            print("Erro ao salvar geometrias transformadas")
            return False

        print(f"Linhas processadas: {total_transformadas}")
        if erros_transformacao:
            print(f"Linhas com erro de transformacao: {erros_transformacao}")

        print("\nPASSO 6: Polygonizar limites ajustados")
        corrigida = processing.run(
            "qgis:fixgeometries",
            {
                "INPUT": camada_linhas_limite,
                "OUTPUT": "memory:LIMITE_ROTA_CORRIGIDA",
            },
        )

        resultado = processing.run(
            "qgis:polygonize",
            {
                "INPUT": corrigida["OUTPUT"],
                "KEEP_FIELDS": True,
                "OUTPUT": "memory:LIMITE_ROTA_POLIGONOS",
            },
        )

        camada_poligonos = resultado.get("OUTPUT")
        if not camada_poligonos or not camada_poligonos.isValid():
            print("Falha ao gerar camada de poligonos a partir do LIMITE_ROTA")
            return False

        if camada_poligonos.featureCount() == 0:
            print("Nenhum poligono foi gerado. Verifique se LIMITE_ROTA forma anel fechado.")
            return False

        nome_saida = f"{dxf_path.stem}_LIMITE_ROTA_POLIGONO_AJUSTADO_PR1_PR2"
        camada_poligonos.setName(nome_saida)
        print(f"Poligonos gerados: {camada_poligonos.featureCount()}")

        print("\nPASSO 7: Salvar shapefile ajustado")
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
            camada_poligonos,
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
        print("=" * 75)
        print(f"Arquivo processado: {dxf_path.name}")
        print(f"Camada final: {camada_final.name()}")
        print(f"Poligonos exibidos (Layer LIMITE_ROTA): {camada_final.featureCount()}")
        print(f"Shapefile: {shp_path}")
        print("A camada exibida foi filtrada para Layer = 'LIMITE_ROTA'")
        print("Campo 'Text' foi renomeado para 'seq_id' quando existente")
        print("Rotulos: seq_id com texto branco e buffer azul")
        print("A escala foi aplicada de forma livre para encaixar PR1/PR2")

        return True

    except Exception as e:
        print(f"ERRO NO PROCESSO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


print("INICIANDO GEOREFERENCIADOR DXF PR1/PR2 PARA LIMITE_ROTA...")
resultado = processar_dxf_limite_rota()

if resultado:
    print("Finalizado com sucesso")
else:
    print("Finalizado com erro")
