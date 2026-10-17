import urllib.request
import json
import os
import subprocess
import base64

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

def fetch_data(token):
    query = """
    query {
      user(login: "bahattinyunus") {
        name
        login
        avatarUrl
        createdAt
        followers { totalCount }
        following { totalCount }
        starredRepositories { totalCount }
        repositories(first: 100, ownerAffiliations: OWNER, orderBy: {field: UPDATED_AT, direction: DESC}) {
          totalCount
          nodes {
            name
            diskUsage
            stargazerCount
            forkCount
            languages(first: 8, orderBy: {field: SIZE, direction: DESC}) {
              edges {
                size
                node { name color }
              }
            }
          }
        }
        contributionsCollection {
          totalCommitContributions
          totalIssueContributions
          totalPullRequestContributions
          totalPullRequestReviewContributions
          totalRepositoriesWithContributedCommits
        }
      }
    }
    """
    req = urllib.request.Request(
        'https://api.github.com/graphql',
        data=json.dumps({'query': query}).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {token}' if token else '',
            'User-Agent': 'MetricsGenerator/1.0',
            'Content-Type': 'application/json'
        }
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def generate_svg(data):
    user = data['data']['user']
    cc = user['contributionsCollection']
    repos = user['repositories']['nodes']
    
    # Calculate languages
    lang_sizes = {}
    lang_colors = {
        'Python': '#3572A5',
        'C++': '#f34b7d',
        'C': '#555555',
        'TypeScript': '#3178c6',
        'JavaScript': '#f1e05a',
        'C#': '#178600',
        'HTML': '#e34c26',
        'CSS': '#563d7c',
        'Shell': '#89e051',
        'Rust': '#dea584'
    }
    total_stars = 0
    total_forks = 0
    total_disk = 0
    for r in repos:
        total_stars += r.get('stargazerCount', 0)
        total_forks += r.get('forkCount', 0)
        total_disk += r.get('diskUsage', 0)
        for edge in r.get('languages', {}).get('edges', []):
            name = edge['node']['name']
            size = edge['size']
            color = edge['node']['color']
            if color:
                lang_colors[name] = color
            lang_sizes[name] = lang_sizes.get(name, 0) + size

    sorted_langs = sorted(lang_sizes.items(), key=lambda x: x[1], reverse=True)[:6]
    total_lang_size = sum(s for _, s in sorted_langs) or 1
    lang_pcts = [(name, s / total_lang_size * 100, lang_colors.get(name, '#00d4ff')) for name, s in sorted_langs]

    # Convert avatar to base64
    try:
        avatar_req = urllib.request.Request(user['avatarUrl'], headers={'User-Agent': 'MetricsGenerator/1.0'})
        with urllib.request.urlopen(avatar_req) as a_res:
            avatar_b64 = "data:image/jpeg;base64," + base64.b64encode(a_res.read()).decode()
    except Exception:
        avatar_b64 = user['avatarUrl']

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="840" height="420" viewBox="0 0 840 420" role="img">
  <defs>
    <style>
      .bg {{ fill: #07121B; stroke: #1A3547; stroke-width: 1.5; }}
      .title {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; font-size: 19px; font-weight: 700; fill: #38BDF8; }}
      .sub {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; font-size: 12px; fill: #8EA7B5; }}
      .sec-title {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; font-size: 14px; font-weight: 600; fill: #2DD4BF; }}
      .label {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; font-size: 12.5px; fill: #CBD5E1; }}
      .val {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; font-size: 12.5px; font-weight: 600; fill: #F8FAFC; }}
      .grid-cell {{ rx: 2; ry: 2; }}
    </style>
    <clipPath id="avatar-clip">
      <circle cx="48" cy="48" r="24" />
    </clipPath>
  </defs>

  <!-- Background Panel -->
  <rect x="1" y="1" width="838" height="418" rx="14" class="bg" />

  <!-- Avatar & Identity Header -->
  <image href="{avatar_b64}" x="24" y="24" width="48" height="48" clip-path="url(#avatar-clip)" />
  <circle cx="48" cy="48" r="24" fill="none" stroke="#38BDF8" stroke-width="1.5" />
  <text x="86" y="42" class="title">{user['name'] or user['login']}</text>
  <text x="86" y="62" class="sub">Joined GitHub 5 years ago • Followed by {user['followers']['totalCount']:,} users</text>

  <!-- Contribution Grid (Top Right) -->
  <g transform="translate(620, 24)">
    <rect x="0" y="0" width="11" height="11" class="grid-cell" fill="#0E4429" />
    <rect x="14" y="0" width="11" height="11" class="grid-cell" fill="#006D32" />
    <rect x="28" y="0" width="11" height="11" class="grid-cell" fill="#26A641" />
    <rect x="42" y="0" width="11" height="11" class="grid-cell" fill="#39D353" />
    <rect x="56" y="0" width="11" height="11" class="grid-cell" fill="#26A641" />
    <rect x="70" y="0" width="11" height="11" class="grid-cell" fill="#39D353" />
    <rect x="84" y="0" width="11" height="11" class="grid-cell" fill="#39D353" />
    <rect x="98" y="0" width="11" height="11" class="grid-cell" fill="#26A641" />
    <rect x="112" y="0" width="11" height="11" class="grid-cell" fill="#39D353" />
    <rect x="126" y="0" width="11" height="11" class="grid-cell" fill="#006D32" />
    <rect x="140" y="0" width="11" height="11" class="grid-cell" fill="#39D353" />
    <rect x="154" y="0" width="11" height="11" class="grid-cell" fill="#39D353" />
    <rect x="168" y="0" width="11" height="11" class="grid-cell" fill="#26A641" />
    <rect x="182" y="0" width="11" height="11" class="grid-cell" fill="#39D353" />

    <rect x="0" y="14" width="11" height="11" class="grid-cell" fill="#161B22" />
    <rect x="14" y="14" width="11" height="11" class="grid-cell" fill="#0E4429" />
    <rect x="28" y="14" width="11" height="11" class="grid-cell" fill="#006D32" />
    <rect x="42" y="14" width="11" height="11" class="grid-cell" fill="#26A641" />
    <rect x="56" y="14" width="11" height="11" class="grid-cell" fill="#39D353" />
    <rect x="70" y="14" width="11" height="11" class="grid-cell" fill="#39D353" />
    <rect x="84" y="14" width="11" height="11" class="grid-cell" fill="#006D32" />
    <rect x="98" y="14" width="11" height="11" class="grid-cell" fill="#26A641" />
    <rect x="112" y="14" width="11" height="11" class="grid-cell" fill="#39D353" />
    <rect x="126" y="14" width="11" height="11" class="grid-cell" fill="#39D353" />
    <rect x="140" y="14" width="11" height="11" class="grid-cell" fill="#26A641" />
    <rect x="154" y="14" width="11" height="11" class="grid-cell" fill="#006D32" />
    <rect x="168" y="14" width="11" height="11" class="grid-cell" fill="#39D353" />
    <rect x="182" y="14" width="11" height="11" class="grid-cell" fill="#39D353" />
    
    <text x="195" y="44" text-anchor="end" class="sub">Contributed to {cc['totalRepositoriesWithContributedCommits']} repos</text>
  </g>

  <!-- Divider -->
  <line x1="24" y1="88" x2="816" y2="88" stroke="#1A3547" stroke-width="1" />

  <!-- Column 1: Activity -->
  <g transform="translate(36, 116)">
    <text x="0" y="0" class="sec-title">📈 Activity</text>
    <text x="0" y="26" class="label">Commits:</text><text x="160" y="26" class="val" text-anchor="end">{cc['totalCommitContributions']:,}</text>
    <text x="0" y="48" class="label">Pull Requests Reviewed:</text><text x="160" y="48" class="val" text-anchor="end">{cc['totalPullRequestReviewContributions']}</text>
    <text x="0" y="70" class="label">Pull Requests Opened:</text><text x="160" y="70" class="val" text-anchor="end">{cc['totalPullRequestContributions']}</text>
    <text x="0" y="92" class="label">Issues Opened:</text><text x="160" y="92" class="val" text-anchor="end">{cc['totalIssueContributions']}</text>
  </g>

  <!-- Column 2: Community Stats -->
  <g transform="translate(290, 116)">
    <text x="0" y="0" class="sec-title">👥 Community</text>
    <text x="0" y="26" class="label">Followers:</text><text x="160" y="26" class="val" text-anchor="end">{user['followers']['totalCount']:,}</text>
    <text x="0" y="48" class="label">Following:</text><text x="160" y="48" class="val" text-anchor="end">{user['following']['totalCount']:,}</text>
    <text x="0" y="70" class="label">Starred Repositories:</text><text x="160" y="70" class="val" text-anchor="end">{user['starredRepositories']['totalCount']:,}</text>
    <text x="0" y="92" class="label">Contributions Count:</text><text x="160" y="92" class="val" text-anchor="end">{cc['totalCommitContributions'] + cc['totalPullRequestContributions']:,}</text>
  </g>

  <!-- Column 3: Repositories -->
  <g transform="translate(540, 116)">
    <text x="0" y="0" class="sec-title">📦 Repositories</text>
    <text x="0" y="26" class="label">Public Repositories:</text><text x="160" y="26" class="val" text-anchor="end">{user['repositories']['totalCount']}</text>
    <text x="0" y="48" class="label">Total Disk Usage:</text><text x="160" y="48" class="val" text-anchor="end">{total_disk / 1024:.1f} MB</text>
    <text x="0" y="70" class="label">Stargazers:</text><text x="160" y="70" class="val" text-anchor="end">{total_stars:,}</text>
    <text x="0" y="92" class="label">Forks:</text><text x="160" y="92" class="val" text-anchor="end">{total_forks:,}</text>
  </g>

  <!-- Divider -->
  <line x1="24" y1="240" x2="816" y2="240" stroke="#1A3547" stroke-width="1" />

  <!-- Most Used Languages Section -->
  <g transform="translate(36, 268)">
    <text x="0" y="0" class="sec-title">⚡ Most Used Languages</text>

    <!-- Progress Bar -->
    <g transform="translate(0, 14)">
      <rect x="0" y="0" width="768" height="12" rx="6" fill="#161B22" />
"""

    # Add colored segments
    curr_x = 0
    for name, pct, col in lang_pcts:
        seg_w = (pct / 100.0) * 768.0
        svg += f'      <rect x="{curr_x:.1f}" y="0" width="{seg_w:.1f}" height="12" rx="4" fill="{col}" />\n'
        curr_x += seg_w

    svg += """    </g>

    <!-- Language Labels -->
    <g transform="translate(0, 48)">
"""
    col_x = 0
    for i, (name, pct, col) in enumerate(lang_pcts):
        x = (i % 3) * 260
        y = (i // 3) * 28
        svg += f"""      <circle cx="{x + 6}" cy="{y}" r="5" fill="{col}" />
      <text x="{x + 18}" y="{y + 4}" class="label">{name} <tspan class="val">({pct:.1f}%)</tspan></text>
"""

    svg += """    </g>
  </g>
</svg>"""
    return svg

def main():
    token = get_token()
    data = fetch_data(token)
    svg = generate_svg(data)
    with open('github-metrics.svg', 'w', encoding='utf-8') as f:
        f.write(svg)
    print("Successfully generated github-metrics.svg!")

if __name__ == '__main__':
    main()
