import { CROP_ART, ICON } from './art';
import type { PlantArt } from '../domain/catalogue';

export function Icon({ name, className }: { name: string; className?: string }) {
  return (
    <svg className={`i-${name}${className ? ` ${className}` : ''}`} viewBox="0 0 36 36" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth={2.2}
      strokeLinecap="round" strokeLinejoin="round" dangerouslySetInnerHTML={{ __html: ICON[name] ?? ICON.plan }} />
  );
}

export function CropArt({ plant }: { plant: PlantArt }) {
  return <svg viewBox="0 0 110 120" aria-hidden="true" dangerouslySetInnerHTML={{ __html: CROP_ART[plant] ?? CROP_ART.unknown }} />;
}
