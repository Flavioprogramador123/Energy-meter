"""
Script para registrar o Eastron SDM630 no banco de dados
Executa uma vez para criar o cliente e dispositivo
"""
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from app.core.db import SessionLocal
from app import crud, schemas


def setup_sdm630(
    client_name: str = "Cliente Principal",
    device_name: str = "SDM630 - Entrada Principal",
    ew11_host: str = "10.0.0.109",
    ew11_port: int = 8899,
    slave_id: int = 1,
):
    """
    Cria cliente e dispositivo SDM630 no banco.

    Args:
        client_name: Nome do cliente
        device_name: Nome do dispositivo
        ew11_host: IP do EW11
        ew11_port: Porta TCP do EW11 (padrão 8899)
        slave_id: ID Modbus do SDM630 (padrão 1)
    """
    db = SessionLocal()

    try:
        # Criar ou buscar cliente
        clients = crud.list_clients(db)
        client = next((c for c in clients if c.name == client_name), None)

        if not client:
            print(f"📋 Criando cliente: {client_name}")
            client = crud.create_client(
                db,
                schemas.ClientCreate(name=client_name, external_id=None)
            )
            print(f"   ✅ Cliente criado com ID: {client.id}")
        else:
            print(f"📋 Cliente já existe: {client_name} (ID: {client.id})")

        # Verificar se dispositivo já existe
        devices = crud.list_devices(db, client_id=client.id)
        existing = next((d for d in devices if d.name == device_name), None)

        if existing:
            print(f"⚠️  Dispositivo '{device_name}' já existe (ID: {existing.id})")
            print(f"   Config atual: {existing.config}")

            update = input("Deseja atualizar a configuração? (s/N): ").lower()
            if update != 's':
                print("❌ Cancelado pelo usuário")
                return

            # Atualizar config (não há método update em crud, vamos fazer manualmente)
            existing.config = {
                "host": ew11_host,
                "port": ew11_port,
                "slave_id": slave_id,
                "driver": "sdm630",
                "timeout": 3.0,
            }
            existing.active = True
            db.commit()
            print(f"✅ Dispositivo atualizado!")
            return

        # Criar novo dispositivo
        print(f"🔌 Criando dispositivo: {device_name}")
        device = crud.create_device(
            db,
            schemas.DeviceCreate(
                client_id=client.id,
                name=device_name,
                device_type="modbus_tcp",  # Importante: tipo modbus_tcp para EW11
                active=True,
                config={
                    "host": ew11_host,
                    "port": ew11_port,
                    "slave_id": slave_id,
                    "driver": "sdm630",  # Driver específico do SDM630
                    "timeout": 3.0,
                }
            )
        )

        print(f"   ✅ Dispositivo criado com ID: {device.id}")
        print()
        print("=" * 60)
        print("✅ SDM630 configurado com sucesso!")
        print("=" * 60)
        print(f"Cliente: {client.name} (ID: {client.id})")
        print(f"Dispositivo: {device.name} (ID: {device.id})")
        print(f"Tipo: {device.device_type}")
        print(f"EW11: {ew11_host}:{ew11_port}")
        print(f"Slave ID: {slave_id}")
        print()
        print("O poller automático coletará dados a cada 30 segundos.")
        print("Inicie o servidor: uvicorn app.main:app --reload")
        print()

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    # Parâmetros via linha de comando (opcional)
    client_name = sys.argv[1] if len(sys.argv) > 1 else "Cliente Principal"
    device_name = sys.argv[2] if len(sys.argv) > 2 else "SDM630 - Entrada Principal"
    ew11_host = sys.argv[3] if len(sys.argv) > 3 else "10.0.0.109"
    ew11_port = int(sys.argv[4]) if len(sys.argv) > 4 else 8899
    slave_id = int(sys.argv[5]) if len(sys.argv) > 5 else 1

    setup_sdm630(client_name, device_name, ew11_host, ew11_port, slave_id)
