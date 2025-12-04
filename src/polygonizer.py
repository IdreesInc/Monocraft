# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

__all__ = [
	"PixelImage",
	"generatePolygons",
]

from enum import IntFlag


class PixelImage:
	"""Class for managing a pixel image.

	Each pixel is a 8-bit integer.
	It also store the position and size of the image, allowing easier operation.
	"""

	__slots__ = ["__data", "_x", "_y", "_w", "_h"]

	def __init__(self, src=None, *, x=0, y=0, width=0, height=0, data=None):
		if src is not None:
			self._x, self._y, self._w, self._h, self.__data = (
				src._x,
				src._y,
				src._w,
				src._h,
				bytearray(src.__data),
			)
			return
		if width < 0:
			raise ValueError("Width < 0")
		if height < 0:
			raise ValueError("Height < 0")

		self._x, self._y, self._w, self._h = x, y, width, height

		if data is not None:
			data = bytearray(data)
			if len(data) != width * height:
				raise ValueError(
					f"Data length mismatch (expected {width * height}, got {len(data)})"
				)
			self.__data = data
		else:
			self.__data = bytearray(width * height)

	@property
	def x(self):
		return self._x

	@property
	def y(self):
		return self._y

	@property
	def x_end(self):
		return self._x + self._w

	@property
	def y_end(self):
		return self._y + self._h

	@property
	def width(self):
		return self._w

	@property
	def height(self):
		return self._h

	@property
	def data(self):
		return bytes(self.__data)

	def __getitem__(self, key):
		"""Gets a pixel at (x, y).

		Defaults to 0 if out of bounds.
		"""
		x, y = key
		x -= self._x
		y -= self._y
		if x < 0 or x >= self._w or y < 0 or y >= self._h:
			return 0
		return self.__data[x + y * self._w]

	def __setitem__(self, key, value):
		"""Sets a pixel at (x, y).

		Do nothing if out of bounds.
		"""
		x, y = key
		x -= self._x
		y -= self._y
		if x < 0 or x >= self._w or y < 0 or y >= self._h:
			return
		self.__data[x + y * self._w] = value

	def __len__(self):
		return self._w * self._h

	def __str__(self):
		return "\n".join(
			" ".join(str(self[x, y]) for x in range(self.x, self.x_end))
			for y in range(self.y, self.y_end)
		)

	def __repr__(self):
		return (
			f"PixelImage(\n  x={self._x},\n"
			f"  y={self._y},\n"
			f"  width={self._w},\n"
			f"  height={self._h},\n"
			f"  data=bytes([\n    "
			+ ",\n    ".join(
				", ".join(f"{self[x, y]:#04x}" for x in range(self.x, self.x_end))
				for y in range(self.y, self.y_end)
			)
			+ "\n  ])\n)"
		)

	def __hash__(self):
		return hash((self._x, self._y, self._w, self._h, self.__data))

	def __eq__(self, other):
		if not isinstance(other, PixelImage):
			return NotImplemented
		return (
			self._x == other._x
			and self._y == other._y
			and self._w == other._w
			and self._h == other._h
			and self.__data == other.__data
		)

	def __ne__(self, other):
		if not isinstance(other, PixelImage):
			return NotImplemented
		return (
			self._x != other._x
			or self._y != other._y
			or self._w != other._w
			or self._h != other._h
			or self.__data != other.__data
		)

	def __or__(self, other):
		if not isinstance(other, PixelImage):
			raise TypeError("Operand must be an instance of PixelImage")

		if self.width == 0 or self.height == 0:
			return other
		elif other.width == 0 or other.height == 0:
			return self
		else:
			x = min(self._x, other.x)
			y = min(self._y, other.y)
			x2 = max(self.x_end, other.x_end)
			y2 = max(self.y_end, other.y_end)

		ret = self.__class__(
			x=x,
			y=y,
			width=x2 - x,
			height=y2 - y,
		)

		dj = self._y - y
		i_min = self._x - x
		i_max = i_min + self._w
		for j in range(self._h):
			j_min = j * self._w
			_j_min = (j + dj) * ret._w
			row = self.__data[j_min : j_min + self._w]
			ret.__data[i_min + _j_min : i_max + _j_min] = row

		dj = other._y - y
		i_min = other.x - x
		i_max = i_min + other.width
		for j in range(other.height):
			j_min = j * other.width
			_j_min = (j + dj) * ret._w
			for i, i_ in enumerate(range(i_min + _j_min, i_max + _j_min)):
				ret.__data[i_] |= other.__data[j_min + i]

		return ret

	def crop(self, min_x, max_x, min_y, max_y):
		if max_x < min_x or max_y < min_y:
			raise ValueError("Invalid bounds")

		min_x = max(min_x, self._x)
		max_x = min(max_x, self.x_end)
		min_y = max(min_y, self._y)
		max_y = min(max_y, self.y_end)
		if max_x <= min_x or max_y <= min_y:
			return PixelImage()

		data = bytearray((max_x - min_x) * (max_y - min_y))
		ix = 0
		for j in range(min_y, max_y):
			for i in range(min_x, max_x):
				data[ix] = self[i, j]
				ix += 1

		return PixelImage(
			x=min_x,
			y=min_y,
			width=max_x - min_x,
			height=max_y - min_y,
			data=data,
		)


