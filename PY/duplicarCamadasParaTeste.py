#NOME: Duplicar Camadas para Teste

#DESCRIÇÃO: Duplica as camadas 'ARRUAMENTO_MA' e 'QUADRAS' preservando simbologia, estilo e CRS, criando cópias de trabalho para testes sem alterar as camadas originais do projeto.

#PRÉ-REQUISITO: Ter as camadas 'ARRUAMENTO_MA' e 'QUADRAS' carregadas no projeto QGIS para que as cópias de teste sejam geradas corretamente.


# -*- coding: utf-8 -*-
"""
duplicarCamadasParaTeste.py

Duplica as camadas 'ARRUAMENTO_MA' e 'QUADRAS' com todas as suas
características visuais (simbologia, cores, estilos, CRS).

As cópias são adicionadas ao projeto QGIS sem afetar as originais.
Você pode então testar o alinhamento nas cópias.

Execução: Cole no console Python do QGIS
          (Plugins > Console Python > Mostrar editor > Executar).
"""

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsMapLayerStyle,
)

# ══════════════════════════════════════════════════════════════════
# CONFIGURAÇÕES
# ══════════════════════════════════════════════════════════════════

CAMADAS_PARA_DUPLICAR = ['ARRUAMENTO_MA', 'QUADRAS']
SUFIXO_COPIA = '_TESTE'  # A cópia será nomeada: ARRUAMENTO_MA_TESTE, etc.

# ══════════════════════════════════════════════════════════════════


def _get_layer(nome):
    """Obtém a camada pelo nome do projeto QGIS."""
    camadas = QgsProject.instance().mapLayersByName(nome)
    if not camadas:
        return None
    return camadas[0]


def _duplicar_camada(camada_original, sufixo):
    """
    Duplica uma camada mantendo:
      - Geometrias (feature-by-feature)
      - CRS (sistema de coordenadas)
      - Campos de atributos
      - Simbologia (estilo visual)
    
    Retorna a nova camada adicionada ao projeto.
    """
    projeto = QgsProject.instance()
    
    # Nome da nova camada
    novo_nome = camada_original.name() + sufixo
    
    # Checar se já existe cópia com este nome
    if _get_layer(novo_nome):
        print(f"  ⚠️  Camada '{novo_nome}' já existe. Pulando...")
        return None
    
    # Criar nova camada com o mesmo tipo de geometria e CRS
    nova_camada = QgsVectorLayer(
        f"{camada_original.geometryType()}?crs={camada_original.crs().authid()}",
        novo_nome,
        'memory',
    )
    
    # Copiar os campos de atributos
    nova_camada.dataProvider().addAttributes(camada_original.fields())
    nova_camada.updateFields()
    
    # Copiar as features (geometrias + atributos)
    features = list(camada_original.getFeatures())
    nova_camada.dataProvider().addFeatures(features)
    
    # Copiar a simbologia (estilo visual)
    estilo = QgsMapLayerStyle()
    estilo.readFromLayer(camada_original)
    estilo.writeToLayer(nova_camada)
    
    # Adicionar a nova camada ao projeto
    projeto.addMapLayer(nova_camada)
    
    print(f"  ✓ Camada '{novo_nome}' criada com sucesso")
    return nova_camada


# ──────────────────────────────────────────────────────────────────
# Processar cada camada
# ──────────────────────────────────────────────────────────────────

projeto = QgsProject.instance()
criadas = 0

print("Duplicando camadas...")
print()

for nome_original in CAMADAS_PARA_DUPLICAR:
    camada = _get_layer(nome_original)
    
    if not camada:
        print(f"  ✗ Camada '{nome_original}' não encontrada.")
        continue
    
    print(f"  Processando: {nome_original}")
    print(f"    • Tipo de geometria: {camada.geometryType()}")
    print(f"    • CRS: {camada.crs().authid()}")
    print(f"    • Features: {camada.featureCount()}")
    print(f"    • Campos: {len(camada.fields())}")
    
    nova = _duplicar_camada(camada, SUFIXO_COPIA)
    if nova:
        criadas += 1
    print()

# ──────────────────────────────────────────────────────────────────
# Resultado final
# ──────────────────────────────────────────────────────────────────

print("═" * 56)
print(f"  Camadas duplicadas: {criadas}")
print("═" * 56)
print("  Próximo passo:")
print(f"  1. Selecione as linhas em 'ARRUAMENTO_MA{SUFIXO_COPIA}'")
print(f"  2. Selecione os polígonos em 'QUADRAS{SUFIXO_COPIA}'")
print("  3. Execute: alinharArruamentoComBordasQuadras.py")
print("  4. Se funcionar, repita com as originais.")
print("═" * 56)
