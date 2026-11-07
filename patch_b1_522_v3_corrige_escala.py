#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NIIMBOT B1 5.22 — V3, ajuste de escala vertical em modo rapido.

Nao se comunica com impressora e nao executa flash. Reproduz de modo controlado
uma hipotese portada do build_final.py (FW 6.19) para os sites 5.22 documentados
pelo projeto ThreeDaPrint. Resultado positivo reportado em uma impressora;
a validação em outros hardwares e midias ainda esta pendente.

Entrada EXATA: B1_5.22_density_coeff.bin (120288 B / MD5 conhecido).
Alteracoes: rampa x1, 4 literais do caminho feed, 9 multiplicadores do renderer,
NOP no fallback mode3 (ja anteriormente usado no experimento veloz).
Preserva: ganchos de densidade, 2 coeficientes de renderizacao compartilhados,
RFID bypass, restante dos bytes e a imagem de entrada.
"""
from __future__ import annotations
import argparse
import hashlib
import struct
import sys
from pathlib import Path

ORIGINAL_MD5 = '023ff56326fe8c65f01b68f32ebdba99'
OUTPUT_SHA256 = 'b1548072c84d99dd1fb4d21ac3242c0d0d7d44cd03a24653261578806c4c49aa'
SIZE = 120288
RAMP_OFFSET = 0x1C2A4
MODE_OFFSET = 0xD3A0

# Multiplicadores originais 5.22 obtidos da documentacao ThreeDaPrint.
# Equivalem aos grupos revertidos em beraT-T 6.19, mas offsets sao da 5.22.
RESTORE_FLOATS = {
    # Contadores/feed alvo, nao exclusivamente valores termicos.
    0x1DEC: 74.4, 0x1DF0: 60.0, 0x1DF4: 60.8, 0x1DF8: 120.0,
    # Renderizador A: 5 multiplicadores da via 'tagged'.
    0x654C: 50.0, 0x6550: 30.0, 0x6554: 150.0,
    0x6558: 100.0, 0x655C: 90.0,
    # Renderizador B: 4 multiplicadores da via 'tagged'.
    0x6C88: 30.0, 0x6C8C: 50.0,
    0x6C90: 120.0, 0x6C94: 100.0,
}
SLOW_RAMP = (
    6375,5640,5188,4143,3471,3042,2892,2742,
    2592,2512,2452,2392,2347,2314,2284,2254,
    2229,2199,2169,2139,2109,2076,2046,2016,
    1983,1953,1923,1893,1863,1833,1803,1786,
    1771,1756,1741,1726,1711,1696,1681,1666,
    1654,1639,1624,1609,1594,1579,1564,1549,
    1534,1519,1485,1470,1455,1440,1425,1410,
    1395,1380,1365,1350,1335,1320,1305,1290,
)


def generate(original: bytes) -> tuple[bytes, int]:
    if len(original) != SIZE:
        raise ValueError(f'Tamanho incorreto ({len(original)} B). Esperado: {SIZE} B.')
    current_md5 = hashlib.md5(original).hexdigest()
    if current_md5 != ORIGINAL_MD5:
        raise ValueError(f'MD5 de entrada incompatível: {current_md5}. ABORTADO.')

    slow = struct.unpack_from('<64H', original, RAMP_OFFSET)
    if slow != SLOW_RAMP:
        raise ValueError('Tabela do motor diferente da referência 5.22. ABORTADO.')
    if original[MODE_OFFSET:MODE_OFFSET + 2] != bytes.fromhex('0b70'):
        raise ValueError('Instrução do modo diferente da referência. ABORTADO.')
    for position in RESTORE_FLOATS:
        current = struct.unpack_from('<f', original, position)[0]
        if current != 400.0:
            raise ValueError(f'Parâmetro 0x{position:X} não está em 400.0. ABORTADO.')

    patched = bytearray(original)
    stock_ramp = [(2 * x + 1) // 3 for x in slow]
    if not all(int(t * 1.5) == source for t, source in zip(stock_ramp, slow)):
        raise ValueError('Tabela do motor não é reversível exatamente. ABORTADO.')
    struct.pack_into('<64H', patched, RAMP_OFFSET, *stock_ramp)

    for position, original_value in RESTORE_FLOATS.items():
        struct.pack_into('<f', patched, position, float(original_value))

    # Remoção da escrita mode3 do handler de densidade para habilitar via rápida.
    # Como foi observado esticamento nessa alteração isolada, nunca é aplicada
    # sem as restaurações adicionais acima.
    patched[MODE_OFFSET:MODE_OFFSET + 2] = bytes.fromhex('00bf')

    # Os dois coeficientes compartilhados continuam 400.0 para preservar
    # parte do comportamento de contraste do build density_coeff.
    for offset in (0x6538, 0x6C84):
        assert struct.unpack_from('<f', patched, offset)[0] == 400.0

    allowed = set(range(RAMP_OFFSET, RAMP_OFFSET + 128))
    allowed.update((MODE_OFFSET, MODE_OFFSET + 1))
    for at in RESTORE_FLOATS:
        allowed.update(range(at, at + 4))
    changed = [i for i, (a, b) in enumerate(zip(original, patched)) if a != b]
    if not changed or not set(changed).issubset(allowed):
        raise ValueError('Diferenças fora dos endereços permitidos. ABORTADO.')

    final = bytes(patched)
    sha = hashlib.sha256(final).hexdigest()
    if sha != OUTPUT_SHA256:
        raise ValueError(f'SHA-256 inesperado: {sha}. Nenhum arquivo será escrito.')
    return final, len(changed)


def main():
    p = argparse.ArgumentParser(description='Gera B1 5.22 V3 testada em uma unidade (nao grava).')
    p.add_argument('--src', type=Path, default=Path(r'C:\Niimbot-B1\5.22\firmware\B1_5.22_density_coeff.bin'))
    p.add_argument('--out', type=Path, default=Path(r'C:\Niimbot-B1\5.22\firmware\B1_5.22_FAST_V3_ESCALA_EXPERIMENTAL.bin'))
    args = p.parse_args()
    if args.src.resolve() == args.out.resolve():
        p.error('Entrada e saída devem ser diferentes.')
    try:
        final, count = generate(args.src.read_bytes())
        with args.out.open('xb') as f:  # NUNCA sobrescreve arquivos existentes.
            f.write(final)
    except (OSError, ValueError) as e:
        p.exit(1, f'ERRO: {e}\n')
    print('V3 gerada com sucesso — NENHUMA GRAVAÇÃO REALIZADA')
    print('Entrada   :', args.src)
    print('Saída     :', args.out)
    print('Tamanho   :', len(final), 'bytes')
    print('Diferenças:', count, 'bytes em áreas autorizadas')
    print('SHA-256   :', hashlib.sha256(final).hexdigest())
    print('ALTERAÇÕES: motor x1.0 + 4 feed literals + 9 renderer literals + modo0 NOP.')
    print('ATENÇÃO: sucesso reportado em uma unidade; demais hardwares e mídias não validados.')


if __name__ == '__main__':
    main()
