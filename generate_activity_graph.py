import urllib.request
import json
import os
import subprocess
from datetime import datetime

def get_token():
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        try:
            res = subprocess.check_output(
                'git credential fill',
                input=b'protocol=https\nhost=github.com\n',
                stderr=subprocess.DEVNULL
            ).decode()
            for line in res.splitlines():
                if line.startswith('password='):
                    return line.split('=', 1)[1]
        except Exception:
            pass
    return token

def fetch_activity(token):
    query = """
    query {
      user(login: "bahattinyunus") {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """
    req = urllib.request.Request(
        'https://api.github.com/graphql',
        data=json.dumps({'query': query}).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {token}' if token else '',
            'User-Agent': 'ActivityGraphGenerator/1.0',
            'Content-Type': 'application/json'
        }
    )
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        
    weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    all_days = []
    for w in weeks:
        for d in w['contributionDays']:
            all_days.append((d['date'], d['contributionCount']))
    return all_days[-30:] # Last 30 days

def generate_activity_svg(days):
    width = 840
    height = 280
    pad_left = 60
    pad_right = 40
    pad_top = 70
    pad_bottom = 50
    chart_w = width - pad_left - pad_right
    chart_h = height - pad_top - pad_bottom

    counts = [c for _, c in days]
    max_c = max(counts) if max(counts) > 0 else 5
    # Round max_c up to next multiple of 2 or 5
    max_y = ((max_c // 5) + 1) * 5 if max_c > 5 else 6
    total_c = sum(counts)
    avg_c = total_c / len(counts)

    # Compute point coordinates
    n = len(days)
    points = []
    for i, (dt, count) in enumerate(days):
        x = pad_left + (i / (n - 1)) * chart_w
        y = pad_top + chart_h - (count / max_y) * chart_h
        points.append((x, y, dt, count))

    # Path data
    line_path = f"M {points[0][0]:.1f} {points[0][1]:.1f}"
    for x, y, _, _ in points[1:]:
        line_path += f" L {x:.1f} {y:.1f}"

    area_path = line_path + f" L {points[-1][0]:.1f} {pad_top + chart_h:.1f} L {points[0][0]:.1f} {pad_top + chart_h:.1f} Z"

    # SVG generation
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
  <defs>
    <style>
      .bg {{ fill: #001f3f; stroke: #004080; stroke-width: 1.5; }}
      .title {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Consolas, monospace; font-size: 15px; font-weight: 700; fill: #00d4ff; letter-spacing: 1px; }}
      .sub {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Consolas, monospace; font-size: 11.5px; fill: #8EA7B5; }}
      .axis-label {{ font-family: Consolas, monospace; font-size: 10.5px; fill: #718096; }}
      .grid-line {{ stroke: #103254; stroke-width: 1; stroke-dasharray: 4,4; }}
    </style>
    <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#00d4ff" stop-opacity="0.35" />
      <stop offset="100%" stop-color="#00d4ff" stop-opacity="0.0" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2.5" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>

  <!-- Panel Background -->
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="12" class="bg" />

  <!-- Header -->
  <text x="{pad_left}" y="34" class="title">TACTICAL ACTIVITY // PAST 30 DAYS</text>
  <text x="{pad_left}" y="52" class="sub">Total: {total_c:,} commits   |   Daily Avg: {avg_c:.1f}   |   Peak: {max_c} commits/day</text>

  <!-- Horizontal Grid Lines & Y-Axis Labels -->
"""
    y_steps = 4
    for s in range(y_steps + 1):
        val = int((max_y / y_steps) * (y_steps - s))
        y = pad_top + (s / y_steps) * chart_h
        svg += f'  <line x1="{pad_left}" y1="{y:.1f}" x2="{pad_left + chart_w}" y2="{y:.1f}" class="grid-line" />\n'
        svg += f'  <text x="{pad_left - 10}" y="{y + 4:.1f}" text-anchor="end" class="axis-label">{val}</text>\n'

    svg += f"""
  <!-- Area & Line -->
  <path d="{area_path}" fill="url(#areaGrad)" />
  <path d="{line_path}" fill="none" stroke="#00d4ff" stroke-width="2.5" filter="url(#glow)" />
"""

    # Add points & X-axis labels
    for i, (x, y, dt, count) in enumerate(points):
        # Draw dot
        r = 3.5 if count > 0 else 2
        fill = "#ffffff" if count > 0 else "#004080"
        svg += f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="#00d4ff" stroke-width="1.5" />\n'

        # X-axis label every 5 days or at ends
        if i % 5 == 0 or i == n - 1:
            label_date = datetime.strptime(dt, "%Y-%m-%d").strftime("%b %d")
            svg += f'  <text x="{x:.1f}" y="{pad_top + chart_h + 20}" text-anchor="middle" class="axis-label">{label_date}</text>\n'

    svg += "</svg>"
    return svg

def main():
    token = get_token()
    days = fetch_activity(token)
    svg = generate_activity_svg(days)
    with open('profile-activity.svg', 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Successfully generated profile-activity.svg with {len(days)} days data!")

if __name__ == '__main__':
    main()
