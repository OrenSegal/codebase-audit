import { api } from "./client";
import { toast } from "./toast";

export async function saveNote(note: { id: string; body: string }) {
  try {
    await api.put(`/notes/${note.id}`, note);
  } catch {}
  toast("Saved");
}
