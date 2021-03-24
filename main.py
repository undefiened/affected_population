from math import ceil
from typing import List, Set

import numpy as np
import simplejson


class AffectedPopulationMap:
    def __init__(self, map: List[List[float]], pixels_per_km: float):
        self.pixels_per_km = pixels_per_km  # number of pixels in 1 km to compute the scale of the map
        self.km_per_pixel = 1 / self.pixels_per_km
        self.m_per_pixel = self.km_per_pixel * 1000

        self.map = np.array(map)

    @staticmethod
    def _bresenham_circle(r: int) -> Set:
        points = set()

        for y in range(-r, r + 1):
            for x in range(-r, r):
                if x * x + y * y <= r * r:
                    points.add((x, y))

        return points

    def _get_population(self, x: int, y: int) -> float:
        if x < 0 or x >= self.map.shape[0] or y < 0 or y >= self.map.shape[1]:
            return 0
        else:
            return self.map[x, y]

    def compute_affected_population_map(self, r: float) -> np.array:
        """
        Builds the affected population map
        :param r: Radius of the safety zone around the drone in meters
        :return: The affected population map
        """
        r_in_pix = ceil(r / self.m_per_pixel)
        affected_population_map = np.zeros_like(self.map)
        disk_offsets = self._bresenham_circle(r_in_pix)

        for x in range(affected_population_map.shape[0]):
            for y in range(affected_population_map.shape[1]):
                affected_population = 0
                for disk_offset in disk_offsets:
                    affected_population = affected_population + self._get_population(x + disk_offset[0], y + disk_offset[1])

                affected_population_map[x, y] = affected_population

            print('x = {}'.format(x))

        return affected_population_map


if __name__ == '__main__':
    with open('./data/map.json', 'r') as f:
        map = simplejson.load(f)
        obj = AffectedPopulationMap(map=map, pixels_per_km=131 / 2)
        affected_population_map = obj.compute_affected_population_map(200)

        with open('./data/affected_map.json', 'w') as aff_f:
            simplejson.dump(affected_population_map.tolist(), aff_f)
