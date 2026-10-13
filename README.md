# Simulador de Controle de Qualidade com CLP

Simulação educacional, desenvolvida em Python e Tkinter, de uma linha industrial com esteira transportadora, prensa pneumática, inspeção de qualidade e separação de peças aprovadas e reprovadas.

> **Aviso de segurança:** a prensa, o botão de emergência e todas as entradas/saídas são simulados. Este programa não controla CLPs nem equipamentos reais e não é um sistema de segurança. Não o utilize para operar máquinas ou substituir proteções industriais.

## Funcionalidades

- Ciclo de varredura simulado de CLP a cada 50 ms.
- Comandos **START** e **STOP** para iniciar e parar a simulação.
- **E-STOP** virtual para interromper o ciclo simulado.
- Opção para forçar a geração de uma peça defeituosa.
- Inspeção simulada com base no peso e no comprimento das peças.
- Separação das peças aprovadas e reprovadas.
- Contadores de produção e indicadores visuais de entradas e saídas digitais.

## Requisitos

- Python 3.
- Tkinter (normalmente incluído nas instalações do Python).
- Nenhum pacote Python externo é necessário.

Em algumas distribuições Linux, instale o Tkinter separadamente, por exemplo:

```bash
sudo apt install python3-tk
```

## Como executar

Abra um terminal na pasta do projeto e execute:

```bash
python industrial_plc_qc_simulator.py
```

Se necessário, use `python3` no Linux/macOS ou `py` no Windows:

```bash
python3 industrial_plc_qc_simulator.py
# Windows
py industrial_plc_qc_simulator.py
```

## Controles

- **START:** inicia o ciclo da linha simulada.
- **STOP:** para o ciclo.
- **E-STOP:** simula uma parada de emergência da linha.
- **Forçar peça defeituosa:** ativa a simulação de uma peça reprovada para observar a inspeção e a separação.
- **Indicadores de I/O e contadores:** mostram o estado das entradas/saídas digitais simuladas e os resultados da produção.

Os nomes e a disposição dos controles podem variar conforme a versão do simulador.

## Finalidade

Projeto didático para explorar conceitos básicos de automação industrial, lógica de controle, inspeção de qualidade e sinais digitais em uma interface gráfica. Toda a operação ocorre dentro do software.
