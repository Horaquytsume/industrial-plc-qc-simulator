# Simulador de Automação Industrial e Inspeção de Qualidade

Aplicação didática em Python com Tkinter que simula uma célula industrial controlada por PLC: esteira transportadora, prensa pneumática, inspeção dimensional e por peso, e separação de peças aprovadas e rejeitadas.

## Funcionalidades

- Simulação do ciclo de um PLC com varredura de 50 ms.
- Controles de partida, parada e parada de emergência simulada.
- Geração aleatória de peso e comprimento para as peças.
- Modo para forçar a próxima peça como defeituosa.
- Contadores de peças inspecionadas, aprovadas e rejeitadas.
- Indicadores de estado e monitor de entradas/saídas digitais.

## Requisitos

- Python 3.
- Tkinter, normalmente incluído na instalação do Python.
  - Em algumas distribuições Linux, pode ser necessário instalar o pacote `python3-tk`.

Não são necessárias bibliotecas Python externas.

## Como executar

1. Baixe ou clone este repositório.
2. Abra um terminal na pasta do projeto.
3. Execute:

```bash
python industrial_plc_qc_simulator.py
```

Se o comando `python` não apontar para o Python 3, tente `python3` (Linux/macOS) ou `py` (Windows).

## Controles da simulação

- **START:** inicia o ciclo de produção.
- **STOP:** interrompe o ciclo.
- **E-STOP:** simula uma condição de emergência e desliga as saídas da simulação.
- **Next Part: DEFECTIVE:** alterna entre peça normal e peça defeituosa para a próxima peça gerada.

## Aviso importante

Este projeto é apenas uma simulação educacional. Os botões, sensores, saídas e a parada de emergência são elementos virtuais: o programa **não controla um PLC, máquinas ou qualquer equipamento físico** e não deve ser usado como sistema de segurança industrial.
