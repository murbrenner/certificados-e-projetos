#NOME: Alinhar Arruamento com Bordas Quadras

#DESCRIÇÃO: alinharArruamentoComBordasQuadras.py Alinha os vértices dos polígonos pré-selecionados em 'QUADRAS' com os vértices das linhas pré-selecionadas em 'ARRUAMENTO_MA'. Algoritmo (snap vértice-para-vértice): 1. Extrai todos os vértices das linhas selecionadas em ARRUAMENTO_MA. 2. Para cada vértice do polígono em QUADRAS, ve.

#PRÉ-REQUISITO: Selecionar previamente as feicoes que serao processadas.


# -*- coding: utf-8 -*-
"""
alinharArruamentoComBordasQuadras.py

Alinha os vértices dos polígonos pré-selecionados em 'QUADRAS' com os
vértices das linhas pré-selecionadas em 'ARRUAMENTO_MA'.

Algoritmo (snap vértice-para-vértice):
  1. Extrai todos os vértices das linhas selecionadas em ARRUAMENTO_MA.
  2. Para cada vértice do polígono em QUADRAS, verifica se há um vértice
     de ARRUAMENTO próximo a ele (dentro de SNAP_DISTANCE).
  3. Se encontrar, substitui as coordenadas do vértice do polígono pelo
     vértice exato da linha de ARRUAMENTO.

A camada 'QUADRAS' fica em modo de edição aguardando commit/rollback manual.

Execução: Cole no console Python do QGIS
          (Plugins > Console Python > Mostrar editor > Executar).
"""

import math

from qgis.core import (
    QgsProject,
    QgsGeometry,
    QgsPointXY,
    QgsWkbTypes,
)

# ══════════════════════════════════════════════════════════════════
# CONFIGURAÇÕES — ajuste antes de executar
# ══════════════════════════════════════════════════════════════════

NOME_ARRUAMENTO = 'ARRUAMENTO_MA'
NOME_QUADRAS    = 'QUADRAS'

# Distância máxima de snap: vértices de QUADRAS dentro desta distância
# de um vértice de ARRUAMENTO serão capturados e igualados.
#
# CRS: SIRGAS 2000 UTM zone 235 (EPSG:31983) — em METROS
#      10.0  = 10 metros   (padrão)
#      5.0   = 5 metros    (mais rígido)
#      20.0  = 20 metros   (mais flexível)
#
# Se vértices próximos não estão sendo capturados, aumente este valor.
SNAP_DISTANCE = 10.0  # ← valor em metros para UTM

# ══════════════════════════════════════════════════════════════════


# ──────────────────────────────────────────────────────────────────
# Funções auxiliares
# ──────────────────────────────────────────────────────────────────

def _get_layer(nome):
    """Obtém a camada pelo nome do projeto QGIS."""
    camadas = QgsProject.instance().mapLayersByName(nome)
    if not camadas:
        raise ValueError(f"Camada '{nome}' não encontrada no projeto QGIS.")
    return camadas[0]


def _dist2d(pt1, pt2):
    """Distância euclidiana entre dois QgsPointXY."""
    return math.sqrt((pt1.x() - pt2.x()) ** 2 + (pt1.y() - pt2.y()) ** 2)


def _encontrar_vertice_proximo(pt, vertices_referencia, snap_dist):
    """
    Busca o vértice mais próximo em 'vertices_referencia' que esteja
    dentro de 'snap_dist' do ponto 'pt'.
    Retorna (QgsPointXY ou None, distância).
    """
    melhor_pt = None
    melhor_dist = snap_dist
    for v in vertices_referencia:
        d = _dist2d(pt, v)
        if d < melhor_dist:
            melhor_dist = d
            melhor_pt = v
    return melhor_pt, melhor_dist


def _snap_anel(anel, vertices_referencia, snap_dist):
    """
    Aplica snap tipo vértice-para-vértice em um anel do polígono.
    anel: lista de QgsPointXY (primeiro == último para anel fechado).
    Retorna (novo_anel, qtd_verts_movidos).
    """
    novos_pts = []
    movidos = 0
    for pt in anel:
        v_proximo, dist = _encontrar_vertice_proximo(pt, vertices_referencia, snap_dist)
        if v_proximo is not None:
            novos_pts.append(QgsPointXY(v_proximo.x(), v_proximo.y()))
            movidos += 1
        else:
            novos_pts.append(pt)
    return novos_pts, movidos


