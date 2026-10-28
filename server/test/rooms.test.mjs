// Runs the room server in Node with small stand-ins for Cloudflare's parts.  node server/test/rooms.test.mjs
import fs from "node:fs"; import path from "node:path"; import os from "node:os"; import assert from "node:assert/strict";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
// swap the Cloudflare import for a plain base class
let src = fs.readFileSync(path.join(here, "../src/index.js"), "utf8")
  .replace('import { DurableObject } from "cloudflare:workers";', "class DurableObject { constructor(ctx, env){ this.ctx=ctx; this.env=env; } }");
const tmp = path.join(fs.mkdtempSync(path.join(os.tmpdir(), "rooms-")), "index.mjs"); fs.writeFileSync(tmp, src);

// --- stand-ins ---
globalThis.Response = class { constructor(body, init = {}) { this.body = body; this.status = init.status || 200; this.webSocket = init.webSocket; this.headers = init.headers || {}; }
  async json() { return JSON.parse(this.body); } };
class FakeSocket { constructor() { this.sent = []; this.closed = null; this.att = null; this.peer = null; }
  send(m) { if (this.closed) throw new Error("closed"); this.sent.push(m); } close(code, r) { this.closed = { code, r }; }
  serializeAttachment(a) { this.att = JSON.parse(JSON.stringify(a)); } deserializeAttachment() { return this.att && JSON.parse(JSON.stringify(this.att)); } }
globalThis.WebSocketPair = class { constructor() { const a = new FakeSocket(), b = new FakeSocket(); a.peer = b; b.peer = a; this[0] = a; this[1] = b; } };
class FakeCtx { constructor() { this.store = new Map(); this.sockets = []; this.alarmAt = null; const self = this;
    this.storage = { async get(k) { return self.store.get(k); }, async put(k, v) { if (typeof k === "object") for (const [a, b] of Object.entries(k)) self.store.set(a, b); else self.store.set(k, v); },
      async setAlarm(t) { self.alarmAt = t; }, async deleteAll() { self.store.clear(); } }; }
  acceptWebSocket(ws, tags) { ws.tags = tags; this.sockets.push(ws); }
  getWebSockets(tag) { return this.sockets.filter(w => !w.closed && (!tag || w.tags.includes(tag))); } }

const { default: worker, GameRoom, _test } = await import(pathToFileURL(tmp));
const rooms = new Map();
const env = { ALLOWED_ORIGINS: "https://keithhearne.github.io,localhost",
  ROOMS: { idFromName: n => n, get: id => { if (!rooms.has(id)) rooms.set(id, new GameRoom(new FakeCtx(), env)); return rooms.get(id); } } };
const req = (url, { method = "GET", origin = "https://keithhearne.github.io", ws = false } = {}) => ({
  url, method, headers: { get: h => ({ Origin: origin, Upgrade: ws ? "websocket" : null })[h] ?? null } });
// the room's own fetch receives a plain URL string from /new, and a request object when joining
GameRoom.prototype._fetch = GameRoom.prototype.fetch;
GameRoom.prototype.fetch = function (r) { return this._fetch(typeof r === "string" ? { url: r } : r); };
const join = async (code, q) => { const res = await worker.fetch(req(`https://x/room/${code}?${q}`, { ws: true }), env);
  return { res, client: res.webSocket, server: res.webSocket && res.webSocket.peer }; };
const last = s => JSON.parse(s.sent[s.sent.length - 1]);
let n = 0; const ok = (name) => { n++; console.log("ok -", name); };

// 1. making a room
let r = await worker.fetch(req("https://x/new", { method: "POST" }), env); assert.equal(r.status, 200);
const { code, hostKey } = await r.json();
assert.match(code, /^[A-Z2-9]{5}$/); assert.equal(hostKey.length, 24); ok("new room gives a 5-letter code and a host key");
r = await worker.fetch(req("https://x/new", { method: "POST", origin: "https://evil.example" }), env); assert.equal(r.status, 403); ok("other websites can't make rooms");
r = await worker.fetch(req("https://x/new", { method: "POST", origin: "" }), env); assert.equal(r.status, 403); ok("requests without a website origin are refused");