def segmentize(image):
	image = PixelImage(image)

	for y in range(image.y, image.y_end):
		for x in range(image.x, image.x_end):
			if not image[x, y]:
				continue

			# Move segment into new image
			ret = PixelImage(
				x=image.x,
				y=image.y,
				width=image.width,
				height=image.height,
			)

			p = (x, y)

			# Flood fill
			stack = [(x, y)]
			while stack:
				x, y = stack.pop()
				if not image[x, y]:
					continue

				ret[x, y] = 1
				image[x, y] = 0

				if image[x - 1, y - 1]:
					stack.append((x - 1, y - 1))
				if image[x - 1, y]:
					stack.append((x - 1, y))
				if image[x - 1, y + 1]:
					stack.append((x - 1, y + 1))
				if image[x, y - 1]:
					stack.append((x, y - 1))
				if image[x, y + 1]:
					stack.append((x, y + 1))
				if image[x + 1, y - 1]:
					stack.append((x + 1, y - 1))
				if image[x + 1, y]:
					stack.append((x + 1, y))
				if image[x + 1, y + 1]:
					stack.append((x + 1, y + 1))

			# Yields segment and staring position
			x, y = p
			yield (ret, p)


class CellFlag(IntFlag):
	ACTIVE = 0b0000_0001
	UP = 0b0001_0000
	DOWN = 0b0010_0000
	LEFT = 0b0100_0000
	RIGHT = 0b1000_0000

	UP_LEFT = UP | LEFT
	UP_RIGHT = UP | RIGHT
	DOWN_LEFT = DOWN | LEFT
	DOWN_RIGHT = DOWN | RIGHT

	def move(self, pos):
		"""Move coordinate according to direction"""
		x, y = pos
		if self & self.__class__.UP:
			y -= 1
		if self & self.__class__.DOWN:
			y += 1
		if self & self.__class__.LEFT:
			x -= 1
		if self & self.__class__.RIGHT:
			x += 1
		return (x, y)

	def corner(self, pos):
		"""Get corner of a cell"""
		x, y = pos
		if self & self.__class__.UP_LEFT == self.__class__.UP_LEFT:
			return (x, y)
		elif self & self.__class__.UP_RIGHT == self.__class__.UP_RIGHT:
			return (x + 1, y)
		elif self & self.__class__.DOWN_RIGHT == self.__class__.DOWN_RIGHT:
			return (x + 1, y + 1)
		elif self & self.__class__.DOWN_LEFT == self.__class__.DOWN_LEFT:
			return (x, y + 1)
		else:
			raise ValueError(f"Invalid corner {self}")

	def cw(self):
		"""Rotate self clockwise"""
		ret = self & self.__class__.ACTIVE
		if self & self.__class__.UP:
			ret |= self.__class__.RIGHT
		if self & self.__class__.DOWN:
			ret |= self.__class__.LEFT
		if self & self.__class__.LEFT:
			ret |= self.__class__.UP
		if self & self.__class__.RIGHT:
			ret |= self.__class__.DOWN
		return ret

	def ccw(self):
		"""Rotate self counterclockwise"""
		ret = self & self.__class__.ACTIVE
		if self & self.__class__.UP:
			ret |= self.__class__.LEFT
		if self & self.__class__.DOWN:
			ret |= self.__class__.RIGHT
		if self & self.__class__.LEFT:
			ret |= self.__class__.DOWN
		if self & self.__class__.RIGHT:
			ret |= self.__class__.UP
		return ret

	def reverse(self):
		"""Reverse self"""
		ret = self & self.__class__.ACTIVE
		if self & self.__class__.UP:
			ret |= self.__class__.DOWN
		if self & self.__class__.DOWN:
			ret |= self.__class__.UP
		if self & self.__class__.LEFT:
			ret |= self.__class__.RIGHT
		if self & self.__class__.RIGHT:
			ret |= self.__class__.LEFT
		return ret


