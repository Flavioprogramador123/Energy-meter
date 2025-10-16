"""
Monitor em tempo real do Eastron SDM630 via EW11
Atualiza a cada 2 segundos
"""
import time
import os
import sys
from datetime import datetime
from pymodbus.client import ModbusTcpClient
from app.connectors.eastron_sdm630 import read_sdm630_metrics

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def format_power(watts):
    """Formata potência com direção (consumo/injeção)."""
    if watts >= 0:
        return f"🔴 {watts:.1f}W (CONSUMO)"
    else:
        return f"🟢 {abs(watts):.1f}W (INJEÇÃO)"


def clear_screen():
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')


def monitor_sdm630(host="10.0.0.109", port=8899, slave_id=1, interval=2):
    """
    Monitora SDM630 em tempo real.

    Args:
        host: IP do EW11
        port: Porta TCP (padrão 8899)
        slave_id: ID Modbus do SDM630
        interval: Intervalo entre leituras (segundos)
    """
    print(f"🔌 Conectando ao SDM630 via EW11 ({host}:{port})...")
    print(f"   Slave ID: {slave_id}")
    print(f"   Intervalo: {interval}s\n")

    client = ModbusTcpClient(host=host, port=port, timeout=3)

    if not client.connect():
        print("❌ Falha ao conectar no EW11")
        return

    client.slave_id = slave_id
    print("✅ Conectado! Iniciando monitoramento...\n")
    time.sleep(1)

    errors = 0
    readings = 0

    try:
        while True:
            try:
                clear_screen()

                # Ler métricas
                metrics = read_sdm630_metrics(client)
                readings += 1

                # Cabeçalho
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print("═" * 70)
                print(f"  EASTRON SDM630-Modbus CT - Monitor em Tempo Real")
                print(f"  {now} | Leituras: {readings} | Erros: {errors}")
                print("═" * 70)
                print()

                # Tensões
                print("📊 TENSÕES (V)")
                print(f"   L1: {metrics['voltage_l1']:>7.2f} V")
                print(f"   L2: {metrics['voltage_l2']:>7.2f} V")
                print(f"   L3: {metrics['voltage_l3']:>7.2f} V")
                print(f"   Média: {metrics['voltage_avg']:>7.2f} V")
                print()

                # Correntes
                print("⚡ CORRENTES (A)")
                print(f"   L1: {metrics['current_l1']:>7.2f} A")
                print(f"   L2: {metrics['current_l2']:>7.2f} A")
                print(f"   L3: {metrics['current_l3']:>7.2f} A")
                print(f"   Total: {metrics['current_total']:>7.2f} A")
                print()

                # Potências
                print("🔋 POTÊNCIAS (W)")
                print(f"   L1: {metrics['power_l1']:>10.1f} W")
                print(f"   L2: {metrics['power_l2']:>10.1f} W")
                print(f"   L3: {metrics['power_l3']:>10.1f} W")
                print(f"   ─────────────────")
                print(f"   TOTAL: {format_power(metrics['power_total'])}")
                print()

                # Outros
                print("📈 OUTROS")
                print(f"   Frequência: {metrics['frequency']:.2f} Hz")
                print(f"   Fator Potência: {metrics['power_factor']:.3f}")
                print(f"   Energia: {metrics['energy_kwh']:.3f} kWh")
                print()

                # Alertas
                alerts = []
                if abs(metrics['voltage_avg'] - 220) > 20:
                    alerts.append(f"⚠️  Tensão fora da faixa nominal")
                if metrics['current_total'] > 50:
                    alerts.append(f"⚠️  Corrente alta: {metrics['current_total']:.1f}A")
                if abs(metrics['power_total']) > 10000:
                    alerts.append(f"⚠️  Potência alta: {abs(metrics['power_total']):.0f}W")

                if alerts:
                    print("🚨 ALERTAS:")
                    for alert in alerts:
                        print(f"   {alert}")
                    print()

                print("═" * 70)
                print(f"Próxima leitura em {interval}s... (Ctrl+C para sair)")

                time.sleep(interval)

            except KeyboardInterrupt:
                raise
            except Exception as e:
                errors += 1
                print(f"\n❌ Erro na leitura #{readings}: {e}")
                time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\n✋ Monitoramento interrompido pelo usuário")

    finally:
        client.close()
        print(f"\n📊 Estatísticas finais:")
        print(f"   Total de leituras: {readings}")
        print(f"   Erros: {errors}")
        if readings > 0:
            print(f"   Taxa de sucesso: {((readings-errors)/readings*100):.1f}%")
        print("\n🔌 Conexão fechada.")


if __name__ == "__main__":
    import sys

    # Parâmetros via linha de comando (opcional)
    host = sys.argv[1] if len(sys.argv) > 1 else "10.0.0.109"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8899
    slave_id = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    interval = float(sys.argv[4]) if len(sys.argv) > 4 else 2

    monitor_sdm630(host, port, slave_id, interval)
