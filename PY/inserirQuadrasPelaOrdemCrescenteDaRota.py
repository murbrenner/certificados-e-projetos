#NOME: Inserir Quadras Pela Ordem Crescente da Rota

#DESCRIÇÃO: Executa a rotina 'Inserir Quadras Pela Ordem Crescente da Rota', inserindo dados, geometrias ou atributos conforme a logica definida no script.

#PRÉ-REQUISITO: Selecionar previamente as feicoes que serao processadas.


from PyQt5.QtWidgets import QInputDialog, QMessageBox
from PyQt5.QtWidgets import QApplication, QWidget
from qgis.utils import iface

qdGisInicio, ok = QInputDialog.getText(None, 'Inserir QUADRA', 'Digite o valor inicial da QUADRA:')
qdGisInicio = int(qdGisInicio)

qdGisFinal, ok2 = QInputDialog.getText(None, 'Inserir ROTA', 'Digite o valor final da QUADRA":')
qdGisFinal = int(qdGisFinal)

rota_gis, ok2 = QInputDialog.getText(None, 'Inserir ROTA', 'Digite o valor inicial da ROTA":')
rota_gis = int(rota_gis)

while qdGisInicio <= qdGisFinal:
    while rota_gis <= 50:            
        if ok:
            if ok2:
                layer = iface.activeLayer()            
                selected_features = layer.selectedFeatures()
                quadra = 'quadra'
                rota = 'rota'
                if selected_features:         
                    for feature in selected_features:
                        feature_id_rota = feature.id()
                        if not layer.isEditable():
                            layer.startEditing()                    
                        feature = layer.getFeature(feature_id_rota)
                        feature_id = feature.id()
                        
                        if feature[rota] == rota_gis:
                            feature = layer.getFeature(feature_id)
                            feature[quadra] = None
                            layer.updateFeature(feature)
                            feature[quadra] = qdGisInicio  # Altere o campo desejado aqui
                            layer.updateFeature(feature)
                            qdGisInicio = qdGisInicio + 1                    
                else:
                    print("Nenhuma feição selecionada.")
        rota_gis = rota_gis + 1
    qdGisInicio = qdGisInicio + 1
