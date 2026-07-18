#NOME: Relatorio QGIS Profissional

#DESCRIÇÃO: Executa rotina de automacao cadastral no QGIS conforme a implementacao do script. Inclui leitura e/ou exportacao de dados em CSV. Camadas envolvidas: 'ARRUAMENTO_MA', 'FIM_PNT', 'IMÓVEL', 'INICIO_PNT', 'MUNICÍPIOS'.

#PRÉ-REQUISITO: Carregar as camadas 'ARRUAMENTO_MA', 'FIM_PNT', 'IMÓVEL', 'INICIO_PNT', 'MUNICÍPIOS' no projeto QGIS; selecionar previamente as feicoes que serao processadas; garantir arquivo CSV valido e no layout esperado.


from qgis.core import *
from collections import defaultdict
from datetime import datetime
import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
import urllib.request
import urllib.parse
import json
import time

# --- Config: enable external geocoding (IBGE or Nominatim) when you have internet
USE_EXTERNAL_GEOCODING = False
EXTERNAL_GEOCODING_PROVIDER = 'nominatim'
EXTERNAL_GEOCODING_DELAY = 1.0


# === CAMADAS ===
imovel = QgsProject.instance().mapLayersByName('IMÓVEL')[0]
overlay = QgsProject.instance().mapLayersByName('OVERLEY')[0]
inicio_pnt = QgsProject.instance().mapLayersByName('INICIO_PNT')[0]
fim_pnt = QgsProject.instance().mapLayersByName('FIM_PNT')[0]
quadras = QgsProject.instance().mapLayersByName('QUADRAS')[0]
municipios = QgsProject.instance().mapLayersByName('MUNICÍPIOS')[0]
arruamento = None
rotas_layer = None
try:
    arruamento = QgsProject.instance().mapLayersByName('ARRUAMENTO_MA')[0]
except Exception:
    print('Camada ARRUAMENTO_MA não encontrada; será ignorada')
try:
    rotas_layer = QgsProject.instance().mapLayersByName('ROTAS DE LEITURA')[0]
except Exception:
    print('Camada "ROTAS DE LEITURA" não encontrada; será ignorada')

# === DICIONÁRIOS ===
dados = defaultdict(lambda: {
    'municipio': '',
    'qtd_imoveis': 0,
    'qtd_imoveis_com_matricula': 0,
    'qtd_imoveis_sem_matricula': 0,
    'qtd_quadras': 0,
    'tem_arruamento': False,
    'latitude': None,
    'longitude': None,
    'qtd_rotas_layer': 0,
    'tem_overlay': False,
    'tem_inicio': False,
    'tem_fim': False
})

# === Seleção de municípios ===
selected_municipios = [f['nm_municip'] for f in municipios.selectedFeatures()]
use_selected = len(selected_municipios) > 0
if use_selected:
    selected_set = set(selected_municipios)
    print('Usando municípios selecionados:', ', '.join(sorted(selected_set)))
else:
    selected_set = None


# === Construir índices espaciais ===
def build_index_for_layer(layer, name, report_every=100000):
    idx = QgsSpatialIndex()
    cnt = 0
    total = layer.featureCount() if hasattr(layer, 'featureCount') else None
    for feat in layer.getFeatures():
        idx.addFeature(feat)
        cnt += 1
        if cnt % report_every == 0:
            print(f'Indexando {name}: {cnt}' + (f' / {total}' if total else ''))
    print(f'Index para {name} criado: {cnt} features')
    return idx

print('Construindo índices espaciais para camadas grandes...')
imovel_idx = build_index_for_layer(imovel, 'IMÓVEL', report_every=100000)
quadras_idx = build_index_for_layer(quadras, 'QUADRAS', report_every=100000)
overlay_idx = build_index_for_layer(overlay, 'OVERLEY', report_every=100000)
inicio_idx = build_index_for_layer(inicio_pnt, 'INICIO_PNT', report_every=100000)
fim_idx = build_index_for_layer(fim_pnt, 'FIM_PNT', report_every=100000)
if arruamento is not None:
    arruamento_idx = build_index_for_layer(arruamento, 'ARRUAMENTO_MA', report_every=100000)
else:
    arruamento_idx = None
if rotas_layer is not None:
    rotas_idx = build_index_for_layer(rotas_layer, 'ROTAS DE LEITURA', report_every=100000)
