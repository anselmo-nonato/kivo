from PIL import Image
import numpy as np

# Load original crop
orig = Image.open('assets/icon_original_cropped.png').convert('RGBA')
arr = np.array(orig)
alpha = arr[:, :, 3]

# Let's find the exact bounding box of the original icon in the crop image:
y_pts, x_pts = np.where(alpha > 100)
print(f"Original in Crop: X=[{x_pts.min()}, {x_pts.max()}] (Width={x_pts.max()-x_pts.min()+1}), Y=[{y_pts.min()}, {y_pts.max()}] (Height={y_pts.max()-y_pts.min()+1})")

# Let's inspect the exact centers and extremities in crop space:
# 1. Stem Left edge:
stem_left = np.where(alpha[100:200, :x_pts.min()+100] > 100)[1].min()
# Stem Right edge:
stem_right = np.where(alpha[100:200, stem_left:stem_left+100] > 100)[1].max() + stem_left
print(f"Stem in Crop: Left={stem_left}, Right={stem_right}, Width={stem_right-stem_left+1}")

# 2. Ring Hole center in Crop:
hole_y, hole_x = np.where((alpha < 50) & (np.arange(440)[:, None] > 300) & (np.arange(360)[None, :] < 150))
print(f"Ring Hole Center in Crop: X={hole_x.mean():.1f}, Y={hole_y.mean():.1f}, Radius X={(hole_x.max()-hole_x.min()+1)/2:.1f}, Radius Y={(hole_y.max()-hole_y.min()+1)/2:.1f}")

# 3. Arrow Tip in Crop:
arrow_y, arrow_x = np.where((alpha > 100) & (np.arange(440)[:, None] < 50))
print(f"Arrow Tip in Crop: X={arrow_x[np.argmin(arrow_y)]}, Y={arrow_y.min()}")

# 4. Lower Arm Tip in Crop:
arm_y, arm_x = np.where((alpha > 100) & (np.arange(440)[:, None] > 300) & (np.arange(360)[None, :] > 250))
print(f"Lower Arm Tip in Crop: X={arm_x.max()}, Y={arm_y[np.argmax(arm_x)]}")
