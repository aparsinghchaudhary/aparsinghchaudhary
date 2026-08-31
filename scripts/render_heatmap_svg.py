import json

def render_heatmap(json_path="data/contributions.json", output_svg="contrib-heatmap.svg"):
    with open(json_path, "r") as f:
        data = json.load(f)
        
    days = data["days"]
    color_map = {
        0: "#161b22",
        1: "#0e4429",
        2: "#006d32",
        3: "#26a641",
        4: "#39d353"
    }
    
    box_size = 10
    box_gap = 3
    left_padding = 40
    top_padding = 40
    
    svg_width = 860
    svg_height = 170
    
    rects = ""
    for idx, day in enumerate(days):
        col = idx // 7
        row = idx % 7
        x = left_padding + col * (box_size + box_gap)
        y = top_padding + row * (box_size + box_gap)
        color = color_map.get(day["level"], color_map[0])
        rects += f'<rect x="{x}" y="{y}" width="{box_size}" height="{box_size}" rx="2" fill="{color}"><title>{day["date"]}: {day["count"]} contributions</title></rect>\n'

    metrics_y = svg_height - 15
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">
  <style>
    .bg {{ fill: #0d0d0d; rx: 10px; stroke: #262626; stroke-width: 1.5; }}
    .title {{ font-family: -apple-system, sans-serif; font-size: 13px; fill: #D4AF37; font-weight: bold; }}
    .metric-label {{ font-family: monospace; font-size: 11px; fill: #8b949e; }}
    .metric-val {{ font-family: monospace; font-size: 11px; fill: #58a6ff; font-weight: bold; }}
  </style>
  <rect width="{svg_width}" height="{svg_height}" class="bg"/>
  <text x="20" y="25" class="title">CONTRIBUTION ENGINE CALENDAR</text>
  
  <g>{rects}</g>
  
  <text x="20" y="{metrics_y}" class="metric-label">Total: <tspan class="metric-val">{data['total']}</tspan></text>
  <text x="220" y="{metrics_y}" class="metric-label">Current Streak: <tspan class="metric-val">{data['current_streak']} days</tspan></text>
  <text x="440" y="{metrics_y}" class="metric-label">Longest Streak: <tspan class="metric-val">{data['longest_streak']} days</tspan></text>
  <text x="660" y="{metrics_y}" class="metric-label">Best Day: <tspan class="metric-val">{data['best_day']['count']} commits</tspan></text>
</svg>'''

    with open(output_svg, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Heatmap SVG generated at {output_svg}")

if __name__ == "__main__":
    render_heatmap()
