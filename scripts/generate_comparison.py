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

  <!-- 2. ARROW SHAFT AND ARROW HEAD -->
  <polygon points="295,505 385,345 425,385 335,545" fill="url(#arrowGrad)" />
  <polygon points="468,288 373,321 385,345 425,385 467,360" fill="url(#arrowGrad)" />

  <!-- 3. LOWER RIBBON ARM (65px wide parallel band at -45 deg) -->
  <path d="M 295,505 
           L 435,608 
           A 32.5,32.5 0 0,1 390,655 
           L 265,565 
           Z" 
        fill="url(#lowerArmGrad)" />

  <!-- 4. 3D INSIDE SHADOW (Curved interior of the ribbon loop, closing cleanly against the stem) -->
  <path d="M 295,505 
           L 240,560 
           C 232,572 245,585 265,565 
           Z" 
        fill="url(#shadowGrad)" />

  <!-- 5. 3D FRONT LIGHT-GREEN FOLD (The continuous folded ribbon surface) -->
  <path d="M 385,345 
           L 240,490 
           C 200,530 210,555 240,560 
           L 295,505 
           L 425,385 
           Z" 
        fill="url(#foldFrontGrad)" />
</svg>"""

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

# Generate comparison image
orig = Image.open("assets/icon_original_cropped.png").convert("RGB")
rend = Image.open(out_abs).convert("RGB").crop((0, 0, orig.width, orig.height))

comp = Image.new("RGB", (orig.width * 2 + 20, orig.height), (34, 34, 34))
comp.paste(orig, (0, 0))
comp.paste(rend, (orig.width + 20, 0))
comp.save("assets/comparison.png")
print("Rendered and compared!")
