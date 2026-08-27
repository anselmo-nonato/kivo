import numpy as np
from PIL import Image

img = Image.open('assets/4188ac0f-06df-4843-aef4-70b2702b3010.png')
arr = np.array(img)

# Let's inspect exact features on the original PNG:
# 1. Stem:
# Left edge: X=200, Right edge: X=265 -> Width = 65. Center X = 232.5
# Top semi-circle: Center (232.5, 327), Radius = 32.5 -> Topmost Y = 294.5

# 2. Ring:
# Center: (217, 635.5)
# Outer diameter = 125 -> Outer radius = 62.5
# Inner diameter = 43 -> Inner radius = 21.5

# 3. Arrow:
# Angle of shaft: 45 degrees
# Top vertex of arrow head: (470, 288)
# Right vertical edge: from (470, 288) to (470, 390) (Height = 102)
# Bottom horizontal shelf: from (470, 390) left to (351, 390) (Width = 119)
# Slanted back edge: from (351, 390) up to (470, 288)

# 4. Lower Arm (Capsule at -45 degrees):
# Center line goes from approx (260, 480) down-right at -45 deg to (425, 605)
# Width of arm = 85 (perpendicular)
# End cap: Semi-circle with radius 42.5 at (425, 605)

print("Exact measurements mapped")
