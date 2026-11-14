import type { Bi } from './format';
import type { PlantArt, Purpose } from '../domain/catalogue';

/* UI chrome and draft farmer wording. Scientific explanations will come from backend templates (D4);
 * until then the result screens build their sentences from the planner's codes and params here.
 * Arabic is a draft for native Egyptian review. */

export const PLANT: Record<PlantArt, Bi & { def: string }> = {
  berseem: { ar: 'برسيم', en: 'Berseem', def: 'البرسيم' },
  // Maize is always "ذرة شامية" on screen: plain "ذرة" is ambiguous (maize or sorghum).
  maize: { ar: 'ذرة شامية', en: 'Maize', def: 'الذرة الشامية' },
  wheat: { ar: 'قمح', en: 'Wheat', def: 'القمح' },
  sorghum: { ar: 'ذرة رفيعة', en: 'Sorghum', def: 'الذرة الرفيعة' },
  rice: { ar: 'أرز', en: 'Rice', def: 'الأرز' },
  faba_bean: { ar: 'فول بلدي', en: 'Faba bean', def: 'الفول البلدي' },
  sugar_beet: { ar: 'بنجر سكر', en: 'Sugar beet', def: 'بنجر السكر' },
  cotton: { ar: 'قطن مصري', en: 'Egyptian cotton', def: 'القطن المصري' },
  unknown: { ar: 'لسه مش عارف', en: "I don't know yet", def: '' },
};

export const PURPOSE: Record<Purpose, Bi> = { forage: { ar: 'علف للمواشي', en: 'animal feed' }, grain: { ar: 'حبوب', en: 'grain' }, sugar: { ar: 'سكر', en: 'sugar' }, fibre: { ar: 'تيلة', en: 'fibre' } };

export const SEASON_KIND: Record<'winter' | 'summer', Bi> = { winter: { ar: 'شتوي', en: 'Winter' }, summer: { ar: 'صيفي', en: 'Summer' } };

export const UI = {
  back: { ar: 'رجوع', en: 'Back' },
  help: { ar: 'مساعدة', en: 'Help' },
  langSwitch: { ar: 'English', en: 'العربية' },
  repeat: { ar: 'تاني', en: 'Repeat' },
  stop: { ar: 'وقّف', en: 'Stop' },
  listen: { ar: 'اسمع', en: 'Listen' },
  talk: { ar: 'اتكلّم', en: 'Talk' },
  doneTalking: { ar: 'خلّصت', en: 'Done talking' },
  change: { ar: 'غيّر', en: 'Change' },
  yes: { ar: 'أيوه، صح', en: 'Yes, that is right' },
  next: { ar: 'التالي', en: 'Next' },
  cont: { ar: 'كمّل', en: 'Continue' },
  heard: { ar: 'سمعت', en: 'I heard' },
  practice: { ar: 'مثال تجريبي — مش بيانات حقيقية', en: 'Practice example, not real data' },
  devData: { ar: 'نتيجة تجريبية من المخطِّط (UH-001)', en: 'Dev data: planner export (UH-001)' },
  deviceVoice: { ar: 'صوت الموبايل', en: 'Device voice' },
  needsReview: { ar: 'محتاج مراجعة', en: 'Needs review' },
  moreCrops: { ar: 'محاصيل تانية', en: 'More crops' },
} satisfies Record<string, Bi>;

export const VOICE_STATE: Record<string, [Bi, Bi]> = {
  idle: [{ ar: 'دوس على الميكروفون واتكلّم', en: 'Tap the mic and talk' }, { ar: 'أو اختار من الصور', en: 'or tap a picture' }],
  speaking: [{ ar: 'بتكلّم دلوقتي…', en: 'Speaking…' }, { ar: 'دوس الميكروفون لو عايز ترد على طول', en: 'Tap the mic to answer now' }],
  listening: [{ ar: 'سامعك… اتكلّم', en: 'Listening… go ahead' }, { ar: 'دوس تاني لما تخلّص', en: 'Tap again when you finish' }],
  processing: [{ ar: 'بفهم كلامك…', en: 'Working out what you said…' }, { ar: '', en: '' }],
  nospeech: [{ ar: 'ماسمعتش حاجة', en: "I didn't hear anything" }, { ar: 'دوس الميكروفون تاني، أو اختار صورة', en: 'Tap the mic again, or tap a picture' }],
  notunderstood: [{ ar: 'مافهمتش كويس', en: "I didn't catch that" }, { ar: 'قولها تاني بطريقة تانية، أو اختار صورة', en: 'Say it another way, or tap a picture' }],
  denied: [{ ar: 'الميكروفون مقفول', en: 'Microphone is off' }, { ar: 'تقدر تختار بالصور', en: 'You can tap the pictures' }],
  unsupported: [{ ar: 'الميكروفون مش متاح هنا', en: 'Voice input is not available here' }, { ar: 'تقدر تختار بالصور', en: 'You can tap the pictures' }],
  asking: [{ ar: 'الموبايل هيسألك تسمح بالميكروفون', en: 'Your phone will ask to use the microphone' }, { ar: 'الكلام بيتبعت علشان يتفهم', en: 'Your words are sent to be understood' }],
  audiooff: [{ ar: 'الصوت مش شغال', en: 'Sound is not working' }, { ar: 'الصور والكلام المكتوب لسه موجودين', en: 'Pictures and text are still here' }],
  fallback: [{ ar: 'خلّينا نختار بالصور', en: "Let's use the pictures" }, { ar: 'الميكروفون لسه موجود', en: 'The mic is still here' }],
};
