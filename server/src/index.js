// Hoops 4 Life 2P: the game-room server.
// One small Cloudflare Worker hands out room codes; each room is a Durable Object that passes messages
// between exactly two phones (the host and the guest) over secure WebSockets. It never reads the game
// messages, it only checks who is allowed in, how big messages are and how fast they come.
import { DurableObject } from "cloudflare:workers";

const CODE_CHARS = "ABCDEFGHJKMNPQRSTUVWXYZ23456789";   // no 0/O or 1/I/L, so codes are easy to read out
const CODE_LEN = 5;                                      // 31^5 = about 28 million codes
const ROOM_TTL_MS = 3 * 60 * 60 * 1000;                  // a room disappears 3 hours after it's made
const MAX_MSG_BYTES = 4096;                              // game messages are tiny; anything bigger is dropped
const RATE_PER_SEC = 90, BURST = 180;                    // about 3x what the game sends; more is dropped
const ROLES = ["host", "guest"];

function randomString(chars, n) {
  const bytes = new Uint8Array(n); crypto.getRandomValues(bytes);
  let s = ""; for (const b of bytes) s += chars[b % chars.length]; return s;
}
const newKey = () => randomString("abcdefghijkmnpqrstuvwxyz23456789", 24);   // a secret only that phone knows

// Which websites may use the server (the game's own pages). Comma-separated; "*.example.com" allowed.
function originAllowed(origin, list) {
  if (!origin) return false;
  let host; try { host = new URL(origin).hostname; } catch { return false; }
  return (list || "").split(",").map(s => s.trim()).filter(Boolean).some(rule => {
    if (rule === origin) return true;
    if (rule.startsWith("*.")) return host.endsWith(rule.slice(1));
    if (rule === "localhost") return host === "localhost" || host === "127.0.0.1";
    return false;
  });
}
function cors(origin) {
  return { "Access-Control-Allow-Origin": origin, "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type", "Vary": "Origin" };
}
const json = (obj, status, extra) => new Response(JSON.stringify(obj), { status: status || 200,
  headers: Object.assign({ "Content-Type": "application/json" }, extra || {}) });

export default {
  async fetch(request, env) {
    const url = new URL(request.url), origin = request.headers.get("Origin") || "";
    const allowed = originAllowed(origin, env.ALLOWED_ORIGINS);
    if (request.method === "OPTIONS") return new Response(null, { status: allowed ? 204 : 403, headers: allowed ? cors(origin) : {} });
    if (url.pathname === "/") return new Response("Hoops 4 Life rooms: ok");

    // the host asks for a new room: gets a code to share and a secret key for itself
    if (url.pathname === "/new" && request.method === "POST") {
      if (!allowed) return json({ error: "not allowed" }, 403);
      for (let tries = 0; tries < 5; tries++) {
        const code = randomString(CODE_CHARS, CODE_LEN);
        const room = env.ROOMS.get(env.ROOMS.idFromName(code));
        const res = await room.fetch("https://room/init", { method: "POST" });
        if (res.status === 200) { const { hostKey } = await res.json(); return json({ code, hostKey }, 200, cors(origin)); }
      }
      return json({ error: "try again" }, 503, cors(origin));
    }

    // a phone joins a room: wss://.../room/ABCDE?role=host&key=...  or  ?role=guest[&key=...]
    const m = url.pathname.match(/^\/room\/([A-Z0-9]{5})$/);
    if (m) {
      if (request.headers.get("Upgrade") !== "websocket") return new Response("expected a websocket", { status: 426 });
      if (!allowed) return new Response("not allowed", { status: 403 });
      return env.ROOMS.get(env.ROOMS.idFromName(m[1])).fetch(request);
    }
    return new Response("not found", { status: 404 });
  }
};

export class GameRoom extends DurableObject {
  async fetch(request) {
    const url = new URL(request.url), st = this.ctx.storage;

    // a brand-new room: remember it exists, make the host's key, and set it to expire
    if (url.pathname === "/init") {
      if (await st.get("created")) return new Response("taken", { status: 409 });
      const hostKey = newKey();
      await st.put({ created: Date.now(), hostKey });
      await st.setAlarm(Date.now() + ROOM_TTL_MS);
      return json({ hostKey });
    }

    // joining: the room must have been made with /new (so guessing codes doesn't create rooms)
    if (!(await st.get("created"))) return new Response("no such room", { status: 404 });
    const role = url.searchParams.get("role"), key = url.searchParams.get("key") || "";
    if (!ROLES.includes(role)) return new Response("bad role", { status: 400 });
    let myKey;
    if (role === "host") {
      if (key !== (await st.get("hostKey"))) return new Response("wrong key", { status: 403 });
      myKey = key;
    } else {
      // the first guest takes the guest seat and gets a key; after that only that phone can come back
      const guestKey = await st.get("guestKey");
      if (guestKey && key !== guestKey) return new Response("room full", { status: 403 });
      myKey = guestKey || newKey();
      if (!guestKey) await st.put("guestKey", myKey);
    }
    // the same phone reconnecting (after a tunnel, say) replaces its old connection
    for (const old of this.ctx.getWebSockets(role)) { try { old.close(4000, "reconnected"); } catch {} }

    const [client, server] = Object.values(new WebSocketPair());
    this.ctx.acceptWebSocket(server, [role]);
    server.serializeAttachment({ role, tokens: BURST, last: Date.now() });
    const other = role === "host" ? "guest" : "host", otherHere = this.ctx.getWebSockets(other).length > 0;
    server.send(JSON.stringify({ t: "hello", role, key: myKey, peer: otherHere }));
    this.sendTo(other, { t: "peer", s: "joined" });
    return new Response(null, { status: 101, webSocket: client });
  }

  sendTo(role, obj) {
    const msg = typeof obj === "string" ? obj : JSON.stringify(obj);
    for (const ws of this.ctx.getWebSockets(role)) { try { ws.send(msg); } catch {} }
  }

  // pass each message to the other phone, after the size and speed checks
  async webSocketMessage(ws, message) {
    const a = ws.deserializeAttachment() || {};
    if (typeof message !== "string" || message.length > MAX_MSG_BYTES) return;
    const now = Date.now();
    a.tokens = Math.min(BURST, (a.tokens ?? BURST) + (now - (a.last || now)) / 1000 * RATE_PER_SEC); a.last = now;
    if (a.tokens < 1) { ws.serializeAttachment(a); return; }   // too fast: drop it
    a.tokens -= 1; ws.serializeAttachment(a);
    this.sendTo(a.role === "host" ? "guest" : "host", message);
  }

  async webSocketClose(ws, code) {
    const a = ws.deserializeAttachment() || {};
    try { ws.close(code === 1005 ? 1000 : code, "bye"); } catch {}
    // tell the other phone, unless this phone has already reconnected
    if (code !== 4000 && a.role && this.ctx.getWebSockets(a.role).filter(w => w !== ws).length === 0)
      this.sendTo(a.role === "host" ? "guest" : "host", { t: "peer", s: "left" });
  }
  async webSocketError(ws) { await this.webSocketClose(ws, 1011); }

  // the room's time is up: close it and forget everything about it
  async alarm() {
    for (const ws of this.ctx.getWebSockets()) { try { ws.close(4002, "room expired"); } catch {} }
    await this.ctx.storage.deleteAll();
  }
}

export const _test = { originAllowed, randomString, CODE_CHARS };
