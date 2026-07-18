#NOME: Inserir Valores de Quadra Pelos Pontos

#DESCRIÇÃO: Executa a rotina 'Inserir Valores de Quadra Pelos Pontos', inserindo dados, geometrias ou atributos conforme a logica definida no script. Camadas envolvidas: 'QUADRAS'.

#PRÉ-REQUISITO: Carregar a camada 'QUADRAS' no projeto QGIS; selecionar previamente as feicoes que serao processadas.


from qgis.core import QgsProject, QgsProcessingFeatureSourceDefinition, QgsFeatureRequest
from qgis.PyQt.QtWidgets import QInputDialog
import processing
import time

# pede o nome da camada de pontos
camPontos, ok = QInputDialog.getText(None, 'Inserir NOME DA CAMADA DE PONTOS', 'Digite o NOME DA CAMADA DE PONTOS:')
camPontos = str(camPontos)

layerNumQuadras = QgsProject.instance().mapLayersByName(camPontos)[0]
layerQuadras = QgsProject.instance().mapLayersByName('QUADRAS')[0]

# garante edição nos layers
layerNumQuadras.startEditing()
layerQuadras.startEditing()

# verifica se há pontos selecionados
if layerNumQuadras.selectedFeatureCount() == 0:
    print('Nenhum ponto selecionado na camada', camPontos)
else:
    # processa cada ponto selecionado separadamente: seleciona cada ponto por id
    selected_point_ids = [f.id() for f in layerNumQuadras.selectedFeatures()]
    field_name = 'quadra'  # nome do campo a ser atualizado nos polígonos
    field_idx = layerQuadras.fields().indexFromName(field_name)
    if field_idx == -1:
        print("Campo '{}' não encontrado na camada QUADRAS. Abortando.".format(field_name))
    else:
        for pid in selected_point_ids:
            # seleciona apenas o ponto atual
            layerNumQuadras.removeSelection()
            layerNumQuadras.selectByIds([pid])

            # pega o ponto atual e seu valor
            try:
                ponto = layerNumQuadras.getFeature(pid)
                textPontos = ponto['quadra']
                textPontos = int(textPontos)
            except Exception as e:
                print("Erro lendo campo 'quadra' do ponto id {} (ignorado):".format(pid), e)
                continue

            print('Valor do ponto (id {}):'.format(pid), textPontos)

            # seleciona polígonos que intersectam apenas esse ponto
            processing.run("native:selectbylocation", {
                'INPUT': layerQuadras,
                'PREDICATE': [0],  # intersects
                'INTERSECT': QgsProcessingFeatureSourceDefinition(
                    camPontos,
                    selectedFeaturesOnly=True,
                    featureLimit=-1,
                    flags=QgsProcessingFeatureSourceDefinition.FlagOverrideDefaultGeometryCheck,
                    geometryCheck=QgsFeatureRequest.GeometryNoCheck
                ),
                'METHOD': 0  # create new selection for this point
            })

            # atualiza os polígonos selecionados com o valor do ponto atual
            for quadra in layerQuadras.selectedFeatures():
                try:
                    print('Antes (id {}):'.format(quadra.id()), quadra[field_name])
                except Exception:
                    print('Sem valor anterior em', field_name, 'para feature id', quadra.id())
                layerQuadras.changeAttributeValue(quadra.id(), field_idx, textPontos)
                print('Atualizado (id {}):'.format(quadra.id()), textPontos)

            # limpa seleção de polígonos e do ponto atual
            layerQuadras.removeSelection()
            layerNumQuadras.removeSelection()

    # salva alterações
    # if layerQuadras.isEditable():
    #     layerQuadras.commitChanges()
    # if layerNumQuadras.isEditable():
    #     layerNumQuadras.commitChanges()
