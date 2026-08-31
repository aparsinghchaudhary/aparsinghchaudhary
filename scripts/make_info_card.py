def generate_info_card(output_path="info-card.svg"):
    config = {
        "username": "[YOUR_GITHUB_USERNAME]",
        "name": "[YOUR_NAME]",
        "title": "[YOUR_TITLE]",
        "location": "[YOUR_LOCATION]",
        "email": "[YOUR_EMAIL]",
        "portfolio": "[YOUR_PORTFOLIO_URL]",
        "frontend": "[e.g., React, TypeScript, Vite, Tailwind CSS]",
        "backend": "[e.g., Node.js, Express, Python, MySQL]",
        "mobile": "[e.g., React Native, Flutter]"
    }
    
    svg_width = 490
    svg_height = 300
    
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">
  <style>
    .bg {{ fill: #0d0d0d; rx: 10px; ry: 10px; stroke: #262626; stroke-width: 1.5; }}
    .header-text {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 11px; fill: #737373; font-weight: 600; }}
    .key {{ font-family: 'Courier New', monospace; font-size: 11.5px; fill: #D4AF37; font-weight: bold; }}
    .val {{ font-family: 'Courier New', monospace; font-size: 11.5px; fill: #E5E5E5; }}
    .accent {{ fill: #38BDF8; font-weight: bold; }}
    .dot-red {{ fill: #ff5f56; }}
    .dot-yellow {{ fill: #ffbd2e; }}
    .dot-green {{ fill: #27c93f; }}
    
    .line {{ animation: fadeIn 0.5s ease-out forwards; opacity: 0; }}
    @keyframes fadeIn {{ to {{ opacity: 1; }} }}
  </style>
  
  <rect width="{svg_width}" height="{svg_height}" class="bg" />
  <circle cx="15" cy="15" r="4" class="dot-red" />
  <circle cx="27" cy="15" r="4" class="dot-yellow" />
  <circle cx="39" cy="15" r="4" class="dot-green" />
  <text x="60" y="18" class="header-text">The Cipher Stack — bash - 80x24</text>
  <line x1="0" y1="30" x2="{svg_width}" y2="30" stroke="#1f1f1f" stroke-width="1" />

  <g transform="translate(20, 50)">
    <g class="line" style="animation-delay: 0.1s;"><text y="0" class="key">USER    </text><text y="0" x="90" class="val">{config['username']} @ {config['name']}</text></g>
    <g class="line" style="animation-delay: 0.2s;"><text y="22" class="key">ROLE    </text><text y="22" x="90" class="val">{config['title']}</text></g>
    <g class="line" style="animation-delay: 0.3s;"><text y="44" class="key">LOC     </text><text y="44" x="90" class="val">{config['location']}</text></g>
    <g class="line" style="animation-delay: 0.4s;"><text y="66" class="key">FRONTEND</text><text y="66" x="90" class="val">{config['frontend']}</text></g>
    <g class="line" style="animation-delay: 0.5s;"><text y="88" class="key">BACKEND </text><text y="88" x="90" class="val">{config['backend']}</text></g>
    <g class="line" style="animation-delay: 0.6s;"><text y="110" class="key">MOBILE  </text><text y="110" x="90" class="val">{config['mobile']}</text></g>
    <g class="line" style="animation-delay: 0.7s;"><text y="132" class="key">EMAIL   </text><text y="132" x="90" class="val accent">{config['email']}</text></g>
    <g class="line" style="animation-delay: 0.8s;"><text y="154" class="key">URL     </text><text y="154" x="90" class="val accent">{config['portfolio']}</text></g>
    <g class="line" style="animation-delay: 0.9s;"><text y="176" class="key">STATUS  </text><text y="176" x="90" class="val" style="fill:#4ADE80;">● Active — Building Next-Gen Web</text></g>
  </g>
</svg>'''

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Info Card SVG saved to {output_path}")

if __name__ == "__main__":
    generate_info_card()
