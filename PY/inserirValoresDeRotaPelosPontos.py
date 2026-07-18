#NOME: Inserir Valores de Rota Pelos Pontos

#DESCRIÇÃO: Executa a rotina 'Inserir Valores de Rota Pelos Pontos', inserindo dados, geometrias ou atributos conforme a logica definida no script. Camadas envolvidas: 'ROTAS DE LEITURA'.

#PRÉ-REQUISITO: Carregar a camada 'ROTAS DE LEITURA' no projeto QGIS; selecionar previamente as feicoes que serao processadas.


from qgis.core import QgsProject, QgsProcessingFeatureSourceDefinition, QgsFeatureRequest
from qgis.PyQt.QtWidgets import QInputDialog
import processing
import time

# pede o nome da camada de pontos
camPontos, ok = QInputDialog.getText(None, 'Inserir NOME DA CAMADA DE PONTOS', 'Digite o NOME DA CAMADA DE PONTOS:')
camPontos = str(camPontos)

layerNumRotas = QgsProject.instance().mapLayersByName(camPontos)[0]
layerRotas = QgsProject.instance().mapLayersByName('ROTAS DE LEITURA')[0]

# garante edição nos layers
layerNumRotas.startEditing()
layerRotas.startEditing()

# verifica se há pontos selecionados
if layerNumRotas.selectedFeatureCount() == 0:
    print('Nenhum ponto selecionado na camada', camPontos)
else:
    # processa cada ponto selecionado separadamente: seleciona cada ponto por id
    selected_point_ids = [f.id() for f in layerNumRotas.selectedFeatures()]
    field_name = 'rota'  # nome do campo a ser atualizado nos polígonos
    field_idx = layerRotas.fields().indexFromName(field_name)
    if field_idx == -1:
        print("Campo '{}' não encontrado na camada ROTAS. Abortando.".format(field_name))
    else:
        for pid in selected_point_ids:
            # seleciona apenas o ponto atual
            layerNumRotas.removeSelection()
            layerNumRotas.selectByIds([pid])

            # pega o ponto atual e seu valor
            try:
                ponto = layerNumRotas.getFeature(pid)
                textPontos = ponto['Text']
                textPontos = int(textPontos)
            except Exception as e:
                print("Erro lendo campo 'Text' do ponto id {} (ignorado):".format(pid), e)
                continue

            print('Valor do ponto (id {}):'.format(pid), textPontos)

            # seleciona polígonos que intersectam apenas esse ponto
            processing.run("native:selectbylocation", {
                'INPUT': layerRotas,
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
            for rota in layerRotas.selectedFeatures():
                try:
                    print('Antes (id {}):'.format(rota.id()), rota[field_name])
                except Exception:
                    print('Sem valor anterior em', field_name, 'para feature id', rota.id())
                layerRotas.changeAttributeValue(rota.id(), field_idx, textPontos)
                print('Atualizado (id {}):'.format(rota.id()), textPontos)

            # limpa seleção de polígonos e do ponto atual
            layerRotas.removeSelection()
            layerNumRotas.removeSelection()

    # salva alterações
    # if layerQuadras.isEditable():
    #     layerQuadras.commitChanges()
    # if layerNumQuadras.isEditable():
    #     layerNumQuadras.commitChanges()
