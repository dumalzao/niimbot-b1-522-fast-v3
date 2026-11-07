"""Autoteste de estrutura, sem arquivo firmware nem impressora."""
import importlib.util
import struct
from pathlib import Path
sp=importlib.util.spec_from_file_location('mod', Path(__file__).resolve().parents[1] / 'patch_b1_522_v3_corrige_escala.py')
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
assert len(m.SLOW_RAMP) == 64
assert len(m.RESTORE_FLOATS) == 13
assert m.MODE_OFFSET not in set(range(m.RAMP_OFFSET,m.RAMP_OFFSET+128))
assert len({p for o in m.RESTORE_FLOATS for p in range(o,o+4)}) == 52
for old in m.SLOW_RAMP:
    back=(2*old+1)//3
    assert int(back*1.5)==old
for offset,orig in m.RESTORE_FLOATS.items():
    assert struct.unpack('<f',struct.pack('<f',orig))[0] > 0
try:
    m.generate(b'wrong file')
except ValueError:
    pass
else:
    raise AssertionError('O gerador aceitou uma entrada invalida')
print('PASS: 64 rampas, 13 coeficientes, faixas isoladas e recusa de entrada invalida')
