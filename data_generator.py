import pandas as pd
import numpy as np
import random

# CONFIGURATION
MINUTES_IN_DAY = 1440 
VOLTAGE_BASE = 230 

# "Virtual Appliances"
APPLIANCES = {
    "Fridge": {"power": 150, "probability": 0.02, "duration_min": 20},
    "AC": {"power": 1500, "probability": 0.005, "duration_min": 60},
    "Laptop": {"power": 65, "probability": 0.05, "duration_min": 120},
    "Heater": {"power": 2000, "probability": 0.002, "duration_min": 15}
}

def generate_smart_home_data():
    print("Initializing Eco-Grid Simulation...")
    timestamps, voltage_data, total_power_data = [], [], []
    active_devices_log = []

    device_timers = {name: 0 for name in APPLIANCES}

    for minute in range(MINUTES_IN_DAY):
        # Time & Voltage
        time_str = f"{minute // 60:02d}:{minute % 60:02d}"
        inst_voltage = VOLTAGE_BASE + np.random.normal(0, 2)
        
        # Calculate Power
        active_power_watts = 0
        current_active_devices = []

        for name, specs in APPLIANCES.items():
            if device_timers[name] > 0:
                active_power_watts += specs["power"]
                device_timers[name] -= 1
                current_active_devices.append(name)
            else:
                if random.random() < specs["probability"]:
                    device_timers[name] = specs["duration_min"]
                    active_power_watts += specs["power"]
                    current_active_devices.append(name)

        vampire_load = random.uniform(10, 30)
        total_load = active_power_watts + vampire_load
        
        timestamps.append(time_str)
        voltage_data.append(round(inst_voltage, 2))
        total_power_data.append(round(total_load, 2))
        
        if not current_active_devices:
            active_devices_log.append("Standby Only")
        else:
            active_devices_log.append(", ".join(current_active_devices))

    # Export Data
    df = pd.DataFrame({
        "Time": timestamps,
        "Voltage_V": voltage_data,
        "Total_Power_W": total_power_data,
        "True_Label": active_devices_log
    })
    df.to_csv("eco_grid_data.csv", index=False)
    print("✅ Data Generated: eco_grid_data.csv")

if __name__ == "__main__":
    generate_smart_home_data()