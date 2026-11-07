# Análise técnica — B1 5.22 FAST V3

Este documento descreve **o gerador disponibilizado**, não uma engenharia reversa nova e independente de toda a imagem binária. A imagem de entrada exata foi desenvolvida e documentada em [ThreeDaPrint/niimbot](https://github.com/ThreeDaPrint/niimbot); os conceitos de correção da distorção vertical foram inspirados em [beraT-T/niimbot-b1-unlock-notes](https://github.com/beraT-T/niimbot-b1-unlock-notes) e [vkolarik/niimbot-b1](https://github.com/vkolarik/niimbot-b1).

## Histórico do problema

1. O firmware 5.22 modificado `density_coeff` permitia impressão visível/escura em etiquetas sem RFID, mas com alimentação mais lenta.
2. Modificar apenas a escrita do modo de impressão (habilitar caminho rápido sem chip) aumentou a velocidade, porém a impressão ficou esticada verticalmente.
3. Restaurar a rampa original do motor (V2) **não** corrigiu o esticamento observado.
4. O estudo do firmware 6.19 indicou que parâmetros considerados apenas térmicos também influenciam caminhos de alimentação, escala e sincronismo de renderização. Portanto, V3 preserva o caminho rápido **e** restaura 13 valores originais em rotinas 5.22.
5. Após a V3, um operador relatou escala correta, sem cortes, impressão rápida e funcionamento no software oficial NIIMBOT. Isso fundamenta a divulgação do experimento, não garante reprodução em todas as unidades.

## Entrada obrigatória

- Arquivo `B1_5.22_density_coeff.bin`, comprimento exatamente `120288` bytes.
- MD5 exato `023ff56326fe8c65f01b68f32ebdba99` (compare sem considerar maiúsculas/minúsculas).
- Só esta imagem é aceita, não outras imagens 5.22 e nunca imagens da família 6.x.

## Mapa de patches (offsets do arquivo, hexadecimal)

| Offset | Tipo | Mudança |
|---|---|---|
| `0x1C2A4` | 64 valores uint16 LE | Recupera períodos `×1,0` a partir da tabela `×1,5` verificada |
| `0x1DEC` | float32 | 400 → 74.4 |
| `0x1DF0` | float32 | 400 → 60.0 |
| `0x1DF4` | float32 | 400 → 60.8 |
| `0x1DF8` | float32 | 400 → 120.0 |
| `0x654C` | float32 | 400 → 50.0 |
| `0x6550` | float32 | 400 → 30.0 |
| `0x6554` | float32 | 400 → 150.0 |
| `0x6558` | float32 | 400 → 100.0 |
| `0x655C` | float32 | 400 → 90.0 |
| `0x6C88` | float32 | 400 → 30.0 |
| `0x6C8C` | float32 | 400 → 50.0 |
| `0x6C90` | float32 | 400 → 120.0 |
| `0x6C94` | float32 | 400 → 100.0 |
| `0xD3A0` | instrução Thumb | `0B 70` (`strb`) → `00 BF` (`nop`) |

Os parâmetros `0x6538` e `0x6C84` permanecem em **400.0**, assim como os hooks de densidade da imagem ThreeDaPrint. A descrição funcional dos floats parte da investigação documentada e não substitui traço completo de execução da CPU.

## Identidade da imagem gerada

```text
Tamanho            120288 bytes
SHA-256            b1548072c84d99dd1fb4d21ac3242c0d0d7d44cd03a24653261578806c4c49aa
Nome de exemplo    B1_5.22_FAST_V3_ESCALA_EXPERIMENTAL.bin
```

O gerador executa os seguintes controles **antes** de gravar o arquivo de saída:

- Confere tamanho e MD5 da imagem-base.
- Confere a tabela completa de 64 entradas de motor e bytes da instrução de modo.
- Confere se os 13 floats de origem têm o valor esperado (400.0).
- Restringe alterações ao conjunto de offsets explicitamente autorizado.
- Confere SHA-256 final esperado.
- Cria arquivo exclusivamente (`xb`), sem sobrescrever backup existente.

Isso comprova **reprodutibilidade byte a byte da transformação**, não comprova segurança elétrica ou térmica nem impede falha de flash.

## Relevância da pesquisa 6.19

No FW 6.19, equipes independentes observaram saída verticalmente distorcida no modo rápido com parâmetros térmicos alterados. Restaurar apenas a rampa do motor não resolveu. Abordagens posteriores restauraram também literais do caminho de feed e multiplicadores do renderer. Em 5.22, usamos **os dados e posições originais de 5.22**, pois os offsets 6.19 não são transferíveis.

## O que ainda falta medir

- Tempo físico **somente do motor**, com cronômetro/vídeo.
- Exatidão da geometria com régua ou paquímetro e foto da etiqueta.
- Repetibilidade em 20+ etiquetas e deriva de alinhamento.
- Outras larguras/comprimentos, tipos de papel e cobertura térmica.
- Temperatura de cabeçote, uso prolongado, durabilidade e compatibilidade com revisões diversas.
- Recuperação/rollback em caso de flash interrompido.
