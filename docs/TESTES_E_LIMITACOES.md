# Registro de resultados e limitações

## Resultado positivo relatado — 07/11/2026

**Origem:** operador da impressora, em uma sessão de testes. A informação a seguir é relato do teste real, **não certificação independente**.

- **Modelo:** NIIMBOT B1.
- **Histórico de hardware:** anteriormente reportado como HW 5.10 em firmware 5.22; após tentativa de atualizar para 6.19, a telemetria passou a reportar HW 6.01. Isso **não comprova** a revisão física e impede generalizações.
- **Imagem V3:** SHA-256 fixado no projeto; gerador partindo da imagem-base conhecida 5.22.
- **Mídia e formato do contexto dos testes:** etiqueta genérica 40 × 30 mm sem RFID.
- **Velocidade:** operador afirmou estar adequada com a variante rápida; **não foi fornecida medição instrumentada de exatamente 3,00 s do motor nesta confirmação**.
- **Geometria:** operador relatou **impressão sem esticar e sem cortes**.
- **Compatibilidade de aplicativo:** operador informou sucesso imprimindo diretamente pelo **software original NIIMBOT**.
- **Risco residual:** não existem testes públicos de longa duração, temperatura ou múltiplas revisões de placa.

## Resultados anteriores relevantes

| Variante | Observação do operador |
|---|---|
| 5.22 `density_coeff` | Etiquetas sem RFID com impressão forte, porém mais lenta |
| V1 — modo rápido | Velocidade desejada, mas texto esticado / cortado |
| V2 — motor x1 + modo rápido | Velocidade considerada OK; esticamento persistiu |
| **V3 — motor x1 + 13 floats originais + modo rápido** | **Impressão rápida, sem cortes/esticamento, funcionando no aplicativo original** |

## Princípios de teste para colaboradores

1. Confirme revisão física quando possível e identifique **firmware anterior**, **hash da fonte** e **hash da variante**. Não confie somente em um campo de versão lido de firmware que passou por downgrade/upgrade cruzado.
2. Comece com uma etiqueta de baixa cobertura, usando a imagem em `examples/` e uma régua para medir escala; não faça longas tiragens às cegas.
3. Faça testes com e sem RFID apenas em equipamento comprovadamente compatível, registrando os resultados separadamente.
4. Anote legibilidade do Code 128, possíveis falhas térmicas, avanço excessivo, primeiro alinhamento e tempo físico de impressão.
5. Interrompa se o cabeçote, papel ou equipamento apresentarem aquecimento incomum, travamentos ou ruídos estranhos.
6. Não divulgue números de série, endereços MAC ou registros com identificadores pessoais.

**Nenhum arquivo de firmware é distribuído aqui**. O código serve para reproduzir o experimento a partir de uma imagem-base obtida legitimamente pelo usuário, assumindo os riscos da gravação.
