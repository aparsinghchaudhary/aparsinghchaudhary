import numpy as np
from PIL import Image

def generate_ascii_svg(image_path="source-prepped.png", output_path="hxni-ascii.svg", width=65):
    img = Image.open(image_path).convert("L")
    
    # Monospace aspect ratio adjustment (characters are ~2x taller than wide)
    aspect_ratio = img.height / img.width
    height = int(width * aspect_ratio * 0.48)
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    
    pixels = np.array(img)
    ramp = " .:-=+*cs#%@"
    ramp_len = len(ramp)
    
    ascii_rows = []
    for row in pixels:
        line = "".join([ramp[int((pixel / 255) * (ramp_len - 1))] for pixel in row])
        ascii_rows.append(line)
    
    # Build SVG
    char_width = 5.5
    line_height = 8.8
    svg_width = int(width * char_width) + 30
    svg_height = int(height * line_height) + 40
    
    tspan_lines = ""
    for idx, row in enumerate(ascii_rows):
        # Escape XML entities
        escaped_row = row.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace(" ", "&#160;")
        tspan_lines += f'<tspan x="15" dy="{line_height if idx > 0 else 0}">{escaped_row}</tspan>\n'
    
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">
  <style>
    .bg {{ fill: #0d0d0d; rx: 10px; ry: 10px; stroke: #262626; stroke-width: 1.5; }}
    .ascii {{
      font-family: 'Courier New', Courier, monospace;
      font-size: 7.5px;
      font-weight: bold;
      fill: #D4AF37;
      letter-spacing: 0.5px;
    }}
    .dot-red {{ fill: #ff5f56; }}
    .dot-yellow {{ fill: #ffbd2e; }}
    .dot-green {{ fill: #27c93f; }}
    @keyframes fin {{
      from {{ opacity: 0; transform: translateY(4px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    .animated-text {{
      animation: fin 0.8s ease-out forwards;
    }}
  </style>
  <rect width="{svg_width}" height="{svg_height}" class="bg" />
  <circle cx="15" cy="15" r="4" class="dot-red" />
  <circle cx="27" cy="15" r="4" class="dot-yellow" />
  <circle cx="39" cy="15" r="4" class="dot-green" />
  <g class="animated-text">
    <text x="15" y="32" class="ascii">
      {tspan_lines}
    </text>
  </g>
</svg>'''

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"ASCII terminal SVG saved to {output_path}")

if __name__ == "__main__":
    generate_ascii_svg()
