# LAN Music Streaming Server

A secure music streaming application for local networks, built in Python using raw sockets and TLS. A server hosts `.mp3` files and streams them to clients over an encrypted connection. Clients cache songs locally after the first download to avoid redundant transfers.

The project includes both a command-line client and a Tkinter-based graphical client.

## Features

- TLS-encrypted socket communication using a self-signed certificate
- Multi-client support via threading
- Client-side caching to eliminate repeat downloads
- Two client implementations: a minimal CLI and a dark-themed GUI
- Server-side logging of connections, transfer rates, and cache hits
- Automatic detection of the local Wi-Fi IP on the CLI client

## Project Structure

```
.
├── server.py            Multi-threaded TLS music server
├── client.py            Command-line client
├── gui_client.py        Tkinter GUI client
├── generate_ssl.py      Generates server.key and server.crt
├── server.crt           Public certificate (distributed to clients)
├── server.key           Private key (server only; never commit)
├── server_metrics.log   Server activity log
└── local_cache/         Client-side cache (auto-created)
```

## Requirements

- Python 3.8 or higher
- Third-party packages:

```
pip install pygame cryptography
```

All other modules (`socket`, `ssl`, `threading`, `tkinter`, `logging`, `os`) are part of the Python standard library.

## Setup and Usage

### 1. Generate the SSL certificate

On the machine that will run the server:

```
python generate_ssl.py
```

This produces `server.key` and `server.crt`. The certificate's Common Name is bound to the machine's current IP address.

### 2. Distribute the certificate

Copy `server.crt` to each client machine. The private key (`server.key`) must remain on the server. Clients use the certificate to verify the server's identity during the TLS handshake.

### 3. Add music files

Place `.mp3` files in the same directory as `server.py`. The server lists every MP3 it finds when a client connects.

### 4. Start the server

```
python server.py
```

The server prints its LAN IP and listens on port 5050:

```
[SERVER LIVE]  192.168.1.10 | Port: 5050
```

### 5. Run a client

Command-line:

```
python client.py
```

Graphical:

```
python gui_client.py
```

Enter the server's IP address, select a track from the list, and start playback.

## Security Considerations

- All traffic between client and server is encrypted with TLS.
- Hostname verification (`check_hostname`) is disabled on the client because the certificate is bound to an IP address rather than a domain name. This is acceptable for LAN use but is not suitable for production or public-facing deployments.
- The private key `server.key` must never be committed to version control. Use the following `.gitignore` entries:

```
server.key
local_cache/
__pycache__/
*.pyc
server_metrics.log
```

If the key has already been pushed to a remote repository, regenerate it with `generate_ssl.py` and redistribute the new certificate to all clients.

## Protocol

A simple text-based exchange occurs over the TLS socket:

1. The client connects. The server responds with a numbered list of available songs, one per line, in the format `1. song.mp3`.
2. The client sends one of the following:
   - A song index (for example, `2`). The server replies with the file size as a 64-byte right-padded ASCII string, then streams the raw file bytes.
   - `ALREADY_HAVE` if the requested song is already cached. The server logs a cache hit and waits for the next request.
   - `QUIT` to close the session.
3. File data is transferred in 16 KB chunks.

## Network Requirements

- The server and all clients must be on the same local network.
- Port 5050 must be open on the server's firewall.
- Exposing the server beyond the LAN is not recommended. If remote access is required, use a VPN or SSH tunnel rather than port forwarding, since the certificate is bound to a private IP.

## Troubleshooting

| Issue | Likely cause |
|---|---|
| `TLSV1_ALERT_UNKNOWN_CA` reported on the server | The client is missing `server.crt`, or the certificate was regenerated without being redistributed |
| Connection times out | A firewall is blocking port 5050, or the client is on a different subnet |
| `No music found` | No `.mp3` files exist in the server's working directory |
| Playback is silent | `pygame.mixer` could not decode the file; verify the MP3 is valid |
| Certificate errors after changing networks | The server's IP has changed; rerun `generate_ssl.py` and redistribute the new `server.crt` |

## License

Released under the MIT License.
