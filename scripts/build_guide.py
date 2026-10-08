"""Render our local Markdown lessons to static HTML using a small safe subset."""
from pathlib import Path
import html
import re
root=Path(__file__).resolve().parents[1]
def inline(value):
    value=html.escape(value)
    value=re.sub(r'`([^`]+)`',r'<code>\1</code>',value)
    value=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',value)
    value=re.sub(r'\[([^\]]+)\]\(([^ )]+)\)',lambda m:'<a href="'+html.escape(m[2],quote=True)+'">'+m[1]+'</a>',value)
    return value
css='html{color-scheme:light dark;font:17px/1.7 system-ui}body{max-width:860px;margin:36px auto;padding:0 24px}h1,h2{line-height:1.3}h2{margin-top:2em}pre{padding:16px;overflow:auto;background:#8882;border-radius:8px}code{font-size:.9em}li{margin:.4em 0}table{border-collapse:collapse}td,th{padding:8px;border-bottom:1px solid #8885}a{color:inherit}'
for source,target in [('docs/tutorial-0.md','web/tutorial-0.html')]:
    lines=(root/source).read_text().splitlines();out=[];paragraph=[];listing=False;code=None
    def flush():
        if paragraph:out.append('<p>'+inline(' '.join(paragraph))+'</p>');paragraph.clear()
    for line in lines:
        if line.startswith('```'):
            flush()
            if code is None:code=[]
            else:out.append('<pre><code>'+html.escape('\n'.join(code))+'</code></pre>');code=None
            continue
        if code is not None:code.append(line);continue
        if not line.startswith('- ') and listing:out.append('</ul>');listing=False
        if not line:flush();continue
        if line.startswith('#'):
            flush();level=len(line)-len(line.lstrip('#'));out.append(f'<h{level}>'+inline(line[level:].strip())+f'</h{level}>')
        elif line.startswith('- '):
            flush()
            if not listing:out.append('<ul>');listing=True
            out.append('<li>'+inline(line[2:])+'</li>')
        else:paragraph.append(line)
    flush()
    (root/target).write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tutorial 0 · GeneretiCore</title><style>'+css+'</style><body>'+''.join(out)+'</body></html>')
