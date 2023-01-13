__all__ = [
    'PixelImage',
    'generatePolygons',
]

from enum import IntFlag
import itertools


class PixelImage:
    ''' Class for managing a pixel image.
    
    Each pixel is a 8-bit integer.
    It also store the position and size of the image, allowing easier operation.
    '''

    __slots__ = ['__data', '_x', '_y', '_w', '_h']

    def __init__(self, src=None, *, x=0, y=0, width=0, height=0, data=None):
        if src is not None:
            self._x, self._y, self._w, self._h, self.__data = src._x, src._y, src._w, src._h, bytearray(
                src.__data)
            return
        if width < 0:
            raise ValueError('Width < 0')
        if height < 0:
            raise ValueError('Height < 0')

        self._x, self._y, self._w, self._h = x, y, width, height

        if data is not None:
            data = bytearray(data)
            if len(data) != width * height:
                raise ValueError(
                    f'Data length mismatch (expected {width * height}, got {len(data)})'
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
        ''' Gets a pixel at (x, y).
        
        Defaults to 0 if out of bounds.
        '''
        x, y = key
        x -= self._x
        y -= self._y
        if x < 0 or x >= self._w or y < 0 or y >= self._h:
            return 0
        return self.__data[x + y * self._w]

    def __setitem__(self, key, value):
        ''' Sets a pixel at (x, y).
        
        Do nothing if out of bounds.
        '''
        x, y = key
        x -= self._x
        y -= self._y
        if x < 0 or x >= self._w or y < 0 or y >= self._h:
            return
        self.__data[x + y * self._w] = value

    def __len__(self):
        return self._w * self._h

    def __str__(self):
        return '\n'.join(' '.join(
            str(self[x, y]) for x in range(self.x, self.x_end))
                         for y in range(self.y, self.y_end))

    def __repr__(self):
        return f'PixelImage(\n  x={self._x},\n' \
            f'  y={self._y},\n' \
            f'  width={self._w},\n' \
            f'  height={self._h},\n' \
            f'  data=bytes([\n    ' + \
            ',\n    '.join(
                ', '.join(
                    f'{self[x, y]:#04x}' for x in range(self.x, self.x_end)
                ) for y in range(self.y, self.y_end)
            ) + \
            '\n  ])\n)'

    def __hash__(self):
        return hash((self._x, self._y, self._w, self._h, self.__data))

    def __eq__(self, other):
        if not isinstance(other, PixelImage):
            return NotImplemented
        return self._x == other._x and \
            self._y == other._y and \
            self._w == other._w and \
            self._h == other._h and \
            self.__data == other.__data

    def __ne__(self, other):
        if not isinstance(other, PixelImage):
            return NotImplemented
        return self._x != other._x or \
            self._y != other._y or \
            self._w != other._w or \
            self._h != other._h or \
            self.__data != other.__data

    def __or__(self, other):
        if not isinstance(other, PixelImage):
            return NotImplemented

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
            row = self.__data[j_min:j_min + self._w]
            ret.__data[i_min + _j_min:i_max + _j_min] = row

        dj = other._y - y
        i_min = other.x - x
        i_max = i_min + other.width
        for j in range(other.height):
            j_min = j * other.width
            _j_min = (j + dj) * ret._w
            for i, i_ in enumerate(range(i_min + _j_min, i_max + _j_min)):
                ret.__data[i_] |= other.__data[j_min + i]

        return ret


def generatePolygons(image):
    for segment, start_pos in segmentize(image):
        yield polygonizeSegment(segment, start_pos)


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
        ''' Move coordinate according to direction '''
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
        ''' Get corner of a cell '''
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
            raise ValueError(f'Invalid corner {self}')

    def cw(self):
        ''' Rotate self clockwise '''
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
        ''' Rotate self counterclockwise '''
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
        ''' Reverse self '''
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


def polygonizeSegment(image, start_pos):
    x, y = start_pos

    # Make sure position is top left
    assert image[x, y]
    assert not (image[x - 1, y] or image[x - 1, y - 1] or image[x, y - 1]
                or image[x + 1, y - 1])

    dir = CellFlag.RIGHT

    def doMove():
        nonlocal x, y, dir

        # Set wall
        d_ccw, d_cw, d_rev = dir.ccw(), dir.cw(), dir.reverse()
        image[x, y] |= d_ccw

        x_, y_ = d_ccw.move((x, y))
        assert not image[x_, y_] & CellFlag.ACTIVE

        # Build boundary wall from this point
        # For all diagrams, it is assumed movement direction is right

        # ? . #
        # ? X ?
        # ? ? ?
        x_, y_ = (dir | d_ccw).move((x, y))
        if image[x_, y_] & CellFlag.ACTIVE:
            # Top-right corner
            ret = [(dir | d_ccw).corner((x, y))]

            # ? . ^
            # ? X ?
            # ? ? ?
            x, y = x_, y_
            dir = d_ccw
            return ret

        # ? . .
        # ? X #
        # ? ? ?
        x_, y_ = dir.move((x, y))
        if image[x_, y_] & CellFlag.ACTIVE:
            # ? . .
            # ? X >
            # ? ? ?
            x, y = x_, y_
            return []  # No corner

        # ? . .
        # ? X .
        # ? ? #
        x_, y_ = (dir | d_cw).move((x, y))
        if image[x_, y_] & CellFlag.ACTIVE:
            # Two corners: top-right and bottom-right
            ret = [
                (dir | d_ccw).corner((x, y)),
                (dir | d_cw).corner((x, y)),
            ]

            # ? . .
            # ? X .
            # ? ? >
            image[x, y] |= dir
            x, y = x_, y_
            return ret

        # ? . .
        # ? X .
        # ? # .
        x_, y_ = d_cw.move((x, y))
        if image[x_, y_] & CellFlag.ACTIVE:
            # Top-right corner
            ret = [(dir | d_ccw).corner((x, y))]

            # ? . .
            # ? X .
            # ? v .
            image[x, y] |= dir
            x, y = x_, y_
            dir = d_cw
            return ret

        # ? . .
        # ? X .
        # # . .
        x_, y_ = (d_rev | d_cw).move((x, y))
        if image[x_, y_] & CellFlag.ACTIVE:
            # Three corners: top-right, bottom-right, and bottom-left
            ret = [
                (dir | d_ccw).corner((x, y)),
                (dir | d_cw).corner((x, y)),
                (d_cw | d_rev).corner((x, y)),
            ]

            # ? . .
            # ? X .
            # v . .
            image[x, y] |= dir | d_cw
            x, y = x_, y_
            dir = d_cw
            return ret

        # ? . .
        # # X .
        # . . .
        x_, y_ = d_rev.move((x, y))
        if image[x_, y_] & CellFlag.ACTIVE:
            # Two corners: top-right and bottom-right
            ret = [
                (dir | d_ccw).corner((x, y)),
                (dir | d_cw).corner((x, y)),
            ]

            # ? . .
            # < X .
            # . . .
            image[x, y] |= dir | d_cw
            x, y = x_, y_
            dir = d_rev
            return ret

        # # . .
        # . X .
        # . . .
        x_, y_ = (d_rev | d_ccw).move((x, y))
        if image[x_, y_] & CellFlag.ACTIVE:
            # Four corners: top-right, bottom-right, bottom-left, and top-left
            ret = [
                (dir | d_ccw).corner((x, y)),
                (dir | d_cw).corner((x, y)),
                (d_cw | d_rev).corner((x, y)),
                (d_ccw | d_rev).corner((x, y)),
            ]

            # < . .
            # . X .
            # . . .
            image[x, y] |= dir | d_cw | d_rev
            x, y = x_, y_
            dir = d_rev
            return ret

        # . . .
        # . X .
        # . . .
        image[x, y] |= dir | d_cw | d_rev
        # Four corners: top-right, bottom-right, bottom-left, and top-left
        return [
            (dir | d_ccw).corner((x, y)),
            (dir | d_cw).corner((x, y)),
            (d_cw | d_rev).corner((x, y)),
            (d_ccw | d_rev).corner((x, y)),
        ]

    def find(l, x):
        try:
            return l.index(x)
        except ValueError:
            return None

    # Generate outer polygon
    outer_poly = [(x, y)]
    line = doMove()
    i = find(line, outer_poly[0])
    while i is None:
        outer_poly += line
        line = doMove()
        i = find(line, outer_poly[0])
    outer_poly += line[:i + 1]

    assert outer_poly[0][1] == outer_poly[1][1]
    assert checkPoly(outer_poly[:-1])

    # Calculate bounding box
    x_min, y_min, x_max, y_max = x, y, x, y
    for x, y in outer_poly:
        if x_min > x:
            x_min = x
        if x_max < x:
            x_max = x
        if y_min > y:
            y_min = y
        if y_max < y:
            y_max = y

    # Generate inner polygon
    for y in range(y_min, y_max):
        for x in range(x_min, x_max):
            v = image[x, y]
            if not v & CellFlag.ACTIVE:
                continue

            if not (image[x, y + 1] & CellFlag.ACTIVE or v & CellFlag.DOWN):
                dir = CellFlag.LEFT
            else:
                continue

            inner_poly = []
            line = doMove()
            i = None
            while i is None:
                inner_poly += line
                line = doMove()
                i = find(line, inner_poly[0])
            inner_poly += line[:i]

            assert checkPoly(inner_poly)

            # Rotate to top-leftmost point
            # (Polygon does not change, just canonicalized)
            p = 0
            x, y = inner_poly[0]
            for i in range(1, len(inner_poly)):
                x_, y_ = inner_poly[i]
                if x_ < x or (x_ == x and y_ < y):
                    p, x, y = i, x_, y_
            inner_poly = inner_poly[p:] + inner_poly[:p]

            # Join with outer polygon

            # Find the joiner line
            xi, yi = inner_poly[0]
            p = 0
            yp = outer_poly[0][1]
            for i in range(1, len(outer_poly) - 1):
                x, y = outer_poly[i]
                x_, y_ = outer_poly[i + 1]

                if y > yi or y_ > yi or y != y_ or yp > y:
                    continue

                p = i
                yp = y

            # Insert into polygon
            if outer_poly[p] == inner_poly[0]:
                # Deduplicate first point
                outer_poly = list(*removeColinearPoints(
                    itertools.chain(
                        outer_poly[:p],
                        inner_poly,
                        outer_poly[p:],
                    )))
            elif outer_poly[p + 1] == inner_poly[0]:
                # Deduplicate second point
                outer_poly = list(
                    removeColinearPoints(
                        itertools.chain(
                            outer_poly[:p + 1],
                            inner_poly,
                            outer_poly[p + 1:],
                        )))
            else:
                # insert inner point
                pp = [(inner_poly[0][0], outer_poly[p][1])]
                outer_poly = list(
                    removeColinearPoints(
                        itertools.chain(
                            outer_poly[:p + 1],
                            pp,
                            inner_poly,
                            [inner_poly[0]],
                            pp,
                            outer_poly[p + 1:],
                        )))

    # Remove last point
    assert outer_poly[-1] == outer_poly[0]
    outer_poly.pop()

    assert checkPoly(outer_poly)

    # Return polygon
    return outer_poly


def removeColinearPoints(poly):
    np = 0

    for p in poly:
        if np == 0:
            x1, y1 = p
            np += 1
            continue

        if np == 1:
            x2, y2 = p
            np += 1
            continue

        x3, y3 = p

        # Check if the two line is colinear
        if x1 == x2 == x3 or y1 == y2 == y3:
            # Skip middle point
            x2, y2 = x3, y3
        else:
            yield (x1, y1)
            x1, y1, x2, y2 = x2, y2, x3, y3

    if np >= 1:
        yield (x1, y1)
    if np >= 2:
        yield (x2, y2)


def checkPoly(poly):
    for i in range(-1, len(poly) - 1):
        x, y = poly[i]
        x_, y_ = poly[i + 1]
        if x != x_ and y != y_:
            print(f'{poly} Error at {i}')
            return False
    for i in range(-2, len(poly) - 2):
        x, y = poly[i]
        x_, y_ = poly[i + 1]
        x__, y__ = poly[i + 2]
        if x == x_ == x__ or y == y_ == y__:
            print(f'{poly} Error at {i}')
            return False
    return True


# Testing
def runTest():
    import json
    characters = json.load(open("./characters.json"))
    diacritics = json.load(open("./diacritics.json"))
    ligatures = json.load(open("./ligatures.json"))

    for v in characters:
        if 'pixels' not in v:
            continue
        testChar(v['character'], v['pixels'])

    for k, v in diacritics.items():
        if 'pixels' not in v:
            continue
        testChar(k, v['pixels'])

    for v in ligatures:
        if 'pixels' not in v:
            continue
        testChar(v['ligature'], v['pixels'])


filter = {'∀'}


def testChar(name, pixels):
    if False and name not in filter:
        return

    image = PixelImage(
        width=len(pixels[0]),
        height=len(pixels),
        data=bytes(x for a in pixels[::-1] for x in a),
    )

    print(f'Character: {name}\n{image}\n\n')

    for poly in generatePolygons(image):
        print('Polygon:\n  ' + '\n  '.join(f'{x}, {y}'
                                           for x, y in poly) + '\n\n')


if __name__ == '__main__':
    runTest()