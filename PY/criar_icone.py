from PIL import Image, ImageDraw, ImageFont
import os

# Criar imagem 256x256 com fundo gradiente
size = 256
image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# Gradiente azul moderno
for y in range(size):
    color_value = int(120 + (y / size) * 100)
    draw.rectangle([(0, y), (size, y+1)], fill=(0, color_value, 212, 255))

# Desenhar círculo branco central
center = size // 2
radius = 90
draw.ellipse([center-radius, center-radius, center+radius, center+radius], 
             fill=(255, 255, 255, 255), outline=(0, 120, 180, 255), width=8)

# Desenhar setas de sincronização (símbolo ↻)
arrow_color = (0, 120, 212, 255)
arrow_width = 12

# Seta circular superior (sentido horário)
draw.arc([center-65, center-65, center+65, center+65], start=45, end=315, 
         fill=arrow_color, width=arrow_width)

# Ponta da seta superior direita
arrow_points = [(center+45, center-25), (center+60, center-10), (center+50, center-40)]
draw.polygon(arrow_points, fill=arrow_color)

# Seta circular inferior (sentido anti-horário)  
draw.arc([center-50, center-50, center+50, center+50], start=225, end=495, 
         fill=arrow_color, width=10)

# Ponta da seta inferior esquerda
arrow_points2 = [(center-45, center+25), (center-60, center+10), (center-50, center+40)]
draw.polygon(arrow_points2, fill=arrow_color)

# Adicionar texto "SC" no centro
try:
    # Tentar usar fonte do sistema
    font = ImageFont.truetype("segoeui.ttf", 50)
except:
    font = ImageFont.load_default()

text = "SC"
# Calcular posição central do texto
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
text_x = center - text_width // 2
text_y = center - text_height // 2

draw.text((text_x, text_y), text, fill=arrow_color, font=font)

# Salvar como ICO (múltiplos tamanhos)
icon_path = os.path.join(os.path.dirname(__file__), 'smartsync_icon.ico')

# Criar versões em diferentes tamanhos
sizes_list = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
icons = []
for icon_size in sizes_list:
    icons.append(image.resize(icon_size, Image.Resampling.LANCZOS))

# Salvar todas as versões em um arquivo .ico
icons[0].save(icon_path, format='ICO', sizes=[(img.width, img.height) for img in icons], 
              append_images=icons[1:])

print(f"✓ Ícone criado com sucesso: {icon_path}")

# Também salvar como PNG para visualização
png_path = os.path.join(os.path.dirname(__file__), 'smartsync_icon.png')
image.save(png_path, 'PNG')
print(f"✓ Preview PNG criado: {png_path}")
