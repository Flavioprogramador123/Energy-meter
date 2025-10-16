# Manual Completo e Detalhado: Módulo de Medição AC PZEM-004T

Este documento consolida e detalha todas as informações do manual do módulo PZEM-004T, incluindo explicações aprofundadas sobre o protocolo de comunicação, exemplos práticos e dicas de hardware.

---

## 1. Visão Geral e Funcionalidades

O módulo PZEM-004T é um dispositivo multifuncional projetado para medir os principais parâmetros de um circuito de corrente alternada (AC).

**Principais Funções:**
- Medição de Tensão (V)
- Medição de Corrente (A)
- Medição de Potência Ativa (W)
- Medição de Energia Acumulada (Wh/kWh)
- Alarme de Sobrepotência (configurável)
- Interface de Comunicação Serial TTL

---

## 2. Parâmetros Elétricos e Especificações

| Parâmetro | Faixa de Medição | Resolução | Precisão | Observações |
| :--- | :--- | :--- | :--- | :--- |
| **Tensão** | 80 ~ 260 V | 0.1 V | ± 0.5% | |
| **Corrente** | 0 ~ 100 A | 0.001 A | ± 0.5% | Inicia a medição a partir de 0.02 A |
| **Potência Ativa** | 0 ~ 23 kW | 0.1 W | ± 0.5% | Inicia a medição a partir de 0.4 W |
| **Energia** | 0 ~ 9999 kWh | 1 Wh | ± 0.5% | O valor acumulado pode ser zerado via software |

**Formato de Exibição dos Dados:**
- **Potência:**
    - Abaixo de 1000 W: Exibido com uma casa decimal (ex: `999.9 W`).
    - Igual ou acima de 1000 W: Exibido como número inteiro (ex: `1000 W`).
- **Energia:**
    - Abaixo de 10 kWh: Exibido em Watt-hora (ex: `9999 Wh`).
    - Igual ou acima de 10 kWh: Exibido em kilowatt-hora (ex: `9.999 kWh`).

---

## 3. Interface de Comunicação e Protocolo

O módulo utiliza uma interface **Serial TTL** com o protocolo **Modbus-RTU** para a comunicação.

#### 3.1. Especificações da Camada Física (TTL)
- **Taxa de Baud (Baud Rate):** 9600
- **Bits de Dados:** 8
- **Bits de Parada (Stop Bits):** 1
- **Paridade:** Nenhuma

#### 3.2. Protocolo Modbus-RTU

O Modbus é um protocolo mestre-escravo. Em sua aplicação, o seu microcontrolador (Arduino, ESP, Raspberry Pi) atuará como **Mestre**, e o módulo PZEM-004T como **Escravo**.

- **Endereço Padrão do Escravo:** `0xF8` (pode ser alterado).

#### 3.3. Estrutura dos Comandos (Frames)

**3.3.1. Leitura dos Registradores de Medição**

Este comando é usado para solicitar os valores de Tensão, Corrente, Potência e Energia.

- **Comando do Mestre (Exemplo para ler tudo):**
  `[Endereço do Escravo] [Código da Função] [End. Inicial (Hi)] [End. Inicial (Lo)] [Nº de Registros (Hi)] [Nº de Registros (Lo)] [CRC (Lo)] [CRC (Hi)]`

  - **Exemplo Prático:**
    `0xF8 0x04 0x00 0x00 0x00 0x04 0x6C 0x05`

- **Resposta do Escravo:**
  `[Endereço do Escravo] [Código da Função] [Contagem de Bytes] [Dados Tensão (Hi)] [Dados Tensão (Lo)] ... [CRC (Lo)] [CRC (Hi)]`

  - **Exemplo de Resposta:**
    `0xF8 0x04 0x08 0x08 0x98 0x00 0x00 0x00 0x74 0x00 0x1E 1E C2`

**3.3.2. Tabela de Registradores e Conversão de Dados**

| Medição | Endereço do Registro | Bytes na Resposta (Exemplo) | Cálculo | Valor Final (Exemplo) |
| :--- | :--- |:--- | :--- | :--- |
| **Tensão** | `0x0000` | `0x08` `0x98` | `((0x08 * 256) + 0x98) / 10.0` | **220.0 V** |
| **Corrente** | `0x0001` | `0x00` `0x00` | `((0x00 * 256) + 0x00) / 1000.0` | **0.000 A** |
| **Potência** | `0x0002` | `0x00` `0x74` | `(0x00 * 256) + 0x74` | **116.0 W** |
| **Energia** | `0x0003` | `0x00` `0x1E` | `(0x00 * 256) + 0x1E` | **30 Wh** |

**3.3.3. Outros Comandos**

- **Alterar Endereço do Escravo:**
  - `[Endereço Atual] 0x06 0x00 0x02 [Novo Endereço] [CRC]`

- **Alterar Limiar do Alarme de Potência:**
  - `[Endereço do Escravo] 0x06 0x00 0x01 [Valor do Limiar] [CRC]`

- **Zerar o Contador de Energia:**
  - `[Endereço do Escravo] 0x42 [CRC]`
  - **Exemplo Prático (com endereço 0xF8):** `0xF8 0x42 0x51 0x40`
  - O módulo responde com o mesmo frame para confirmar a execução.

---

## 4. Diagrama de Fiação e Conexões

![Diagrama de Fiação do PZEM-004T](https://i.imgur.com/k9E3wXG.png)

#### 4.1. Circuito de Alta Tensão (AC)
- **ENTRADA (SOURCE):** Conecte a fase (L) e o neutro (N) da sua rede elétrica.
- **SAÍDA (LOAD):** Conecte a fase (L) e o neutro (N) que vão para a sua carga (aparelho a ser medido).
- **Transformador de Corrente (TC):** O fio da fase (L) que vai para a carga **deve passar por dentro** do anel do TC. A direção não importa.

#### 4.2. Interface de Comunicação (TTL)
- **5V:** **Alimentação externa obrigatória.** Conecte a uma fonte de 5V estável do seu microcontrolador (pino 5V do Arduino, por exemplo).
- **RX:** Conecte ao pino **TX** (Transmissor) do seu microcontrolador.
- **TX:** Conecte ao pino **RX** (Receptor) do seu microcontrolador.
- **GND:** Conecte ao pino de Terra (GND) do seu microcontrolador.

> **AVISO DE SEGURANÇA:** A interface de comunicação TTL é opticamente isolada do circuito de alta tensão. No entanto, sempre manuseie o circuito com a energia desligada e tome as devidas precauções ao trabalhar com eletricidade AC.

---

## 5. Instruções Adicionais

- **Ambiente de Operação:**
    - **Temperatura de Operação:** -20 °C a +60 °C
    - **Temperatura de Armazenamento:** -40 °C a +85 °C
- **Cálculo de CRC:** O CRC (Cyclic Redundancy Check) é um campo de verificação de erros de 16 bits. Bibliotecas Modbus para plataformas como Arduino e Python geralmente calculam o CRC automaticamente, simplificando a implementação.