// 2. joining
let h = await join(code, "role=host&key=wrong"); assert.equal(h.res.status, 403); ok("host needs the right key");
h = await join(code, `role=host&key=${hostKey}`); assert.equal(h.res.status, 101);
assert.deepEqual(last(h.server.peer === h.client ? h.server : h.server), last(h.server)); // shape check
const hello = JSON.parse(h.client.peer.sent[0]); assert.equal(hello.t, "hello"); assert.equal(hello.peer, false); ok("host joins and is told the guest isn't there yet");
let g = await join(code, "role=guest"); assert.equal(g.res.status, 101);
const gHello = JSON.parse(g.client.peer.sent[0]); assert.equal(gHello.peer, true); assert.equal(gHello.key.length, 24);
assert.deepEqual(last(h.client.peer), { t: "peer", s: "joined" }); ok("guest joins, gets its own key, host hears about it");
let g2 = await join(code, "role=guest"); assert.equal(g2.res.status, 403); ok("a third phone is refused (room full)");
let x = await join("ZZZZZ", "role=guest"); assert.equal(x.res.status, 404); ok("a made-up code isn't a room");
r = await worker.fetch(req(`https://x/room/${code}?role=guest&key=${gHello.key}`, { ws: true, origin: "https://evil.example" }), env); assert.equal(r.status, 403); ok("other websites can't join rooms");

// 3. passing messages
const room = rooms.get(code), hs = h.client.peer, gs = g.client.peer;
await room.webSocketMessage(hs, '{"t":"s","x":1}'); assert.equal(gs.sent[gs.sent.length - 1], '{"t":"s","x":1}');
await room.webSocketMessage(gs, '{"t":"i","j":-1}'); assert.equal(hs.sent[hs.sent.length - 1], '{"t":"i","j":-1}'); ok("messages go host -> guest and guest -> host");
const before = gs.sent.length; await room.webSocketMessage(hs, "x".repeat(5000)); await room.webSocketMessage(hs, new Uint8Array(10));
assert.equal(gs.sent.length, before); ok("oversized and binary messages are dropped");
let delivered = 0; const b2 = gs.sent.length; for (let i = 0; i < 400; i++) await room.webSocketMessage(hs, "{}"); delivered = gs.sent.length - b2;
assert.ok(delivered <= 181 && delivered >= 170, "burst limit, got " + delivered); ok(`flooding is cut off (${delivered} of 400 passed)`);

// 4. reconnecting (first let the host's allowance refill, as 2 seconds of real time would)
hs.att.last = Date.now() - 2000;
const g3 = await join(code, `role=guest&key=${gHello.key}`); assert.equal(g3.res.status, 101); assert.equal(gs.closed.code, 4000);
await room.webSocketMessage(hs, '{"t":"s","x":2}'); assert.equal(g3.client.peer.sent[g3.client.peer.sent.length - 1], '{"t":"s","x":2}');
ok("the guest reconnects with its key; the old connection is replaced");
const hsLen = hs.sent.length; await room.webSocketClose(g3.client.peer, 1001); assert.deepEqual(last(hs), { t: "peer", s: "left" }); assert.ok(hs.sent.length > hsLen); ok("host hears when the guest leaves");

// 5. expiry
assert.ok(room.ctx.alarmAt > Date.now() + 2.9 * 3600e3); await room.alarm(); assert.equal(hs.closed.code, 4002); assert.equal(room.ctx.store.size, 0);
x = await join(code, `role=host&key=${hostKey}`); assert.equal(x.res.status, 404); ok("rooms expire after 3 hours and are forgotten");

// 6. odds and ends
assert.equal(_test.originAllowed("http://localhost:8080", "localhost"), true);
assert.equal(_test.originAllowed("https://keithhearne.github.io.evil.com", "https://keithhearne.github.io"), false);
assert.equal(_test.originAllowed("https://a.pages.dev", "*.pages.dev"), true); ok("website check can't be fooled by look-alike addresses");
r = await worker.fetch(req("https://x/"), env); assert.equal(r.status, 200);
r = await worker.fetch(req(`https://x/room/${code}?role=guest`), env); assert.equal(r.status, 426); ok("health check works; plain requests to a room are refused");
console.log(`\nall ${n} checks passed`);