else:
    rotas_idx = None

# Preparar transformações de coordenadas
project = QgsProject.instance()
transform_context = project.transformContext()
muni_crs = municipios.crs()
def _get_transform(layer):
    try:
        if layer.crs() != muni_crs:
            return QgsCoordinateTransform(layer.crs(), muni_crs, transform_context)
    except Exception:
        return None
    return None

transforms = {
    'imovel': _get_transform(imovel),
    'quadras': _get_transform(quadras),
    'overlay': _get_transform(overlay),
    'inicio': _get_transform(inicio_pnt),
    'fim': _get_transform(fim_pnt),
    'arruamento': _get_transform(arruamento) if arruamento is not None else None,
    'rotas': _get_transform(rotas_layer) if rotas_layer is not None else None
}


# --- Helper: external geocoding (optional) ---
_external_cache = {}
_external_cache_loaded = False

def _load_external_cache(cache_path):
    global _external_cache, _external_cache_loaded
    try:
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as cf:
                _external_cache = json.load(cf)
        else:
            _external_cache = {}
    except Exception:
        _external_cache = {}
    _external_cache_loaded = True

def _save_external_cache(cache_path):
    try:
        with open(cache_path, 'w', encoding='utf-8') as cf:
            json.dump(_external_cache, cf, ensure_ascii=False, indent=2)
    except Exception:
        pass

def _query_nominatim(municipio_name, country_hint='Brazil'):
    base = 'https://nominatim.openstreetmap.org/search'
    q = f"{municipio_name}, {country_hint}"
    params = {'q': q, 'format': 'jsonv2', 'limit': 1}
    url = base + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'relatorioQGIS/1.0 (+https://example.org)'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            arr = json.loads(data.decode('utf-8'))
            if arr:
                item = arr[0]
                lat = float(item.get('lat'))
                lon = float(item.get('lon'))
                return lat, lon
    except Exception:
        return None

