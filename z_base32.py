import itertools
import math
import collections


SYMBOLS = 'ybndrfg8ejkmcpqxot1uwisza345h769'
SYMBOLS = [(i, c if c.isdigit() else c + c.upper(), c)
           for i, c in zip(itertools.count(), SYMBOLS)]
DECODE_SYMBOLS = dict((b, a[0]) for a in SYMBOLS for b in a[1])
ENCODE_SYMBOLS = dict((a[0], a[2]) for a in SYMBOLS)


def encode_bytes(b):
    # Iter Bytes 5 Per 5 Bits
    def ib5p5b(b):
        m = 0
        it = iter(b)
        c = next(it)
        run = True
        while run:
            if m < 3:
                r = c >> 3 - m & 0x1F
            else:
                s = 5 - (8 - m)
                r = c << s & 0x1F
                try:
                    c = next(it)
                except StopIteration:
                    c = 0
                    run = False
                r = (r | c >> 8 - s) & 0x1F
            m = (m + 5) % 8
            yield r
        raise StopIteration()
    return ''.join(ENCODE_SYMBOLS[c] for c in ib5p5b(b))


def decode_bytes(s):
    o = bytearray()
    m = 0
    cb = 0
    for cs in s:
        try:
            i = DECODE_SYMBOLS[cs]
        except KeyError:
            raise ValueError('Malformed z-base-32 string')
        if m < 3:
            cb = cb | i << 3 - m
        else:
            s = 5 - (8 - m)
            cb = cb | i >> s
            o.append(cb)
            cb = i << (8 - s) & 0xFF
        m = (m + 5) % 8
    return o


def encode_int(i):
    if i < 0:
        raise ValueError("i can't be lower than 0")
    if i == 0:
        return ENCODE_SYMBOLS[0]
    i_bitlen = i.bit_length()
    b = i.to_bytes(int(math.ceil(i_bitlen / 8.0)), byteorder='big')
    right_len = i_bitlen // 40 * 5
    if right_len > 0:
        o = encode_bytes(b[-right_len:])
    else:
        o = ''
    if i_bitlen % 40:
        i = i >> i_bitlen // 40 * 40
        o2 = collections.deque()
        while i > 0:
            o2.appendleft(ENCODE_SYMBOLS[i & 0x1F])
            i >>= 5
        o2.append(o)
        o = ''.join(o2)
    return o


def decode_int(b):
    if b == 'y':
        return 0
    right_len = len(b) // 8 * 8
    if right_len > 0:
        o1 = int.from_bytes(decode_bytes(b[-right_len:]), byteorder='big')
        b = b[:right_len]
    else:
        o1 = 0
    if len(b) % 8:
        o2 = 0
        for c in b:
            try:
                o2 = o2 << 5 | DECODE_SYMBOLS[c]
            except KeyError:
                raise ValueError('Malformed z-base-32 string')
    return o2 << right_len * 5 | o1
