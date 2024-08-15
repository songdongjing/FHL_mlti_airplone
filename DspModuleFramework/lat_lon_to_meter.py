import math
import numpy as np

CONSTANTS_RADIUS_OF_EARTH = 6371000.  # meters (m)


def XYtoGPS(x, y, ref_lat, ref_lon):
    x_rad = float(x) / CONSTANTS_RADIUS_OF_EARTH
    y_rad = float(y) / CONSTANTS_RADIUS_OF_EARTH
    c = math.sqrt(x_rad * x_rad + y_rad * y_rad)

    ref_lat_rad = math.radians(ref_lat)
    ref_lon_rad = math.radians(ref_lon)

    ref_sin_lat = math.sin(ref_lat_rad)
    ref_cos_lat = math.cos(ref_lat_rad)

    if abs(c) > 0:
        sin_c = math.sin(c)
        cos_c = math.cos(c)

        lat_rad = math.asin(cos_c * ref_sin_lat + (x_rad * sin_c * ref_cos_lat) / c)
        lon_rad = (ref_lon_rad + math.atan2(y_rad * sin_c, c * ref_cos_lat * cos_c - x_rad * ref_sin_lat * sin_c))

        lat = math.degrees(lat_rad)
        lon = math.degrees(lon_rad)

    else:
        lat = math.degrees(ref_lat)
        lon = math.degrees(ref_lon)

    return lat, lon


def GPStoXY(lat, lon, ref_lat, ref_lon):
    # input GPS and Reference GPS in degrees
    # output XY in meters (m) X:North Y:East
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    ref_lat_rad = math.radians(ref_lat)
    ref_lon_rad = math.radians(ref_lon)

    sin_lat = math.sin(lat_rad)
    cos_lat = math.cos(lat_rad)
    ref_sin_lat = math.sin(ref_lat_rad)
    ref_cos_lat = math.cos(ref_lat_rad)

    cos_d_lon = math.cos(lon_rad - ref_lon_rad)

    arg = np.clip(ref_sin_lat * sin_lat + ref_cos_lat * cos_lat * cos_d_lon, -1.0, 1.0)
    c = math.acos(arg)

    k = 1.0
    if abs(c) > 0:
        k = (c / math.sin(c))

    x = float(k * (ref_cos_lat * sin_lat - ref_sin_lat * cos_lat * cos_d_lon) * CONSTANTS_RADIUS_OF_EARTH)
    y = float(k * cos_lat * math.sin(lon_rad - ref_lon_rad) * CONSTANTS_RADIUS_OF_EARTH)

    return x, y

#     "task_area": [
# 		{
# 			"index": 0,
#             "task_area_point_alt": 0.0,
#             "task_area_point_lat": 23.327439513436268,
#             "task_area_point_lon": 120.87467193603516
#         },
#         {
# 			"index": 1,
#             "task_area_point_alt": 0.0,
#             "task_area_point_lat": 23.327754771531193,
#             "task_area_point_lon": 121.07242584228516
#         },
# 		{
# 			"index": 2,
#             "task_area_point_alt": 0.0,
#             "task_area_point_lat": 23.51362636346272,
#             "task_area_point_lon": 121.07242584228516
#         },
#         {
# 			"index": 3,
#             "task_area_point_alt": 0.0,
#             "task_area_point_lat": 23.51362636346272,
#             "task_area_point_lon": 120.87467193603516
#         }
#     ],
# # 0
#
# 120.87467193603516, 23.327439513436268
#
# 1
#
# 121.07242584228516, 23.327754771531193
#
#
# 2
#
# 121.07242584228516, 23.51362636346272
#
#
# 3
#
# 120.87467193603516, 23.51362636346272