def _query_ibge(municipio_name):
    try:
        nm = urllib.parse.quote(municipio_name)
        url = f'https://servicodados.ibge.gov.br/api/v1/localidades/municipios?nome={nm}'
        req = urllib.request.Request(url, headers={'User-Agent': 'relatorioQGIS/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            arr = json.loads(data.decode('utf-8'))
            if arr:
                return None
    except Exception:
        return None

def _get_external_coords(municipio_name, cache_path=None):
    key = municipio_name.strip().upper()
    if not key:
        return None
    if not _external_cache_loaded and cache_path:
        _load_external_cache(cache_path)
    if key in _external_cache:
        return tuple(_external_cache[key])
    latlon = None
    if EXTERNAL_GEOCODING_PROVIDER == 'ibge':
        latlon = _query_ibge(municipio_name)
        if latlon is None:
            time.sleep(EXTERNAL_GEOCODING_DELAY)
            latlon = _query_nominatim(municipio_name)
    else:
        latlon = _query_nominatim(municipio_name)
        if latlon is None:
            time.sleep(EXTERNAL_GEOCODING_DELAY)
            latlon = _query_ibge(municipio_name)
    if latlon is not None and cache_path:
        try:
            _external_cache[key] = [latlon[0], latlon[1]]
            _save_external_cache(cache_path)
        except Exception:
            pass
    time.sleep(EXTERNAL_GEOCODING_DELAY)
    return latlon


# DEBUG: mostrar campos e amostra de imv_id
try:
    print('Campos IMÓVEL:', imovel.fields().names())
    sample = []
    cnt = 0
    for ff in imovel.getFeatures():
        if 'imv_id' in ff.fields().names():
            sample.append(ff['imv_id'])
        else:
            for cand in ('IMV_ID', 'imvId', 'imvId'.upper()):
                if cand in ff.fields().names():
                    sample.append(ff[cand])
                    break
        cnt += 1
        if cnt >= 10:
            break
    print('Amostra imv_id (até 10):', sample)
except Exception as e:
    print('Erro ao obter amostra de imv_id:', e)


# Lista de feições de município a processar
if use_selected:
    municipio_features = list(municipios.selectedFeatures())
else:
    municipio_features = list(municipios.getFeatures())

print(f'Processando {len(municipio_features)} municípios...')
for mf in municipio_features:
    nome = mf['nm_municip']
    if not nome:
        continue
    dados[nome]['municipio'] = nome
    muni_geom = mf.geometry()
    if muni_geom is None or muni_geom.isEmpty():
        continue
    
    def muni_geom_for_layer(layer):
        try:
            layer_crs = layer.crs()
        except Exception:
            return QgsGeometry(muni_geom)
        try:
            if layer_crs != muni_crs:
                tr = QgsCoordinateTransform(muni_crs, layer_crs, transform_context)
                mg = QgsGeometry(muni_geom)
                mg.transform(tr)
                return mg
        except Exception:
            pass
        return QgsGeometry(muni_geom)

    # Calcular coordenadas representativas do município em WGS84
    try:
        mg = QgsGeometry(muni_geom)
        if hasattr(mg, 'pointOnSurface'):
            rep = mg.pointOnSurface()
        else:
            rep = mg.centroid()
        if rep is None or rep.isEmpty():
            dados[nome]['latitude'] = None
            dados[nome]['longitude'] = None
        else:
            try:
                crs_wgs = QgsCoordinateReferenceSystem(4326)
                tr_wgs = QgsCoordinateTransform(muni_crs, crs_wgs, transform_context)
                rep_geom = QgsGeometry(rep)
                rep_geom.transform(tr_wgs)
                pt = rep_geom.asPoint()
                dados[nome]['latitude'] = round(pt.y(), 6)
                dados[nome]['longitude'] = round(pt.x(), 6)
            except Exception:
                dados[nome]['latitude'] = None
                dados[nome]['longitude'] = None
    except Exception:
        dados[nome]['latitude'] = None
        dados[nome]['longitude'] = None

    # Geocoding externo (opcional)
    try:
        if USE_EXTERNAL_GEOCODING:
            try:
                cache_path = os.path.join(project.homePath() if project and project.homePath() else os.getcwd(), '.cache_muni_coords.json')
            except Exception:
                cache_path = os.path.join(os.getcwd(), '.cache_muni_coords.json')
            ext = _get_external_coords(nome, cache_path)
            if ext is not None:
                try:
                    dados[nome]['latitude'] = round(float(ext[0]), 6)
                    dados[nome]['longitude'] = round(float(ext[1]), 6)
                except Exception:
                    pass
    except Exception:
        pass

    # IMÓVEL
    muni_imovel = muni_geom_for_layer(imovel)
    cand = set(imovel_idx.intersects(muni_imovel.boundingBox()))
    if cand:
        req = QgsFeatureRequest().setFilterFids(list(cand))
        for f in imovel.getFeatures(req):
            g = f.geometry()
            if g is None:
                continue
            g = QgsGeometry(g)
            tr = transforms.get('imovel')
            if tr is not None:
                try:
                    g.transform(tr)
                except Exception:
                    pass
            try:
                if not (muni_geom.contains(g) or muni_geom.intersects(g)):
                    continue
            except Exception:
                if not muni_geom.intersects(g):
                    continue
            dados[nome]['qtd_imoveis'] += 1
            v = None
            if 'imv_id' in f.fields().names():
                v = f['imv_id']
            else:
                for cand in ('IMV_ID', 'imvId', 'IMVId'):
                    if cand in f.fields().names():
                        v = f[cand]
                        break
            has_mat = False
            if v is None:
                has_mat = False
            else:
                try:
                    if float(v) != 0:
                        has_mat = True
                except Exception:
                    sv = str(v).strip()
                    if sv and sv.upper() not in ('0', 'NULL'):
                        has_mat = True
            if has_mat:
                dados[nome]['qtd_imoveis_com_matricula'] += 1
            else:
                dados[nome]['qtd_imoveis_sem_matricula'] += 1

    # ARRUAMENTO_MA
    if arruamento_idx is not None:
        muni_arr = muni_geom_for_layer(arruamento)
        cand = arruamento_idx.intersects(muni_arr.boundingBox())
        if cand:
            req = QgsFeatureRequest().setFilterFids(cand)
            for f in arruamento.getFeatures(req):
                g = f.geometry()
                if g is None:
                    continue
                try:
                    if not (muni_arr.contains(g) or muni_arr.intersects(g)):
                        continue
                except Exception:
                    if not muni_arr.intersects(g):
                        continue
                dados[nome]['tem_arruamento'] = True
                break

    # QUADRAS
    muni_quad = muni_geom_for_layer(quadras)
    cand = quadras_idx.intersects(muni_quad.boundingBox())
    if cand:
        req = QgsFeatureRequest().setFilterFids(cand)
        for f in quadras.getFeatures(req):
            g = f.geometry()
            if g is None:
                continue
            try:
                if not (muni_quad.contains(g) or muni_quad.intersects(g)):
                    continue
            except Exception:
                if not muni_quad.intersects(g):
                    continue
            dados[nome]['qtd_quadras'] += 1

    # OVERLEY
    muni_ov = muni_geom_for_layer(overlay)
    cand = overlay_idx.intersects(muni_ov.boundingBox())
    if cand:
        req = QgsFeatureRequest().setFilterFids(cand)
        for f in overlay.getFeatures(req):
            g = f.geometry()
            if g is None:
                continue
            try:
                if not (muni_ov.contains(g) or muni_ov.intersects(g)):
                    continue
            except Exception:
                if not muni_ov.intersects(g):
                    continue
            dados[nome]['tem_overlay'] = True

    # INICIO_PNT
    muni_ini = muni_geom_for_layer(inicio_pnt)
    cand = inicio_idx.intersects(muni_ini.boundingBox())
    if cand:
        req = QgsFeatureRequest().setFilterFids(cand)
        for f in inicio_pnt.getFeatures(req):
            g = f.geometry()
            if g is None:
                continue
            try:
                if not (muni_ini.contains(g) or muni_ini.intersects(g)):
                    continue
            except Exception:
                if not muni_ini.intersects(g):
                    continue
            dados[nome]['tem_inicio'] = True

    # FIM_PNT
    muni_fim = muni_geom_for_layer(fim_pnt)
    cand = fim_idx.intersects(muni_fim.boundingBox())
    if cand:
        req = QgsFeatureRequest().setFilterFids(cand)
        for f in fim_pnt.getFeatures(req):
            g = f.geometry()
            if g is None:
                continue
            try:
                if not (muni_fim.contains(g) or muni_fim.intersects(g)):
                    continue
            except Exception:
                if not muni_fim.intersects(g):
                    continue
            dados[nome]['tem_fim'] = True

    # ROTAS DE LEITURA
    if rotas_idx is not None:
        muni_rot = muni_geom_for_layer(rotas_layer)
        cand = rotas_idx.intersects(muni_rot.boundingBox())
        if cand:
            req = QgsFeatureRequest().setFilterFids(cand)
            for f in rotas_layer.getFeatures(req):
                g = f.geometry()
                if g is None:
                    continue
                try:
                    if not (muni_rot.contains(g) or muni_rot.intersects(g)):
                        continue
                except Exception:
                    if not muni_rot.intersects(g):
                        continue
                dados[nome]['qtd_rotas_layer'] += 1

    arr_flag_dbg = 'OK' if dados[nome].get('tem_arruamento') else 'NÃO'
    print(f"{nome}: imoveis={dados[nome]['qtd_imoveis']} | com_mat={dados[nome]['qtd_imoveis_com_matricula']} | sem_mat={dados[nome]['qtd_imoveis_sem_matricula']} | quadras={dados[nome]['qtd_quadras']} | arruamento={arr_flag_dbg} | rotas_layer={dados[nome]['qtd_rotas_layer']}")


# === EXPORTAR CSV ===
desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
data_pasta = datetime.now().strftime("RELATORIO-%d-%m-%Y")
pasta_relatorio = os.path.join(desktop, data_pasta)
os.makedirs(pasta_relatorio, exist_ok=True)

csv_path = os.path.join(pasta_relatorio, "relatorio_municipios.csv")

with open(csv_path, 'w', encoding='utf-8') as f:
    f.write("Municipio;Latitude;Longitude;Qtd_Imoveis;Com_Matricula;Sem_Matricula;Qtd_Quadras;Tem_Arruamento;Qtd_Rotas_Layer;Tem_Overlay;Tem_Inicio;Tem_Fim\n")
    for m, d in dados.items():
        arr_flag = 'OK' if d.get('tem_arruamento') else 'NÃO'
        lat = d.get('latitude')
        lon = d.get('longitude')
        if isinstance(lat, float):
            lat_s = f"{lat:.6f}"
        elif lat is None:
            lat_s = ""
        else:
            lat_s = str(lat)
        if isinstance(lon, float):
            lon_s = f"{lon:.6f}"
        elif lon is None:
            lon_s = ""
        else:
            lon_s = str(lon)
        f.write(
            f"{d['municipio']};{lat_s};{lon_s};{d['qtd_imoveis']};{d['qtd_imoveis_com_matricula']};{d['qtd_imoveis_sem_matricula']};"
            f"{d['qtd_quadras']};{arr_flag};{d['qtd_rotas_layer']};{d['tem_overlay']};{d['tem_inicio']};{d['tem_fim']}\n"
        )


# === GERAR PDF PROFISSIONAL ===
pdf_path = os.path.join(pasta_relatorio, "relatorio_municipios_executivo.pdf")

# Classe para cabeçalho e rodapé
class ReportCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, total_pages):
        self.saveState()
        # Barra superior suave
        self.setFillColor(colors.HexColor("#3B8FBF"))
        self.rect(0, landscape(A4)[1] - 0.6*cm, landscape(A4)[0], 0.6*cm, fill=1, stroke=0)
        
        # Texto no cabeçalho
        self.setFont('Helvetica', 9)
        self.setFillColor(colors.white)
        self.drawString(1*cm, landscape(A4)[1] - 0.4*cm, "CAEMA | Coordenadoria de Cadastro e Geoprocessamento")
        
        # Rodapé minimalista
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.HexColor("#888888"))
        page_num = f"Página {self._pageNumber} de {total_pages}"
        self.drawRightString(landscape(A4)[0] - 1*cm, 0.6*cm, page_num)
        data_rodape = datetime.now().strftime("%d/%m/%Y às %H:%M")
        self.drawString(1*cm, 0.6*cm, data_rodape)
        
        # Linha inferior suave
        self.setStrokeColor(colors.HexColor("#D0E8F0"))
        self.setLineWidth(1)
        self.line(1*cm, 1*cm, landscape(A4)[0] - 1*cm, 1*cm)
        
        self.restoreState()

