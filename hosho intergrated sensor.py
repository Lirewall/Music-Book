import smbus
import time

# MPU6050 Addresses
MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B

# Initialize I2C
bus = smbus.SMBus(1)

# Wake up MPU6050
bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)

def read_accel_x():
    high = bus.read_byte_data(MPU6050_ADDR, ACCEL_XOUT_H)
    low = bus.read_byte_data(MPU6050_ADDR, ACCEL_XOUT_H+1)
    value = (high << 8) + low
    if value >= 0x8000:
        value = -((65535 - value) + 1)
    return abs(value)

while True:
    accel_x = read_accel_x() // 1000  # Normalize values

    if accel_x > 15:
        print("🪘 CHA (Strong Shake)")
    elif accel_x > 8:
        print("🎶 CHI (Soft Shake)")
    else:
        print("🔕 Rest")

    time.sleep(0.3)