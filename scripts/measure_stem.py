from PIL import Image
import numpy as np

img = Image.open('assets/4188ac0f-06df-4843-aef4-70b2702b3010.png')
arr = np.array(img)

# Crop the icon region exactly
# X: [150, 480], Y: [280, 720]
icon = arr[280:720, 150:480]

# Let's find the exact center and radius of the bottom ring:
# Outer boundary of bottom ring:
y_ext, x_ext = np.where((arr[560:715, 150:285, 3] > 128))
# Offset to global coords
y_ext = y_ext + 560
x_ext = x_ext + 150

# Fit a circle to outer ring:
# (x - cx)^2 + (y - cy)^2 = r^2
# Let's find min/max in X and Y
min_x, max_x = x_ext.min(), x_ext.max()
min_y, max_y = y_ext.min(), y_ext.max()
cx_outer = (min_x + max_x) / 2.0
cy_outer = (min_y + max_y) / 2.0
r_outer_x = (max_x - min_x) / 2.0
r_outer_y = (max_y - min_y) / 2.0
print(f"Outer Ring: Center=({cx_outer:.1f}, {cy_outer:.1f}), Rx={r_outer_x:.1f}, Ry={r_outer_y:.1f}")

# Fit circle to inner hole (alpha < 50 inside the ring):
y_int, x_int = np.where((arr[590:680, 180:255, 3] < 50))
y_int = y_int + 590
x_int = x_int + 180
cx_inner = (x_int.min() + x_int.max()) / 2.0
cy_inner = (y_int.min() + y_int.max()) / 2.0
r_inner_x = (x_int.max() - x_int.min()) / 2.0
r_inner_y = (y_int.max() - y_int.min()) / 2.0
print(f"Inner Hole: Center=({cx_inner:.1f}, {cy_inner:.1f}), Rx={r_inner_x:.1f}, Ry={r_inner_y:.1f}")

# Fit semi-circle to top of stem:
y_top, x_top = np.where((arr[285:360, 195:270, 3] > 128))
y_top = y_top + 285
x_top = x_top + 195
min_xt, max_xt = x_top.min(), x_top.max()
min_yt = y_top.min()
stem_width = max_xt - min_xt
stem_cx = (min_xt + max_xt) / 2.0
stem_r = stem_width / 2.0
stem_cy = min_yt + stem_r
print(f"Stem Top: Center=({stem_cx:.1f}, {stem_cy:.1f}), Radius={stem_r:.1f}, X_left={min_xt}, X_right={max_xt}, Top_Y={min_yt}")
