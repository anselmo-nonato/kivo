import subprocess
import os

svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1536 1024" width="100%" height="100%">
  <defs>
    <!-- Gradiente da Haste Vertical Esquerda (Verde Esmeralda Topo -> Verde Petróleo Base) -->
    <linearGradient id="stemGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#14E59C" />
      <stop offset="30%" stop-color="#00C980" />
      <stop offset="65%" stop-color="#00A068" />
      <stop offset="100%" stop-color="#006C59" />
    </linearGradient>

    <!-- Gradiente da Seta Superior de Crescimento -->
    <linearGradient id="arrowGrad" x1="0%" y1="100%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00AD6D" />
      <stop offset="100%" stop-color="#00DC8C" />
    </linearGradient>

    <!-- Gradiente do Braço Inferior (Capsule 45 deg) -->
    <linearGradient id="lowerArmGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#007F55" />
      <stop offset="40%" stop-color="#00AF72" />
      <stop offset="85%" stop-color="#00DC8C" />
      <stop offset="100%" stop-color="#14E59C" />
    </linearGradient>

    <!-- Gradiente da Face Frontal da Dobra (Luz Iluminada no Origami) -->
    <linearGradient id="ribbonFoldFrontGrad" x1="0%" y1="100%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#3EF7AE" />
      <stop offset="45%" stop-color="#14E39B" />
      <stop offset="100%" stop-color="#00BA7A" />
    </linearGradient>

    <!-- Gradiente da Face Interna Sombreada da Dobra (Profundidade 3D) -->
    <linearGradient id="ribbonShadowGrad" x1="0%" y1="0%" x2="50%" y2="100%">
      <stop offset="0%" stop-color="#00704A" />
      <stop offset="50%" stop-color="#004A32" />
      <stop offset="100%" stop-color="#002D1E" />
    </linearGradient>
  </defs>

  <!-- ==================== ÍCONE KIVO ==================== -->
  <g id="kivo-icon">
    <!-- 1. HASTE VERTICAL COM ANEL VAZADO INFERIOR -->
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

    <!-- 2. BRAÇO SUPERIOR E PONTA DA SETA -->
    <polygon points="265,505 375,395 422,395 265,552" fill="url(#arrowGrad)" />
    <polygon points="472,288 472,390 340,390" fill="#00DC8C" />

    <!-- 3. BRAÇO DIAGONAL INFERIOR (Cápsula com ponta arredondada) -->
    <path d="M 270,515 
             L 435,608 
             A 28.5,28.5 0 0,1 435,648 
             L 395,648 
             L 255,580 
             Z" 
          fill="url(#lowerArmGrad)" />

    <!-- 4. FACE INTERNA SOMBREADA DA DOBRA (CUNHA 3D) -->
    <path d="M 285,480 
             L 245,520 
             C 238,542 245,562 258,580 
             L 295,540 
             Z" 
          fill="url(#ribbonShadowGrad)" />

    <!-- 5. FACE FRONTAL ILUMINADA DA DOBRA (FITA EM V) -->
    <path d="M 375,395 
             L 255,515 
             A 28.5,28.5 0 0,1 215,475 
             L 328,362 
             L 375,395 
             Z" 
          fill="url(#ribbonFoldFrontGrad)" />
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
    <text x="567" y="650" font-family="system-ui, -apple-system, 'Plus Jakarta Sans', 'Inter', 'Segoe UI', sans-serif" font-size="34" font-weight="700" letter-spacing="24">
      FINANÇAS
    </text>
  </g>
</svg>'''

with open('assets/kivo_logo.svg', 'w', encoding='utf-8') as f:
    f.write(svg_content)

# Icon only SVG
svg_icon = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="100%" height="100%">
  <defs>
    <linearGradient id="iconStemGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#14E59C" />
      <stop offset="30%" stop-color="#00C980" />
      <stop offset="65%" stop-color="#00A068" />
      <stop offset="100%" stop-color="#006C59" />
    </linearGradient>
    <linearGradient id="iconArrowGrad" x1="0%" y1="100%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00AD6D" />
      <stop offset="100%" stop-color="#00DC8C" />
    </linearGradient>
    <linearGradient id="iconLowerArmGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#007F55" />
      <stop offset="40%" stop-color="#00AF72" />
      <stop offset="85%" stop-color="#00DC8C" />
      <stop offset="100%" stop-color="#14E59C" />
    </linearGradient>
    <linearGradient id="iconFoldFrontGrad" x1="0%" y1="100%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#3EF7AE" />
      <stop offset="45%" stop-color="#14E39B" />
      <stop offset="100%" stop-color="#00BA7A" />
    </linearGradient>
    <linearGradient id="iconShadowGrad" x1="0%" y1="0%" x2="50%" y2="100%">
      <stop offset="0%" stop-color="#00704A" />
      <stop offset="50%" stop-color="#004A32" />
      <stop offset="100%" stop-color="#002D1E" />
    </linearGradient>
  </defs>

  <g transform="translate(145, 50)">
    <path d="M 60,47 A 32.5,32.5 0 0,1 125,47 L 125,302 A 62.5,62.5 0 0,1 139.5,355.5 A 62.5,62.5 0 1,1 14.5,355.5 A 62.5,62.5 0 0,1 60,302 Z M 77,334 A 21.5,21.5 0 1,0 77,377 A 21.5,21.5 0 1,0 77,334 Z" fill="url(#iconStemGrad)" fill-rule="evenodd" />
    <polygon points="125,225 235,115 282,115 125,272" fill="url(#iconArrowGrad)" />
    <polygon points="332,8 332,110 200,110" fill="#00DC8C" />
    <path d="M 130,235 L 295,328 A 28.5,28.5 0 0,1 295,368 L 255,368 L 115,300 Z" fill="url(#iconLowerArmGrad)" />
    <path d="M 145,200 L 105,240 C 98,262 105,282 118,300 L 155,260 Z" fill="url(#iconShadowGrad)" />
    <path d="M 235,115 L 115,235 A 28.5,28.5 0 0,1 75,195 L 188,82 L 235,115 Z" fill="url(#iconFoldFrontGrad)" />
  </g>
</svg>'''

with open('assets/kivo_icon.svg', 'w', encoding='utf-8') as f:
    f.write(svg_icon)

# Dark mode SVG
svg_dark = svg_content.replace(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1536 1024" width="100%" height="100%">',
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1536 1024" width="100%" height="100%">\n  <rect width="1536" height="1024" fill="#0B132B" />'
).replace('fill="#051329"', 'fill="#FFFFFF"').replace('fill="#009B66"', 'fill="#00E599"')

with open('assets/kivo_logo_dark.svg', 'w', encoding='utf-8') as f:
    f.write(svg_dark)

edge = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
html_path = os.path.abspath('assets/preview.html').replace('\\', '/')
out_path = os.path.abspath('assets/rendered_output.png')

cmd = [
    edge,
    '--headless',
    '--disable-gpu',
    f'--screenshot={out_path}',
    '--window-size=1200,900',
    f'file:///{html_path}'
]
subprocess.run(cmd, capture_output=True)
print("Final render completed!")
