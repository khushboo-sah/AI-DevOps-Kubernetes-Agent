import { createClient } from "@insforge/sdk";

const baseUrl =
  process.env.NEXT_PUBLIC_INSFORGE_BASE_URL ??
  "https://wznstw3m.eu-central.insforge.app";
const anonKey = process.env.NEXT_PUBLIC_INSFORGE_ANON_KEY;

if (!anonKey) {
  throw new Error(
    "NEXT_PUBLIC_INSFORGE_ANON_KEY is missing. Copy frontend/.env.example to frontend/.env.local and set your InsForge anon key.",
  );
}

export const insforge = createClient({
  baseUrl,
  anonKey,
});
