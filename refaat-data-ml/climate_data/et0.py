"""Daily short-grass reference evapotranspiration: FAO-56 with ASCE Eq. 18.

The implementation preserves the archived daily equations. Inputs are in °C,
kPa, m/s at 2 m, MJ/m²/day, decimal degrees N and metres above sea level.
No missing input is imputed. The raw solar ratio is returned before bounding.
"""
from dataclasses import dataclass
from datetime import date
from math import acos, cos, exp, isfinite, pi, radians, sin, sqrt, tan

METHOD_VERSION = "fao56-dewpoint-asce-floor-v1"


@dataclass(frozen=True)
class DailyET0:
    et0_mm_day: float
    et0_rhmean_approx_mm_day: float
    et0_without_cloud_floor_mm_day: float
    rs_over_rso: float
    vpd_kpa: float


def saturation_pressure(temperature_c: float) -> float:
    """FAO-56 Eq. 11, kPa."""
    if temperature_c <= -237.3:
        raise ValueError("Temperature outside the supported vapour-pressure domain")
    return 0.6108 * exp(17.27 * temperature_c / (temperature_c + 237.3))


def extraterrestrial_radiation(latitude: float, day_of_year: int) -> float:
    """Return extraterrestrial radiation in MJ/m²/day using FAO-56 Eq. 21."""
    if not -90 < latitude < 90 or not 1 <= day_of_year <= 366:
        raise ValueError("Invalid latitude or day of year")
    phi = radians(latitude)
    distance = 1 + 0.033 * cos(2 * pi * day_of_year / 365)
    declination = 0.409 * sin(2 * pi * day_of_year / 365 - 1.39)
    sunset = acos(max(-1, min(1, -tan(phi) * tan(declination))))
    geometry = sunset * sin(phi) * sin(declination) + cos(phi) * cos(declination) * sin(sunset)
    return 24 * 60 / pi * 0.0820 * distance * geometry


def calculate_daily_et0(*, day: date, tmax_c: float, tmin_c: float, tdew_c: float,
                        rh_percent: float, wind2_m_s: float, solar_mj_m2_day: float,
                        pressure_kpa: float, latitude: float, elevation_m: float) -> DailyET0:
    """Compute three reference ET₀ pathways, the raw radiation ratio and VPD.

    The primary calculation uses measured-in-product dewpoint. RH mean is an
    explicitly separate sensitivity. G=0 for the daily calculation. A valid
    daily date and all inputs are required. Raises ValueError on invalid input.
    """
    inputs = (tmax_c, tmin_c, tdew_c, rh_percent, wind2_m_s, solar_mj_m2_day,
              pressure_kpa, latitude, elevation_m)
    if type(day) is not date or any(type(v) not in (int, float) or not isfinite(v) for v in inputs):
        raise ValueError("A calendar date and finite numeric weather inputs are required")
    if tmax_c < tmin_c or not 0 <= rh_percent <= 100:
        raise ValueError("Temperature extrema or relative humidity are invalid")
    if wind2_m_s < 0 or solar_mj_m2_day < 0 or pressure_kpa <= 0:
        raise ValueError("Invalid wind, radiation or surface pressure")

    mean_t = (tmax_c + tmin_c) / 2
    saturation = (saturation_pressure(tmax_c) + saturation_pressure(tmin_c)) / 2
    actual = saturation_pressure(tdew_c)
    slope = 4098 * saturation_pressure(mean_t) / (mean_t + 237.3) ** 2
    gamma = 0.000665 * pressure_kpa
    ra = extraterrestrial_radiation(latitude, day.timetuple().tm_yday)
    clear_sky = (0.75 + 0.00002 * elevation_m) * ra
    if clear_sky <= 0:
        raise ValueError("Nonpositive clear-sky radiation outside supported domain")
    ratio = solar_mj_m2_day / clear_sky
    bounded_ratio = max(0.3, min(1.0, ratio))
    net_shortwave = 0.77 * solar_mj_m2_day
    longwave_term = 4.903e-9 * ((tmax_c + 273.16) ** 4 + (tmin_c + 273.16) ** 4) / 2

    def flux(vapour_pressure: float, ratio_used: float) -> float:
        longwave = longwave_term * ((0.34 - 0.14 * sqrt(vapour_pressure)) * (1.35 * ratio_used - 0.35))
        net = net_shortwave - longwave
        result = (0.408 * slope * net + gamma * 900 / (mean_t + 273)
                  * wind2_m_s * (saturation - vapour_pressure)) / (slope + gamma * (1 + 0.34 * wind2_m_s))
        if not isfinite(result):
            raise ValueError("Non-finite ET0 calculation")
        return result

    return DailyET0(flux(actual, bounded_ratio), flux(saturation * rh_percent / 100, bounded_ratio),
                    flux(actual, min(1.0, ratio)), ratio, saturation - actual)
