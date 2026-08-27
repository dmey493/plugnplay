/**
 * Short room-code generator for the phone-as-remote pairing flow.
 *
 * The alphabet deliberately drops visually ambiguous glyphs (no I/O/0/1)
 * so a teacher who reads "RX7K" off the projection won't type "RXIK" or
 * "RX7K0" on their phone. 32 chars × 4 positions = ~1.05M combinations.
 * Collisions are checked against the caller's "in-use" set on every
 * mint; in the unlikely event of a hit we retry up to a hard cap.
 *
 * Centralised here so the same alphabet is used everywhere — server-side
 * generation, client-side validation/formatting, and any future
 * collision-rate analytics all agree on what a "valid" code looks like.
 */

/** Chars used in room codes. 32 entries; powers of 2 are nice for entropy
 *  but the real win is dropping `I`, `O`, `0`, `1` so codes are
 *  unambiguous when read off a projector by a tired teacher. */
export const ROOM_CODE_ALPHABET =
  "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" as const;

/** Length of a room code. Short enough to type one-handed, long enough
 *  that brute-forcing live rooms is not a thing. */
export const ROOM_CODE_LENGTH = 4;

/** Generate a fresh room code. Pass the set of currently-live codes so we
 *  can avoid collisions; the caller is responsible for atomically reading
 *  the live set + inserting the new code. */
export function generateRoomCode(isInUse: (code: string) => boolean): string {
  // Hard cap on regenerations. At 1.05M combos and (say) 10k live rooms
  // the collision rate is ~1%, so 50 attempts gives a vanishing miss
  // probability. If we ever blow this cap, something else is broken.
  for (let attempt = 0; attempt < 50; attempt++) {
    const code = mintOne();
    if (!isInUse(code)) return code;
  }
  throw new Error("Failed to mint a unique room code after 50 attempts");
}

/** Single-shot code mint. Exported for tests; production should go through
 *  `generateRoomCode` so collisions get retried. */
export function mintOne(): string {
  let out = "";
  for (let i = 0; i < ROOM_CODE_LENGTH; i++) {
    out += ROOM_CODE_ALPHABET[Math.floor(Math.random() * ROOM_CODE_ALPHABET.length)];
  }
  return out;
}

/** Normalise user-typed codes: uppercase, strip whitespace, allow only
 *  alphabet chars. Returns the normalised string regardless of validity
 *  so the caller can pass it straight to `isValidRoomCode`. */
export function normaliseRoomCode(raw: string): string {
  return (raw || "")
    .toUpperCase()
    .split("")
    .filter((ch) => ROOM_CODE_ALPHABET.includes(ch as (typeof ROOM_CODE_ALPHABET)[number]))
    .join("");
}

/** True if `code` is exactly the right length and contains only alphabet
 *  chars. Does NOT check whether the room exists — that's the caller's
 *  job against the live store. */
export function isValidRoomCode(code: string): boolean {
  if (code.length !== ROOM_CODE_LENGTH) return false;
  for (const ch of code) {
    if (!ROOM_CODE_ALPHABET.includes(ch as (typeof ROOM_CODE_ALPHABET)[number])) {
      return false;
    }
  }
  return true;
}
