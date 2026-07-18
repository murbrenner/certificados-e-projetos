#NOME: Atualizar Sequências para Métrico

#DESCRIÇÃO: Executa a rotina 'Atualizar Sequências para Métrico', atualizando sequências e campos conforme as regras do fluxo cadastral. Depende de interação do operador por clique no mapa.

#PRÉ-REQUISITO: Selecionar previamente ao menos uma feição em 'ROTAS DE LEITURA'. A camada de pontos é escolhida na janela do script.


from qgis.core import (
    QgsProject,
    QgsGeometry,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QgsVectorLayer,
    QgsFeatureRequest,
    QgsWkbTypes,
)
from qgis.gui import QgsMapToolIdentifyFeature
from qgis.PyQt.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QSpinBox,
    QLineEdit,
    QComboBox,
)


def _list_point_layers():
    out = []
    for lyr in QgsProject.instance().mapLayers().values():
        if isinstance(lyr, QgsVectorLayer) and lyr.geometryType() == QgsWkbTypes.PointGeometry:
            out.append(lyr)
    return sorted(out, key=lambda l: l.name().lower())


def _transform_geometry(geom, src_crs, dst_crs):
    if src_crs == dst_crs:
        return QgsGeometry(geom)
    out = QgsGeometry(geom)
    xform = QgsCoordinateTransform(src_crs, dst_crs, QgsProject.instance())
    out.transform(xform)
    return out


def _build_route_mask_in_points_crs(points_layer):
    rotas_layers = QgsProject.instance().mapLayersByName("ROTAS DE LEITURA")
    if not rotas_layers:
        raise ValueError("Camada 'ROTAS DE LEITURA' não encontrada.")

    rotas = rotas_layers[0]
    if rotas.selectedFeatureCount() == 0:
        raise ValueError("Selecione ao menos uma feição em 'ROTAS DE LEITURA'.")

    geoms = []
    for feat in rotas.selectedFeatures():
        g = feat.geometry()
        if not g or g.isEmpty():
            continue
        geoms.append(_transform_geometry(g, rotas.crs(), points_layer.crs()))

    if not geoms:
        raise ValueError("Não foi possível montar máscara com as rotas selecionadas.")

    mask = QgsGeometry.unaryUnion(geoms)
    if not mask or mask.isEmpty():
        raise ValueError("Máscara das rotas ficou vazia.")
    return mask


# Estado global da execução
layer = None
current_number = 1
last_feature = None
last_seq_value = 0
setor_value = ""
rot_id_value = ""
gerencia_value = ""
last_point = None
transform = None
route_mask = None
allowed_ids = set()
tool = None


class AutoNumberingTool(QgsMapToolIdentifyFeature):
    def __init__(self, canvas, point_layer):
        super().__init__(canvas)
        self.layer = point_layer
        self.canvas = canvas

    def canvasReleaseEvent(self, event):
        global current_number, last_feature, last_seq_value, setor_value, rot_id_value, gerencia_value, last_point
        feature = self.identify(event.x(), event.y(), [self.layer])
        distance = 0

        try:
            new_point = QgsGeometry.fromPointXY(self.toMapCoordinates(event.pos())).asPoint()
            if last_point:
                last_transformed = transform.transform(last_point, QgsCoordinateTransform.ForwardTransform)
                new_transformed = transform.transform(new_point, QgsCoordinateTransform.ForwardTransform)
                distance = last_transformed.distance(new_transformed)
                last_seq_value += int(distance)
                print(f"Distância contabilizada: {distance:.2f} metros. Seq ID atualizado: {int(last_seq_value)}")

            last_point = new_point
        except Exception as e:
            print(f"Erro ao transformar coordenadas: {e}")
            return

        if not feature:
            return

        feature = feature[0].mFeature
        feature_id = feature.id()

        # Processa apenas pontos pertencentes às rotas pré-selecionadas
        if feature_id not in allowed_ids:
            print(f"Feição {feature_id} ignorada (fora da rota pré-selecionada).")
            return

        self.layer.startEditing()

        self.layer.changeAttributeValue(feature_id, self.layer.fields().indexFromName("visita_campo"), int(current_number))
        self.layer.changeAttributeValue(feature_id, self.layer.fields().indexFromName("seq_id"), int(last_seq_value))

        if setor_value.strip():
            self.layer.changeAttributeValue(feature_id, self.layer.fields().indexFromName("Setor"), setor_value)
        if rot_id_value.strip():
            self.layer.changeAttributeValue(feature_id, self.layer.fields().indexFromName("rot_id"), rot_id_value)
        if gerencia_value.strip():
            self.layer.changeAttributeValue(feature_id, self.layer.fields().indexFromName("gerencia"), gerencia_value)

        print(f"Atributos atualizados para feição {feature_id}:")
        print(f" - visita_campo: {current_number}")
        print(f" - seq_id: {int(last_seq_value)}")
        print(f" - Setor: {setor_value}")
        print(f" - rot_id: {rot_id_value}")
        print(f" - gerencia: {gerencia_value}")

        current_number += 1


def stop_tool():
    global tool
    if tool is not None:
        iface.mapCanvas().unsetMapTool(tool)
        tool = None
    print("Ferramenta desativada.")


def close_event(event):
    stop_tool()
    event.accept()


