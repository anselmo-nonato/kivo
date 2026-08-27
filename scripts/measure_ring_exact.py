import numpy as np
from PIL import Image

img = Image.open('assets/4188ac0f-06df-4843-aef4-70b2702b3010.png')
arr = np.array(img)
alpha = arr[:, :, 3].astype(float) / 255.0

# Let's inspect the ring:
# Center of ring:
# Look at horizontal slice through center Y=636
slice_h = alpha[636, 140:300]
xs = np.arange(140, 300)
# Outer left, inner left, inner right, outer right
edges = np.where(np.diff((slice_h > 0.5).astype(int)) != 0)[0] + 140
print("Horizontal ring edges at Y=636:", edges)
# Radius outer = (edges[3] - edges[0]) / 2, Center X = (edges[3] + edges[0]) / 2
cx = (edges[3] + edges[0]) / 2.0
r_out = (edges[3] - edges[0]) / 2.0
r_in = (edges[2] - edges[1]) / 2.0
cx_in = (edges[2] + edges[1]) / 2.0
print(f"Ring X-profile: Center={cx:.2f}, R_out={r_out:.2f}, Inner_center={cx_in:.2f}, R_in={r_in:.2f}")

# Look at vertical slice through center X=217
slice_v = alpha[550:715, 217]
ys = np.arange(550, 715)
edges_v = np.where(np.diff((slice_v > 0.5).astype(int)) != 0)[0] + 550
print("Vertical ring edges at X=217:", edges_v)
cy = (edges_v[2] + edges_v[0]) / 2.0
r_out_y = (edges_v[2] - edges_v[0]) / 2.0
r_in_y = (edges_v[1] - edges_v[0]) # top inner
print(f"Ring Y-profile: Center Y={cy:.2f}, R_out_y={r_out_y:.2f}")
