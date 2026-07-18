#NOME: Inserir Valor das Quadras Apartir do CSV

#DESCRIÇÃO: Insere dados, geometrias ou atributos nas camadas de destino conforme a rotina do script. Inclui leitura e/ou exportacao de dados em CSV. Camadas envolvidas: 'IMÓVEL', 'QUADRAS'.

#PRÉ-REQUISITO: Carregar as camadas 'IMÓVEL', 'QUADRAS' no projeto QGIS; selecionar previamente as feicoes que serao processadas; garantir arquivo CSV valido e no layout esperado.


from qgis.core import QgsProject, QgsProcessingFeatureSourceDefinition, QgsFeatureRequest
import pandas as pd

database = "C:\\CSV\\PATOS-CITY.csv"
db = pd.read_csv(database)

layerImovel = QgsProject.instance().mapLayersByName("IMÓVEL")[0]
layerQuadras = QgsProject.instance().mapLayersByName("QUADRAS")[0]
layerImovel.startEditing()
layerQuadras.startEditing()

quadra_field = 'quadra'  # Altere para o nome correto do campo se necessário

layerQuadras.removeSelection()  # Garante que começa sem seleção

imoveis = list(layerImovel.selectedFeatures())
i = 0
while i < len(imoveis):
    imovel = imoveis[i]
    imv_id = imovel['imv_id']
    rot_id = imovel['rot_id']

    # Procura primeiro por quadra diferente da rota
    filtro_dif = (db['MATRICULA'] == imv_id) & (db['ROTA'] == rot_id) & (db['QUADRA'] != rot_id)
    quadras_dif = db.loc[filtro_dif, 'QUADRA']

    if not quadras_dif.empty:
        dbQuadra = quadras_dif.iloc[0]
    else:
        # Se não encontrar, aceita quadra igual à rota
        filtro_igual = (db['MATRICULA'] == imv_id) & (db['ROTA'] == rot_id) & (db['QUADRA'] == rot_id)
        quadras_igual = db.loc[filtro_igual, 'QUADRA']
        if not quadras_igual.empty:
            dbQuadra = quadras_igual.iloc[0]
        else:
            # Não encontrou quadra para essa matrícula, vai para a próxima
            i += 1
            continue

    layerQuadras.removeSelection()  # Deseleciona antes de selecionar nova quadra

    # Seleciona apenas o imóvel atual
    layerImovel.removeSelection()
    layerImovel.selectByIds([imovel.id()])

    # Seleciona a quadra que contém o imóvel atual
    processing.run("native:selectbylocation", {
        'INPUT': layerQuadras,
        'PREDICATE': [0,1,4,5,6,7],  # intersects
        'INTERSECT': QgsProcessingFeatureSourceDefinition(
            'IMÓVEL',
            selectedFeaturesOnly=True,
            featureLimit=-1,
            flags=QgsProcessingFeatureSourceDefinition.FlagOverrideDefaultGeometryCheck,
            geometryCheck=QgsFeatureRequest.GeometryNoCheck
        ),
        'METHOD': 0
    })

    # Atualiza o atributo da quadra selecionada
    for quadra in layerQuadras.selectedFeatures():
        quadra.setAttribute(quadra_field, int(dbQuadra))
        layerQuadras.updateFeature(quadra)
        print(f'Quadra {quadra.id()} atualizada para {dbQuadra} (matricula {imv_id})')
        break  # Só atualiza a primeira quadra encontrada

    i += 1

layerQuadras.removeSelection()  # Deseleciona ao final
# layerQuadras.commitChanges()
# layerImovel.removeSelection()
