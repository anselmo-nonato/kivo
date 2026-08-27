import numpy as np
from PIL import Image

def generate_perfect_svgs():
    # Coordenadas exatas extraídas do PNG 1536x1024
    
    # 1. kivo_logo.svg (Light mode / Transparente com texto original)
    svg_light = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1536 1024" width="100%" height="100%">
  <defs>
    <!-- Gradiente da Haste Vertical Esquerda (Verde vibrante para Verde Petróleo) -->
    <linearGradient id="kivoStemGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#00D287" />
      <stop offset="60%" stop-color="#00AD6F" />
      <stop offset="100%" stop-color="#006C59" />
    </linearGradient>

    <!-- Gradiente da Seta Superior de Crescimento -->
    <linearGradient id="kivoArrowGrad" x1="0%" y1="100%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00B373" />
      <stop offset="100%" stop-color="#00D98B" />
    </linearGradient>

    <!-- Gradiente do Braço / Fita Inferior -->
    <linearGradient id="kivoLowerRibbonGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#009B66" />
      <stop offset="60%" stop-color="#00B87A" />
      <stop offset="100%" stop-color="#00D287" />
    </linearGradient>

    <!-- Gradiente do Destaque de Dobra da Fita (Luz Frontal) -->
    <linearGradient id="kivoFoldHighlight" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#3BF0AB" />
      <stop offset="50%" stop-color="#00D287" />
      <stop offset="100%" stop-color="#00A86E" />
    </linearGradient>

    <!-- Gradiente da Sombra Interna da Dobra -->
    <linearGradient id="kivoFoldShadow" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#008055" />
      <stop offset="100%" stop-color="#004D38" />
    </linearGradient>
  </defs>

  <!-- ==================== ÍCONE KIVO ==================== -->
  <g id="kivo-symbol">
    <!-- 1. HASTE VERTICAL COM ANEL VAZADO INFERIOR -->
    <path d="M 200,327 
             A 32.5,32.5 0 0,1 265,327 
             L 265,580 
             A 62.5,62.5 0 0,1 279.5,635.5 
             A 62.5,62.5 0 1,1 154.5,635.5 
             A 62.5,62.5 0 0,1 200,580 
             Z
             M 217,614
             A 21.5,21.5 0 1,0 217,657
             A 21.5,21.5 0 1,0 217,614
             Z" 
          fill="url(#kivoStemGrad)" 
          fill-rule="evenodd" />

    <!-- 2. BRAÇO DIAGONAL SUPERIOR COM SETA DE CRESCIMENTO -->
    <path d="M 245,515 
             L 375,390 
             L 415,390 
             L 265,540 
             Z" 
          fill="url(#kivoArrowGrad)" />
    <!-- Ponta da Seta (Triângulo retângulo de precisão) -->
    <polygon points="473,288 473,390 351,390" fill="#00D287" />

    <!-- 3. BRAÇO DIAGONAL INFERIOR (FITA COM PONTA ARREDONDADA) -->
    <!-- Corpo principal da fita inferior: vai da interseção até a ponta inferior direita -->
    <path d="M 248,475 
             L 445,585 
             A 26,26 0 0,1 472,618 
             A 26,26 0 0,1 445,644 
             L 263,644 
             L 240,560 
             Z" 
          fill="url(#kivoLowerRibbonGrad)" />

    <!-- 4. SOMBRA INTERNA DA DOBRA (PROFUNDIDADE 3D) -->
    <polygon points="248,475 315,532 260,578 240,540" fill="url(#kivoFoldShadow)" />

    <!-- 5. DOBRA FRONTAL LUMINOSA (EFEITO ORIGAMI / FITA VIVA) -->
    <path d="M 242,460 
             C 242,442 262,430 282,445 
             L 330,488 
             C 338,495 338,508 330,515 
             L 278,556 
             C 255,570 242,548 242,530 
             Z" 
          fill="url(#kivoFoldHighlight)" />
  </g>

  <!-- ==================== TIPOGRAFIA: K I V O ==================== -->
  <g id="kivo-wordmark" fill="#051329">
    <!-- K -->
    <path d="M 559,373 L 608,373 L 608,578 L 559,578 Z
             M 684,373 L 751,373 L 634,482 L 751,578 L 684,578 L 596,498 L 684,373 Z" />
    <!-- I -->
    <rect x="797" y="373" width="47" height="205" rx="3" />
    <!-- V -->
    <path d="M 878,373 L 930,373 L 995,540 L 1060,373 L 1112,373 L 1021,578 L 969,578 Z" />
    <!-- O -->
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

  <!-- ==================== TIPOGRAFIA: F I N A N Ç A S ==================== -->
  <g id="kivo-subtitle" fill="#009B66">
    <text x="567" y="650" 
          font-family="system-ui, -apple-system, 'Plus Jakarta Sans', 'Inter', 'Segoe UI', sans-serif" 
          font-size="34" 
          font-weight="700" 
          letter-spacing="24">
      FINANÇAS
    </text>
  </g>
