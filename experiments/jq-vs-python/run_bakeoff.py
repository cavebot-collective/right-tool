from __future__ import annotations
import ast, hashlib, json, statistics, subprocess, sys, time
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'; OUT=ROOT/'out'; OUT.mkdir(exist_ok=True)
JQ=ROOT/'transform.jq'; PY=ROOT/'python_transform.py'

def sha256(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def run(cmd, data_path):
    with data_path.open('rb') as inp:
        cp=subprocess.run(cmd,stdin=inp,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return cp.stdout

def measure(cmd, data_path):
    run(cmd,data_path)
    samples=[]; output=None
    for _ in range(7):
        t0=time.perf_counter(); output=run(cmd,data_path); samples.append(time.perf_counter()-t0)
    return {'samples_seconds':samples,'median_seconds':statistics.median(samples),'output':output}

def noncomment_lines(path):
    return sum(1 for line in path.read_text().splitlines() if line.strip() and not line.lstrip().startswith('#'))

def py_loop_count(path):
    tree=ast.parse(path.read_text())
    return sum(isinstance(n,(ast.For,ast.While,ast.AsyncFor)) for n in ast.walk(tree))

jq_cmd=['jq','-cS','-f',str(JQ)]
py_cmd=[sys.executable,str(PY)]
results={'schema_version':1,'versions':{
    'jq':subprocess.check_output(['jq','--version'],text=True).strip(),
    'python':sys.version.split()[0],
}}
results['source_metrics']={
    'jq':{'noncomment_source_lines':noncomment_lines(JQ)},
    'python':{'noncomment_source_lines':noncomment_lines(PY),'explicit_loop_statements':py_loop_count(PY)},
}
for name in ('small','large'):
    data=DATA/f'{name}.json'
    jq=measure(jq_cmd,data); py=measure(py_cmd,data)
    jq_path=OUT/f'{name}.jq.json'; py_path=OUT/f'{name}.python.json'
    jq_path.write_bytes(jq['output']); py_path.write_bytes(py['output'])
    results[name]={
        'input_bytes':data.stat().st_size,
        'input_sha256':sha256(data),
        'outputs_equal':jq['output']==py['output'],
        'output_sha256':hashlib.sha256(jq['output']).hexdigest(),
        'jq':{k:v for k,v in jq.items() if k!='output'},
        'python':{k:v for k,v in py.items() if k!='output'},
    }
    results[name]['jq_over_python_median_ratio']=jq['median_seconds']/py['median_seconds']
(ROOT/'results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
