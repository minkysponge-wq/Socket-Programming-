import tkinter as tk
from tkinter import messagebox
import socket, ssl, os, threading, pygame

PORT, CACHE_DIR = 5050, "local_cache"
BG, BG2, FG, DIM = "#1e1e1e", "#2a2a2a", "#f0f0f0", "#888888"

def connect():
    ip = ip_entry.get().strip()
    if not ip: return
    def task():
        try:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.load_verify_locations("server.crt"); ctx.check_hostname = False
            global ssock
            ssock = ctx.wrap_socket(socket.create_connection((ip, PORT)), server_hostname=ip)
            songs = [l.split('. ',1)[1] for l in ssock.recv(4096).decode().split('\n') if '. ' in l]
            listbox.delete(0, tk.END)
            for s in songs: listbox.insert(tk.END, "  " + s)
            status.set(f"Connected — {len(songs)} songs")
        except Exception as e: messagebox.showerror("Error", str(e))
    threading.Thread(target=task, daemon=True).start()

def play():
    if not listbox.curselection(): return
    idx = listbox.curselection()[0]
    filename = listbox.get(idx).strip()
    local_path = os.path.join(CACHE_DIR, filename)
    os.makedirs(CACHE_DIR, exist_ok=True)
    def task():
        try:
            if os.path.exists(local_path):
                ssock.send(b"ALREADY_HAVE"); status.set("Playing from cache...")
            else:
                ssock.send(str(idx + 1).encode())
                size = int(ssock.recv(64).decode().strip())
                status.set("Downloading...")
                with open(local_path, "wb") as f:
                    recv = 0
                    while recv < size:
                        chunk = ssock.recv(min(16384, size - recv))
                        if not chunk: break
                        f.write(chunk); recv += len(chunk)
            pygame.mixer.init(); pygame.mixer.music.load(local_path)
            pygame.mixer.music.play(); status.set(f"Now playing: {filename}")
        except Exception as e: messagebox.showerror("Error", str(e))
    threading.Thread(target=task, daemon=True).start()

def stop():
    pygame.mixer.music.stop(); status.set("Stopped")

# ── UI ────────────────────────────────────────────────────────────────────────
ssock = None
root = tk.Tk(); root.title("Music Client"); root.geometry("360x420")
root.resizable(False, False); root.configure(bg=BG)

tk.Label(root, text="Server IP", bg=BG, fg=DIM, font=("Segoe UI", 8)).pack(anchor="w", padx=20, pady=(18,2))
row = tk.Frame(root, bg=BG); row.pack(fill="x", padx=20)
ip_entry = tk.Entry(row, bg=BG2, fg=FG, insertbackground=FG, relief="flat", font=("Segoe UI", 11), bd=0)
ip_entry.pack(side="left", fill="x", expand=True, ipady=6)
ip_entry.bind("<Return>", lambda _: connect())
tk.Button(row, text="Connect", command=connect, bg="#3a3a3a", fg=FG, relief="flat",
          font=("Segoe UI", 10), padx=12, cursor="hand2").pack(side="left", padx=(8,0), ipady=4)

listbox = tk.Listbox(root, bg=BG2, fg=FG, selectbackground="#3a3a3a", selectforeground=FG,
                     relief="flat", bd=0, font=("Segoe UI", 11), activestyle="none",
                     highlightthickness=0, height=11)
listbox.pack(fill="both", padx=20, pady=(14,0))
listbox.bind("<Double-Button-1>", lambda _: play())

ctrl = tk.Frame(root, bg=BG); ctrl.pack(pady=12)
for txt, cmd in [("▶  Play", play), ("■  Stop", stop)]:
    tk.Button(ctrl, text=txt, command=cmd, bg=BG2, fg=FG, relief="flat",
              font=("Segoe UI", 10), padx=20, pady=6, cursor="hand2").pack(side="left", padx=5)

status = tk.StringVar(value="Not connected")
tk.Label(root, textvariable=status, bg=BG, fg=DIM, font=("Segoe UI", 9)).pack()
root.mainloop()
