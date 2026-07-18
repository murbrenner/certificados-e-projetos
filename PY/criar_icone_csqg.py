"""
Criar ícone para CSQG Mapper
"""
from PIL import Image, ImageDraw, ImageFont

# Criar imagem 256x256
size = 256
img = Image.new('RGB', (size, size), color='#0078d4')

# Desenhar
draw = ImageDraw.Draw(img)

# Desenhar borda
border_width = 8
draw.rectangle(
    [(border_width, border_width), (size-border_width, size-border_width)],
    outline='white',
    width=border_width
)

# Texto CSQG
try:
    # Tentar fonte grande
    font = ImageFont.truetype("arial.ttf", 80)
except:
    font = ImageFont.load_default()

text = "CSQG"
# Calcular posição central
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (size - text_width) // 2
y = (size - text_height) // 2 - 20

draw.text((x, y), text, fill='white', font=font)

# Texto Mapper (menor)
try:
    font_small = ImageFont.truetype("arial.ttf", 30)
except:
    font_small = ImageFont.load_default()

text2 = "Mapper"
bbox2 = draw.textbbox((0, 0), text2, font=font_small)
text2_width = bbox2[2] - bbox2[0]
x2 = (size - text2_width) // 2
y2 = y + text_height + 10

draw.text((x2, y2), text2, fill='#ffcc00', font=font_small)

# Salvar como PNG primeiro
png_path = "g:\\Meu Drive\\PYTHON\\AUTOMAÇÃO GSAN\\PY\\csqg_mapper_icon.png"
img.save(png_path, 'PNG')

# Converter para ICO com múltiplos tamanhos
ico_path = "g:\\Meu Drive\\PYTHON\\AUTOMAÇÃO GSAN\\PY\\csqg_mapper_icon.ico"
icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
img.save(ico_path, format='ICO', sizes=icon_sizes)

print(f"✓ Ícone criado: {ico_path}")
print(f"✓ PNG criado: {png_path}")
