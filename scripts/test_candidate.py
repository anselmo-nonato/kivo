import subprocess
import os
import numpy as np
from PIL import Image

# ViewBox matching the crop: 140 280 360 440 (so coordinates are in original 1536x1024 space)
def build_icon_svg(stem_grad_stops, arrow_grad_stops, front_grad_stops, shadow_grad_stops, lower_grad_stops, paths):
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="140 280 360 440" width="360" height="440">
  <defs>
    <!-- 1. Stem Gradient -->
    <linearGradient id="stemGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      {stem_grad_stops}
    </linearGradient>

    <!-- 2. Arrow Gradient -->
    <linearGradient id="arrowGrad" x1="0%" y1="100%" x2="80%" y2="0%">
      {arrow_grad_stops}
    </linearGradient>

    <!-- 3. Front Fold Gradient -->
    <linearGradient id="foldFrontGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      {front_grad_stops}
    </linearGradient>

    <!-- 4. Shadow Gradient -->
    <linearGradient id="shadowGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      {shadow_grad_stops}
    </linearGradient>

    <!-- 5. Lower Arm Gradient -->
    <linearGradient id="lowerArmGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      {lower_grad_stops}
    </linearGradient>
  </defs>

  {paths}
</svg>"""
    return svg

# Let's define the paths with high geometric precision:
stem_path = """
    <!-- Stem & Ring -->
    <path d="M 200,327 
             A 32.5,32.5 0 0,1 265,327 
             L 265,582 
             A 62.5,62.5 0 0,1 279.5,635.5 
             A 62.5,62.5 0 1,1 154.5,635.5 
             A 62.5,62.5 0 0,1 200,582 
             Z
             M 217,614
             A 21.5,21.5 0 1,0 217,657
             A 21.5,21.5 0 1,0 217,614
             Z" 
          fill="url(#stemGrad)" 
          fill-rule="evenodd" />
"""

arrow_path = """
    <!-- Upper Arrow Shaft & Head -->
    <polygon points="265,500 375,390 420,390 265,545" fill="url(#arrowGrad)" />
    <polygon points="472,288 472,390 340,390" fill="#00DB8B" />
"""

# Let's refine lower arm and 3D origami fold
lower_arm_path = """
    <!-- Lower Arm (Capsule angled at -45 deg) -->
    <path d="M 270,515 
             L 435,608 
             A 28.5,28.5 0 0,1 435,648 
             L 395,648 
             L 255,580 
             Z" 
          fill="url(#lowerArmGrad)" />
"""

fold_path = """
    <!-- 3D Shadow (Inside Fold) -->
    <path d="M 288,485 
             L 245,528 
             C 240,550 248,570 265,585 
             L 300,538 
             Z" 
          fill="url(#shadowGrad)" />

    <!-- 3D Front Fold (Light Highlight) -->
    <!-- The folded ribbon comes from upper arrow, curls smoothly over stem to the left with rounded loop, and ends at crease line -->
    <path d="M 375,390 
             L 248,518 
             C 232,534 208,510 224,494 
             L 320,398 
             L 375,390 
             Z" 
          fill="url(#foldFrontGrad)" />
"""

paths_all = stem_path + arrow_path + lower_arm_path + fold_path

stem_stops = """
      <stop offset="0%" stop-color="#14E59C" />
      <stop offset="30%" stop-color="#00C980" />
      <stop offset="65%" stop-color="#00A068" />
      <stop offset="100%" stop-color="#006C59" />
"""

arrow_stops = """
      <stop offset="0%" stop-color="#00AB6D" />
      <stop offset="100%" stop-color="#00DB8B" />
"""

front_stops = """
      <stop offset="0%" stop-color="#46F8B6" />
      <stop offset="35%" stop-color="#1AEAA0" />
      <stop offset="70%" stop-color="#00C982" />
      <stop offset="100%" stop-color="#009B66" />
"""

shadow_stops = """
      <stop offset="0%" stop-color="#006042" />
      <stop offset="100%" stop-color="#003525" />
"""

lower_stops = """
      <stop offset="0%" stop-color="#007F55" />
      <stop offset="40%" stop-color="#00AF72" />
      <stop offset="85%" stop-color="#00DC8C" />
      <stop offset="100%" stop-color="#14E59C" />
"""

svg_code = build_icon_svg(stem_stops, arrow_stops, front_stops, shadow_stops, lower_stops, paths_all)

# Save and render
with open("assets/kivo_icon_test.svg", "w", encoding="utf-8") as f:
    f.write(svg_code)

html = f"""<!DOCTYPE html>
<html>
<head><style>
  body {{ margin: 0; padding: 0; background: #222222; overflow: hidden; }}
  svg {{ width: 360px; height: 440px; display: block; }}
</style></head>
<body>
  {svg_code}
</body>
</html>"""

with open("assets/render_wrapper.html", "w", encoding="utf-8") as f:
    f.write(html)

edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
html_abs = os.path.abspath("assets/render_wrapper.html").replace("\\", "/")
out_abs = os.path.abspath("assets/test_render_icon.png")

cmd = [
    edge,
    "--headless",
    "--disable-gpu",
    f"--screenshot={out_abs}",
    "--window-size=360,440",
    f"file:///{html_abs}"
]
subprocess.run(cmd, capture_output=True)
print("Rendered candidate icon!")