# Estilos customizados
styles = getSampleStyleSheet()
style_title = ParagraphStyle(
    'CustomTitle',
    parent=styles['Title'],
    fontSize=26,
    textColor=colors.HexColor("#0D4F6E"),
    spaceAfter=30,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold',
    leading=32
)
style_heading = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading1'],
    fontSize=18,
    textColor=colors.HexColor("#3B8FBF"),
    spaceAfter=16,
    spaceBefore=20,
    fontName='Helvetica-Bold',
    borderWidth=0,
    leftIndent=0,
    borderPadding=8,
    backColor=colors.white
)
style_normal = ParagraphStyle(
    'CustomNormal',
    parent=styles['Normal'],
    fontSize=10,
    alignment=TA_JUSTIFY,
    spaceAfter=6
)

doc = SimpleDocTemplate(
    pdf_path,
    pagesize=landscape(A4),
    rightMargin=1*cm,
    leftMargin=1*cm,
    topMargin=2*cm,
    bottomMargin=2*cm
)
elements = []

# === PÁGINA 1: CAPA MODERNA 2025 ===
elements.append(Spacer(1, 1*cm))

# Logo CAEMA
try:
    logo_caema_path = os.path.join(os.path.dirname(__file__), 'logo_caema.png')
    if os.path.exists(logo_caema_path):
        logo_caema = Image(logo_caema_path, width=10*cm, height=3*cm, kind='proportional')
        elements.append(logo_caema)
    else:
        logo_placeholder = Paragraph(
            "<b>CAEMA</b>",
            ParagraphStyle('logo', parent=styles['Title'], fontSize=32, alignment=TA_CENTER, 
                          textColor=colors.HexColor("#3B8FBF"), fontName='Helvetica-Bold')
        )
        elements.append(logo_placeholder)
