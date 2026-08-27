import subprocess
import os

svg_full_light = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1536 1024" width="100%" height="100%">
  <defs>
    <!-- 1. Stem Gradient (Top-to-Bottom) -->
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

  <!-- ==================== SÍMBOLO KIVO ==================== -->
  <g id="kivo-icon">
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

    <!-- 3. ARROW HEAD -->
    <polygon points="468,288 375,318 385,345 428,388 472,368" fill="url(#arrowGrad)" />

    <!-- 4. LOWER RIBBON ARM -->
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
  </g>

  <!-- ==================== TIPOGRAFIA: K I V O ==================== -->
  <g id="kivo-text" fill="#051329">
    <path d="M 559,373 L 606,373 L 606,578 L 559,578 Z
             M 686,373 L 751,373 L 634,482 L 751,578 L 686,578 L 596,498 L 686,373 Z" />
    <rect x="797" y="373" width="47" height="205" rx="3" />
    <path d="M 878,373 L 930,373 L 995,540 L 1060,373 L 1112,373 L 1021,578 L 969,578 Z" />
    <path d="M 1245,368 A 119,108 0 1,1 1245,584 A 119,108 0 1,1 1245,368 Z M 1245,415 A 72,61 0 1,0 1245,537 A 72,61 0 1,0 1245,415 Z" fill-rule="evenodd" />
  </g>

  <!-- ==================== SUBTÍTULO: F I N A N Ç A S ==================== -->
  <g id="kivo-subtitle" fill="#009B66">
    <text x="567" y="650" 
          font-family="system-ui, -apple-system, 'Plus Jakarta Sans', 'Inter', 'Segoe UI', sans-serif" 
          font-size="34" 
          font-weight="700" 
          letter-spacing="24">
      FINANÇAS
    </text>
  </g>
</svg>"""

svg_icon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="140 280 360 440" width="100%" height="100%">
  <defs>
    <linearGradient id="iconStemGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1AEAA0" />
      <stop offset="25%" stop-color="#00CE86" />
      <stop offset="65%" stop-color="#00A26A" />
      <stop offset="100%" stop-color="#006C59" />
    </linearGradient>

    <linearGradient id="iconArrowGrad" x1="0%" y1="100%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00AD6D" />
      <stop offset="60%" stop-color="#00C980" />
      <stop offset="100%" stop-color="#00E599" />
    </linearGradient>

    <linearGradient id="iconLowerArmGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#007F55" />
      <stop offset="40%" stop-color="#00AF72" />
      <stop offset="85%" stop-color="#00DC8C" />
      <stop offset="100%" stop-color="#1AEAA0" />
    </linearGradient>

    <linearGradient id="iconFoldFrontGrad" x1="15%" y1="0%" x2="85%" y2="100%">
      <stop offset="0%" stop-color="#46F8B6" />
      <stop offset="35%" stop-color="#1AEAA0" />
      <stop offset="70%" stop-color="#00C982" />
      <stop offset="100%" stop-color="#009B66" />
    </linearGradient>

    <linearGradient id="iconShadowGrad" x1="0%" y1="0%" x2="70%" y2="100%">
      <stop offset="0%" stop-color="#006042" />
      <stop offset="45%" stop-color="#00432E" />
      <stop offset="100%" stop-color="#002318" />
    </linearGradient>
  </defs>

  <path d="M 200,326.5 A 32.5,32.5 0 0,1 265,326.5 L 265,565 A 76.5,76.5 0 0,1 308,636 A 76.5,76.5 0 1,1 155,636 A 76.5,76.5 0 0,1 200,565 Z M 231.5,605 A 31,31 0 1,0 231.5,667 A 31,31 0 1,0 231.5,605 Z" fill="url(#iconStemGrad)" fill-rule="evenodd" />
  <polygon points="265,490 380,350 435,395 285,550" fill="url(#iconArrowGrad)" />
  <polygon points="468,288 375,318 385,345 428,388 472,368" fill="url(#iconArrowGrad)" />
  <path d="M 295,435 L 438,572 A 33,33 0 0,1 468,605 A 33,33 0 0,1 396,638 L 258,514 Z" fill="url(#iconLowerArmGrad)" />
  <path d="M 295,435 L 238,562 C 225,580 238,600 258,514 Z" fill="url(#iconShadowGrad)" />
  <path d="M 385,345 L 240,490 C 195,530 205,555 238,562 L 295,435 L 430,390 Z" fill="url(#iconFoldFrontGrad)" />
</svg>"""

svg_full_dark = svg_full_light.replace(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1536 1024" width="100%" height="100%">',
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1536 1024" width="100%" height="100%">\n  <rect width="1536" height="1024" fill="#0B132B" />'
).replace('fill="#051329"', 'fill="#FFFFFF"').replace('fill="#009B66"', 'fill="#00E599"')

with open('assets/kivo_logo.svg', 'w', encoding='utf-8') as f:
    f.write(svg_full_light)

with open('assets/kivo_icon.svg', 'w', encoding='utf-8') as f:
    f.write(svg_icon)

with open('assets/kivo_logo_dark.svg', 'w', encoding='utf-8') as f:
    f.write(svg_full_dark)

# Render full preview screenshot
edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
html_abs = os.path.abspath("assets/preview.html").replace("\\", "/")
out_abs = os.path.abspath("assets/rendered_output.png")

cmd = [
    edge,
    "--headless",
    "--disable-gpu",
    f"--screenshot={out_abs}",
    "--window-size=1200,950",
    f"file:///{html_abs}"
]
subprocess.run(cmd, capture_output=True)
print("All official assets written and final preview generated!")
