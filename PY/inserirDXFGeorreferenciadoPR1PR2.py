#NOME: Inserir Pontos com pontos de referência no DXF

#DESCRIÇÃO: Importa um arquivo DXF georreferenciado utilizando pontos de referência PR1 e PR2. O script identifica os pontos PR1 e PR2 no DXF, solicita ao usuário que clique nos pontos correspondentes no mapa, e aplica uma transformação de translação, rotação e escala livre para ajustar o desenho do DXF ao sistema de coordenadas do projeto. O resultado é salvo como um shapefile contendo apenas os pontos da camada SEQ_ROTA, com rótulos baseados no campo 'Text' (renomeado para 'seq_id').

#PRÉ-REQUISITO: Inserir camadas PR1 e PR2 no DXF marcando os pontos de referência.


# IMPORTADOR DXF COM GEOREFERENCIAMENTO POR PR1/PR2
# Seleciona DXF, identifica PR1/PR2 e ajusta todo o desenho por 2 pontos de controle
# Data: Mar/2026


def processar_dxf_completo():
    """
    Fluxo:
    1) Seleciona arquivo DXF
    2) Carrega camada DXF (entities)
    3) Encontra pontos de referência no DXF (Layer = PR1 e PR2)
    4) Solicita 2 cliques no mapa (destino PR1 e PR2)
    5) Aplica transformação com translação + rotação + escala livre
    6) Salva shapefile ajustado na pasta SHAPES e adiciona ao projeto
    """

    print("🚀 GEOREFERENCIADOR DXF (PR1/PR2)")
    print("=" * 55)

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
                f"{dxf_file}|layername=entities|geometrytype=Point",
            ]

            for i, uri in enumerate(uris_teste, 1):
                print(f"   🔎 Tentativa {i}: {uri}")
                camada_teste = QgsVectorLayer(uri, f"DXF_{nome_base}", "ogr")
                if camada_teste.isValid() and camada_teste.featureCount() > 0:
                    print(f"   ✅ DXF carregado ({camada_teste.featureCount()} feições)")
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

        def _criar_camada_ponto_filtrada(camada, campo_layer, crs_saida, nome_camada):
            authid = crs_saida.authid() if crs_saida and crs_saida.isValid() else "EPSG:31983"
            camada_ponto = QgsVectorLayer(f"Point?crs={authid}", nome_camada, "memory")

            if not camada_ponto.isValid():
                return None, 0, 0

            prov = camada_ponto.dataProvider()

            campos_destino = []
            mapa_origem_destino = {}

            for field in camada.fields():
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

            prov.addAttributes(campos_destino)
            camada_ponto.updateFields()

            total_ponto = 0
            validos = 0

            for feat in camada.getFeatures():
                if _normalizar(feat.attribute(campo_layer)) != "SEQ_ROTA":
                    continue

                total_ponto += 1

                ponto = _ponto_da_geometria(feat.geometry())
                if not ponto:
                    continue

                nova = QgsFeature(camada_ponto.fields())
                nova.setGeometry(QgsGeometry.fromPointXY(ponto))

                for field in camada_ponto.fields():
                    nome_destino = field.name()
                    nome_origem = mapa_origem_destino.get(nome_destino, nome_destino)

                    if feat.fieldNameIndex(nome_origem) != -1:
                        nova.setAttribute(nome_destino, feat.attribute(nome_origem))

                prov.addFeature(nova)
                validos += 1

            camada_ponto.updateExtents()
            return camada_ponto, total_ponto, validos

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

        print("📂 PASSO 1: Selecionar arquivo DXF")
        dxf_file, _ = QFileDialog.getOpenFileName(
            None,
            "Selecionar arquivo DXF",
            "",
            "Arquivos DXF (*.dxf);;Todos os Arquivos (*)",
        )

        if not dxf_file:
            print("❌ Processo cancelado: nenhum arquivo selecionado")
            return False

        dxf_path = Path(dxf_file)
        print(f"✅ Arquivo: {dxf_path.name}")

        print("\n📥 PASSO 2: Carregar DXF e filtrar Layer = SEQ_ROTA")
        dxf_layer = _carregar_dxf(dxf_file, dxf_path.stem)
        if not dxf_layer:
            print("❌ Não foi possível carregar o DXF")
            return False

        project = QgsProject.instance()
        crs_projeto = project.crs()
        if not crs_projeto.isValid():
            crs_projeto = QgsCoordinateReferenceSystem("EPSG:31983")
        dxf_layer.setCrs(crs_projeto)

        campo_layer = _campo_layer(dxf_layer)
        if not campo_layer:
            print("❌ Campo de layer não encontrado no DXF (esperado: Layer)")
            return False

        print(f"✅ Campo layer detectado: {campo_layer}")

        camada_ponto, total_ponto, ponto_valido = _criar_camada_ponto_filtrada(
            dxf_layer,
            campo_layer,
            crs_projeto,
            f"{dxf_path.stem}_SEQ_ROTA",
        )

        if total_ponto == 0:
            print("❌ Nenhuma feição encontrada com Layer = 'SEQ_ROTA' no DXF")
            return False

        if ponto_valido == 0 or not camada_ponto:
            print("❌ Foram encontradas feições 'SEQ_ROTA', mas nenhuma geometria pôde ser convertida para ponto")
            return False

        print(f"✅ Feições Layer 'SEQ_ROTA' encontradas: {total_ponto}")
        print(f"✅ Pontos válidos para exibição: {ponto_valido}")

        origem_pr1, qtd_pr1 = _obter_ponto_referencia(dxf_layer, "PR1", campo_layer)
        origem_pr2, qtd_pr2 = _obter_ponto_referencia(dxf_layer, "PR2", campo_layer)

        if not origem_pr1 or not origem_pr2:
            print("❌ Não foi possível localizar PR1 e PR2 no DXF")
            print("💡 Verifique se há feições com Layer = 'PR1' e Layer = 'PR2'")
            return False

        print(f"✅ PR1 no DXF: {qtd_pr1} feição(ões) | ponto médio ({origem_pr1.x():.3f}, {origem_pr1.y():.3f})")
        print(f"✅ PR2 no DXF: {qtd_pr2} feição(ões) | ponto médio ({origem_pr2.x():.3f}, {origem_pr2.y():.3f})")

        print("\n🖱️ PASSO 3: Capturar referências no mapa")
        canvas = iface.mapCanvas()

        destino_pr1 = _capturar_ponto(
            canvas,
            "Referência PR1",
            "Clique no ponto do mapa que representa o PR1.",
        )
        if not destino_pr1:
            print("❌ Processo cancelado na captura do PR1")
            return False

        print(f"✅ PR1 destino: ({destino_pr1.x():.3f}, {destino_pr1.y():.3f})")

        destino_pr2 = _capturar_ponto(
            canvas,
            "Referência PR2",
            "Clique no ponto do mapa que representa o PR2.",
        )
        if not destino_pr2:
            print("❌ Processo cancelado na captura do PR2")
            return False

        print(f"✅ PR2 destino: ({destino_pr2.x():.3f}, {destino_pr2.y():.3f})")

        print("\n🧮 PASSO 4: Calcular transformação (translação + rotação + escala livre)")
        dx_origem = origem_pr2.x() - origem_pr1.x()
        dy_origem = origem_pr2.y() - origem_pr1.y()
        dx_destino = destino_pr2.x() - destino_pr1.x()
        dy_destino = destino_pr2.y() - destino_pr1.y()

        dist_origem = math.hypot(dx_origem, dy_origem)
        dist_destino = math.hypot(dx_destino, dy_destino)

        if dist_origem == 0 or dist_destino == 0:
            print("❌ Distância inválida entre PR1 e PR2 para calcular transformação")
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

        print(f"✅ Escala aplicada (livre): {escala:.6f}")
        print(f"✅ Rotação aplicada: {math.degrees(angulo):.4f}°")

        print("\n🔧 PASSO 5: Aplicar transformação na camada de pontos (SEQ_ROTA)")
        camada_ajustada = camada_ponto
        if not camada_ajustada or not camada_ajustada.isValid():
            print("❌ Falha ao preparar camada de pontos para ajuste")
            return False

        camada_ajustada.setName(f"{dxf_path.stem}_SEQ_ROTA_AJUSTADO_PR1_PR2")

        if not camada_ajustada.startEditing():
            print("❌ Não foi possível iniciar edição da camada ajustada")
            return False

        erros_transformacao = 0
        total = 0

        for feat in camada_ajustada.getFeatures():
            total += 1
            geom = feat.geometry()
            if not geom or geom.isEmpty():
                continue

            retorno = geom.transform(matriz)
            if retorno != 0:
                erros_transformacao += 1
                continue

            camada_ajustada.changeGeometry(feat.id(), geom)

        if not camada_ajustada.commitChanges():
            camada_ajustada.rollBack()
            print("❌ Erro ao salvar geometrias transformadas")
            return False

        print(f"✅ Pontos processados: {total}")
        if erros_transformacao:
            print(f"⚠️ Pontos com erro de transformação: {erros_transformacao}")

        print("\n💾 PASSO 6: Salvar shapefile ajustado")
        output_dir = dxf_path.parent / "SHAPES"
        output_dir.mkdir(exist_ok=True)

        nome_saida = f"{dxf_path.stem}_SEQ_ROTA_AJUSTADO_PR1_PR2"
        shp_path = output_dir / f"{nome_saida}.shp"

        if shp_path.exists():
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            shp_path = output_dir / f"{nome_saida}_{stamp}.shp"

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "ESRI Shapefile"
        options.fileEncoding = "UTF-8"

        erro = QgsVectorFileWriter.writeAsVectorFormatV3(
            camada_ajustada,
            str(shp_path),
            project.transformContext(),
            options,
        )

        if erro[0] != QgsVectorFileWriter.NoError:
            print(f"❌ Erro ao salvar shapefile: {erro[1]}")
            return False

        camada_final = QgsVectorLayer(str(shp_path), nome_saida, "ogr")
        if not camada_final.isValid():
            print("❌ Shapefile salvo, mas falhou ao recarregar no QGIS")
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
            print("✅ Rotulagem aplicada: campo 'seq_id' | texto branco | buffer azul")
        else:
            print("⚠️ Campo 'seq_id' não encontrado após exportação")

        canvas.setExtent(camada_final.extent())
        canvas.refresh()

        print("\n🎉 PROCESSO CONCLUÍDO COM SUCESSO")
        print("=" * 55)
        print(f"📁 Arquivo processado: {dxf_path.name}")
        print(f"📄 Camada final: {camada_final.name()}")
        print(f"📍 Pontos exibidos (Layer SEQ_ROTA): {total}")
        print(f"💾 Shapefile: {shp_path}")
        print("💡 A camada exibida foi filtrada para Layer = 'SEQ_ROTA'")
        print("💡 Campo 'Text' foi renomeado para 'seq_id' na camada final")
        print("💡 Rótulos: seq_id com texto branco e buffer azul")
        print("💡 A escala foi aplicada de forma livre para encaixar PR1/PR2")

        return True

    except Exception as e:
        print(f"💥 ERRO NO PROCESSO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


print("🚀 INICIANDO GEOREFERENCIADOR DXF PR1/PR2...")
resultado = processar_dxf_completo()

if resultado:
    print("✅ Finalizado com sucesso")
else:
    print("❌ Finalizado com erro")
