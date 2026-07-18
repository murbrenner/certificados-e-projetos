#NOME: Transformar Sequencial para Metrico

#DESCRIÇÃO: 08/06/2026 - Transforma sequência (seq_id) em métrica (metros) para pontos da camada escolhida. - Pergunta a camada de pontos (combobox) e o campo de sequência (padrão: seq_id). - Opcional: usar somente feições selecionadas. - Opcional: gravar em novo campo (padrão: seq_id_m) ou sobrescrever o seq_id. - Saída: cria uma CÓPIA em mem. O resultado final e adicionado ao projeto.

#PRÉ-REQUISITO: Selecionar previamente as feicoes que serao processadas.


# -*- coding: utf-8 -*-
"""
08/06/2026 - Transforma sequência (seq_id) em métrica (metros) para pontos da camada escolhida.
- Pergunta a camada de pontos (combobox) e o campo de sequência (padrão: seq_id).
- Opcional: usar somente feições selecionadas.
- Opcional: gravar em novo campo (padrão: seq_id_m) ou sobrescrever o seq_id.
- Saída: cria uma CÓPIA em memória com os valores calculados; NÃO altera a camada original (sem commit).

Uso: execute este arquivo no Console Python do QGIS ou via plugin.
Requisitos: QGIS 3.x (iface disponível).
"""

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsFields,
    QgsField,
    QgsWkbTypes,
    QgsGeometry,
    QgsPointXY,
    QgsDistanceArea,
    QgsMapLayerProxyModel,
    QgsCoordinateTransform,
)
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QMessageBox,
)
from qgis.gui import QgsMapLayerComboBox

# Verificações básicas do ambiente QGIS
try:
    iface  # type: ignore # fornecido pelo QGIS
except NameError:
    raise RuntimeError("Este script deve ser executado dentro do QGIS (iface não encontrado).")


class SeqToMetricDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Transformar Sequencial → Métrico (cópia)")
        self.setMinimumWidth(420)

        # Layout principal
        main_layout = QVBoxLayout()

        # Seleção da camada
        main_layout.addWidget(QLabel("IMÓVEL"))
        self.layer_combo = QgsMapLayerComboBox()
        self.layer_combo.setFilters(QgsMapLayerProxyModel.PointLayer)
        if iface.activeLayer():
            try:
                self.layer_combo.setLayer(iface.activeLayer())
            except Exception:
                pass
        main_layout.addWidget(self.layer_combo)

        # Campo de sequência
        seq_row = QHBoxLayout()
        seq_row.addWidget(QLabel("Campo de sequência (ordem):"))
        self.seq_field_input = QLineEdit("seq_id")
        self.seq_field_input.setPlaceholderText("ex.: seq_id")
        seq_row.addWidget(self.seq_field_input)
        main_layout.addLayout(seq_row)

        # Informativo: polígono de ROTAS DE LEITURA
        info_label = QLabel(
            "⚠️ Selecione previamente 1 polígono na camada\n"
            "'ROTAS DE LEITURA'. Apenas os pontos contidos\n"
            "nesse polígono serão processados."
        )
        info_label.setStyleSheet("color: #8B4513; font-style: italic;")
        main_layout.addWidget(info_label)

        # Novo campo ou sobrescrever
        self.new_field_chk = QCheckBox("Escrever em NOVO campo (recomendado)")
        self.new_field_chk.setChecked(True)
        main_layout.addWidget(self.new_field_chk)

        out_row = QHBoxLayout()
        out_row.addWidget(QLabel("Nome do novo campo:"))
        self.out_field_input = QLineEdit("seq_id_m")
        out_row.addWidget(self.out_field_input)
        main_layout.addLayout(out_row)

        # Botões
        btn_row = QHBoxLayout()
        self.run_btn = QPushButton("Executar")
        self.close_btn = QPushButton("Fechar")
        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.close_btn)
        main_layout.addLayout(btn_row)

        self.setLayout(main_layout)

        # Sinais
        self.new_field_chk.toggled.connect(self._on_toggle_new_field)
        self.run_btn.clicked.connect(self._on_run)
        self.close_btn.clicked.connect(self.close)

        # Estado inicial
        self._on_toggle_new_field(self.new_field_chk.isChecked())


    def _on_toggle_new_field(self, checked: bool):
        self.out_field_input.setEnabled(checked)

    def _warn(self, title: str, msg: str):
        QMessageBox.warning(self, title, msg)
        print(f"⚠️ {title}: {msg}")

    def _info(self, title: str, msg: str):
        QMessageBox.information(self, title, msg)
        print(f"ℹ️ {title}: {msg}")

    def _on_run(self):
        layer = self.layer_combo.currentLayer()
        if layer is None:
            self._warn("Camada inválida", "Selecione uma camada de pontos válida.")
            return

        if layer.geometryType() != QgsWkbTypes.PointGeometry:
            self._warn("Tipo incorreto", "A camada selecionada não é de pontos.")
            return

        seq_field = self.seq_field_input.text().strip()
        if not seq_field:
            self._warn("Campo obrigatório", "Informe o nome do campo de sequência (ex.: seq_id).")
            return

        fields = layer.fields()
        if fields.indexFromName(seq_field) < 0:
            self._warn("Campo não encontrado", f"O campo '{seq_field}' não existe na camada selecionada.")
            return

        # Busca a camada ROTAS DE LEITURA (busca por nome, case-insensitive)
        rotas_layer = None
        for lyr in QgsProject.instance().mapLayers().values():
            if 'rotas de leitura' in lyr.name().lower():
                rotas_layer = lyr
                break
        if rotas_layer is None:
            self._warn(
                "Camada não encontrada",
                "A camada 'ROTAS DE LEITURA' não foi encontrada no projeto.\n"
                "Adicione-a ao projeto e tente novamente."
            )
            return

        selected_polys = rotas_layer.selectedFeatures()
        if len(selected_polys) == 0:
            self._warn(
                "Nenhum polígono selecionado",
                "Selecione exatamente 1 polígono na camada 'ROTAS DE LEITURA' antes de executar."
            )
            return
        if len(selected_polys) > 1:
            self._warn(
                "Seleção inválida",
                f"{len(selected_polys)} polígonos selecionados em 'ROTAS DE LEITURA'.\n"
                "Selecione apenas 1 polígono e tente novamente."
            )
            return

        poly_geom = selected_polys[0].geometry()
        if poly_geom is None or poly_geom.isEmpty():
            self._warn("Geometria inválida", "O polígono selecionado não possui geometria válida.")
            return

        # Reprojeta o polígono para o SRC da camada de pontos, se necessário
        if rotas_layer.crs() != layer.crs():
            transform = QgsCoordinateTransform(
                rotas_layer.crs(), layer.crs(), QgsProject.instance()
            )
            poly_geom.transform(transform)

        # Filtra pontos contidos no polígono selecionado
        features_src = [
            f for f in layer.getFeatures()
            if not f.geometry().isEmpty() and poly_geom.contains(f.geometry())
        ]
        if len(features_src) == 0:
            self._warn(
                "Sem feições",
                "Nenhum ponto da camada está contido no polígono selecionado em 'ROTAS DE LEITURA'."
            )
            return
        print(f"📍 {len(features_src)} ponto(s) encontrado(s) dentro do polígono selecionado.")

        # Ordena pela sequência (tratando valores nulos/não numéricos)
        def parse_seq(feat):
            try:
                v = feat[seq_field]
                if v is None:
                    return float('inf')
                return int(v)
            except Exception:
                return float('inf')

        features_sorted = sorted(features_src, key=parse_seq)

        # Valida quantidade
        if len(features_sorted) < 2:
            self._warn("Poucas feições", "São necessárias pelo menos 2 feições para calcular distâncias.")
            return

        # Medidor geodésico (metros), independente do SRC da camada
        dist = QgsDistanceArea()
        try:
            dist.setSourceCrs(layer.crs(), QgsProject.instance().transformContext())
        except Exception:
            # fallback sem transformContext
            dist.setSourceCrs(layer.crs(), None)
        try:
            # usa elipsóide do projeto, quando configurado
            dist.setEllipsoid(QgsProject.instance().ellipsoid())
        except Exception:
            # fallback para WGS84
            dist.setEllipsoid('WGS84')
        try:
            dist.setEllipsoidalMode(True)
        except Exception:
            try:
                dist.setEllipsoidal(True)
            except Exception:
                pass

        # Calcula distâncias cumulativas (inteiros em metros)
        results = {}  # fid -> metros (int)
        cumulative = 0

        def point_of(feat):
            geom = feat.geometry()
            if geom is None or geom.isEmpty():
                return None
            if geom.type() != QgsWkbTypes.PointGeometry:
                return None
            try:
                return geom.asPoint()
            except Exception:
                # Pode ser multipoint
                try:
                    mp = geom.asMultiPoint()
                    return mp[0] if mp else None
                except Exception:
                    return None

        p_prev = point_of(features_sorted[0])
        if p_prev is None:
            self._warn("Geometria inválida", "A primeira feição não possui ponto válido.")
            return

        # Primeira feição → 0 m
        results[features_sorted[0].id()] = 0

        for i in range(1, len(features_sorted)):
            p_cur = point_of(features_sorted[i])
            if p_cur is None:
                self._warn("Geometria inválida", f"Feição {features_sorted[i].id()} não possui ponto válido; distância ignorada.")
                results[features_sorted[i].id()] = cumulative
                continue
            try:
                seg = dist.measureLine(p_prev, p_cur)  # metros
            except Exception:
                seg = 0.0
            if seg is None:
                seg = 0.0
            cumulative += int(round(seg))
            results[features_sorted[i].id()] = cumulative
            p_prev = p_cur

        # Cria camada em memória (cópia) e escreve resultado
        out_overwrite = not self.new_field_chk.isChecked()
        out_field = self.out_field_input.text().strip() or "seq_id_m"

        # Replica esquema da camada original
        out_uri = f"Point?crs={layer.crs().authid()}"
        out_name = f"{layer.name()}_metrificado"
        out_layer = QgsVectorLayer(out_uri, out_name, "memory")
        prov = out_layer.dataProvider()

        # Copia campos
        out_fields = QgsFields()
        for f in fields:
            out_fields.append(f)
        # Garante o campo de saída se for novo
        if not out_overwrite:
            if out_fields.indexFromName(out_field) < 0:
                out_fields.append(QgsField(out_field, QVariant.Int))
        # addAttributes requer uma lista de QgsField
        prov.addAttributes([f for f in out_fields])
        out_layer.updateFields()

        # Copia feições com atributos atualizados (apenas as do polígono)
        feats_to_add = []
        for feat in features_sorted:
            new_feat = QgsFeature(out_layer.fields())
            new_feat.setGeometry(feat.geometry())
            attrs = [feat[attr.name()] for attr in fields]

            # Prepara dicionário de atributos para facilitar edição
            attr_map = {attr.name(): val for attr, val in zip(fields, attrs)}

            if feat.id() in results:
                metric_val = int(results[feat.id()])
                if out_overwrite:
                    # Sobrescreve o campo seq_field
                    attr_map[seq_field] = metric_val
                else:
                    # Escreve no novo campo, preservando o seq_field original
                    attr_map[out_field] = metric_val

            # Atribui na ordem dos campos do out_layer
            final_attrs = []
            for fld in out_layer.fields():
                final_attrs.append(attr_map.get(fld.name(), None))

            new_feat.setAttributes(final_attrs)
            feats_to_add.append(new_feat)

        prov.addFeatures(feats_to_add)
        out_layer.updateExtents()

        QgsProject.instance().addMapLayer(out_layer)

        msg = (
            f"✅ Processo concluído. Camada de saída adicionada: '{out_layer.name()}'.\n"
            f"Feições processadas: {len(results)} (ordem baseada em '{seq_field}').\n"
            f"Modo: {'SOBRESCREVENDO ' + seq_field if out_overwrite else 'NOVO CAMPO: ' + out_field}."
        )
        self._info("Concluído", msg)
        print("🧭 Resumo:")
        print(f" - Camada original: {layer.name()}")
        print(f" - Camada de saída: {out_layer.name()}")
        print(f" - Campo de ordem: {seq_field}")
        print(f" - Escrever: {'sobrescrever ' + seq_field if out_overwrite else 'novo campo ' + out_field}")
        print(f" - Feições calculadas: {len(results)}")


# Instancia e mostra a janela (não modal)
dlg = SeqToMetricDialog()
dlg.setWindowModality(False)
dlg.show()
print("🟦 Janela aberta: selecione a camada, configure os campos e clique em Executar.")
