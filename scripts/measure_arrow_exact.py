from PIL import Image
import numpy as np

img = Image.open('assets/4188ac0f-06df-4843-aef4-70b2702b3010.png')
arr = np.array(img)

# Arrow shaft:
# Let's find lines on the arrow shaft
# Points on upper-left edge of arrow shaft:
# From near fold to arrow head base:
print("--- Arrow Shaft Upper-Left Edge ---")
for y in range(350, 480, 20):
    # Search for edge between X=250 and 400
    slice_a = arr[y, 250:420, 3] > 128
    if np.any(slice_a):
        x_first = np.where(slice_a)[0][0] + 250
        print(f"Y={y}: X_edge={x_first}")

# Points on lower-right edge of arrow shaft:
# Between arrow shaft and lower ribbon (the inner corner of K)
print("--- Arrow Shaft Lower-Right Edge ---")
for y in range(380, 500, 20):
    # Find boundary
    slice_a = arr[y, 300:460, 3] > 128
    if np.any(slice_a):
        x_last = np.where(slice_a)[0][-1] + 300
        print(f"Y={y}: X_last={x_last}")
