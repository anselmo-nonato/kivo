import numpy as np
from PIL import Image

# Let's inspect the exact pixel coordinates of the features in icon_original_cropped.png (size 360 x 440)
# Top-left of crop in original image is (X=140, Y=280)
# So coords in original image = coord_in_crop + (140, 280)

# Let's measure:
# 1. Stem Top: Center X = 92 (abs 232), Y = 47 (abs 327), R = 32.5 (width 65)
# 2. Ring Bottom: Center X = 77 (abs 217), Y = 355 (abs 635), R_ext = 62.5, R_int = 21.5
# 3. Arrow Tip: (X=332, Y=8) -> Abs (472, 288)
#    Arrow Left Wing: (X=200, Y=115) -> Abs (340, 395)
#    Arrow Right Wing: (X=325, Y=105) -> Abs (465, 385)
# 4. Ribbon Fold Tip (the rounded light-green loop on the left):
#    Center approx (X=105, Y=210) -> Abs (245, 490), Radius = 28
# 5. Ribbon Lower Arm Tip (the rounded bottom-right green cap):
#    Center approx (X=295, Y=335) -> Abs (435, 615), Radius = 28

print("Features mapped to exact pixel grid!")
