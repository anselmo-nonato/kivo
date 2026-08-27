import subprocess
import os
import numpy as np
from PIL import Image

def test_svg(svg_code):
    with open("assets/kivo_icon_test.svg", "w", encoding="utf-8") as f:
        f.write(svg_code)
    
    # Render with Edge to PNG at exact dimensions (360 x 440)
    edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    svg_abs = os.path.abspath("assets/kivo_icon_test.svg").replace("\\", "/")
    out_abs = os.path.abspath("assets/test_render_icon.png")
    
    # HTML wrapper for exact 1:1 render matching icon_original_cropped.png
    html = f"""<!DOCTYPE html>
<html>
<head><style>
  body {{ margin: 0; padding: 0; background: #1a1a1a; overflow: hidden; }}
  svg {{ width: 360px; height: 440px; display: block; }}
</style></head>
<body>
  {svg_code}
</body>
</html>"""
    with open("assets/render_wrapper.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    html_abs = os.path.abspath("assets/render_wrapper.html").replace("\\", "/")
    
    cmd = [
        edge,
        "--headless",
        "--disable-gpu",
        f"--screenshot={out_abs}",
        "--window-size=360,440",
        f"file:///{html_abs}"
    ]
    subprocess.run(cmd, capture_output=True)
    
    # Compare with original icon
    orig = Image.open("assets/icon_original_cropped.png").convert("RGBA")
    rend = Image.open(out_abs).convert("RGBA")
    
    # Let's crop rend to 360x440
    rend = rend.crop((0, 0, 360, 440))
    rend.save("assets/test_render_icon_cropped.png")
    
    print("Rendered and saved test icon screenshot!")

print("Tester module ready")