except:
    logo_placeholder = Paragraph(
        "<b>CAEMA</b>",
        ParagraphStyle('logo', parent=styles['Title'], fontSize=32, alignment=TA_CENTER, 
                      textColor=colors.HexColor("#3B8FBF"), fontName='Helvetica-Bold')
    )
    elements.append(logo_placeholder)

elements.append(Spacer(1, 1.2*cm))

# Título principal moderno
titulo = Paragraph(
    "<b>RELATÓRIO DE GEOPROCESSAMENTO</b>",
    ParagraphStyle('modern_title', parent=style_title, fontSize=26, 
                  textColor=colors.HexColor("#0D4F6E"), spaceAfter=8, leading=30)
)
elements.append(titulo)

# Subtítulo coordenadoria
subtitulo = Paragraph(
    "<b>COORDENADORIA DE CADASTRO E GEOPROCESSAMENTO</b>",
    ParagraphStyle('subtitle', parent=styles['Normal'], fontSize=14, alignment=TA_CENTER, 
                  textColor=colors.HexColor("#3B8FBF"), spaceAfter=10, fontName='Helvetica-Bold')
)
elements.append(subtitulo)
elements.append(Spacer(1, 1.5*cm))

# Cards informativos modernos na capa (visual mais leve)
data_geracao = datetime.now().strftime("%d/%m/%Y")