class Turtle:
	__slots__ = ["img", "x", "y", "dir"]

	def __init__(self, img, x, y, dir):
		self.img, self.x, self.y, self.dir = img, x, y, dir

	def _move(self):
		# Set wall
		d_ccw, d_cw, d_rev = self.dir.ccw(), self.dir.cw(), self.dir.reverse()
		p = self.x, self.y
		self.img[p] |= d_ccw

		p_ = d_ccw.move(p)
		assert not self.img[p_] & CellFlag.ACTIVE

		# Build boundary wall from this point
		# For all diagrams, it is assumed movement direction is right

		# ? . #
		# ? X ?
		# ? ? ?
		p_ = (self.dir | d_ccw).move(p)
		if self.img[p_] & CellFlag.ACTIVE:
			# Top-right corner
			ret = [(self.dir | d_ccw).corner(p)]

			# ? . ^
			# ? X ?
			# ? ? ?
			(self.x, self.y), self.dir = p_, d_ccw
			return ret

		# ? . .
		# ? X #
		# ? ? ?
		p_ = self.dir.move(p)
		if self.img[p_] & CellFlag.ACTIVE:
			# ? . .
			# ? X >
			# ? ? ?
			self.x, self.y = p_
			return []  # No corner

		# ? . .
		# ? X .
		# ? ? #
		p_ = (self.dir | d_cw).move(p)
		if self.img[p_] & CellFlag.ACTIVE:
			# Two corners: top-right and bottom-right
			ret = [
				(self.dir | d_ccw).corner(p),
				(self.dir | d_cw).corner(p),
			]

			# ? . .
			# ? X .
			# ? ? >
			self.img[p] |= self.dir
			self.x, self.y = p_
			return ret

		# ? . .
		# ? X .
		# ? # .
		p_ = d_cw.move(p)
		if self.img[p_] & CellFlag.ACTIVE:
			# Top-right corner
			ret = [(self.dir | d_ccw).corner(p)]

			# ? . .
			# ? X .
			# ? v .
			self.img[p] |= self.dir
			(self.x, self.y), self.dir = p_, d_cw
			return ret

		# ? . .
		# ? X .
		# # . .
		p_ = (d_rev | d_cw).move(p)
		if self.img[p_] & CellFlag.ACTIVE:
			# Three corners: top-right, bottom-right, and bottom-left
			ret = [
				(self.dir | d_ccw).corner(p),
				(self.dir | d_cw).corner(p),
				(d_cw | d_rev).corner(p),
			]

			# ? . .
			# ? X .
			# v . .
			self.img[p] |= self.dir | d_cw
			(self.x, self.y), self.dir = p_, d_cw
			return ret

		# ? . .
		# # X .
		# . . .
		p_ = d_rev.move(p)
		if self.img[p_] & CellFlag.ACTIVE:
			# Two corners: top-right and bottom-right
			ret = [
				(self.dir | d_ccw).corner(p),
				(self.dir | d_cw).corner(p),
			]

			# ? . .
			# < X .
			# . . .
			self.img[p] |= self.dir | d_cw
			(self.x, self.y), self.dir = p_, d_rev
			return ret

		# # . .
		# . X .
		# . . .
		p_ = (d_rev | d_ccw).move(p)
		if self.img[p_] & CellFlag.ACTIVE:
			# Four corners: top-right, bottom-right, bottom-left, and top-left
			ret = [
				(self.dir | d_ccw).corner(p),
				(self.dir | d_cw).corner(p),
				(d_cw | d_rev).corner(p),
				(d_ccw | d_rev).corner(p),
			]

			# < . .
			# . X .
			# . . .
			self.img[p] |= self.dir | d_cw | d_rev
			(self.x, self.y), self.dir = p_, d_rev
			return ret

		# . . .
		# . X .
		# . . .
		self.img[p] |= self.dir | d_cw | d_rev
		# Four corners: top-right, bottom-right, bottom-left, and top-left
		return [
			(self.dir | d_ccw).corner(p),
			(self.dir | d_cw).corner(p),
			(d_cw | d_rev).corner(p),
			(d_ccw | d_rev).corner(p),
		]

	def _move_4way(self):
		# Set wall
		d_ccw, d_cw, d_rev = self.dir.ccw(), self.dir.cw(), self.dir.reverse()
		p = self.x, self.y
		self.img[p] |= d_ccw

		p_ = d_ccw.move(p)
		assert not self.img[p_] & CellFlag.ACTIVE

		# Build boundary wall from this point
		# For all diagrams, it is assumed movement direction is right

		# ? . ?
		# ? X #
		# ? ? ?
		p_ = self.dir.move(p)
		if self.img[p_] & CellFlag.ACTIVE:
			# ? . #
			# ? X #
			# ? ? ?
			p__ = d_ccw.move(p_)
			if self.img[p__] & CellFlag.ACTIVE:
				# Top-right corner
				ret = [(self.dir | d_ccw).corner(p)]

				# ? . ^
				# ? X #
				# ? ? ?
				(self.x, self.y), self.dir = p__, d_ccw
				return ret

			# ? . .
			# ? X #
			# ? ? ?
			else:
				# ? . .
				# ? X >
				# ? ? ?
				self.x, self.y = p_
				return []  # No corner

		# ? . ?
		# ? X .
		# ? # ?
		p_ = d_cw.move(p)
		if self.img[p_] & CellFlag.ACTIVE:
			self.img[p] |= self.dir

			# ? . ?
			# ? X .
			# ? # #
			p__ = self.dir.move(p_)
			if self.img[p__] & CellFlag.ACTIVE:
				# Two corners: top-right and bottom-right
				ret = [
					(self.dir | d_ccw).corner(p),
					(self.dir | d_cw).corner(p),
				]

				# ? . ?
				# ? X .
				# ? # >
				self.x, self.y = p__
				return ret

			# ? . ?
			# ? X .
			# ? # .
			else:
				# Top-right corner
				ret = [(self.dir | d_ccw).corner(p)]

				# ? . ?
				# ? X .
				# ? v .
				(self.x, self.y), self.dir = p_, d_cw
				return ret

		# ? . ?
		# # X .
		# ? . ?
		p_ = d_rev.move(p)
		if self.img[p_] & CellFlag.ACTIVE:
			self.img[p] |= self.dir | d_cw

			# ? . ?
			# # X .
			# # . ?
			p__ = d_cw.move(p_)
			if self.img[p__] & CellFlag.ACTIVE:
				# Three corners: top-right, bottom-right, and bottom-left
				ret = [
					(self.dir | d_ccw).corner(p),
					(self.dir | d_cw).corner(p),
					(d_cw | d_rev).corner(p),
				]

				# ? . ?
				# # X .
				# v . .
				(self.x, self.y), self.dir = p__, d_cw
				return ret

			# ? . ?
			# # X .
			# . . ?
			else:
				# Two corners: top-right and bottom-right
				ret = [
					(self.dir | d_ccw).corner(p),
					(self.dir | d_cw).corner(p),
				]

				# ? . ?
				# < X .
				# . . ?
				(self.x, self.y), self.dir = p_, d_rev
				return ret

		# ? . ?
		# . X .
		# ? . ?
		self.img[p] |= self.dir | d_cw | d_rev
		# Four corners: top-right, bottom-right, bottom-left, and top-left
		return [
			(self.dir | d_ccw).corner(p),
			(self.dir | d_cw).corner(p),
			(d_cw | d_rev).corner(p),
			(d_ccw | d_rev).corner(p),
		]

	def trace(self, stop_pos, exclude_corners=False):
		poly = []
		while True:
			j = len(poly)
			poly += self._move_4way() if exclude_corners else self._move()
			try:
				i = poly.index(stop_pos, j)
			except ValueError:
				continue

			return poly[: i + 1]


