# Hoops 4 Life 2P

The two-phone edition of [Hoops 4 Life](https://github.com/keithhearne/hoops-4-life): the same game, being developed so Zackie and Keelan can play each other on two phones, at home, on mobile data or travelling.

## Plan
- One phone hosts the game, the other joins with a short room code
- A small Cloudflare Worker with a Durable Object per game room passes messages between the phones over secure WebSockets (`wss://`)
- The host phone is the referee (scores, blocks, steals); the guest sends its controls and smooths what it sees
- "Reconnecting…" pause when the signal drops (tunnels, switching masts)

## Branches
- `main`: what the GitHub Pages site serves
- `dev`: work in progress; merged to `main` when it's ready to try on the phones

## Living next to Hoops 4 Life
Both games are on keithhearne.github.io, so this one has its own name ("Hoops 4 Life 2P"), its own offline cache (`hoops4life2p-…`) and its own save (`hoops4life2p`). The first time it opens it copies the boys' progress, prizes, players and kits from Hoops 4 Life.

## Source
`source/game-source.html` is the master file (`TEST_UNLOCK=true` for previews). Build the site with
`python3 -I source/tools/build_site.py <source with TEST_UNLOCK=false> . <version> "Hoops 4 Life 2P" hoops4life2p`.

## Sound credits
The crowd, whistle, ball, rim and backboard sounds are real recordings released as CC0 (public domain) on [Freesound](https://freesound.org); see the credits in the Hoops 4 Life README.
