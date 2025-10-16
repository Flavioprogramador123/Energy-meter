"""Conector Modbus TCP para dispositivos via rede (Elfin-EW11A, etc)."""
from __future__ import annotations
from typing import Any
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException


class ModbusTCPClient:
    """Cliente Modbus TCP para conversores RS485 para Ethernet/WiFi."""

    def __init__(self, host: str, port: int = 502, slave_id: int = 1, timeout: float = 3.0):
        """
        Args:
            host: IP ou hostname do conversor (ex: 192.168.1.100)
            port: Porta TCP Modbus (padrão 502)
            slave_id: ID do escravo Modbus (padrão 1)
            timeout: Timeout em segundos (padrão 3s)
        """
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self.timeout = timeout
        self.client = None

    def connect(self) -> bool:
        """Conecta ao dispositivo Modbus TCP."""
        try:
            self.client = ModbusTcpClient(
                host=self.host,
                port=self.port,
                timeout=self.timeout
            )
            return self.client.connect()
        except Exception as e:
            print(f"Erro ao conectar Modbus TCP {self.host}:{self.port} - {e}")
            return False

    def read_input_registers(self, address: int, count: int) -> list[int]:
        """Lê registradores de entrada (function code 4)."""
        if not self.client or not self.client.connected:
            if not self.connect():
                raise ConnectionError(f"Falha ao conectar em {self.host}:{self.port}")

        try:
            result = self.client.read_input_registers(
                address=address,
                count=count,
                slave=self.slave_id
            )

            if result.isError():
                raise ModbusException(f"Erro Modbus: {result}")

            return result.registers
        except Exception as e:
            raise Exception(f"Erro ao ler registradores: {e}")

    def read_holding_registers(self, address: int, count: int) -> list[int]:
        """Lê registradores de retenção (function code 3)."""
        if not self.client or not self.client.connected:
            if not self.connect():
                raise ConnectionError(f"Falha ao conectar em {self.host}:{self.port}")

        try:
            result = self.client.read_holding_registers(
                address=address,
                count=count,
                slave=self.slave_id
            )

            if result.isError():
                raise ModbusException(f"Erro Modbus: {result}")

            return result.registers
        except Exception as e:
            raise Exception(f"Erro ao ler registradores: {e}")

    def write_register(self, address: int, value: int) -> Any:
        """Escreve em um registrador (function code 6)."""
        if not self.client or not self.client.connected:
            if not self.connect():
                raise ConnectionError(f"Falha ao conectar em {self.host}:{self.port}")

        try:
            result = self.client.write_register(
                address=address,
                value=value,
                slave=self.slave_id
            )

            if result.isError():
                raise ModbusException(f"Erro Modbus: {result}")

            return result
        except Exception as e:
            raise Exception(f"Erro ao escrever registrador: {e}")

    def close(self):
        """Fecha a conexão."""
        if self.client:
            self.client.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