def polygonize(image, exclude_corners=False):
	image = PixelImage(image)

	ret = []
	turtle = Turtle(image, 0, 0, CellFlag.LEFT)
	for y in range(image.y, image.y_end):
		for x in range(image.x, image.x_end):
			v = image[x, y]
			if not v & CellFlag.ACTIVE:
				continue

			if not (v & CellFlag.UP or image[x, y - 1] & CellFlag.ACTIVE):
				turtle.dir, stop_pos = CellFlag.RIGHT, (x, y)
			elif not (v & CellFlag.RIGHT or image[x + 1, y] & CellFlag.ACTIVE):
				turtle.dir, stop_pos = CellFlag.DOWN, (x + 1, y)
			else:
				continue
			turtle.x, turtle.y = x, y

			ret.append(turtle.trace(stop_pos, exclude_corners)[::-1])
			assert checkPoly(ret[-1])

	return ret


def joinPolygons(polygons):
	def first_equals(i, j, *, key=lambda x: x):
		i, j = enumerate(map(key, i)), enumerate(map(key, j))
		try:
			(ai, av), (bi, bv) = next(i), next(j)
			while av != bv:
				if av < bv:
					ai, av = next(i)
				else:
					bi, bv = next(j)
			return ai, bi
		except StopIteration:
			pass

	def merge(i, j):
		r = []
		i, j = iter(i), iter(j)
		a, b = next(i, None), next(j, None)
		while a is not None and b is not None:
			if a[1] == b[1]:
				r.append((min(a[0], b[0]), a[1]))
				a, b = next(i, None), next(j, None)
			elif a[1] < b[1]:
				r.append(a)
				a = next(i, None)
			else:
				r.append(b)
				b = next(j, None)

		if a is not None:
			r.extend(i)
		elif b is not None:
			r.extend(j)

		return r

	kf = lambda v: v[1]

	def f(p):
		l = []
		x = None
		for i, v in sorted(enumerate(p), key=kf):
			if x != v:
				x = v
				l.append((i, v))
		return p, l

	def checkPoints(p, l):
		if not checkPoly(p):
			return False
		for i in range(len(l)):
			j, v = l[i]
			if j >= len(p) or p[j] != v:
				print(f"{p}\n{l} Error at {i} ({j}, {v}) (got {None if j >= len(p) else p[j]})")
				return False
			if i < 1:
				continue
			_, t = l[i - 1]
			if t == v:
				print(f"{p}\n{l} Error at {i} ({j}, {v})")
				return False
		return True

	points = [f(i) for i in polygons]
	for i in range(len(points) - 1, 0, -1):
		p, l = points[i]
		for j in range(i):
			p_, l_ = points[j]
			t = first_equals(l, l_, key=kf)
			if t is None:
				continue

			a, b = t
			a, _ = l[a]
			b, _ = l_[b]
			p = [*p[:a], *p_[b:], *p_[:b], *p[a:]]

			t = len(p_)
			s = t - b + a
			r = a - b
			l = merge(
				((i + t if i >= a else i, v) for i, v in l),
				((i + r if i >= b else i + s, v) for i, v in l_),
			)

			assert checkPoints(p, l)
			points[j] = p, l
			del points[i]
			break

	return [p[0] for p in points]


