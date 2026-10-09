"""
NOVA Thermal Guard Service & Hardware Protection Subsystem
Monitors hardware sensors (CPU, GPU, MB), handles multi-level thermal thresholds,
triggers notifications/voice warnings, and safe shutdown protection.
"""

import os
import sys
import glob
import time
import logging
from typing import Dict, Any, List, Optional, Callable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NOVA Thermal Guard")

class HardwareSensorReader:
    """Reads Linux hwmon / thermal zone sysfs endpoints."""

    @staticmethod
    def get_temperatures() -> Dict[str, float]:
        temps = {}
        # Read sysfs /sys/class/thermal/thermal_zone*/temp
        thermal_zones = glob.glob("/sys/class/thermal/thermal_zone*")
        for tz in thermal_zones:
            try:
                type_file = os.path.join(tz, "type")
                temp_file = os.path.join(tz, "temp")
                if os.path.exists(temp_file):
                    tz_type = "cpu"
                    if os.path.exists(type_file):
                        with open(type_file, "r") as tf:
                            tz_type = tf.read().strip().lower()
                    with open(temp_file, "r") as f:
                        raw = float(f.read().strip())
                        # sysfs reports millidegrees C
                        val = raw / 1000.0 if raw > 1000 else raw
                        if 0 <= val <= 130:  # Ignore corrupted / non-responsive sensor values (<0 or >130C)
                            temps[tz_type] = val
            except Exception:
                pass
        return temps


class ThermalGuard:
    def __init__(self, sensor_reader: Optional[Any] = None):
        self.sensor_reader = sensor_reader or HardwareSensorReader()

        # Thresholds in Celsius
        self.ELEVATED_TEMP = 80.0
        self.DANGEROUS_TEMP = 90.0
        self.CRITICAL_TEMP = 98.0

        self.voice_warnings_enabled = True
        self.last_status = "NORMAL"
        self.callbacks: List[Callable[[str, float, str], None]] = []

    def register_callback(self, cb: Callable[[str, float, str], None]):
        self.callbacks.append(cb)

    def evaluate_temp(self, max_temp: float) -> Dict[str, Any]:
        """Evaluates hardware temperature against manufacturer/system thresholds."""
        if max_temp >= self.CRITICAL_TEMP:
            status = "CRITICAL"
            voice_msg = "Ваш ПК перегрелся. Сохраните работу и завершите её. Если температура останется критической, NOVA OS автоматически завершит работу для защиты оборудования."
            ui_msg = "Критический перегрев! Запуск процедуры безопасного сохранения и экстренного завершения работы."
        elif max_temp >= self.DANGEROUS_TEMP:
            status = "DANGEROUS"
            voice_msg = "Внимание. Ваш ПК перегревается. Сохраните работу и выключите компьютер."
            ui_msg = "Опасная температура процессора/видеокарты! Настоятельно рекомендуется закрыть ресурсоёмкие приложения."
        elif max_temp >= self.ELEVATED_TEMP:
            status = "ELEVATED"
            voice_msg = None
            ui_msg = "Повышенная температура оборудования. Рекомендуем снизить нагрузку и проверить систему охлаждения."
        else:
            status = "NORMAL"
            voice_msg = None
            ui_msg = "Температура в норме."

        return {
            "max_temp": max_temp,
            "status": status,
            "voice_message": voice_msg if self.voice_warnings_enabled else None,
            "ui_message": ui_msg
        }

    def check_system(self, mock_temps: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        temps = mock_temps if mock_temps is not None else self.sensor_reader.get_temperatures()

        if not temps:
            return {
                "status": "SENSOR_ERROR",
                "max_temp": 0.0,
                "ui_message": "Не удалось прочитать данные с аппаратных датчиков температуры.",
                "voice_message": None,
                "sensor_data": {}
            }

        max_temp = max(temps.values())
        eval_res = self.evaluate_temp(max_temp)
        eval_res["sensor_data"] = temps

        # Trigger callbacks on status change or danger
        if eval_res["status"] != self.last_status and eval_res["status"] != "NORMAL":
            for cb in self.callbacks:
                try:
                    cb(eval_res["status"], max_temp, eval_res["ui_message"])
                except Exception as e:
                    logger.error(f"Error in thermal callback: {e}")

        self.last_status = eval_res["status"]
        return eval_res

    def execute_safe_shutdown(self, dry_run: bool = True) -> bool:
        """Executes safe shutdown sequence saving system state/logs."""
        logger.warning("Thermal Guard executing safe system shutdown procedure...")
        # Save logs
        log_file = "/var/log/nova-os/thermal_shutdown.log"
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, "a") as f:
                f.write(f"[{time.ctime()}] Thermal Guard initiated safe shutdown due to critical temperature.\n")
        except Exception:
            pass

        if not dry_run:
            # Call systemd shutdown command
            os.system("systemctl poweroff")
            return True
        return True
