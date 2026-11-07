# NIIMBOT B1 — Firmware 5.22 FAST V3 (sem RFID)

**Projeto comunitário e independente.** Gerador de patch para a NIIMBOT B1 com firmware **5.22**, voltado a etiquetas térmicas genéricas sem RFID. **Não é firmware oficial da NIIMBOT**, não contém binário de firmware e não é afiliado à fabricante.

> **Resultado reportado em 07/11/2026:** em **uma** impressora B1, o operador confirmou que a variante V3 manteve a impressão rápida, corrigiu o esticamento vertical observado nas variantes anteriores, não cortou o conteúdo e imprimiu inclusive pelo **software original da NIIMBOT**. Trata-se de um relato de campo; não é validação independente, teste de durabilidade ou garantia de compatibilidade geral. A velocidade exata do mecanismo **não foi cronometrada isoladamente** nesta confirmação.

[English documentation](README.en.md) · [Notas técnicas](docs/ANALISE_TECNICA.md) · [Histórico e limitações](docs/TESTES_E_LIMITACOES.md)

## O que esta versão altera

A V3 **não é apenas a V2 com motor mais rápido**. Ela reaproveita o desbloqueio do modo rápido, mas restaura os parâmetros que podem interferir no avanço/na temporização dos renderizadores:

| Parte da imagem 5.22 | Alteração | Objetivo |
|---|---|---|
| Tabela de 64 períodos do motor (`0x1C2A4`) | Retira o fator ×1,5, restaurando ×1,0 | Voltar à temporização original de avanço |
| Quatro floats do caminho de alimentação (`0x1DEC` a `0x1DF8`) | Restabelece os valores originais | Corrigir dependências de contadores e avanço |
| Nove floats dos dois renderizadores | Restabelece os valores originais | Evitar incompatibilidade com o caminho rápido |
| Escrita do modo 3 (`0xD3A0`) | `0B 70` → `00 BF` (NOP Thumb) | Evitar a seleção lenta no caso sem RFID |
| Hooks de densidade, bypass RFID e demais bytes | Preservados | Manter o comportamento da imagem-base |

A hipótese técnica foi inspirada no trabalho com FW **6.19**, mas **os offsets aqui são exclusivos da 5.22**. Nenhum patch 6.19 é aplicado diretamente.

## Compatibilidade e segurança

- **Somente para a NIIMBOT B1 que já utiliza firmware da família 5.x compatível com a 5.22.** Verifique também a revisão física do hardware. A unidade do relato era identificada inicialmente como HW 5.10; após testes cruzando versões, o firmware 6.19 passou a *reportar* HW 6.01, informação que não prova alteração da revisão física.
- **Nunca use esta imagem em uma B1 com firmware 6.x ou hardware 6.01 não confirmado compatível com 5.22.** Misturar famílias pode inutilizar o equipamento.
- O cabeçote pode aquecer; interrompa se houver superaquecimento, marcas irregulares, ruídos ou falhas de avanço.
- Tenha um arquivo funcional conhecido e **um método real de recuperação** antes de tentar gravar. Possuir o backup não garante recuperação USB após falha de flash.
- Uma única impressão correta não comprova confiabilidade, vida útil do cabeçote ou comportamento em outros tipos de etiqueta.

## Arquivos e hashes obrigatórios

O repositório distribui **somente o código para reproduzir o patch**, não distribui firmware proprietário.

| Identificação | Valor |
|---|---|
| Entrada | `B1_5.22_density_coeff.bin`, proveniente do trabalho ThreeDaPrint |
| Tamanho de entrada | `120288` bytes |
| **MD5 da entrada** | `023ff56326fe8c65f01b68f32ebdba99` |
| Saída | `B1_5.22_FAST_V3_ESCALA_EXPERIMENTAL.bin` |
| Tamanho de saída | `120288` bytes |
| **SHA-256 da saída** | `b1548072c84d99dd1fb4d21ac3242c0d0d7d44cd03a24653261578806c4c49aa` |

Se os hashes não coincidirem, o programa **interrompe sem gerar a imagem**. Não tente aplicar o patch em outra versão.

## 1. Gerar a imagem V3 (sem gravar)

Requisitos: **Python 3**. Não há dependências Python externas; o gerador usa só a biblioteca padrão.

