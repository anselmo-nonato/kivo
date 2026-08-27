import subprocess
import os
import numpy as np
from PIL import Image

# Read the SVG code
with open('assets/kivo_icon.svg', 'r', encoding='utf-8') as f:
    svg_code = f.read()

# Make transparent render
html = f"""<!DOCTYPE html>
<html>
<head><style>
  body {{ margin: 0; padding: 0; background: transparent; overflow: hidden; }}
  svg {{ width: 360px; height: 440px; display: block; }}
</style></head>
<body>
  {svg_code}
</body>
</html>"""

with open("assets/render_wrapper_transparent.html", "w", encoding="utf-8") as f:
    f.write(html)

edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
html_abs = os.path.abspath("assets/render_wrapper_transparent.html").replace("\\", "/")
out_abs = os.path.abspath("assets/test_render_transparent.png")

cmd = [
    edge,
    "--headless",
    "--disable-gpu",
    f"--screenshot={out_abs}",
    "--window-size=360,440",
    f"file:///{html_abs}"
]
subprocess.run(cmd, capture_output=True)

# Load original crop and transparent render
orig = Image.open('assets/icon_original_cropped.png').convert('RGBA')
rend = Image.open(out_abs).convert('RGBA').crop((0, 0, orig.width, orig.height))

arr_orig = np.array(orig)
arr_rend = np.array(rend)

alpha_orig = arr_orig[:, :, 3] > 80
alpha_rend = arr_rend[:, :, 3] > 80

shape_diff = alpha_orig != alpha_rend
print(f"REAL Total shape mismatch pixels: {np.sum(shape_diff)}")

# Generate diff heatmap:
# Red = in Original but missing in Render
# Blue = in Render but not in Original
# Yellow/Green = in Both
diff_map = np.zeros((orig.height, orig.width, 3), dtype=np.uint8)
diff_map[alpha_orig & (~alpha_rend)] = [255, 0, 0]  # Missing (Red)
diff_map[(~alpha_orig) & alpha_rend] = [0, 100, 255]  # Extra (Blue)
diff_map[alpha_orig & alpha_rend] = [0, 255, 0]  # Overlap (Green)

diff_img = Image.fromarray(diff_map)
diff_img.save('assets/diff_overlay.png')
print("Diff overlay saved to assets/diff_overlay.png!")
