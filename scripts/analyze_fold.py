from PIL import Image
import numpy as np

img = Image.open('assets/4188ac0f-06df-4843-aef4-70b2702b3010.png')
arr = np.array(img)

# Crop the fold region: X=[200, 360], Y=[400, 580]
fold_crop = arr[400:580, 200:360]

# Let's find the sharp crease line / boundary between:
# 1. The light green fold surface (front)
# 2. The dark green shadow (inside fold)
# 3. The vertical stem underneath
# 4. The background (transparent)

# In the fold area, let's inspect the gradient and colors:
# Bright front fold has R > 15, G > 180
# Shadow has R < 10, G < 160

print("Fold dimensions:", fold_crop.shape)

# Let's save a visualization with color-coded regions to analyze:
# Region A: Stem (X < 265 and not covered by front fold)
# Region B: Front Fold (The curved light-green shape)
# Region C: Shadow (The dark green shaded interior)
# Region D: Arrow shaft (Upper right)
# Region E: Lower ribbon (Lower right)

