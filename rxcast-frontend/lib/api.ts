 import type { InventoryItem, ForecastPoint } from "@/src/types";

export async function getInventory(): Promise<InventoryItem[]> {
  return [
    {
      ndc: "12345-6789",
      drug_name: "Tamiflu",
      on_hand: 50,
      on_order: 20,
      lead_time_days: 3,
      pred14_p50: 80,
      risk: true,
      suggested_po_qty: 40,
    },
    {
      ndc: "98765-4321",
      drug_name: "Amoxicillin",
      on_hand: 200,
      on_order: 0,
      lead_time_days: 5,
      pred14_p50: 150,
      risk: false,
      suggested_po_qty: 0,
    },
  ];
}

export async function getForecast(ndc: string): Promise<ForecastPoint[]> {
  return [
    { date: "2025-09-20", p05: 5, p50: 10, p95: 15 },
    { date: "2025-09-21", p05: 6, p50: 12, p95: 18 },
    { date: "2025-09-22", p05: 7, p50: 14, p95: 20 },
  ];
}

export async function postPurchaseOrder(
  ndc: string,
  qty: number
): Promise<{ status: string }> {
  console.log(`Pretend submitted PO for ${ndc}, qty ${qty}`);
  return { status: "ok (mock)" };
}
