# Home Security System - Micro:bit Controller
from microbit import *
import spi
import music

# RFID Setup
class MFRC522:
    def __init__(self):
        self.spi = spi.init(baudrate=1000000, bits=8, mode=0, sclk=pin13, mosi=pin15, miso=pin14)
        pin2.write_digital(1)  # SDA
        pin8.write_digital(1)  # RST
    
    def read_card(self):
        # Simplified RFID reading
        return "52C31C2F"  # Example card ID

# LCD I2C Class
class LCD_I2C:
    def __init__(self):
        i2c.init(freq=400000, sda=pin14, scl=pin13)
    
    def clear(self):
        # Clear LCD command
        pass
    
    def print(self, text, line=0):
        # Print text to LCD
        display.scroll(text)  # Fallback to micro:bit display

# Initialize components
rfid = MFRC522()
lcd = LCD_I2C()
servo_pos = 0
password = "00000000"
master_key = "A1B2C3D4DD"
entered_password = ""
is_unlocked = False
valid_card = "52C31C2F"

# Keypad matrix
keypad_map = {
    (0,0): 'A', (0,1): '1', (0,2): '2', (0,3): '3',
    (1,0): 'B', (1,1): '4', (1,2): '5', (1,3): '6',
    (2,0): 'C', (2,1): '7', (2,2): '8', (2,3): '9',
    (3,0): 'D', (3,1): 'CLR', (3,2): '0', (3,3): 'ENT'
}

def beep():
    """เสียงแจ้งเตือน"""
    pin1.write_digital(1)
    sleep(100)
    pin1.write_digital(0)

def servo_control(angle):
    """ควบคุม Servo Motor"""
    global servo_pos
    servo_pos = angle
    pin0.write_analog(angle * 4)  # Convert to PWM

def check_rfid():
    """ตรวจสอบ RFID Card"""
    card_id = rfid.read_card()
    if card_id == valid_card:
        beep()
        lcd.print("Card OK", 0)
        return True
    else:
        beep()
        beep()
        lcd.print("Invalid Card", 0)
        return False

def read_keypad():
    """อ่านค่าจาก Keypad"""
    # Simplified keypad reading
    if button_a.was_pressed():
        return 'A'
    elif button_b.was_pressed():
        return 'B'
    return None

def check_password(input_pass):
    """ตรวจสอบรหัสผ่าน"""
    global password
    if input_pass == master_key:
        return "MASTER"
    elif input_pass == password:
        return "CORRECT"
    else:
        return "WRONG"

def reset_password():
    """รีเซ็ตรหัสผ่าน"""
    global password
    password = "00000000"
    lcd.print("Password Reset", 0)

# Main Loop
while True:
    # Check RFID Card
    if not is_unlocked:
        card_status = check_rfid()
        if card_status:
            is_unlocked = True
            servo_control(90)  # Unlock door
            lcd.print("Enter Password", 0)
    
    # Read Keypad Input
    if is_unlocked:
        key = read_keypad()
        if key:
            beep()
            if key == 'CLR':
                entered_password = ""
                lcd.print("Cleared", 0)
            elif key == 'ENT':
                result = check_password(entered_password)
                if result == "MASTER":
                    lcd.print("Master Mode", 0)
                    # Enter new password mode
                elif result == "CORRECT":
                    lcd.print("Access Granted", 0)
                    servo_control(180)  # Full unlock
                else:
                    lcd.print("Wrong Password", 0)
                    # Sound alarm
                    for i in range(10):
                        beep()
                        sleep(200)
                entered_password = ""
            else:
                entered_password += key
                lcd.print("*" * len(entered_password), 1)
    
    sleep(100)