# ──────────────────────────────────────────────────────────────────
# Carregar camadas e validar seleções
# ──────────────────────────────────────────────────────────────────

camada_arr  = _get_layer(NOME_ARRUAMENTO)
camada_quad = _get_layer(NOME_QUADRAS)

linhas_sel    = list(camada_arr.selectedFeatures())
poligonos_sel = list(camada_quad.selectedFeatures())

if not linhas_sel:
    raise RuntimeError("Nenhuma linha selecionada em 'ARRUAMENTO_MA'.")
if not poligonos_sel:
    raise RuntimeError("Nenhum polígono selecionado em 'QUADRAS'.")

print(f"Linhas selecionadas    : {len(linhas_sel)}")
print(f"Polígonos selecionados : {len(poligonos_sel)}")

# ──────────────────────────────────────────────────────────────────
# Extrair todos os vértices das linhas de ARRUAMENTO
# ──────────────────────────────────────────────────────────────────

vertices_arruamento = []

for feat in linhas_sel:
    geom = feat.geometry()
    if geom.isEmpty():
        continue
    wt = geom.wkbType()
    if QgsWkbTypes.isMultiType(wt):
        for parte in geom.asMultiPolyline():
            vertices_arruamento.extend(parte)
    else:
        pts = geom.asPolyline()
        if pts:
            vertices_arruamento.extend(pts)

# Remover duplicatas (vértices que aparecem em múltiplas linhas)
vertices_unicos = []
for v in vertices_arruamento:
    # Verifica se este vértice já está na lista (com tolerância de 1e-12)
    encontrado = False
    for vu in vertices_unicos:
        if _dist2d(v, vu) < 1e-10:
            encontrado = True
            break
    if not encontrado:
        vertices_unicos.append(v)

print(f"Vértices de ARRUAMENTO : {len(vertices_arruamento)} (únicos: {len(vertices_unicos)})")

if not vertices_unicos:
    raise RuntimeError("Nenhum vértice extraído das linhas de ARRUAMENTO_MA.")

# ──────────────────────────────────────────────────────────────────
# Aplicar snap vertex-to-vertex nos polígonos de QUADRAS
# ──────────────────────────────────────────────────────────────────

camada_quad.startEditing()

alterados           = 0
sem_modificacao     = 0
total_verts_movidos = 0
erros               = 0

for feat in poligonos_sel:
    fid  = feat.id()
    geom = feat.geometry()

    if geom.isEmpty():
        continue

    wt       = geom.wkbType()
    is_multi = QgsWkbTypes.isMultiType(wt)
    partes   = geom.asMultiPolygon() if is_multi else [geom.asPolygon()]

    novas_partes  = []
    verts_movidos = 0

    for parte in partes:
        novos_aneis = []
        for anel in parte:
            novo_anel, mv = _snap_anel(anel, vertices_unicos, SNAP_DISTANCE)
            novos_aneis.append(novo_anel)
            verts_movidos += mv
        novas_partes.append(novos_aneis)

    if verts_movidos == 0:
        sem_modificacao += 1
        continue

    nova_geom = (
        QgsGeometry.fromMultiPolygonXY(novas_partes)
        if is_multi
        else QgsGeometry.fromPolygonXY(novas_partes[0])
    )

    if nova_geom.isEmpty():
        erros += 1
        print(f"  FID {fid}: geometria resultante vazia — ignorado.")
        continue

    if camada_quad.changeGeometry(fid, nova_geom):
        alterados += 1
        total_verts_movidos += verts_movidos
    else:
        erros += 1
        print(f"  FID {fid}: falha ao aplicar nova geometria.")

# ──────────────────────────────────────────────────────────────────
# Atualizar visualização e reportar resultado
# ──────────────────────────────────────────────────────────────────

camada_quad.updateExtents()
camada_quad.triggerRepaint()

print()
print("═" * 56)
print(f"  Polígonos alterados                : {alterados}")
print(f"  Vértices capturados/movidos (total): {total_verts_movidos}")
print(f"  Polígonos sem vértice próximo      : {sem_modificacao}")
print(f"  Erros                              : {erros}")
print("═" * 56)
print("  Camada 'QUADRAS' em modo de edição.")
print("  Faça commit (✓) ou rollback (✗) manualmente.")
print("═" * 56)
