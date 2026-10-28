# Hoops 4 Life 2P: room server

A Cloudflare Worker that hands out room codes, and one Durable Object per room that passes messages between
the two phones over secure WebSockets. It doesn't read the game messages; it only decides who may join and
drops anything too big or too fast.

## How phones use it
- **Host:** `POST /new` returns `{ code, hostKey }`, e.g. `{ "code": "K7QWM", ... }`. The host then opens
  `wss://<worker>/room/K7QWM?role=host&key=<hostKey>`.
- **Guest:** opens `wss://<worker>/room/K7QWM?role=guest`. The first guest gets the guest seat and a key
  (in the `hello` message) to reconnect with: `...&key=<guestKey>`.
- **Server messages:**
  - `{ "t": "hello", "role", "key", "peer": true|false }` when a phone joins
  - `{ "t": "peer", "s": "joined" | "left" }` when the other phone arrives or goes
  - everything else is the other phone's own messages, passed on unchanged

## Safety rules
- Only the game's own website (`ALLOWED_ORIGINS` in `wrangler.jsonc`) can make or join rooms
- Codes are 5 characters (about 28 million combinations); a code only works once it's been made with `/new`
- Two seats only. The host seat needs the host key; the guest seat belongs to the first phone that takes it
- Messages over 4 KB, binary messages and floods (over about 90 a second) are dropped
- Rooms delete themselves 3 hours after they're made
- No names, chat or personal data pass through the server

## Deploying
Cloudflare Workers Builds watches this repository: root directory `server`, deploy command `npx wrangler deploy`,
production branch `main`. Every push to `main` that changes `server/` redeploys it.

## Tests
`node test/rooms.test.mjs` runs the server against stand-ins for Cloudflare's parts (17 checks).