Obtenha **por conta própria** uma cópia legítima da imagem-base `B1_5.22_density_coeff.bin` referente ao projeto [ThreeDaPrint/niimbot](https://github.com/ThreeDaPrint/niimbot). O script não faz downloads nem modifica a impressora.

No **PowerShell**, a partir da pasta do repositório:

```powershell
python .\patch_b1_522_v3_corrige_escala.py `
  --src "C:\Niimbot-B1\5.22\firmware\B1_5.22_density_coeff.bin" `
  --out ".\B1_5.22_FAST_V3_ESCALA_EXPERIMENTAL.bin"

Get-FileHash ".\B1_5.22_FAST_V3_ESCALA_EXPERIMENTAL.bin" -Algorithm SHA256
```

A saída tem de apresentar o SHA-256 da tabela acima. O gerador **não sobrescreve** arquivos existentes.

Para executar o autoteste estático, sem impressora:

```powershell
python .\tests\teste_b1_522_v3_script.py
```

## 2. Verificar o equipamento antes de gravar

Requisitos para esta etapa: Node.js com `npx`, USB e porta serial correta (exemplo COM7):

```powershell
npx --yes @mmote/niimblue-node info -t serial -a COM7
```

**Pare se a versão identificada não for 5.22/5.x comprovadamente compatível.** `-n 5.22` no comando seguinte não converte uma impressora de outra família.

## 3. Gravar — operação de risco, opcional

Somente se confirmou hardware/firmware compatíveis e aceita a possibilidade de dano permanente:

```powershell
npx --yes @mmote/niimblue-node flash -t serial -a COM7 -n 5.22 -f ".\B1_5.22_FAST_V3_ESCALA_EXPERIMENTAL.bin"
```

Não desligue o aparelho nem desconecte o cabo durante a operação. Ao concluir, o aparelho pode desligar; ligue-o novamente antes de obter `info`. Uma versão reportada como 5.22 **não comprova** a variante V3 — use o arquivo gerado e seu hash para rastreabilidade.

## 4. Imprimir uma etiqueta de teste 40 × 30 mm

Este repositório inclui um PNG genérico com régua, borda, texto e código de barras **Code 128**. Com o aparelho ligado, mídia carregada e imagem compatível:

```powershell
npx --yes @mmote/niimblue-node print -d -t serial -a COM7 -p B1 -o top -w 320 -h 240 -q 3 -l 1 ".\examples\label-40x30-code128.png"
```

Em uma B1 de 203 dpi, 40 × 30 mm correspondem aproximadamente a **320 × 240 pontos**. A cabeça da B1 tem 384 pontos de largura máxima, o que não obriga a imprimir 384 pontos na etiqueta de 40 mm.

Verifique com régua: **tamanho impresso, proporção, margens e alinhamento**; confirme a leitura do código de barras e observe ruído/temperatura. Comece com **uma** etiqueta e só amplie os testes após conferir o resultado.

> `Measure-Command { npx ... print ... }` contabiliza conexão e envio USB, além do movimento do papel. Não é uma medição isolada do motor.

## Histórico resumido

- **5.22 `density_coeff`**: impressão escura de etiquetas genéricas, porém mais lenta sem RFID.
- **V1 rápida**: velocidade aumentou, mas houve distorção/corte na escala vertical.
- **V2**: motor restaurado, caminho rápido preservado; escala ainda esticada.
- **V3 (este projeto)**: motor original + 13 parâmetros restaurados + modo rápido; **usuário relatou impressão correta, sem cortes, inclusive pelo software original**.

Os registros e os limites das evidências estão em [docs/TESTES_E_LIMITACOES.md](docs/TESTES_E_LIMITACOES.md).

## Créditos e fontes

- [ThreeDaPrint/niimbot](https://github.com/ThreeDaPrint/niimbot): base modificada 5.22, diagnóstico da energia e do motor, mapa de offsets e densidade.
- [beraT-T/niimbot-b1-unlock-notes](https://github.com/beraT-T/niimbot-b1-unlock-notes): abordagem FW 6.19 de restauração da rampa, literais e seleção de modo.
- [vkolarik/niimbot-b1](https://github.com/vkolarik/niimbot-b1): análise da distorção vertical, aquecimento e alimentação.
- [@mmote/niimblue-node](https://www.npmjs.com/package/@mmote/niimblue-node): ferramentas CLI utilizadas para informação/gravação/impressão.

**Licença:** MIT para o código e a documentação próprios deste repositório. Isso **não** concede direitos sobre firmware, marcas ou software de terceiros.

## Contribuições

Relatos de outras unidades são bem-vindos via GitHub Issues. Inclua **versão do hardware físico (se conhecida)**, firmware anterior, imagem de entrada validada, mídia, formato, resultado real medido, legibilidade, erro e passos de reprodução. **Nunca publique o número de série ou MAC da sua impressora.**
