/* Crops the UI can offer. The list of crop_ids comes from the data release catalogue
 * (`scope.available_crop_ids`); this file only adds how each one is drawn and named.
 * A crop_id with no entry here is still shown, with the unknown picture and its id. */

export type PlantArt = 'berseem' | 'maize' | 'wheat' | 'sorghum' | 'unknown';
export type Purpose = 'forage' | 'grain';

export interface CropView { crop_id: string; plant: PlantArt; purpose: Purpose | null }

const KNOWN: Record<string, CropView> = {
  berseem: { crop_id: 'berseem', plant: 'berseem', purpose: 'forage' },
  grain_maize: { crop_id: 'grain_maize', plant: 'maize', purpose: 'grain' },
  wheat: { crop_id: 'wheat', plant: 'wheat', purpose: 'grain' },
  grain_sorghum: { crop_id: 'grain_sorghum', plant: 'sorghum', purpose: 'grain' },
};

export function cropView(cropId: string): CropView {
  return KNOWN[cropId] ?? { crop_id: cropId, plant: 'unknown', purpose: null };
}

/** Group catalogue crop_ids by plant: one picture per plant, purposes asked only if a plant has several. */
export function plantsFrom(cropIds: string[]): { plant: PlantArt; options: CropView[] }[] {
  const order: PlantArt[] = ['berseem', 'maize', 'wheat', 'sorghum', 'unknown'];
  const groups = new Map<PlantArt, CropView[]>();
  for (const id of cropIds) {
    const v = cropView(id);
    groups.set(v.plant, [...(groups.get(v.plant) ?? []), v]);
  }
  return order.filter((p) => groups.has(p)).map((plant) => ({ plant, options: groups.get(plant)! }));
}

/** Berseem is cut several times: the fact asked first is its LAST cut (a protected date in UH-001). */
export const asksLastCut = (cropId: string | null) => cropId !== null && cropView(cropId).plant === 'berseem';
