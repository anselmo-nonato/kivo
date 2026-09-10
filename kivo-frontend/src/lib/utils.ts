export function cleanUserNotes(rawNotes?: string | null): string {
  if (!rawNotes) return "";
  return rawNotes.replace(/\[transfer_direction:[^\]]+\]/g, "").trim();
}

export function formatCurrency(value: number | string | undefined | null): string {
  const num = typeof value === "string" ? parseFloat(value) : value || 0;
  return `R$ ${num.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}
