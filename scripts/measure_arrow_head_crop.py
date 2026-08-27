from PIL import Image
import numpy as np

img = Image.open('assets/icon_original_cropped.png')
arr = np.array(img)

# Let's inspect the arrow head:
# In crop coordinates (0 to 360, 0 to 440):
# Arrow head is in X: [180, 340], Y: [0, 130]
arrow_crop = arr[0:130, 180:340]
alpha_arrow = arrow_crop[:, :, 3] > 128

# Let's find vertices of arrow head:
# 1. Tip:
y_tip, x_tip = np.where(alpha_arrow)
tip_idx = np.argmin(y_tip)
print(f"Arrow Tip: X={x_tip[tip_idx]+180}, Y={y_tip[tip_idx]}")

# Let's print the boundary points of arrow head:
for y in range(5, 125, 10):
    xs = np.where(alpha_arrow[y, :])[0]
    if len(xs) > 0:
        print(f"Y={y}: X_min={xs.min()+180}, X_max={xs.max()+180}")
