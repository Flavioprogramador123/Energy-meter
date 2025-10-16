# app/services/hybrid_storage.py
import os
import io
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.core.db import SessionLocal
from app.models import Measurement
from app.connectors.google_drive import GoogleDriveStorage

class HybridStorage:
    def __init__(self):
        self.db = SessionLocal()
        self.gdrive = GoogleDriveStorage()
        self.use_gdrive = self._check_gdrive_config()
    
    def _check_gdrive_config(self) -> bool:
        """Verificar se Google Drive está configurado"""
        credentials_file = os.getenv("GOOGLE_DRIVE_CREDENTIALS_FILE")
        folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
        
        if credentials_file and folder_id and os.path.exists(credentials_file):
            print("✅ Google Drive configurado - usando storage híbrido")
            return True
        else:
            print("⚠️ Google Drive não configurado - usando apenas SQLite")
            return False
    
    def save_measurement(self, device_id: int, metric: str, value: float, timestamp: datetime = None):
        """Salvar medição em ambos os locais (SQLite + Google Drive)"""
        if timestamp is None:
            timestamp = datetime.now()
        
        success_count = 0
        
        # 1. Salvar no SQLite (sempre)
        try:
            measurement = Measurement(
                device_id=device_id,
                metric=metric,
                value=value,
                timestamp=timestamp
            )
            self.db.add(measurement)
            self.db.commit()
            success_count += 1
            print(f"✅ Medição salva no SQLite: {metric}={value}")
        except Exception as e:
            print(f"❌ Erro ao salvar no SQLite: {e}")
            self.db.rollback()
        
        # 2. Salvar no Google Drive (se configurado)
        if self.use_gdrive:
            try:
                if self.gdrive.save_measurement(device_id, metric, value, timestamp):
                    success_count += 1
            except Exception as e:
                print(f"❌ Erro ao salvar no Google Drive: {e}")
        
        return success_count > 0
    
    def get_measurements(self, device_id: int, metric: str, limit: int = 100) -> List[Dict]:
        """Buscar medições (prioridade: SQLite, fallback: Google Drive)"""
        measurements = []
        
        # 1. Tentar SQLite primeiro
        try:
            db_measurements = self.db.query(Measurement).filter(
                Measurement.device_id == device_id,
                Measurement.metric == metric
            ).order_by(Measurement.timestamp.desc()).limit(limit).all()
            
            if db_measurements:
                measurements = [
                    {
                        "id": m.id,
                        "device_id": m.device_id,
                        "metric": m.metric,
                        "value": m.value,
                        "timestamp": m.timestamp.isoformat()
                    }
                    for m in db_measurements
                ]
                print(f"✅ {len(measurements)} medições carregadas do SQLite")
                return measurements
                
        except Exception as e:
            print(f"❌ Erro ao buscar no SQLite: {e}")
        
        # 2. Fallback para Google Drive
        if self.use_gdrive and not measurements:
            try:
                gdrive_measurements = self.gdrive.get_measurements(device_id, metric, days=7)
                if gdrive_measurements:
                    measurements = gdrive_measurements[:limit]
                    print(f"✅ {len(measurements)} medições carregadas do Google Drive")
            except Exception as e:
                print(f"❌ Erro ao buscar no Google Drive: {e}")
        
        return measurements
    
    def backup_to_gdrive(self) -> bool:
        """Fazer backup de todos os dados para Google Drive"""
        if not self.use_gdrive:
            print("❌ Google Drive não configurado")
            return False
        
        try:
            # Buscar todas as medições do SQLite
            measurements = self.db.query(Measurement).all()
            
            success_count = 0
            for measurement in measurements:
                if self.gdrive.save_measurement(
                    measurement.device_id,
                    measurement.metric,
                    measurement.value,
                    measurement.timestamp
                ):
                    success_count += 1
            
            print(f"✅ Backup realizado: {success_count}/{len(measurements)} medições")
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Erro no backup: {e}")
            return False
    
    def restore_from_gdrive(self) -> bool:
        """Restaurar dados do Google Drive para SQLite"""
        if not self.use_gdrive:
            print("❌ Google Drive não configurado")
            return False
        
        try:
            # Buscar medições dos últimos 30 dias
            all_measurements = []
            for day in range(30):
                date = datetime.now() - timedelta(days=day)
                filename = f"measurements_{date.strftime('%Y-%m-%d')}.csv"
                
                file_id = self.gdrive._get_file_id(filename)
                if file_id:
                    content = self.gdrive.service.files().get_media(fileId=file_id).execute()
                    df = pd.read_csv(io.BytesIO(content))
                    all_measurements.extend(df.to_dict('records'))
            
            # Salvar no SQLite
            success_count = 0
            for data in all_measurements:
                try:
                    measurement = Measurement(
                        device_id=data['device_id'],
                        metric=data['metric'],
                        value=data['value'],
                        timestamp=datetime.fromisoformat(data['timestamp'])
                    )
                    self.db.add(measurement)
                    success_count += 1
                except Exception as e:
                    print(f"❌ Erro ao restaurar medição: {e}")
            
            self.db.commit()
            print(f"✅ Restauração realizada: {success_count} medições")
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Erro na restauração: {e}")
            return False
    
    def get_storage_status(self) -> Dict:
        """Obter status do armazenamento"""
        status = {
            "sqlite": "connected",
            "google_drive": "not_configured",
            "hybrid_mode": False,
            "last_backup": None
        }
        
        # Verificar SQLite
        try:
            self.db.query(Measurement).first()
            status["sqlite"] = "connected"
        except Exception:
            status["sqlite"] = "error"
        
        # Verificar Google Drive
        if self.use_gdrive:
            if self.gdrive.test_connection():
                status["google_drive"] = "connected"
                status["hybrid_mode"] = True
            else:
                status["google_drive"] = "error"
        
        return status
    
    def close(self):
        """Fechar conexões"""
        self.db.close()