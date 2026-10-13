from pathlib import Path
from zipfile import ZipFile
import re
from bs4 import BeautifulSoup
from docx import Document


def html_to_md(text: str) -> str:
    soup = BeautifulSoup(text, 'html.parser')
    lines = []
    for node in soup.find_all(['h1','h2','h3','p','li']):
        value = node.get_text(' ', strip=True)
        if node.name.startswith('h'):
            lines.append('#' * int(node.name[1]) + ' ' + value)
        elif node.name == 'li':
            lines.append('- ' + value)
        else:
            lines.append(value)
    return '\n\n'.join(lines) + '\n'


def convert(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == '.md':
        return path.read_text(encoding='utf-8')
    if ext == '.html':
        return html_to_md(path.read_text(encoding='utf-8'))
    if ext == '.docx':
        doc = Document(path)
        lines = []
        for p in doc.paragraphs:
            text = p.text.strip()
            if not text:
                continue
            style = p.style.name if p.style else ''
            if style.startswith('Heading'):
                level = int(style.split()[-1]) if style.split()[-1].isdigit() else 1
                lines.append('#' * level + ' ' + text)
            elif style.startswith('List'):
                lines.append('- ' + text)
            else:
                lines.append(text)
        return '\n\n'.join(lines) + '\n'
    if ext == '.epub':
        with ZipFile(path) as z:
            docs = [n for n in z.namelist() if n.lower().endswith(('.xhtml','.html','.htm'))]
            return '\n'.join(html_to_md(z.read(n).decode('utf-8')) for n in docs)
    if ext == '.tex':
        text = path.read_text(encoding='utf-8')
        lines = []
        m = re.search(r'\\section\{([^}]*)\}', text)
        if m:
            lines.append('# ' + m.group(1))
        body = re.sub(r'\\section\{[^}]*\}', '', text)
        body = re.sub(r'\\begin\{itemize\}|\\end\{itemize\}', '', body)
        items = re.findall(r'\\item\s+([^\\\n]+)', body)
        body = re.sub(r'\\item\s+[^\\\n]+', '', body)
        prose = ' '.join(x.strip() for x in body.splitlines() if x.strip())
        if prose:
            lines.append(prose)
        lines.extend('- ' + x.strip() for x in items)
        return '\n\n'.join(lines) + '\n'
    if ext == '.rst':
        lines = path.read_text(encoding='utf-8').splitlines()
        out = []
        i = 0
        while i < len(lines):
            if i + 1 < len(lines) and lines[i] and set(lines[i+1]) == {'='}:
                out.append('# ' + lines[i]); i += 2; continue
            line = lines[i].strip()
            if line:
                out.append(line)
            i += 1
        return '\n\n'.join(out) + '\n'
    raise ValueError(f'unsupported format: {ext}')
