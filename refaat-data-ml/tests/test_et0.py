"""Run without any NASA files; tests the public climate calculation directly."""
import math
import unittest
from datetime import date

from climate_data.et0 import calculate_daily_et0, extraterrestrial_radiation, saturation_pressure


class DailyET0Tests(unittest.TestCase):
    weather = dict(day=date(2001,1,1), tmax_c=22.83,tmin_c=7.15,tdew_c=1.95,rh_percent=49.49,
                   wind2_m_s=1.73,solar_mj_m2_day=11.15,pressure_kpa=101.35,latitude=31.1,elevation_m=4.96)

    def test_first_canonical_day_and_separate_sensitivities(self):
        result = calculate_daily_et0(**self.weather)
        self.assertAlmostEqual(result.et0_mm_day, 2.7039757858768434, places=12)
        self.assertAlmostEqual(result.et0_rhmean_approx_mm_day, 2.3962955486146678, places=12)
        self.assertEqual(result.et0_mm_day, result.et0_without_cloud_floor_mm_day)
        cloud = calculate_daily_et0(**{**self.weather,"solar_mj_m2_day":1.0})
        self.assertLess(cloud.rs_over_rso, .3)
        self.assertNotEqual(cloud.et0_mm_day, cloud.et0_without_cloud_floor_mm_day)

    def test_published_fao_examples_via_public_implementation(self):
        self.assertAlmostEqual(saturation_pressure(24.5), 3.075, delta=.002)
        self.assertAlmostEqual(extraterrestrial_radiation(-20,246), 32.2, delta=.1)
        # FAO-56 Example 18 supplies RH extrema and sunshine duration. Translate ea into
        # its mathematically equivalent dewpoint to exercise the released dewpoint API.
        ea = (saturation_pressure(12.3)*.84 + saturation_pressure(21.5)*.63)/2
        ratio = math.log(ea/.6108)
        dew = 237.3 * ratio / (17.27 - ratio)
        day = date(2001,7,6)  # day of year 187
        phi = math.radians(50.8)
        declination = .409*math.sin(2*math.pi*187/365-1.39)
        daylight = 24/math.pi*math.acos(-math.tan(phi)*math.tan(declination))
        radiation = (.25+.5*9.25/daylight)*extraterrestrial_radiation(50.8,187)
        result = calculate_daily_et0(day=day,tmax_c=21.5,tmin_c=12.3,tdew_c=dew,rh_percent=73.5,
                                     wind2_m_s=(10/3.6)*4.87/math.log(67.8*10-5.42),solar_mj_m2_day=radiation,
                                     pressure_kpa=101.3*((293-.0065*100)/293)**5.26,latitude=50.8,elevation_m=100)
        self.assertAlmostEqual(result.et0_mm_day,3.88,delta=.04)

    def test_invalid_and_missing_public_inputs(self):
        for key,value in (("pressure_kpa",None),("tdew_c",float("nan")),("rh_percent",-1),
                          ("wind2_m_s",-1),("tmin_c",23.1),("latitude",90),("day","2001-01-01")):
            with self.subTest(key=key), self.assertRaises(ValueError):
                calculate_daily_et0(**{**self.weather,key:value})

if __name__ == "__main__":
    unittest.main()
