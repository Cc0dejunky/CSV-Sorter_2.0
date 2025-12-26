"""Generate an HTML word-cloud diagnostics from products and feedback.

- Reads `products` and `feedback` from dev.db via `db_adapter`.
- Computes frequency of `text_content` and average confidence for each unique value.
- Writes `diagnostics.html` using WordCloud2.js and attempts to open it in the browser.

Usage:
    python scripts/generate_cloud.py --out diagnostics.html --limit 200
"""
import os
import json
import argparse
import webbrowser
from collections import defaultdict
from db_adapter import get_connection, ensure_tables

HTML_TEMPLATE = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>CSV-Sorter Diagnostics Word Cloud</title>
  <style>body {{ font-family: Arial, Helvetica, sans-serif; margin: 24px; }}</style>
</head>
<body>
  <h1>Word Cloud — Frequency & Confidence</h1>
  <p>Size = frequency of the raw text. Color = average confidence (green=high, red=low).</p>
  <div id="wordcloud" style="width:100%; height:700px; border:1px solid #eee"></div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/wordcloud2.js/1.1.0/wordcloud2.min.js"></script>
  <script>
    const list = {list_json};
    const colors = {colors_json};

    function getColor(word, weight) {{
      return colors[word] || '#444';
    }}

    // convert list to wordcloud format: [['text', weight], ...]
    const arr = list.map(o => [o.text, o.weight]);

    WordCloud(document.getElementById('wordcloud'), {{
      list: arr,
      gridSize: Math.max(8, Math.round(16 * (window.innerWidth / 1024))),
      weightFactor: function (size) {{ return Math.log(size+1) * 20; }},
      color: function (word, weight) {{ return getColor(word, weight); }},
      rotateRatio: 0.1,
      backgroundColor: '#fff'
    }});
  </script>
</body>
</html>
"""


def conf_to_hex(c):
    """Interpolate between red (0) and green (1) for confidence c in [0,1]."""
    c = max(0.0, min(1.0, float(c)))
    r = int((1.0 - c) * 255)
    g = int(c * 200 + c * 55)  # boost green slightly
    b = int((1.0 - c) * 100)
    return f"#{r:02x}{g:02x}{b:02x}"


def collect_stats(limit=200):
    ensure_tables()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT text_content, confidence FROM products")
    rows = cur.fetchall()

    freq = defaultdict(int)
    conf_sum = defaultdict(float)
    conf_count = defaultdict(int)
    for r in rows:
        text = r[0] or ''
        text = text.strip()
        if not text:
            continue
        freq[text] += 1
        try:
            conf = float(r[1] or 0.0)
        except Exception:
            conf = 0.0
        conf_sum[text] += conf
        conf_count[text] += 1

    # Build list sorted by frequency
    items = []
    for t, f in freq.items():
        avg_conf = (conf_sum[t] / conf_count[t]) if conf_count[t] else 0.0
        items.append((t, f, round(avg_conf, 3)))
    items.sort(key=lambda x: x[1], reverse=True)
    items = items[:limit]

    list_json = json.dumps([{"text": t, "weight": f} for t,f,_ in items])
    colors_json = json.dumps({t: conf_to_hex(avg) for (t,f,avg) in items})
    conn.close()
    return list_json, colors_json


def write_html(out_path, list_json, colors_json):
    html = HTML_TEMPLATE.format(list_json=list_json, colors_json=colors_json)
    with open(out_path, 'w', encoding='utf-8') as fh:
        fh.write(html)
    print(f"Wrote diagnostics HTML to {out_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='diagnostics.html')
    parser.add_argument('--limit', type=int, default=200)
    parser.add_argument('--open', dest='do_open', action='store_true', default=True,
                        help='Attempt to open generated HTML in browser')
    parser.add_argument('--no-open', dest='do_open', action='store_false',
                        help='Do not open generated HTML in browser')
    parser.add_argument('--open-n', type=int, default=1, help='Number of windows/tabs to open (max 10)')
    parser.add_argument('--new-window', action='store_true', help='Open in new browser window(s) instead of new tab(s)')
    args = parser.parse_args()

    list_json, colors_json = collect_stats(limit=args.limit)
    write_html(args.out, list_json, colors_json)

    # Attempt to open (honor flags)
    if not args.do_open:
        print(f"Skipped opening {args.out} in browser (--no-open)")
        return

    file_url = 'file://' + os.path.abspath(args.out)
    opened = 0
    max_open = max(0, min(10, args.open_n))
    for i in range(max_open):
        try:
            if args.new_window:
                # new=1 requests a new browser window
                success = webbrowser.open(file_url, new=1)
            else:
                success = webbrowser.open_new_tab(file_url)
            if success:
                opened += 1
            print(f"Attempted to open {file_url} ({'window' if args.new_window else 'tab'})")
        except Exception as e:
            print(f"Could not open browser automatically on attempt {i+1}: {e}")
            break

    if opened:
        print(f"Opened {opened} instance(s) of {file_url} in your browser (best-effort)")
    else:
        print("No browser windows/tabs were opened automatically; you can open the file manually.")


if __name__ == '__main__':
    main()
