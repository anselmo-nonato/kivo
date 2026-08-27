import numpy as np
from PIL import Image

img = Image.open('assets/4188ac0f-06df-4843-aef4-70b2702b3010.png')
arr = np.array(img)

# Let's inspect the exact paths of the icon:
# 1. STEM & RING:
# Top rounded cap: center X=232.5, Y=327, radius=32.5 (from Y=294.5 to 360, width 65, left X=200, right X=265)
# Ring center: X=217, Y=635.5
# Outer radius = 62.5 (left X=154.5, right X=279.5, top Y=573, bottom Y=698)
# Inner radius (hole) = 21.5 (left X=195.5, right X=238.5, top Y=614, bottom Y=657)
# Tangent from stem to ring on the left: X=200 goes down to meet ring at Y=580.
# On the right: stem right edge X=265 goes down to Y=580 where it blends with the ring and ribbon.

# 2. ARROW:
# Starts from intersection around X=240, Y=475, rises at angle ~45 deg
# Shaft left edge: from (240, 480) up to (351, 388)
# Shaft right edge: from (265, 520) up to (405, 388) -> shaft width approx 48px perpendicular
# Arrow head:
# Top peak: (470, 288)
# Right edge: vertical down to (470, 390)
# Bottom horizontal shelf: from (470, 390) left to (351, 390)
# Top slant edge: from (351, 390) up-right to (470, 288)

# 3. RIBBON FOLD (Front):
# The ribbon originates at the stem near (240, 460), curves forward and down-right.
# Left/Top edge of front ribbon: starts at (240, 460), curves through (265, 430) to (300, 470) then straight down-right to (425, 595).
# Bottom-right rounded cap: center at (445, 615), radius ~26px (curves smoothly from (425, 595) to (471, 620) to (445, 645)).
# Bottom-left edge of front ribbon: goes from (445, 645) straight up-left to (280, 520) and meets the back fold.

# 4. RIBBON FOLD (Back Shadow):
# Triangular shadow area connecting the front fold under the stem:
# Vertices approx: (250, 490), (310, 550), (265, 585)

print("Geometry parameters calculated")
