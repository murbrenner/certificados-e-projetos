#NOME: Remover Duplicidade de Quadras

#DESCRIÇÃO: Remove feicoes ou inconsistencias com base nos criterios implementados neste script. Camadas envolvidas: 'QUADRAS'.

#PRÉ-REQUISITO: Carregar a camada 'QUADRAS' no projeto QGIS; selecionar previamente as feicoes que serao processadas.


from qgis.core import QgsProject

layer = QgsProject.instance().mapLayersByName("QUADRAS")[0]
layer.startEditing()

selected_feats = list(layer.selectedFeatures())

geom_map = {}

for feat in selected_feats:
    clean_geom = feat.geometry().buffer(0, 5)
    geom_map[feat.id()] = clean_geom

remover_ids = set()

for i, feat in enumerate(selected_feats):
    if feat.id() in remover_ids:
        continue

    geom_i = geom_map[feat.id()]

    for j in range(i + 1, len(selected_feats)):
        other = selected_feats[j]
        if other.id() in remover_ids:
            continue

        geom_j = geom_map[other.id()]

        if geom_i.equals(geom_j) or geom_i.intersects(geom_j):
            remover_ids.add(max(feat.id(), other.id()))

print(f"Removendo {len(remover_ids)} feições duplicadas selecionadas...")
layer.deleteFeatures(list(remover_ids))

#layer.commitChanges()
print("Remoção concluída.")
