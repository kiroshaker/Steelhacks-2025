export type InventoryItem = {
  ndc: string;
  drug_name: string;
  on_hand: number;
  on_order: number;
  lead_time_days: number;
  pred14_p50: number;
  risk: boolean;
  suggested_po_qty: number;
};

export type ForecastPoint = {
  date: string;
  p05: number;
  p50: number;
  p95: number;
}; 
