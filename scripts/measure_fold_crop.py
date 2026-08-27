from PIL import Image
import numpy as np

img = Image.open('assets/icon_original_cropped.png')
arr = np.array(img)

# Crop coordinates:
# Fold is in Y: [130, 290], X: [40, 200]
fold_crop = arr[130:290, 40:200]

# Let's find the boundary points of the light green fold in crop coordinates:
for y in range(140, 280, 10):
    # In crop space
    # High green surface: G > 160 and alpha > 128
    row = arr[y, 40:200]
    high_green = np.where((row[:, 3] > 128) & (row[:, 1] > 160))[0]
    if len(high_green) > 0:
        print(f"Y_crop={y}: X_min={high_green.min()+40}, X_max={high_green.max()+40}")
