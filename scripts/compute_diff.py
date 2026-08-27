from PIL import Image
import numpy as np

# Load original crop
orig = Image.open('assets/icon_original_cropped.png').convert('RGBA')
# Load rendered icon crop
rend = Image.open('assets/test_render_icon.png').convert('RGBA').crop((0, 0, orig.width, orig.height))

arr_orig = np.array(orig)
arr_rend = np.array(rend)

# Compute absolute difference in RGB for non-transparent pixels
alpha_orig = arr_orig[:, :, 3] > 100
alpha_rend = arr_rend[:, :, 3] > 100

# 1. Shape difference: pixels where one is solid and other is empty
shape_diff = alpha_orig != alpha_rend
print(f"Total shape mismatch pixels: {np.sum(shape_diff)}")

# 2. Let's find where the shape mismatches occur:
y_diff, x_diff = np.where(shape_diff)
if len(y_diff) > 0:
    print(f"Shape diff Y bounds: [{y_diff.min()}, {y_diff.max()}], X bounds: [{x_diff.min()}, {x_diff.max()}]")
    
    # Check regions of mismatch:
    # Top region (arrow head): Y < 130
    arrow_diff = shape_diff[0:130, :]
    print(f"Arrow head shape mismatch pixels: {np.sum(arrow_diff)}")
    
    # Fold region: Y 130 to 290
    fold_diff = shape_diff[130:290, :]
    print(f"Fold shape mismatch pixels: {np.sum(fold_diff)}")
    
    # Lower arm region: Y > 290
    arm_diff = shape_diff[290:, :]
    print(f"Lower arm & stem shape mismatch pixels: {np.sum(arm_diff)}")

# Save a difference heatmap image!
diff_map = np.zeros((orig.height, orig.width, 3), dtype=np.uint8)
# Red = only in original, Blue = only in rendered, Green = color diff
diff_map[alpha_orig & (~alpha_rend)] = [255, 0, 0]  # Missing in SVG
diff_map[(~alpha_orig) & alpha_rend] = [0, 0, 255]  # Extra in SVG

# For common pixels, compute RGB difference:
common = alpha_orig & alpha_rend
rgb_diff = np.max(np.abs(arr_orig[common, :3].astype(int) - arr_rend[common, :3].astype(int)), axis=1)
# Intensity of color diff
for idx, (y, x) in enumerate(zip(*np.where(common))):
    val = min(255, rgb_diff[idx] * 2)
    diff_map[y, x] = [val, val, val]

diff_img = Image.fromarray(diff_map)
diff_img.save('assets/diff_heatmap.png')
print("Difference heatmap saved to assets/diff_heatmap.png!")
