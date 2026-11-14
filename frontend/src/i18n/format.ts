export type Locale = 'ar' | 'en';
export type Bi = { ar: string; en: string };

const AR_DIGITS = '٠١٢٣٤٥٦٧٨٩';
export const MONTHS: Record<Locale, string[]> = {
  ar: ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'],
  en: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
};

/** Numbers are shown as digits (Arabic-Indic in Arabic); month names stay words. */
export const num = (n: number | string, loc: Locale) => (loc === 'ar' ? String(n).replace(/[0-9]/g, (d) => AR_DIGITS[+d]) : String(n));

export function parseIso(isoDate: string) {
  const [y, m, d] = isoDate.split('-').map(Number);
  return { y, m, d };
}

/** "20 May 2027" / "٢٠ مايو ٢٠٢٧"; plain text, wrap in <bdi> when placed inside mixed text. */
export function dateText(isoDate: string, loc: Locale, opts: { noYear?: boolean } = {}) {
  const { y, m, d } = parseIso(isoDate);
  return opts.noYear ? `${num(d, loc)} ${MONTHS[loc][m - 1]}` : `${num(d, loc)} ${MONTHS[loc][m - 1]} ${num(y, loc)}`;
}

export const pick = (b: Bi, loc: Locale) => b[loc];