def generatePolygons(image, *, join_polygons=True, exclude_corners=False, **kw):
	ret = polygonize(image, exclude_corners)
	if join_polygons:
		ret = joinPolygons(ret)
	return ret


def checkPoly(poly):
	for i in range(-1, len(poly) - 1):
		x, y = poly[i]
		x_, y_ = poly[i + 1]
		if x != x_ and y != y_:
			print(f"{poly} Error at {i}")
			return False
	for i in range(-2, len(poly) - 2):
		x, y = poly[i]
		x_, y_ = poly[i + 1]
		x__, y__ = poly[i + 2]
		if x == x_ == x__ or y == y_ == y__:
			print(f"{poly} Error at {i}")
			return False
	return True


# Testing
def runTest():
	import json

	characters = json.load(open("./characters.json"))
	diacritics = json.load(open("./diacritics.json"))
	ligatures = json.load(open("./ligatures.json"))

	for v in characters:
		if "pixels" not in v:
			continue
		testChar(v["character"], v["pixels"])

	for k, v in diacritics.items():
		if "pixels" not in v:
			continue
		testChar(k, v["pixels"])

	for v in ligatures:
		if "pixels" not in v:
			continue
		testChar(v["ligature"], v["pixels"])


filter = {}


def testChar(name, pixels):
	if filter and name not in filter:
		return

	image = PixelImage(
		width=len(pixels[0]),
		height=len(pixels),
		data=bytes(x for a in pixels[::-1] for x in a),
	)

	print(f"Character: {name}\n{image}\n\n")

	for poly in generatePolygons(image, join_polygons=False, exclude_corners=True):
		print("Polygon:\n  " + "\n  ".join(f"{x}, {y}" for x, y in poly) + "\n\n")


if __name__ == "__main__":
	runTest()
