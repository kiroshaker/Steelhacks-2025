import type { InventoryItem, ForecastPoint } from "@/src/types";

// Shape of the backend JSON response. Keep minimal and widen if you add
// fields later.
type BackendResponse = {
  forecast_dates: string[];
  predicted_demand: number[];
  status: string;
  confidence?: number;
  suggested_po_qty?: number;
  at_risk?: boolean;
};

// Read the backend URL from the environment so we can configure it at build
// or deploy time. In Next.js, `NEXT_PUBLIC_` vars are embedded into the
// client bundle at build time. We provide a fallback for local dev and when
// running in the browser without the env var set.
const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  (typeof window !== "undefined"
    ? // When running in the browser, default to the same origin (useful if
      // you proxy the backend under the same domain) or localhost port 8080.
      `${window.location.protocol}//${window.location.host}`
    : // Server-side fallback (when building/SSR) => localhost dev backend
      "http://localhost:8080");

// This is a shared cache to store the API response so we don't have to call it twice.
// typed as `any` because backend returns a plain JSON object; narrow if you
// add an OpenAPI/TypeScript client later.
let apiDataCache: BackendResponse | null = null;

/**
 * The new central function that calls your live backend API.
 */
async function getApiData(): Promise<BackendResponse> {
  // If we already have the data, return it from the cache.
  if (apiDataCache !== null) {
    return apiDataCache;
  }

  try {
    const response = await fetch(`${BACKEND_URL}/predict`);
    if (!response.ok) {
      throw new Error(`API call failed with status: ${response.status}`);
    }
    const data = (await response.json()) as BackendResponse;
    apiDataCache = data; // Store the successful response in the cache
    return data;
  } catch (error) {
    console.error("Failed to fetch data from backend:", error);
    // Return a default error state if the API fails
    const fallback: BackendResponse = {
      status: "Error: API connection failed",
      forecast_dates: [],
      predicted_demand: [],
    };
    return fallback;
  }
}

/**
 * This function now uses the live API data to build the inventory list.
 */
export async function getInventory(): Promise<InventoryItem[]> {
  const data: BackendResponse = await getApiData();

  // Compute total predicted demand and suggested PO per your formula:
  // suggested_po_qty = max(0, totalPred - on_hand + 20)
  const on_hand = 50; // demo inventory value for Tamiflu
  const totalPred = Array.isArray(data.predicted_demand)
    ? data.predicted_demand.reduce((a: number, b: number) => a + b, 0)
    : 0;
  const suggested = totalPred - on_hand + 20;
  const suggested_po_qty = suggested > 0 ? suggested : 0;

  const tamifluItem: InventoryItem = {
    ndc: "00004-0800-85",
    drug_name: "Tamiflu (Oseltamivir)",
    on_hand,
    on_order: 0,
    lead_time_days: 3,
    pred14_p50: totalPred,
    // Risk when on_hand - predicted_demand <= 20
    risk: on_hand - totalPred <= 20,
    suggested_po_qty,
  };

  return [tamifluItem];
}

/**
 * This function now uses the live API data to build the forecast chart.
 */
export async function getForecast(ndc: string): Promise<ForecastPoint[]> {
  // We only get data for Tamiflu from the backend.
  if (!ndc.startsWith("00004")) {
    return [];
  }

  const data: BackendResponse = await getApiData();

  // Transform the backend's forecast data into the format the frontend chart expects.
  const forecastDates = Array.isArray(data.forecast_dates) ? data.forecast_dates : [];
  const predicted = Array.isArray(data.predicted_demand) ? data.predicted_demand : [];
  return forecastDates.map((date: string, index: number) => {
    const p50: number = typeof predicted[index] === "number" ? predicted[index] : 0;
    return {
      date: date,
      p05: Math.round(p50 * 0.75), // Create approximate confidence bands
      p50: p50,
      p95: Math.round(p50 * 1.25),
    };
  });
}

/**
 * This function remains mocked for the demo, as the backend does not
 * have an endpoint for submitting purchase orders.
 */
export async function postPurchaseOrder(
  ndc: string,
  qty: number
): Promise<{ status: string }> {
  console.log(`Pretend submitted PO for ${ndc}, qty ${qty}`);
  return { status: "ok (mock)" };
}