</svg>'''

    # 2. kivo_icon.svg (Apenas o símbolo isolado em proporção quadrada 600x600)
    svg_icon = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="100%" height="100%">
  <defs>
    <linearGradient id="iconStemGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#00D287" />
      <stop offset="60%" stop-color="#00AD6F" />
      <stop offset="100%" stop-color="#006C59" />
    </linearGradient>

    <linearGradient id="iconArrowGrad" x1="0%" y1="100%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00B373" />
      <stop offset="100%" stop-color="#00D98B" />
    </linearGradient>

    <linearGradient id="iconLowerRibbonGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#009B66" />
      <stop offset="60%" stop-color="#00B87A" />
      <stop offset="100%" stop-color="#00D287" />
    </linearGradient>

    <linearGradient id="iconFoldHighlight" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#3BF0AB" />
      <stop offset="50%" stop-color="#00D287" />
      <stop offset="100%" stop-color="#00A86E" />
    </linearGradient>

    <linearGradient id="iconFoldShadow" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#008055" />
      <stop offset="100%" stop-color="#004D38" />
    </linearGradient>
  </defs>

  <g transform="translate(140, 50)">
    <!-- Haste e Anel -->
    <path d="M 50,45 A 32.5,32.5 0 0,1 115,45 L 115,298 A 62.5,62.5 0 0,1 129.5,353.5 A 62.5,62.5 0 1,1 4.5,353.5 A 62.5,62.5 0 0,1 50,298 Z M 67,332 A 21.5,21.5 0 1,0 67,375 A 21.5,21.5 0 1,0 67,332 Z" fill="url(#iconStemGrad)" fill-rule="evenodd" />

    <!-- Seta Diagonal Superior -->
    <path d="M 95,233 L 225,108 L 265,108 L 115,258 Z" fill="url(#iconArrowGrad)" />
    <polygon points="323,6 323,108 201,108" fill="#00D287" />

    <!-- Fita Inferior -->
    <path d="M 98,193 L 295,303 A 26,26 0 0,1 322,336 A 26,26 0 0,1 295,362 L 113,362 L 90,278 Z" fill="url(#iconLowerRibbonGrad)" />

    <!-- Sombra Interna da Dobra -->
    <polygon points="98,193 165,250 110,296 90,258" fill="url(#iconFoldShadow)" />

    <!-- Dobra Frontal Luminosa -->
    <path d="M 92,178 C 92,160 112,148 132,163 L 180,206 C 188,213 188,226 180,233 L 128,274 C 105,288 92,266 92,248 Z" fill="url(#iconFoldHighlight)" />
  </g>
</svg>'''

    # 3. kivo_logo_dark.svg (Dark Mode)
    svg_dark = svg_light.replace(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1536 1024" width="100%" height="100%">',
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1536 1024" width="100%" height="100%">\n  <rect width="1536" height="1024" fill="#0B132B" />'
    ).replace('fill="#051329"', 'fill="#FFFFFF"').replace('fill="#009B66"', 'fill="#00E599"')

    with open('assets/kivo_logo.svg', 'w', encoding='utf-8') as f:
        f.write(svg_light)
    with open('assets/kivo_icon.svg', 'w', encoding='utf-8') as f:
        f.write(svg_icon)
    with open('assets/kivo_logo_dark.svg', 'w', encoding='utf-8') as f:
        f.write(svg_dark)
        
    print("All SVGs updated with exact geometry and smooth vectors!")

generate_perfect_svgs()
