from pathlib import Path
import ast, hashlib, importlib, json, platform, subprocess, sys, time

ROOT=Path(__file__).resolve().parent
FIX=ROOT/'fixtures'; OUT=ROOT/'out'; OUT.mkdir(exist_ok=True)
MARKER='RIGHT_TOOL_PANDOC_MARKER_314159'; TITLE='Right Tool Bakeoff'; ITEMS=['Alpha item','Beta item']
FILES=sorted(FIX.iterdir())

def load(name): return importlib.import_module(name)

def check(text):
    return {
        'marker': MARKER in text,
        'heading': TITLE in text,
        'item_alpha': ITEMS[0] in text,
        'item_beta': ITEMS[1] in text,
    }

def timed(module_name, dest):
    mod=load(module_name); dest.mkdir(parents=True, exist_ok=True)
    t0=time.perf_counter(); rows=[]
    for p in FILES:
        try:
            text=mod.convert(p); ok=check(text); success=all(ok.values()); error=None
        except Exception as e:
            text=''; ok={k:False for k in ('marker','heading','item_alpha','item_beta')}; success=False; error=repr(e)
        (dest/(p.name+'.md')).write_text(text,encoding='utf-8')
        rows.append({'file':p.name,'success':success,'checks':ok,'error':error,'output_chars':len(text)})
    return time.perf_counter()-t0, rows

def source_metrics(path):
    text=path.read_text(encoding='utf-8'); tree=ast.parse(text)
    code_lines=[]
    for line in text.splitlines():
        s=line.strip()
        if s and not s.startswith('#'): code_lines.append(line)
    suffix_branches=0
    for node in ast.walk(tree):
        if isinstance(node,ast.If):
            src=ast.get_source_segment(text,node.test) or ''
            if 'ext' in src or 'suffix' in src: suffix_branches += 1
    return {'noncomment_source_lines':len(code_lines),'format_dispatch_branches':suffix_branches}

def sha256(p):
    h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()

results={'schema_version':1,'files':[{'name':p.name,'bytes':p.stat().st_size,'sha256':sha256(p)} for p in FILES]}
for name in ['pandoc_converter','python_converter']:
    cold, cold_rows=timed(name,OUT/name.replace('_converter',''))
    warm, warm_rows=timed(name,OUT/name.replace('_converter',''))
    src=ROOT/(name+'.py')
    results[name.replace('_converter','')]={'cold_seconds':cold,'second_seconds':warm,'cold':cold_rows,'second':warm_rows,'coverage':sum(r['success'] for r in warm_rows),'source_metrics':source_metrics(src)}

results['versions']={
    'python':sys.version.split()[0],
    'platform':platform.platform(),
    'pandoc':subprocess.check_output(['pandoc','--version'],text=True).splitlines()[0],
}
(ROOT/'results.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
print(json.dumps(results,indent=2))