info_cards = [
    ["📅  DATA", "📊  MUNICÍPIOS", "🗺️  QGIS"],
    [data_geracao, str(len(dados)), "3.44.5"],
]

info_table = Table(info_cards, colWidths=[9*cm, 9*cm, 9*cm])
info_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E8F4F8")),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#0D4F6E")),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 11),
    ('FONTSIZE', (0, 1), (-1, 1), 16),
    ('TOPPADDING', (0, 0), (-1, -1), 12),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor("#A8D5E2")),
    ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor("#3B8FBF")),
    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
]))
elements.append(info_table)
elements.append(Spacer(1, 2*cm))

# Logo QGIS
try:
    logo_qgis_path = os.path.join(os.path.dirname(__file__), 'logo_qgis.png')
    if os.path.exists(logo_qgis_path):
        logo_qgis = Image(logo_qgis_path, width=4*cm, height=1.5*cm, kind='proportional')
        elements.append(logo_qgis)
    else:
        qgis_text = Paragraph(
            "<b>Powered by QGIS</b>",
            ParagraphStyle('qgis', parent=styles['Normal'], fontSize=11, alignment=TA_CENTER,
                          textColor=colors.HexColor("#589632"), fontName='Helvetica-Bold')
        )
        elements.append(qgis_text)
except:
    qgis_text = Paragraph(
        "<b>Powered by QGIS</b>",
        ParagraphStyle('qgis', parent=styles['Normal'], fontSize=11, alignment=TA_CENTER,
                      textColor=colors.HexColor("#589632"), fontName='Helvetica-Bold')
    )
    elements.append(qgis_text)

elements.append(Spacer(1, 0.5*cm))

elements.append(PageBreak())

# === PÁGINA 2: RESUMO ===
elements.append(Paragraph("<b>RESUMO</b>", style_heading))
elements.append(Spacer(1, 0.3*cm))

# Calcular totais e estatísticas
total_imoveis = sum(d['qtd_imoveis'] for d in dados.values())
total_com_matricula = sum(d['qtd_imoveis_com_matricula'] for d in dados.values())
total_sem_matricula = sum(d['qtd_imoveis_sem_matricula'] for d in dados.values())
total_quadras = sum(d['qtd_quadras'] for d in dados.values())
total_rotas_layer = sum(d['qtd_rotas_layer'] for d in dados.values())
qtd_municipios = len(dados)
qtd_com_arruamento = sum(1 for d in dados.values() if d.get('tem_arruamento'))
qtd_com_overlay = sum(1 for d in dados.values() if d.get('tem_overlay'))
qtd_com_inicio = sum(1 for d in dados.values() if d.get('tem_inicio'))
qtd_com_fim = sum(1 for d in dados.values() if d.get('tem_fim'))

# Percentuais
perc_matriculados = (total_com_matricula / total_imoveis * 100) if total_imoveis > 0 else 0
perc_arruamento = (qtd_com_arruamento / qtd_municipios * 100) if qtd_municipios > 0 else 0
perc_overlay = (qtd_com_overlay / qtd_municipios * 100) if qtd_municipios > 0 else 0

