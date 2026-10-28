"""A local stand-in for the room server (same protocol), using only Python's standard library.
POST /new -> {code, hostKey};  WebSocket /room/CODE?role=host|guest&key=...  usage: python3 -I fake_rooms.py 8787"""
import asyncio, base64, hashlib, json, os, random, struct, sys, urllib.parse
CHARS = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
rooms = {}   # code -> {"hostKey", "guestKey", "socks": {role: writer}}

def frame(text):
    b = text.encode(); n = len(b)
    head = bytes([0x81]) + (bytes([n]) if n < 126 else bytes([126]) + struct.pack(">H", n))
    return head + b

async def read_frame(r):
    h = await r.readexactly(2); op = h[0] & 15; n = h[1] & 127
    if n == 126: n = struct.unpack(">H", await r.readexactly(2))[0]
    elif n == 127: n = struct.unpack(">Q", await r.readexactly(8))[0]
    mask = await r.readexactly(4) if h[1] & 128 else b"\0\0\0\0"
    data = bytes(c ^ mask[i % 4] for i, c in enumerate(await r.readexactly(n)))
    return op, data

async def handle(reader, writer):
    try:
        req = (await reader.readuntil(b"\r\n\r\n")).decode()
        line, *hdrs = req.split("\r\n"); method, path, _ = line.split(" ")
        H = {k.lower(): v for k, v in (h.split(": ", 1) for h in hdrs if ": " in h)}
        cors = "Access-Control-Allow-Origin: *\r\nAccess-Control-Allow-Methods: POST, OPTIONS\r\nAccess-Control-Allow-Headers: Content-Type\r\n"
        u = urllib.parse.urlparse(path); q = dict(urllib.parse.parse_qsl(u.query))
        if method == "OPTIONS":
            writer.write(f"HTTP/1.1 204 No Content\r\n{cors}Content-Length: 0\r\n\r\n".encode()); await writer.drain(); writer.close(); return
        if u.path == "/new" and method == "POST":
            code = "".join(random.choice(CHARS) for _ in range(5)); key = os.urandom(12).hex()
            rooms[code] = {"hostKey": key, "guestKey": None, "socks": {}}
            body = json.dumps({"code": code, "hostKey": key}).encode()
            writer.write(f"HTTP/1.1 200 OK\r\n{cors}Content-Type: application/json\r\nContent-Length: {len(body)}\r\n\r\n".encode() + body)
            await writer.drain(); writer.close(); return
        code = u.path.rsplit("/", 1)[-1]; role = q.get("role"); key = q.get("key", ""); room = rooms.get(code)
        ok = room and role in ("host", "guest") and (key == room["hostKey"] if role == "host" else (room["guestKey"] is None or key == room["guestKey"]))
        if not ok or H.get("upgrade", "").lower() != "websocket":
            writer.write(b"HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\n\r\n"); await writer.drain(); writer.close(); return
        if role == "guest" and room["guestKey"] is None: room["guestKey"] = os.urandom(12).hex()
        acc = base64.b64encode(hashlib.sha1((H["sec-websocket-key"] + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
        writer.write(f"HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: {acc}\r\n\r\n".encode())
        other = "guest" if role == "host" else "host"; room["socks"][role] = writer
        writer.write(frame(json.dumps({"t": "hello", "role": role, "key": room["hostKey"] if role == "host" else room["guestKey"], "peer": other in room["socks"]})))
        if other in room["socks"]: room["socks"][other].write(frame(json.dumps({"t": "peer", "s": "joined"})))
        await writer.drain()
        while True:
            op, data = await read_frame(reader)
            if op == 8: break
            if op == 1 and other in room["socks"]:
                room["socks"][other].write(frame(data.decode())); await room["socks"][other].drain()
    except (asyncio.IncompleteReadError, ConnectionError):
        pass
    finally:
        for c, room in rooms.items():
            for role, w in list(room["socks"].items()):
                if w is writer:
                    del room["socks"][role]; o = "guest" if role == "host" else "host"
                    if o in room["socks"]: room["socks"][o].write(frame(json.dumps({"t": "peer", "s": "left"})))
        try: writer.close()
        except Exception: pass

async def main():
    srv = await asyncio.start_server(handle, "127.0.0.1", int(sys.argv[1] if len(sys.argv) > 1 else 8787)); print("fake rooms on", srv.sockets[0].getsockname(), flush=True)
    async with srv: await srv.serve_forever()
asyncio.run(main())
