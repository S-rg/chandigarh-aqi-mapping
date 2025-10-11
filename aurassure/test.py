import serial

def read_serial_to_file(port, baudrate, output_file):
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser, open(output_file, 'w') as file:
            print("Reading from serial port...")
            while True:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    print(line)
                    file.write(line + '\n')
    except KeyboardInterrupt:
        print("Stopped by user.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    read_serial_to_file('/dev/cu.usbserial-110', 115200, 'out.txt')