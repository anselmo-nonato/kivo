from PIL import Image
import numpy as np
import shutil

# 1. Copiar PNG original como kivo_logo.png oficial
shutil.copy("assets/4188ac0f-06df-4843-aef4-70b2702b3010.png", "assets/kivo_logo.png")

# 2. Abrir original para recortar o ícone
img = Image.open("assets/4188ac0f-06df-4843-aef4-70b2702b3010.png").convert("RGBA")
arr = np.array(img)

# Bounding box exata do ícone (X < 500)
alpha = arr[:, :, 3]
y_idx, x_idx = np.where((alpha > 10) & (np.arange(arr.shape[1])[None, :] < 500))

min_x, max_x = x_idx.min(), x_idx.max()
min_y, max_y = y_idx.min(), y_idx.max()

print(f"Ícone recortado nos limites exatos: X=[{min_x}, {max_x}] (L={max_x-min_x+1}), Y=[{min_y}, {max_y}] (A={max_y-min_y+1})")

# Recorte preciso do ícone
icon_exact = img.crop((min_x, min_y, max_x + 1, max_y + 1))
icon_exact.save("assets/kivo_icon_tight.png", optimize=True)

# Criar versão quadrada com respiro harmônico (padding de 8% em cada lado)
w, h = icon_exact.size
size = max(w, h)
padding = int(size * 0.12)
total_size = size + 2 * padding

square_icon = Image.new("RGBA", (total_size, total_size), (0, 0, 0, 0))
offset_x = (total_size - w) // 2
offset_y = (total_size - h) // 2
square_icon.paste(icon_exact, (offset_x, offset_y), icon_exact)

# Salvar o ícone mestre PNG em alta resolução
square_icon.save("assets/kivo_icon.png", optimize=True)

# Salvar versões padrão para web e mobile
square_icon.resize((512, 512), Image.Resampling.LANCZOS).save("assets/kivo_icon_512.png", optimize=True)
square_icon.resize((192, 192), Image.Resampling.LANCZOS).save("assets/kivo_icon_192.png", optimize=True)
square_icon.resize((64, 64), Image.Resampling.LANCZOS).save("assets/favicon_64.png", optimize=True)
square_icon.resize((32, 32), Image.Resampling.LANCZOS).save("assets/favicon_32.png", optimize=True)

print("Todos os PNGs oficiais gerados com perfeição e resolução nativa!")
