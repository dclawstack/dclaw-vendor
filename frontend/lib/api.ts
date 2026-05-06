const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api';

export async function evaluateVendor(vendor_name: string, category: string) {
  const res = await fetch(`${API_BASE}/evaluations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ vendor_name, category }),
  });
  if (!res.ok) throw new Error('Failed to evaluate vendor');
  return res.json();
}

export async function getAlternatives(evaluationId: string) {
  const res = await fetch(`${API_BASE}/evaluations/${evaluationId}/alternatives`);
  if (!res.ok) throw new Error('Failed to fetch alternatives');
  return res.json();
}
