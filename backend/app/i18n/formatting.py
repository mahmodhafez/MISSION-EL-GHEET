"""Dates and numbers for the two template variants (backend design §7.4).
text: digits (Arabic-Indic in Arabic), month names as words. speech: numbers spelled out (Egyptian Arabic words),
so pre-generated audio never reads digits. Arabic wording is a DRAFT for native Egyptian review."""
from __future__ import annotations

from datetime import date

AR_DIGITS = "٠١٢٣٤٥٦٧٨٩"
MONTHS = {
    "ar-EG": ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"],
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
}
AR_ONES = ["", "واحد", "اتنين", "تلاتة", "أربعة", "خمسة", "ستة", "سبعة", "تمانية", "تسعة", "عشرة",
           "حداشر", "اتناشر", "تلاتاشر", "أربعتاشر", "خمستاشر", "ستاشر", "سبعتاشر", "تمنتاشر", "تسعتاشر"]
AR_TENS = {20: "عشرين", 30: "تلاتين", 40: "أربعين", 50: "خمسين", 60: "ستين", 70: "سبعين", 80: "تمانين", 90: "تسعين"}
EN_ONES = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen",
           "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
EN_TENS = {20: "twenty", 30: "thirty", 40: "forty", 50: "fifty", 60: "sixty", 70: "seventy", 80: "eighty", 90: "ninety"}


def digits(n: int | str, locale: str) -> str:
    s = str(n)
    return "".join(AR_DIGITS[int(c)] if c.isdigit() else c for c in s) if locale == "ar-EG" else s


def words(n: int, locale: str) -> str:
    """0 < n < 100 as words; Egyptian Arabic puts units before tens ("سبعة وعشرين")."""
    if not 0 < n < 100:
        return digits(n, locale)
    if locale == "ar-EG":
        if n < 20:
            return AR_ONES[n]
        t, u = n - n % 10, n % 10
        return AR_TENS[t] if u == 0 else f"{AR_ONES[u]} و{AR_TENS[t]}"
    if n < 20:
        return EN_ONES[n]
    t, u = n - n % 10, n % 10
    return EN_TENS[t] if u == 0 else f"{EN_TENS[t]}-{EN_ONES[u]}"


def year_words(y: int, locale: str) -> str:
    if 2000 < y < 2100:
        return f"ألفين {words(y - 2000, locale)}" if locale == "ar-EG" else f"twenty {words(y - 2000, locale)}"
    return digits(y, locale)


def date_text(iso: str, locale: str, year: bool = True) -> str:
    d = date.fromisoformat(iso)
    out = f"{digits(d.day, locale)} {MONTHS[locale][d.month - 1]}"
    return f"{out} {digits(d.year, locale)}" if year else out


def date_speech(iso: str, locale: str, year: bool = True) -> str:
    d = date.fromisoformat(iso)
    out = f"{words(d.day, locale)} {MONTHS[locale][d.month - 1]}" if locale == "ar-EG" else f"{MONTHS[locale][d.month - 1]} {words(d.day, locale)}"
    return f"{out} {year_words(d.year, locale)}" if year else out


def days(n: int, locale: str, spoken: bool) -> str:
    """Count of days with the right Arabic plural (3–10 أيام, else يوم)."""
    num = words(n, locale) if spoken else digits(n, locale)
    if locale == "ar-EG":
        if spoken and 3 <= n <= 10:
            num = {7: "سبع", 8: "تمن", 3: "تلات", 4: "أربع", 5: "خمس", 6: "ست", 9: "تسع", 10: "عشر"}[n]
        return f"{num} {'أيام' if 3 <= n <= 10 else 'يوم'}"
    return f"{num} day{'s' if n != 1 else ''}"
