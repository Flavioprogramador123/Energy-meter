from typing import Any, Optional
import minimalmodbus
from pymodbus.client import ModbusTcpClient as PyModbusTcpClient


class ModbusTCPClient:
    """Cliente Modbus TCP para comunicação via EW11 ou gateway TCP."""

    def __init__(self, host: str, port: int = 502, slave_id: int = 1, timeout: float = 2.0):
        """
        Args:
            host: IP do gateway (ex: '10.0.0.109' para EW11)
            port: Porta TCP (502 padrão Modbus, 8899 para EW11)
            slave_id: ID Modbus do dispositivo escravo
            timeout: Timeout em segundos
        """
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self.client = PyModbusTcpClient(host=host, port=port, timeout=timeout)
        self._connected = False

    def connect(self) -> bool:
        """Conecta ao servidor Modbus TCP."""
        self._connected = self.client.connect()
        return self._connected

    def read_registers(self, address: int, count: int) -> list[int]:
        """Lê Holding Registers (função 0x03)."""
        if not self._connected:
            self.connect()
        result = self.client.read_holding_registers(address=address, count=count, slave=self.slave_id)
        if result.isError():
            raise Exception(f"Erro ao ler registradores: {result}")
        return result.registers

    def read_input_registers(self, address: int, count: int) -> list[int]:
        """Lê Input Registers (função 0x04)."""
        if not self._connected:
            self.connect()
        result = self.client.read_input_registers(address=address, count=count, slave=self.slave_id)
        if result.isError():
            raise Exception(f"Erro ao ler registradores de entrada: {result}")
        return result.registers

    def write_register(self, address: int, value: int):
        """Escreve em um Holding Register (função 0x06)."""
        if not self._connected:
            self.connect()
        result = self.client.write_register(address=address, value=value, slave=self.slave_id)
        if result.isError():
            raise Exception(f"Erro ao escrever registrador: {result}")
        return result

    def close(self):
        """Fecha a conexão TCP."""
        if self._connected:
            self.client.close()
            self._connected = False

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class ModbusRTUClient:
    def __init__(self, port: str, slave_id: int, baudrate: int = 9600, timeout: float = 0.5):
        self.instrument = minimalmodbus.Instrument(port, slave_id)
        self.instrument.serial.baudrate = baudrate
        self.instrument.serial.timeout = timeout
        self.instrument.mode = minimalmodbus.MODE_RTU

    def read_registers(self, address: int, count: int) -> list[int]:
        return self.instrument.read_registers(address, count, functioncode=3)

    def read_input_registers(self, address: int, count: int) -> list[int]:
        return self.instrument.read_registers(address, count, functioncode=4)

    def write_register(self, address: int, value: int) -> Any:
        return self.instrument.write_register(address, value)

    def close(self):
        """Fecha a conexão serial para liberar a porta."""
        if self.instrument and self.instrument.serial and self.instrument.serial.is_open:
            self.instrument.serial.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

