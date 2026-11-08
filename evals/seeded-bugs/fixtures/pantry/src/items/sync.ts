import { api } from "../api";
import { toast } from "../toast";

export async function saveItem(item: { id: string; name: string }) {
  try {
    await api.save(item);
  } catch {}
  toast("Saved");
}
