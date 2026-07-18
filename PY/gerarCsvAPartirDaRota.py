#NOME: GERAR CSV A PARTIR DA ROTA

#DESCRIÇÃO: Gera dados e camadas de saida a partir das informacoes do projeto QGIS. Inclui leitura e/ou exportacao de dados em CSV. Camadas envolvidas: 'ARRUAMENTO_MA', 'IMÓVEL', 'OVERLEY', 'QUADRAS', 'ROTAS DE LEITURA'.

#PRÉ-REQUISITO: Carregar as camadas 'ARRUAMENTO_MA', 'IMÓVEL', 'OVERLEY', 'QUADRAS', 'ROTAS DE LEITURA' no projeto QGIS; selecionar previamente as feicoes que serao processadas; garantir arquivo CSV valido e no layout esperado.


from qgis.core import QgsProject, QgsSpatialIndex, QgsDistanceArea, QgsProcessingFeatureSourceDefinition
from qgis.PyQt.QtWidgets import QFileDialog
import processing, csv, os

def normalizar_localidade(valor):
    try:
        return int(float(str(valor).replace(',', '.')))
    except (TypeError, ValueError):
        return 0


def obter_localidade_overlay(overlay):
    if 'localidade ' in overlay.fields().names():
        return normalizar_localidade(overlay['localidade '])
    if 'localidade' in overlay.fields().names():
        return normalizar_localidade(overlay['localidade'])
    return 0


def escolher_arquivo_saida():
    downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
    caminho_padrao = os.path.join(downloads, 'relatorio.csv')
    caminho, _ = QFileDialog.getSaveFileName(
        None,
        'Salvar relatório CSV',
        caminho_padrao,
        'Arquivos CSV (*.csv);;Todos os arquivos (*)'
    )
    return caminho if caminho else caminho_padrao


arquivo_saida = escolher_arquivo_saida()

layerImovel = QgsProject.instance().mapLayersByName("IMÓVEL")[0]
layerQuadras = QgsProject.instance().mapLayersByName("QUADRAS")[0]
layerArruamento = QgsProject.instance().mapLayersByName("ARRUAMENTO_MA")[0]
layerOverlay = QgsProject.instance().mapLayersByName("OVERLEY")[0]
layerRotas = QgsProject.instance().mapLayersByName("ROTAS DE LEITURA")[0]

layerImovel.startEditing()
layerQuadras.startEditing()
layerArruamento.startEditing()
layerOverlay.startEditing()

cabeçalho = ['localidade', 'Setor', 'quadra', 'seq_id', 'rot_id', 'imv_id', 'latitude', 'longitude', 'alterar']
with open(arquivo_saida, mode="w", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(cabeçalho)

    rotas_preselecionadas = layerRotas.selectedFeatures()

    for rota in rotas_preselecionadas:
        layerRotas.selectByIds([rota.id()])
        layerQuadras.removeSelection()
        layerOverlay.removeSelection()

        # Selecionar quadras a partir da rota pré-selecionada pelo usuário
        processing.run("native:selectbylocation", {
            'INPUT': layerQuadras,
            'PREDICATE': [0,1,5,6,7],
            'INTERSECT': QgsProcessingFeatureSourceDefinition(layerRotas.id(), True, rota.id()),
            'METHOD': 0
        })

        # Selecionar overlay que intersecta com a rota atual
        processing.run("native:selectbylocation", {
            'INPUT': layerOverlay,
            'PREDICATE': [0,1,5,6,7],
            'INTERSECT': QgsProcessingFeatureSourceDefinition(layerRotas.id(), True, rota.id()),
            'METHOD': 0
        })

        localidade = 0
        for overlay in layerOverlay.selectedFeatures():
            localidade = obter_localidade_overlay(overlay)
            break

        for quadra in layerQuadras.selectedFeatures():
            layerQuadras.selectByIds([quadra.id()])
            layerImovel.removeSelection()

            # Selecionar imóveis que intersectam com a quadra atual
            processing.run("native:selectbylocation", {
                'INPUT': layerImovel,
                'PREDICATE': [0,1,4,5,6,7],
                'INTERSECT': QgsProcessingFeatureSourceDefinition(layerQuadras.id(), True, quadra.id()),
                'METHOD': 0
            })

            for imovel in layerImovel.selectedFeatures():
                linha = localidade, (quadra['setor']), (quadra['quadra']), (imovel['seq_id']), (imovel['rot_id']), (imovel['imv_id']), (imovel['latitude']), (imovel['longitude']), '1'
                escritor = writer.writerow(linha)
