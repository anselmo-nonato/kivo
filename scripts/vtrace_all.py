import vtracer
from PIL import Image
import os
import re

# 1. Vetorizar a logo completa
print("Vetorizando logo completa...")
vtracer.convert_image_to_svg_py(
    "assets/4188ac0f-06df-4843-aef4-70b2702b3010.png",
    "assets/kivo_logo.svg",
    colormode="color",
    hierarchical="stacked",
    mode="spline",
    filter_speckle=4,
    color_precision=8,
    layer_difference=12,
    corner_threshold=60,
    length_threshold=3.5,
    max_iterations=10,
    splice_threshold=45,
    path_precision=3
)

# 2. Criar crop do ícone de alta resolução com fundo transparente
print("Recortando e vetorizando ícone isolado...")
img = Image.open("assets/4188ac0f-06df-4843-aef4-70b2702b3010.png")
# Bounding box do ícone: X=[154, 474], Y=[288, 710]
# Adicionando uma margem harmônica quadrada
icon_crop = img.crop((120, 260, 508, 738))
icon_crop_path = "assets/temp_icon_crop.png"
icon_crop.save(icon_crop_path)

vtracer.convert_image_to_svg_py(
    icon_crop_path,
    "assets/kivo_icon.svg",
    colormode="color",
    hierarchical="stacked",
    mode="spline",
    filter_speckle=4,
    color_precision=8,
    layer_difference=12,
    corner_threshold=60,
    length_threshold=3.5,
    max_iterations=10,
    splice_threshold=45,
    path_precision=3
)

if os.path.exists(icon_crop_path):
    os.remove(icon_crop_path)

print("Vetorização concluída com sucesso!")
