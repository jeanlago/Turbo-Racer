# Física de Carros - Turbo Racer

## Visão Geral

O sistema de física de carros foi completamente reescrito para oferecer uma experiêncIA de drift realista baseada no jogo "Absolute Drift". O novo sistema implementa diferentes tipos de tração e comportamentos de drift únicos para cada tipo.

## Tipos de Tração

### 1. Tração Traseira (Rear Wheel Drive - RWD)
- **Características**: Potência aplicada apenas nas rodas traseiras
- **Comportamento**: Mais propenso ao drift, especIAlmente em curvas
- **Drift**: Clássico - a traseira derrapa naturalmente
- **Carros**: Mustang, Supra, Skyline, RX-7, S2000, 350Z

### 2. Tração Frontal (Front Wheel Drive - FWD)
- **Características**: Potência aplicada apenas nas rodas dIAnteiras
- **Comportamento**: Mais estável, menos propenso ao drift
- **Drift**: Mais sutil, baseado em transferêncIA de peso
- **Carros**: Civic, Golf, Focus

### 3. Tração Integral (All Wheel Drive - AWD)
- **Características**: Potência distribuída entre todas as rodas
- **Comportamento**: Equilibrado entre estabilidade e capacidade de drift
- **Drift**: Controlado, permite drift mas com mais aderêncIA
- **Carros**: Impreza, Evo, WRX

## Sistema de Drift

### Ativação do Drift
- **Tecla**: Espaço (P1) ou Shift (P2)
- **Condições**: Velocidade mínima + direção + handbrake
- **Comportamento**: Reduz grip lateral e adiciona derrapagem controlada

### Diferenças por Tipo de Tração

#### Tração Traseira
- Redução de grip lateral: 80%
- Derrapagem lateral mais pronuncIAda
- Resposta mais agressiva ao drift
- Ideal para drift clássico

#### Tração Frontal
- Redução de grip lateral: 40%
- Drift mais sutil e controlado
- Melhor para inicIAntes
- Foco na estabilidade

#### Tração Integral
- Redução de grip lateral: 60%
- Comportamento equilibrado
- Permite drift mas com controle
- Boa opção para todos os níveis

## Física Avançada

### Parâmetros dos Pneus
- **Grip Lateral**: AderêncIA nas curvas
- **Grip Longitudinal**: Aceleração e frenagem
- **Atrito de Rolamento**: ResistêncIA natural
- **Ângulo Máximo**: Limite de esterçamento

### Centro de Massa
- **Traseira**: Centro mais à frente (mais instável)
- **Frontal**: Centro mais atrás (mais estável)
- **Integral**: Centro equilibrado

### Forças Aplicadas
- **Força do Motor**: Baseada na potêncIA do carro
- **Força de Freio**: ResistêncIA à aceleração
- **Forças dos Pneus**: Calculadas dinamicamente

## Controles

### Básicos
- **W/↑**: Acelerar
- **S/↓**: Frear/Ré
- **A/←**: Virar à esquerda
- **D/→**: Virar à direita

### Drift
- **Espaço (P1)**: Handbrake/Drift
- **Shift (P2)**: Handbrake/Drift

### Nitro
- **Ctrl (P1)**: Nitro
- **Ctrl (P2)**: Nitro

## Configuração de Carros

Cada carro pode ser configurado com diferentes tipos de tração no arquivo `main.py`:

```python
CARROS_DISPONIVEIS = [
    {"nome": "Mustang", "tipo_tracao": "rear"},    # Tração traseira
    {"nome": "Carro 2", "tipo_tracao": "front"},   # Tração frontal
    {"nome": "Carro 4", "tipo_tracao": "awd"},     # Tração integral
]
```

## Ajustes de Física

### Parâmetros Ajustáveis
- **PotêncIA do Motor**: Força de aceleração
- **Torque Máximo**: Força de rotação
- **Grip dos Pneus**: AderêncIA lateral e longitudinal
- **Centro de Massa**: Estabilidade do carro
- **Sensibilidade do Volante**: Responsividade da direção

### Tuning por Tipo
- **Traseira**: Menos grip traseiro, mais potêncIA
- **Frontal**: Menos grip frontal, mais estabilidade
- **Integral**: Grip equilibrado, potêncIA moderada

## Efeitos Visuais

### Partículas de Drift
- Emitidas durante derrapagem
- Intensidade baseada na velocidade lateral
- Direção baseada no movimento do carro

### Indicadores
- Estado de drift ativo
- Intensidade do drift
- Tipo de tração do carro

## Compatibilidade

O novo sistema é totalmente compatível com:
- Sistema de corrida existente
- Sistema de checkpoints
- IA dos oponentes
- Sistema de nitro
- Efeitos visuais

## Próximas MelhorIAs

- Sistema de suspensão
- DiferencIAção de pneus por carro
- Sistema de danos
- Tuning personalizável
- Física de colisões mais realista
