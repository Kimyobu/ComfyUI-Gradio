from importlib.metadata import distributions
import os
import subprocess
import sys

print('[ComfyUI-Gradio] Checking Requirements')
reqs = open(f'{os.path.dirname(__file__)}/requirements.txt').read().split('\n')
pkgs = {}

for x in distributions():
    pkgs[x.metadata.get('name')] = x.version

for p in reqs:
    a = p.split('==')
    name = a[0]
    if len(a) == 1:
        a.append(pkgs.get(name))
    ver = a[1]
    if pkgs.get(name) is None or pkgs.get(name) != ver:
        print(f'[ComfyUI-Gradio] Missing Package Gradio... Installing {p}' if pkgs.get(name) is None else f'[ComfyUI-Gradio] Package Wrong Version {name}~={pkgs.get(name)}')
        subprocess.call([sys.executable, '-m', 'pip', 'install', p], 
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT)
        print(f'[ComfyUI-Gradio] Installed {p}')