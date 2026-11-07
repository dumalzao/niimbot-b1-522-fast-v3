# NIIMBOT B1 — 5.22 FAST V3 (RFID-free printing)

[Documentação em português](README.md)

**Unofficial, community research project.** This repository provides a reproducible **patch generator** for a specific NIIMBOT B1 firmware **5.22** derivative. **It does not contain or redistribute a manufacturer firmware binary.** Not affiliated with or endorsed by NIIMBOT.

## Field result (November 7, 2026)

One operator reported that FAST V3 produced **fast, correctly scaled, uncropped 40 × 30 mm prints on third-party labels without RFID**, including printing through the **original NIIMBOT application**. Earlier experimental builds were fast but stretched output vertically. This is **one-device, operator-reported evidence**; no independent instrumented 3-second timing, long-run reliability, head temperature or broad hardware compatibility have been demonstrated.

## What changed

The script derives V3 from the **exact** ThreeDaPrint `B1_5.22_density_coeff.bin` image:

- Reverses the 64-entry motor line-period table from **1.5× to 1.0×** (`0x1C2A4`).
- Restores **4 original feed-related float constants** (`0x1DEC..0x1DF8`).
- Restores **9 original renderer multipliers** (locations listed in the script).
- Replaces a mode-3 fallback store with a Thumb NOP (`0xD3A0`, `0B 70` → `00 BF`) to enable the fast tagless path.
- Preserves existing RFID bypass and density hooks from the parent image.

This strategy was inspired by the **6.19** research, **not** by copying 6.19 offsets into 5.22.

## Exact inputs and output

| | Identity |
|---|---|
| Source | `B1_5.22_density_coeff.bin`, 120288 bytes |
| Input MD5 | `023ff56326fe8c65f01b68f32ebdba99` |
| Generated image | `B1_5.22_FAST_V3_ESCALA_EXPERIMENTAL.bin`, 120288 bytes |
| Output SHA-256 | `b1548072c84d99dd1fb4d21ac3242c0d0d7d44cd03a24653261578806c4c49aa` |

The generator checks all expected source bytes, affected addresses, and the exact final SHA-256. It **does not flash a printer or overwrite existing files**.

## Generate (Python 3, standard library only)

```bash
python patch_b1_522_v3_corrige_escala.py \
  --src /path/to/B1_5.22_density_coeff.bin \
  --out ./B1_5.22_FAST_V3_ESCALA_EXPERIMENTAL.bin

python tests/teste_b1_522_v3_script.py
```

Obtain the base image lawfully from its project/source. Never commit firmware images to this repository.

## Critical warning

**Do not flash this 5.22 image onto 6.x firmware/hardware.** Major-version mismatches may permanently brick the device. Verify the **physical hardware revision** as well as reported versions; one test machine reported contradictory hardware versions after an unrelated cross-major experiment. A backup file does not guarantee USB recovery.

Optional commands, once hardware compatibility and recoverability have been independently established (adjust serial port and file names):

```bash
npx --yes @mmote/niimblue-node info -t serial -a COM7
npx --yes @mmote/niimblue-node flash -t serial -a COM7 -n 5.22 -f ./B1_5.22_FAST_V3_ESCALA_EXPERIMENTAL.bin
npx --yes @mmote/niimblue-node print -d -t serial -a COM7 -p B1 -o top -w 320 -h 240 -q 3 -l 1 ./examples/label-40x30-code128.png
```

Confirm geometry physically (ruler, borders and scan of Code 128); test one label first. Stop for unusual heating or motion. Success on one printer cannot establish reliability or thermal safety.

## Attribution

- [ThreeDaPrint/niimbot](https://github.com/ThreeDaPrint/niimbot) — 5.22 reverse engineering, source image and patch map.
- [beraT-T/niimbot-b1-unlock-notes](https://github.com/beraT-T/niimbot-b1-unlock-notes) — 6.19 approach for restoring feed and renderer parameters.
- [vkolarik/niimbot-b1](https://github.com/vkolarik/niimbot-b1) — vertical-stretch investigation.

The repository's new script/documentation are MIT licensed; **manufacturer firmware and trademarks are not covered**. Please report reproducible outcomes, without sharing serial numbers or MAC addresses.
