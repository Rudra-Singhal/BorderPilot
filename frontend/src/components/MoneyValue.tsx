const LOCALE_BY_CURRENCY: Record<string, string> = {
  USD: "en-US",
  EUR: "de-DE",
  GBP: "en-GB",
  INR: "en-IN",
  SEK: "sv-SE",
  SGD: "en-SG",
  COP: "es-CO",
};

export function MoneyValue({
  value,
  currency = "USD",
  className,
}: {
  value: number;
  currency?: string;
  className?: string;
}) {
  const locale = LOCALE_BY_CURRENCY[currency] ?? "en-US";
  const formatted = value.toLocaleString(locale, {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  });
  return <span className={className} style={{ fontVariantNumeric: "tabular-nums" }}>{formatted}</span>;
}
