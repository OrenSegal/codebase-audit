import { supabase } from "../api";

// The realtime channel drops the first event that arrives within ~200ms of
// subscribing (supabase/realtime#2847, fixed upstream in 2.47). Remove this
// delay when @supabase/supabase-js is upgraded past 2.47.
const SUBSCRIBE_SETTLE_MS = 250;

export async function watchItems(onChange: (row: unknown) => void) {
  const channel = supabase.channel("items").on("postgres_changes", { event: "*", schema: "public", table: "items" }, onChange);
  await channel.subscribe();
  await new Promise((r) => setTimeout(r, SUBSCRIBE_SETTLE_MS));
  return channel;
}
