from PIL import Image
import numpy as np

rend = Image.open('assets/test_render_transparent.png').convert('RGB')
arr_rend = np.array(rend)

# Pixels that are NOT white (R < 240 or G < 240 or B < 240)
is_rendered_icon = (arr_rend[:, :, 0] < 240) | (arr_rend[:, :, 1] < 240) | (arr_rend[:, :, 2] < 240)

orig = Image.open('assets/icon_original_cropped.png').convert('RGBA')
arr_orig = np.array(orig)
is_orig_icon = arr_orig[:, :, 3] > 80

print(f"Total solid pixels in Original: {np.sum(is_orig_icon)}")
print(f"Total solid pixels in Rendered: {np.sum(is_rendered_icon)}")

overlap = is_orig_icon & is_rendered_icon
print(f"Overlap pixels: {np.sum(overlap)}")
print(f"Missing pixels (Red): {np.sum(is_orig_icon & (~is_rendered_icon))}")
print(f"Extra pixels (Blue): {np.sum((~is_orig_icon) & is_rendered_icon)}")

# Save overlay visual:
# Red = in Original but not in Render
# Blue = in Render but not in Original
# White = in Both (Perfect overlap)
diff_map = np.zeros((orig.height, orig.width, 3), dtype=np.uint8)
diff_map[is_orig_icon & (~is_rendered_icon)] = [255, 0, 0]  # Missing (Red)
diff_map[(~is_orig_icon) & is_rendered_icon] = [0, 100, 255]  # Extra (Blue)
diff_map[overlap] = [255, 255, 255]  # Overlap (White)

diff_img = Image.fromarray(diff_map)
diff_img.save('assets/diff_overlay_fixed.png')
print("Saved fixed diff overlay to assets/diff_overlay_fixed.png!")
