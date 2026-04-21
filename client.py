import socket, ssl, pygame, os, re, subprocess

PORT, CACHE_DIR = 5050, "local_cache"

def get_wifi_ip():
    try:
        out = subprocess.check_output("ipconfig", text=True)
        m = re.search(r'Wireless LAN adapter Wi-Fi.*?IPv4.*?(\d+\.\d+\.\d+\.\d+)', out, re.S)
        return m.group(1) if m else None
    except: return None

def run():
    wifi = get_wifi_ip()
    ip = input(f"Server IP [{wifi or ''}]: ").strip() or wifi
    if not ip: return

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.load_verify_locations("server.crt"); ctx.check_hostname = False

    with socket.create_connection((ip, PORT)) as raw:
        with ctx.wrap_socket(raw, server_hostname=ip) as s:
            print(data := s.recv(4096).decode())
            choice = input("Pick a song: ")
            lines = data.strip().split('\n')
            filename = lines[int(choice)-1].split('. ',1)[1]
            local = os.path.join(CACHE_DIR, filename)
            os.makedirs(CACHE_DIR, exist_ok=True)

            if os.path.exists(local):
                s.send(b"ALREADY_HAVE"); print("Playing from cache...")
            else:
                s.send(choice.encode())
                size = int(s.recv(64).decode().strip())
                with open(local, "wb") as f:
                    recv = 0
                    while recv < size:
                        chunk = s.recv(min(16384, size - recv))
                        if not chunk: break
                        f.write(chunk); recv += len(chunk)

            pygame.mixer.init(); pygame.mixer.music.load(local)
            pygame.mixer.music.play(); print(f"Playing {filename}...")
            while pygame.mixer.music.get_busy(): pass

if __name__ == "__main__": run()
