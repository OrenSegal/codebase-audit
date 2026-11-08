import { db } from "../api";

export async function handleStripeWebhook(req: { body: any }) {
  const event = req.body;
  if (event.type === "checkout.session.completed") {
    const userId = event.data.object.client_reference_id;
    const pack = event.data.object.metadata.scan_pack_size;
    const user = await db.from("profiles").select("scan_credits").eq("id", userId).single();
    await db.from("profiles").update({ scan_credits: user.data.scan_credits + Number(pack) }).eq("id", userId);
  }
  return { status: 200 };
}