resumo_texto = f"""
Este relatório apresenta uma análise abrangente de {qtd_municipios} municípios, 
contemplando informações sobre imóveis cadastrados, infraestrutura de quadras, 
arruamento, rotas de leitura e demais elementos geoespaciais relevantes para 
gestão territorial e operações de campo.
<br/><br/>
<b>Principais Indicadores:</b><br/>
• Total de imóveis identificados: {total_imoveis:,}<br/>
• Índice de matrículas: {perc_matriculados:.1f}% ({total_com_matricula:,} imóveis)<br/>
• Quadras mapeadas: {total_quadras:,}<br/>
• Rotas de leitura: {total_rotas_layer:,}<br/>
• Municípios com arruamento: {qtd_com_arruamento} ({perc_arruamento:.1f}%)<br/>
• Municípios com overlay: {qtd_com_overlay} ({perc_overlay:.1f}%)<br/>
"""
elements.append(Paragraph(resumo_texto, style_normal))
elements.append(Spacer(1, 0.5*cm))

# Cards de indicadores principais
card_data = [
    ["INDICADOR", "VALOR", "OBSERVAÇÕES"],
    ["Total de Municípios", f"{qtd_municipios}", "Municípios analisados"],
    ["Total de Imóveis", f"{total_imoveis:,}", "Todos os imóveis identificados"],
    ["Imóveis com matrícula", f"{total_com_matricula:,}", f"{perc_matriculados:.1f}% do total"],
    ["Imóveis Sem Matrícula", f"{total_sem_matricula:,}", "Requer regularização"],
    ["Quadras Mapeadas", f"{total_quadras:,}", "Polígonos de quadras"],
    ["Rotas de Leitura", f"{total_rotas_layer:,}", "Rotas cadastradas"],
]

card_table = Table(card_data, colWidths=[6*cm, 4*cm, 8*cm])
card_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3B8FBF")),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('ALIGN', (1, 0), (1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 11),
    ('FONTSIZE', (0, 1), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('TOPPADDING', (0, 0), (-1, 0), 12),
    ('LEFTPADDING', (0, 0), (-1, -1), 14),
    ('RIGHTPADDING', (0, 0), (-1, -1), 14),
    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#D0E8F0")),
    ('LINEBELOW', (0, 0), (-1, 0), 0, colors.white),
    ('LINEBEFORE', (0, 0), (0, -1), 0, colors.white),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FBFD"), colors.white]),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
]))
elements.append(card_table)
elements.append(PageBreak())

# === PÁGINA 3: ANÁLISE DE COBERTURA ===
elements.append(Paragraph("<b>ANÁLISE DE COBERTURA TERRITORIAL</b>", style_heading))
elements.append(Spacer(1, 0.3*cm))

cobertura_texto = f"""
A análise de cobertura territorial avalia a presença de elementos essenciais 
para operações de campo e gestão territorial em cada município.
"""
elements.append(Paragraph(cobertura_texto, style_normal))
elements.append(Spacer(1, 0.3*cm))

cobertura_data = [
    ["ELEMENTO", "MUNICÍPIOS COM PRESENÇA", "PERCENTUAL", "STATUS"],
    ["Arruamento", f"{qtd_com_arruamento}/{qtd_municipios}", f"{perc_arruamento:.1f}%", "✓" if perc_arruamento > 50 else "⚠"],
    ["Overlay", f"{qtd_com_overlay}/{qtd_municipios}", f"{perc_overlay:.1f}%", "✓" if perc_overlay > 50 else "⚠"],
    ["Ponto de Início", f"{qtd_com_inicio}/{qtd_municipios}", f"{(qtd_com_inicio/qtd_municipios*100):.1f}%", "✓" if qtd_com_inicio > qtd_municipios/2 else "⚠"],
    ["Ponto de Fim", f"{qtd_com_fim}/{qtd_municipios}", f"{(qtd_com_fim/qtd_municipios*100):.1f}%", "✓" if qtd_com_fim > qtd_municipios/2 else "⚠"],
]

cobertura_table = Table(cobertura_data, colWidths=[7*cm, 5*cm, 4*cm, 3*cm])
cobertura_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3B8FBF")),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 11),
    ('FONTSIZE', (0, 1), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('TOPPADDING', (0, 0), (-1, 0), 12),
    ('LEFTPADDING', (0, 0), (-1, -1), 14),
    ('RIGHTPADDING', (0, 0), (-1, -1), 14),
    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#D0E8F0")),
    ('LINEBELOW', (0, 0), (-1, 0), 0, colors.white),
    ('LINEBEFORE', (0, 0), (0, -1), 0, colors.white),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F8FBFD"), colors.white]),
]))
elements.append(cobertura_table)
elements.append(Spacer(1, 0.5*cm))

