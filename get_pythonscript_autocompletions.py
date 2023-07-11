from pathlib import Path
import re

import Npp
from Npp import editor, notepad

CURDIR = Path(__file__).parent

def is_enum(name):
    return re.fullmatch('[A-Z_][A-Z_\d]+', name)

completions = []
stuff = dir(Npp)
for name in stuff:
    if is_enum(name):
        enum_ = getattr(Npp, name)
        completions.append(name)
        completions.extend((
            name + '.' + member
            for member in dir(enum_)
            if is_enum(member)))

for editor_name in ['editor', 'editor1', 'editor2']:
    completions.append(editor_name)
    completions.extend(('%s.%s' % (editor_name, method)
        for method in dir(editor)
        if not method.startswith('_')))

completions.append('notepad')
completions.extend(('notepad.' + method
    for method in dir(notepad)
    if not method.startswith('_')))

autocomp_file = CURDIR / 'pythonscript_autocompletions.txt'

with autocomp_file.open('w') as f:
    f.write('\n'.join(sorted(completions)))