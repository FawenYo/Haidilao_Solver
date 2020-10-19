#!/usr/bin/env python3

"""
    Maze Solver

    Usage:
        python solve.py <maze-image-in>

    Output:
        An image of the original maze with the solution path drawn in.

    Note:
        This program relies on colors.
        For example, assumes explorable space is WHITE and the maze is BLACK.
"""

import os
import sys
import math
import logging
from PIL import Image

logging.basicConfig(
    level=logging.INFO, format="[%(levelname)s]: %(asctime)-15s %(message)s"
)


class Solver:
    """
    file_in = Input maze image filename.
    image   = Maze image object.
    pixels  = Maze image pixel array.
    """

    def __init__(self, maze):
        # Colors.
        self.COLOR_MAP = {
            (0, 255, 0): "GREEN",
            (255, 0, 0): "RED",
            (0, 0, 255): "BLUE",
            (255, 255, 255): "WHITE",
            (0, 0, 0): "BLACK",
        }
        self.COLOR_RED = (255, 0, 0)
        self.COLOR_GREEN = (0, 255, 0)
        self.COLOR_BLUE = (0, 0, 255)
        self.COLOR_WHITE = (255, 255, 255)
        self.COLOR_BLACK = (0, 0, 0)
        self.START_COLOR = self.COLOR_GREEN
        self.END_COLOR = self.COLOR_RED
        self.FRONTIER_COLOR = self.COLOR_GREEN
        self.memoized_color_map = {}

        # Output file.
        self.DIR_OUT = "out"
        self.file_in = maze
        ext = maze.split(".")[-1]
        self.file_out = os.path.join(
            self.DIR_OUT, os.path.basename(maze).split(".")[0] + "." + ext
        )

        # Output parameters.
        self.SNAPSHOT_FREQ = 20000  # Save an image every SNAPSHOT_FREQ steps.

        # BFS parameters.
        self.tmp_dir = "tmp"
        self.iterations = 0

        # Load image.
        self.image = Image.open(self.file_in)
        logging.info(
            "Loaded image '{0}' ({1} = {2} pixels).".format(
                self.file_in, self.image.size, self.image.size[0] * self.image.size[1]
            )
        )
        self.image = self.image.convert("RGB")
        self.pixels = self.image.load()
        self.START = self._find_start()
        self.END = self._find_end()
        self._save_image(self.image, "{0}/start_end.jpg".format(self.tmp_dir))
        self._clean_image()
        self._draw_square(self.START, self.START_COLOR)
        self._draw_square(self.END, self.END_COLOR)
        self._save_image(self.image, "{0}/clean.jpg".format(self.tmp_dir))

    def solve(self):
        logging.info("Solving...")
        path = self._bfs(self.START, self.END)
        if path is None:
            logging.error("No path found.")
            self._draw_x(self.START)
            self._draw_x(self.END)
            self.image.save(self.file_out)
            sys.exit(1)

        # Draw solution path.
        for position in path:
            x, y = position
            self.pixels[x, y] = self.COLOR_RED

        self.image.save(self.file_out)
        logging.info("Solution saved as '{0}'.".format(self.file_out))

    """
    Purify pixels to either pure black or white, except for the start/end pixels.
    """

    def _clean_image(self):
        logging.info("Cleaning image...")
        x, y = self.image.size
        for i in range(x):
            for j in range(y):
                if (i, j) == self.START:
                    self.pixels[i, j] == self.START_COLOR
                    continue
                if (i, j) == self.END:
                    self.pixels[i, j] == self.END_COLOR
                    continue
                closest_color = self._find_closest_color(self.pixels[i, j])
                for color in [self.COLOR_WHITE, self.COLOR_BLACK]:
                    if closest_color == color:
                        self.pixels[i, j] = color
                for color in [self.START_COLOR, self.END_COLOR]:
                    if closest_color == color:
                        self.pixels[i, j] = self.COLOR_WHITE

    def _find_closest_color(self, color, memoize=False):
        colors = list(self.COLOR_MAP.keys())
        if color in self.memoized_color_map and memoize:
            return color
        closest_color = sorted(colors, key=lambda c: distance(c, color))[0]
        if memoize:
            self.memoized_color_map[color] = closest_color
        return closest_color

    def _find_color_center(self, color):
        found_color = False
        x_min, x_max, y_min, y_max = (
            float("inf"),
            float("-inf"),
            float("inf"),
            float("-inf"),
        )
        x, y = self.image.size
        for i in range(x):
            for j in range(y):
                code = self._find_closest_color(self.pixels[i, j])
                if code == color:
                    found_color = True
                    x_min, y_min = min(x_min, i), min(y_min, j)
                    x_max, y_max = max(x_max, i), max(y_max, j)
        if not found_color:
            return (0, 0), False
        return (mean([x_min, x_max]), mean([y_min, y_max])), True

    def _find_start(self):
        logging.info("Finding START point...")
        # start, ok = self._findColorCenter(self.START_COLOR)
        start, ok = [(385, 985), True]
        if not ok:
            logging.error("Oops, failed to find start point in maze!")
        self._draw_square(start, self.START_COLOR)
        logging.info(start)
        return start

    def _find_end(self):
        logging.info("Finding END point...")
        # end, ok = self._findColorCenter(self.END_COLOR)
        end, ok = [(399, 27), True]
        if not ok:
            logging.error("Oops, failed to find end point in maze!")
        self._draw_square(end, self.END_COLOR)
        logging.info(end)
        return end

    def _draw_x(self, pos, color=(0, 0, 255)):
        x, y = pos
        d = 10
        for i in range(-d, d):
            self.pixels[x + i, y] = color
        for j in range(-d, d):
            self.pixels[x, y + j] = color

    def _draw_square(self, pos, color=(0, 0, 255)):
        x, y = pos
        d = 1
        for i in range(-d, d):
            for j in range(-d, d):
                self.pixels[x + i, y + j] = color

    def _in_bounds(self, dim, x, y):
        mx, my = dim
        if x < 0 or y < 0 or x >= mx or y >= my:
            return False
        return True

    def _is_white(self, pixels, pos):
        i, j = pos
        r, g, b = pixels[i, j]
        th = 240
        if (
            pixels[i, j] == self.COLOR_WHITE
            or pixels[i, j] == 0
            or (r > th and g > th and b > th)
            or pixels[i, j] == self.END_COLOR
        ):
            return True

    # Left, Down, Right, Up
    def _get_neighbours(self, pos):
        x, y = pos
        return [(x - 1, y), (x, y - 1), (x + 1, y), (x, y + 1)]

    def _save_image(self, img, path):
        img.save(path)

    """
    Breadth-first search.
    """

    def _bfs(self, start, end):
        # Copy of maze to hold temporary search state.
        image = self.image.copy()
        pixels = image.load()

        self.iterations = 0
        seen = set()
        q = [[start]]
        img = 0

        while len(q) != 0:
            if self.iterations > 0 and self.iterations % self.SNAPSHOT_FREQ == 0:
                logging.info("...")
            path = q.pop(0)
            pos = path[-1]
            seen.add(pos)

            if pos == end:
                # Draw solution path.
                for position in path:
                    x, y = position
                    pixels[x, y] = self.COLOR_RED
                for i in range(10):
                    self._save_image(image, "{0}/{1:05d}.jpg".format(self.tmp_dir, img))
                    img += 1
                logging.info(
                    "Found a path after {0} iterations.".format(self.iterations)
                )
                image.show("Solution Path")
                return path

            for neighbour in self._get_neighbours(pos):
                x, y = neighbour
                if (
                    (x, y) not in seen
                    and self._in_bounds(image.size, x, y)
                    and self._is_white(pixels, (x, y))
                ):
                    pixels[x, y] = self.FRONTIER_COLOR
                    new_path = list(path)
                    new_path.append(neighbour)
                    q += [new_path]
            if self.iterations % self.SNAPSHOT_FREQ == 0:
                self._save_image(image, "{0}/{1:05d}.jpg".format(self.tmp_dir, img))
                img += 1
            self.iterations += 1
        print("Returning after ", self.iterations, " iterations.")
        return None


def mean(numbers):
    return int(sum(numbers)) / max(len(numbers), 1)


def distance(c1, c2):
    (r1, g1, b1) = c1
    (r2, g2, b2) = c2
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)


if __name__ == "__main__":
    solver = Solver(sys.argv[1])
    solver.solve()
