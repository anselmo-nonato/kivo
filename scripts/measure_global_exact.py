from PIL import Image
import numpy as np

img = Image.open('assets/4188ac0f-06df-4843-aef4-70b2702b3010.png')
arr = np.array(img)
alpha = arr[:, :, 3]

# 1. Stem:
# Slice at Y = 360 (below top rounded cap, above fold)
stem_xs = np.where(alpha[360, :400] > 100)[0]
print(f"Stem at Y=360: X_left={stem_xs.min()}, X_right={stem_xs.max()}, Width={stem_xs.max()-stem_xs.min()+1}")

# Topmost cap of stem:
stem_ys = np.where(alpha[:400, stem_xs.min():stem_xs.max()] > 100)[0]
print(f"Stem Topmost Y={stem_ys.min()}")

# 2. Bottom Ring:
# Slice at Y = 636 (through horizontal center of ring)
ring_xs = np.where(alpha[636, :300] > 100)[0]
# Ring hole at Y = 636 (where alpha < 50 inside ring)
hole_xs = np.where((alpha[636, :300] < 50) & (np.arange(300) > stem_xs.min()))[0]
print(f"Ring at Y=636: Outer Left={ring_xs.min()}, Hole Left={hole_xs.min()}, Hole Right={hole_xs.max()}")
print(f"Hole Center X={(hole_xs.min()+hole_xs.max())/2:.1f}, Hole Radius={(hole_xs.max()-hole_xs.min()+1)/2:.1f}")

# Bottommost Y of ring:
ring_bottom_ys = np.where(alpha[550:720, :300] > 100)[0] + 550
print(f"Ring Bottommost Y={ring_bottom_ys.max()}")

# 3. Arrow:
# Slice at Y = 350
arrow_xs = np.where(alpha[350, 300:500] > 100)[0] + 300
print(f"Arrow at Y=350: X_min={arrow_xs.min()}, X_max={arrow_xs.max()}")

# 4. Lower Arm:
# Slice at Y = 610
arm_xs = np.where(alpha[610, 200:500] > 100)[0] + 200
print(f"Lower Arm at Y=610: X_min={arm_xs.min()}, X_max={arm_xs.max()}")