def set_attributes():
    global layer, current_number, last_seq_value, setor_value, rot_id_value, gerencia_value
    global transform, route_mask, allowed_ids, tool, last_point

    selected_layer_name = layer_combo.currentText().strip()
    if not selected_layer_name:
        print("Selecione uma camada de pontos.")
        return

    layers = QgsProject.instance().mapLayersByName(selected_layer_name)
    if not layers:
        print(f"Camada '{selected_layer_name}' não encontrada.")
        return

    layer = layers[0]

    setor_value = setor_input.text()
    rot_id_value = rot_id_input.text()
    gerencia_value = gerencia_input.text()
    current_number = spin_box.value()
    last_seq_value = seq_spin_box.value()
    last_point = None

    crs_src = layer.crs()
    crs_dest = QgsCoordinateReferenceSystem("EPSG:4326")
    transform = QgsCoordinateTransform(crs_src, crs_dest, QgsProject.instance())

    try:
        route_mask = _build_route_mask_in_points_crs(layer)
    except Exception as e:
        print(f"Erro ao preparar máscara das rotas: {e}")
        return

    req = QgsFeatureRequest().setFilterRect(route_mask.boundingBox())
    ids = []
    for feat in layer.getFeatures(req):
        g = feat.geometry()
        if g and not g.isEmpty() and g.intersects(route_mask):
            ids.append(feat.id())

    allowed_ids = set(ids)
    if not allowed_ids:
        print("Nenhum ponto da camada escolhida intersecta as rotas selecionadas.")
        return

    tool = AutoNumberingTool(iface.mapCanvas(), layer)
    iface.mapCanvas().setMapTool(tool)

    print("Ferramenta ativada. Clique nas feições para numerá-las automaticamente.")
    print(f"Pontos elegíveis pela rota: {len(allowed_ids)}")
    print("Atributos definidos:")
    print(f" - Camada de pontos: {layer.name()}")
    print(f" - Setor: {setor_value}")
    print(f" - rot_id: {rot_id_value}")
    print(f" - Gerência: {gerencia_value}")
    print(f" - visita_campo inicial: {current_number}")
    print(f" - seq_id inicial: {last_seq_value}")


point_layers = _list_point_layers()
if not point_layers:
    raise ValueError("Nenhuma camada de ponto encontrada no projeto.")

window = QWidget()
window.setWindowTitle("Controle de Numeração")
window.setFixedSize(430, 460)
window.closeEvent = close_event
layout = QVBoxLayout()
layout.setContentsMargins(14, 14, 14, 14)
layout.setSpacing(8)

# Tema light no padrão SmartPyGISCA
window.setStyleSheet(
    """
QWidget { background: #f4f7fb; color: #1a2440; font-family: 'Segoe UI', 'Arial', sans-serif; }
QLabel { color: #1a2440; font-size: 10px; }
QLineEdit, QSpinBox, QComboBox {
    background: #ffffff;
    border: 1px solid #d0daf0;
    border-radius: 8px;
    padding: 4px 8px;
    color: #1a2440;
}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus { border-color: #2f6ed6; }
QPushButton {
    background: #eef2fb;
    color: #2a4080;
    border: 1px solid #d0daf0;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 10px;
    font-weight: 700;
}
QPushButton:hover { background: #dde6f8; }
QPushButton#btnPrimary { background: #0b57d0; color: #ffffff; border: none; }
QPushButton#btnPrimary:hover { background: #1466e0; }
"""
)

camada_label = QLabel("Camada de pontos:")
layout.addWidget(camada_label)

layer_combo = QComboBox()
layer_combo.addItems([l.name() for l in point_layers])
layer_combo.setFixedHeight(34)
layout.addWidget(layer_combo)

label = QLabel("Número atual:")
layout.addWidget(label)

spin_box = QSpinBox()
spin_box.setMinimum(1)
spin_box.setMaximum(999)
spin_box.setValue(current_number)
spin_box.setFixedHeight(34)
layout.addWidget(spin_box)

seq_label = QLabel("Seq ID inicial:")
layout.addWidget(seq_label)

seq_spin_box = QSpinBox()
seq_spin_box.setMinimum(0)
seq_spin_box.setMaximum(9999)
seq_spin_box.setValue(last_seq_value)
seq_spin_box.setFixedHeight(34)
layout.addWidget(seq_spin_box)

setor_label = QLabel("Setor:")
layout.addWidget(setor_label)
setor_input = QLineEdit()
setor_input.setFixedHeight(34)
layout.addWidget(setor_input)

rot_id_label = QLabel("rot_id:")
layout.addWidget(rot_id_label)
rot_id_input = QLineEdit()
rot_id_input.setFixedHeight(34)
layout.addWidget(rot_id_input)

gerencia_label = QLabel("Gerência:")
layout.addWidget(gerencia_label)
gerencia_input = QLineEdit()
gerencia_input.setFixedHeight(34)
layout.addWidget(gerencia_input)

set_attributes_button = QPushButton("Definir e Iniciar")
set_attributes_button.setObjectName("btnPrimary")
set_attributes_button.clicked.connect(set_attributes)
layout.addWidget(set_attributes_button)

stop_button = QPushButton("Parar Numeração")
stop_button.clicked.connect(stop_tool)
layout.addWidget(stop_button)

window.setLayout(layout)
window.show()