# Análise crítica (box destacado)
elements.append(Paragraph("<b>Análise Crítica:</b>", ParagraphStyle('bold', parent=style_normal, fontName='Helvetica-Bold')))
analise_style = ParagraphStyle(
    'analise',
    parent=style_normal,
    leftIndent=15,
    rightIndent=15,
    spaceBefore=10,
    spaceAfter=10,
    backColor=colors.HexColor("#FFF9E6"),
    borderColor=colors.HexColor("#FFD700"),
    borderWidth=0,
    borderPadding=10
)
analise = f"""
• <b>Regularização Fundiária:</b> {total_sem_matricula:,} imóveis ({(total_sem_matricula/total_imoveis*100 if total_imoveis > 0 else 0):.1f}%) 
necessitam de regularização cadastral.<br/><br/>
• <b>Infraestrutura:</b> {qtd_com_arruamento} municípios ({perc_arruamento:.1f}%) possuem arruamento mapeado.<br/><br/>
• <b>Rotas Operacionais:</b> Total de {total_rotas_layer} rotas cadastradas para operações de leitura.<br/>
"""
elements.append(Paragraph(analise, analise_style))
elements.append(PageBreak())

# === PÁGINA 4+: DADOS DETALHADOS POR MUNICÍPIO ===
elements.append(Paragraph("<b>DADOS DETALHADOS POR MUNICÍPIO</b>", style_heading))
elements.append(Spacer(1, 0.3*cm))

# Tabela detalhada
table_data = [
    ["Município", "Lat", "Lon", "Imóveis", "Matric.", "S/Matric.", "Quadras", "Arrua.", "Rotas", "Over.", "Início", "Fim"]
]

for m, d in sorted(dados.items()):
    lat = d.get('latitude')
    lon = d.get('longitude')
    lat_disp = f"{lat:.4f}" if isinstance(lat, float) else ""
    lon_disp = f"{lon:.4f}" if isinstance(lon, float) else ""
    row = [
        d['municipio'],
        lat_disp,
        lon_disp,
        str(d['qtd_imoveis']),
        str(d['qtd_imoveis_com_matricula']),
        str(d['qtd_imoveis_sem_matricula']),
        str(d['qtd_quadras']),
        "✓" if d.get('tem_arruamento') else "✗",
        str(d['qtd_rotas_layer']),
        "✓" if d['tem_overlay'] else "✗",
        "✓" if d['tem_inicio'] else "✗",
        "✓" if d['tem_fim'] else "✗"
    ]
    table_data.append(row)

tabela = Table(table_data, repeatRows=1, colWidths=[4*cm, 2*cm, 2*cm, 1.8*cm, 1.8*cm, 1.8*cm, 1.8*cm, 1.5*cm, 1.5*cm, 1.5*cm, 1.5*cm, 1.5*cm])
tabela.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3B8FBF")),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('FONTSIZE', (0, 1), (-1, -1), 8),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ('TOPPADDING', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ('TOPPADDING', (0, 1), (-1, -1), 6),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#D0E8F0")),
    ('LINEBELOW', (0, 0), (-1, 0), 0, colors.white),
    ('INNERGRID', (0, 1), (-1, -1), 0.5, colors.HexColor("#E8F4F8")),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FBFD")]),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
]))

elements.append(tabela)
elements.append(Spacer(1, 0.5*cm))

# Legenda
legenda_texto = """
<b>Legenda:</b><br/>
• <b>Matric.:</b> Imóveis com matrícula cadastrada<br/>
• <b>S/Matric.:</b> Imóveis sem matrícula (necessitam regularização)<br/>
• <b>Arrua.:</b> Presença de arruamento mapeado<br/>
• <b>Over.:</b> Presença de overlay<br/>
• <b>✓:</b> Presente | <b>✗:</b> Ausente<br/>
"""
elements.append(Paragraph(legenda_texto, ParagraphStyle('legenda', parent=style_normal, fontSize=8, textColor=colors.HexColor("#666666"))))

# Construir PDF com canvas customizado
doc.build(elements, canvasmaker=ReportCanvas)

print("✅ Relatório Executivo Profissional gerado com sucesso!")
print("📄 CSV:", csv_path)
print("📘 PDF Executivo:", pdf_path)
print(f"📁 Pasta: {pasta_relatorio}")
