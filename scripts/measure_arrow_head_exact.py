from PIL import Image
import numpy as np

img = Image.open('assets/icon_original_cropped.png')
arr = np.array(img)

# In crop coordinates (0 to 360, 0 to 440):
# Arrow head is in X: [180, 340], Y: [0, 140]
arrow = arr[0:140, 180:340]
alpha = arrow[:, :, 3] > 128

# Let's find the exact outline points of the arrow head:
# Topmost point:
y_pts, x_pts = np.where(alpha)
top_idx = np.argmin(y_pts)
print(f"Top tip: X={x_pts[top_idx]+180}, Y={y_pts[top_idx]}")

# Leftmost barb of arrow head:
# It occurs around Y=40..60
sub_left = np.where(alpha[30:70, :])
left_idx = np.argmin(sub_left[1])
print(f"Left barb: X={sub_left[1][left_idx]+180}, Y={sub_left[0][left_idx]+30}")

# Rightmost barb / bottom right of arrow head:
sub_right = np.where(alpha[80:125, :])
right_idx = np.argmax(sub_right[1])
print(f"Right barb: X={sub_right[1][right_idx]+180}, Y={sub_right[0][right_idx]+80}")

# Where shaft enters arrow head (base notch):
# Shaft is around X=230..280 at Y=100..120
print(f"Base inner notch left: X=245, Y=65")
