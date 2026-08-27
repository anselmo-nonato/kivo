import subprocess
import os
import numpy as np
from PIL import Image

svg_code = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="140 280 360 440" width="360" height="440">
  <defs>
    <!-- 1. Stem Gradient -->
    <linearGradient id="stemGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1AEAA0" />
      <stop offset="25%" stop-color="#00CE86" />
      <stop offset="65%" stop-color="#00A26A" />
      <stop offset="100%" stop-color="#006C59" />
    </linearGradient>

    <!-- 2. Arrow Shaft & Head Gradient (45 deg) -->
    <linearGradient id="arrowGrad" x1="0%" y1="100%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00AD6D" />
      <stop offset="60%" stop-color="#00C980" />
      <stop offset="100%" stop-color="#00E599" />
    </linearGradient>

    <!-- 3. Lower Arm Gradient (-45 deg) -->
    <linearGradient id="lowerArmGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#007F55" />
      <stop offset="40%" stop-color="#00AF72" />
      <stop offset="85%" stop-color="#00DC8C" />
      <stop offset="100%" stop-color="#1AEAA0" />
    </linearGradient>

    <!-- 4. Front Light-Green Fold Surface -->
    <linearGradient id="foldFrontGrad" x1="15%" y1="0%" x2="85%" y2="100%">
      <stop offset="0%" stop-color="#46F8B6" />
      <stop offset="35%" stop-color="#1AEAA0" />
      <stop offset="70%" stop-color="#00C982" />
      <stop offset="100%" stop-color="#009B66" />
    </linearGradient>

    <!-- 5. 3D Inside Shadow Gradient -->
    <linearGradient id="shadowGrad" x1="0%" y1="0%" x2="70%" y2="100%">
      <stop offset="0%" stop-color="#006042" />
      <stop offset="45%" stop-color="#00432E" />
      <stop offset="100%" stop-color="#002318" />
    </linearGradient>
  </defs>

  <!-- 1. STEM AND BOTTOM RING -->
  <path d="M 200,326.5 
           A 32.5,32.5 0 0,1 265,326.5 
           L 265,565 
           A 76.5,76.5 0 0,1 308,636 
           A 76.5,76.5 0 1,1 155,636 
           A 76.5,76.5 0 0,1 200,565 
           Z
           M 231.5,605 
           A 31,31 0 1,0 231.5,667 
           A 31,31 0 1,0 231.5,605 
           Z" 
        fill="url(#stemGrad)" 
        fill-rule="evenodd" />

  <!-- 2. ARROW SHAFT -->
  <polygon points="265,490 380,350 435,395 285,550" fill="url(#arrowGrad)" />

  <!-- 3. ARROW HEAD (Perfect overlap) -->
  <polygon points="468,288 375,318 385,345 428,388 472,368" fill="url(#arrowGrad)" />

  <!-- 4. LOWER RIBBON ARM (Calibrated width and smooth rounded cap) -->
  <path d="M 295,435 
           L 438,572 
           A 33,33 0 0,1 468,605 
           A 33,33 0 0,1 396,638 
           L 258,514 
           Z" 
        fill="url(#lowerArmGrad)" />

  <!-- 5. 3D INSIDE SHADOW -->
  <path d="M 295,435 
           L 238,562 
           C 225,580 238,600 258,514 
           Z" 
        fill="url(#shadowGrad)" />

  <!-- 6. 3D FRONT LIGHT-GREEN FOLD -->
  <path d="M 385,345 
           L 240,490 
           C 195,530 205,555 238,562 
           L 295,435 
           L 430,390 
           Z" 
        fill="url(#foldFrontGrad)" />
</svg>"""

with open("assets/kivo_icon_test.svg", "w", encoding="utf-8") as f:
    f.write(svg_code)

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

# Compute pixel overlap
orig = Image.open('assets/icon_original_cropped.png').convert('RGBA')
rend = Image.open(out_abs).convert('RGB').crop((0, 0, orig.width, orig.height))

arr_orig = np.array(orig)
arr_rend = np.array(rend)

is_orig = arr_orig[:, :, 3] > 80
is_rend = (arr_rend[:, :, 0] < 240) | (arr_rend[:, :, 1] < 240) | (arr_rend[:, :, 2] < 240)

overlap = is_orig & is_rend
missing = is_orig & (~is_rend)
extra = (~is_orig) & is_rend

accuracy = np.sum(overlap) / np.sum(is_orig | is_rend) * 100.0
print(f"Shape Accuracy: {accuracy:.2f}% (Overlap={np.sum(overlap)}, Missing={np.sum(missing)}, Extra={np.sum(extra)})")

# Save diff visual
diff_map = np.zeros((orig.height, orig.width, 3), dtype=np.uint8)
diff_map[missing] = [255, 0, 0]   # Red
diff_map[extra] = [0, 100, 255]   # Blue
diff_map[overlap] = [255, 255, 255] # White
Image.fromarray(diff_map).save('assets/diff_overlay_fixed.png')

# Save side by side comparison:
comp = Image.new("RGB", (orig.width * 2 + 20, orig.height), (34, 34, 34))
comp.paste(orig.convert("RGB"), (0, 0))
comp.paste(rend, (orig.width + 20, 0))
comp.save("assets/comparison.png")
print("Rendered and evaluated accuracy!")
