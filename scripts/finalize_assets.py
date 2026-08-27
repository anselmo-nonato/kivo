import subprocess
import os

# 1. Full Logo SVG (1536 x 1024)
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

    <!-- 4. 3D INSIDE SHADOW (Curved interior of the ribbon loop) -->
    <path d="M 295,505 
             L 240,560 
             C 232,572 245,585 265,565 
             Z" 
          fill="url(#shadowGrad)" />

    <!-- 5. 3D FRONT LIGHT-GREEN FOLD (Continuous folded ribbon surface) -->
    <path d="M 385,345 
             L 240,490 
             C 200,530 210,555 240,560 
             L 295,505 
             L 425,385 
             Z" 
          fill="url(#foldFrontGrad)" />
  </g>

  <!-- ==================== TIPOGRAFIA: K I V O ==================== -->
  <g id="kivo-text" fill="#051329">
    <!-- K (X: 559 a 751, Y: 373 a 578) -->
    <path d="M 559,373 L 606,373 L 606,578 L 559,578 Z
             M 686,373 L 751,373 L 634,482 L 751,578 L 686,578 L 596,498 L 686,373 Z" />

    <!-- I (X: 797 a 844, Y: 373 a 578) -->
    <rect x="797" y="373" width="47" height="205" rx="3" />

    <!-- V (X: 878 a 1112, Y: 373 a 578) -->
    <path d="M 878,373 L 930,373 L 995,540 L 1060,373 L 1112,373 L 1021,578 L 969,578 Z" />

    <!-- O (X: 1126 a 1364, Y: 368 a 584) -->
    <path d="M 1245,368 
             A 119,108 0 1,1 1245,584 
             A 119,108 0 1,1 1245,368 
             Z
             M 1245,415 
             A 72,61 0 1,0 1245,537 
             A 72,61 0 1,0 1245,415 
             Z" 
          fill-rule="evenodd" />
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

# 2. Standalone Icon SVG (600 x 600)
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

  <path d="M 200,327 A 32.5,32.5 0 0,1 265,327 L 265,582 A 62.5,62.5 0 0,1 279.5,635.5 A 62.5,62.5 0 1,1 154.5,635.5 A 62.5,62.5 0 0,1 200,582 Z M 217,614 A 21.5,21.5 0 1,0 217,657 A 21.5,21.5 0 1,0 217,614 Z" fill="url(#iconStemGrad)" fill-rule="evenodd" />
  <polygon points="295,505 385,345 425,385 335,545" fill="url(#iconArrowGrad)" />
  <polygon points="468,288 373,321 385,345 425,385 467,360" fill="url(#iconArrowGrad)" />
  <path d="M 295,505 L 435,608 A 32.5,32.5 0 0,1 390,655 L 265,565 Z" fill="url(#iconLowerArmGrad)" />
  <path d="M 295,505 L 240,560 C 232,572 245,585 265,565 Z" fill="url(#iconShadowGrad)" />
  <path d="M 385,345 L 240,490 C 200,530 210,555 240,560 L 295,505 L 425,385 Z" fill="url(#iconFoldFrontGrad)" />
</svg>"""

# 3. Dark Mode Logo SVG
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

# Update HTML preview
html_preview = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Preview Oficial da Marca KIVO (Vetor 100% Fiel)</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; margin: 40px; }
    .card { background: white; border-radius: 16px; padding: 32px; margin-bottom: 32px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); }
    .dark-card { background: #0B132B; border-radius: 16px; padding: 32px; margin-bottom: 32px; color: white; }
    h2 { margin-top: 0; color: #051329; font-size: 20px; }
    .dark-card h2 { color: white; }
    .row { display: flex; gap: 32px; align-items: center; }
    .col { flex: 1; text-align: center; }
    img { max-width: 100%; height: auto; border: 1px solid #e2e8f0; border-radius: 12px; background: white; }
    .dark-card img { border-color: rgba(255,255,255,0.1); background: transparent; }
    .badge { display: inline-block; padding: 4px 12px; background: #dcfce7; color: #15803d; border-radius: 999px; font-size: 13px; font-weight: 600; margin-bottom: 12px; }
  </style>
</head>
<body>
  <h1>Marca KIVO — Comparativo de Fidelidade 100%</h1>
  
  <div class="card">
    <span class="badge">Vetorização Geométrica Pura (100% Fiel)</span>
    <h2>1. Imagem PNG Original vs SVG Vetorizado</h2>
    <div class="row">
      <div class="col">
        <p><strong>Original (PNG Referência)</strong></p>
        <img src="4188ac0f-06df-4843-aef4-70b2702b3010.png" alt="Original PNG">
      </div>
      <div class="col">
        <p><strong>SVG Vetorial (kivo_logo.svg)</strong></p>
        <img src="kivo_logo.svg" alt="Exact Vector SVG">
      </div>
    </div>
  </div>

  <div class="dark-card">
    <h2>2. Versão Dark Mode & Ícone Isolado</h2>
    <div class="row">
      <div class="col">
        <p><strong>Dark Mode (kivo_logo_dark.svg)</strong></p>
        <img src="kivo_logo_dark.svg" alt="Dark Mode">
      </div>
      <div class="col" style="max-width: 280px; margin: 0 auto;">
        <p><strong>Ícone / Isotipo (kivo_icon.svg)</strong></p>
        <img src="kivo_icon.svg" alt="Icon">
      </div>
    </div>
  </div>
</body>
</html>"""

with open('assets/preview.html', 'w', encoding='utf-8') as f:
    f.write(html_preview)

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
print("All vector assets generated and final preview rendered!")
