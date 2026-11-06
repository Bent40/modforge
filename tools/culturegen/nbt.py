"""Minimal NBT writer/reader (Java edition, big-endian, gzip) for vanilla structure files. No dependencies."""
import gzip
import struct

END, BYTE, SHORT, INT, LONG, FLOAT, DOUBLE, BYTE_ARRAY, STRING, LIST, COMPOUND, INT_ARRAY, LONG_ARRAY = range(13)


class Int(int):
    pass


class Byte(int):
    pass


class Short(int):
    pass


class IntArray(list):
    pass


class ByteArray(list):
    pass


class LongArray(list):
    pass


class Float(float):
    pass


class Long(int):
    pass


def _tag_of(v):
    if isinstance(v, Byte) or isinstance(v, bool):
        return BYTE
    if isinstance(v, Long):
        return LONG
    if isinstance(v, Float):
        return FLOAT
    if isinstance(v, Short):
        return SHORT
    if isinstance(v, IntArray):
        return INT_ARRAY
    if isinstance(v, ByteArray):
        return BYTE_ARRAY
    if isinstance(v, LongArray):
        return LONG_ARRAY
    if isinstance(v, int):
        return INT
    if isinstance(v, float):
        return DOUBLE
    if isinstance(v, str):
        return STRING
    if isinstance(v, list):
        return LIST
    if isinstance(v, dict):
        return COMPOUND
    raise TypeError(type(v))


def _str(s):
    b = s.encode("utf-8")
    return struct.pack(">H", len(b)) + b


def _payload(tag, v):
    if tag == BYTE:
        return struct.pack(">b", int(v))
    if tag == INT:
        return struct.pack(">i", v)
    if tag == SHORT:
        return struct.pack(">h", v)
    if tag == LONG:
        return struct.pack(">q", v)
    if tag == FLOAT:
        return struct.pack(">f", v)
    if tag == INT_ARRAY:
        return struct.pack(">i", len(v)) + struct.pack(f">{len(v)}i", *v)
    if tag == BYTE_ARRAY:
        return struct.pack(">i", len(v)) + struct.pack(f">{len(v)}b", *v)
    if tag == LONG_ARRAY:
        return struct.pack(">i", len(v)) + struct.pack(f">{len(v)}q", *v)
    if tag == DOUBLE:
        return struct.pack(">d", v)
    if tag == STRING:
        return _str(v)
    if tag == LIST:
        if not v:
            return struct.pack(">bi", END, 0)
        et = _tag_of(v[0])
        return struct.pack(">bi", et, len(v)) + b"".join(_payload(et, e) for e in v)
    if tag == COMPOUND:
        out = b""
        for k, e in v.items():
            t = _tag_of(e)
            out += struct.pack(">b", t) + _str(k) + _payload(t, e)
        return out + struct.pack(">b", END)
    raise TypeError(tag)


def write(path, root, name=""):
    """Write a gzipped NBT file. Use the Byte/Short/Long/Float/*Array wrappers to keep exact tag types."""
    data = struct.pack(">b", COMPOUND) + _str(name) + _payload(COMPOUND, root)
    with gzip.open(path, "wb") as f:
        f.write(data)


def read(path):
    """Round-trip check reader (returns plain python values)."""
    data = gzip.open(path, "rb").read()
    pos = [0]

    def take(n):
        b = data[pos[0]:pos[0] + n]
        pos[0] += n
        return b

    def rstr():
        (n,) = struct.unpack(">H", take(2))
        return take(n).decode("utf-8")

    def payload(t):
        if t == BYTE:
            return Byte(struct.unpack(">b", take(1))[0])
        if t == SHORT:
            return Short(struct.unpack(">h", take(2))[0])
        if t == INT:
            return struct.unpack(">i", take(4))[0]
        if t == LONG:
            return Long(struct.unpack(">q", take(8))[0])
        if t == FLOAT:
            return Float(struct.unpack(">f", take(4))[0])
        if t == DOUBLE:
            return struct.unpack(">d", take(8))[0]
        if t == STRING:
            return rstr()
        if t == BYTE_ARRAY:
            (n,) = struct.unpack(">i", take(4))
            return ByteArray(struct.unpack(f">{n}b", take(n)))
        if t == INT_ARRAY:
            (n,) = struct.unpack(">i", take(4))
            return IntArray(struct.unpack(f">{n}i", take(4 * n)))
        if t == LONG_ARRAY:
            (n,) = struct.unpack(">i", take(4))
            return LongArray(struct.unpack(f">{n}q", take(8 * n)))
        if t == LIST:
            et, n = struct.unpack(">bi", take(5))
            return [payload(et) for _ in range(n)]
        if t == COMPOUND:
            d = {}
            while True:
                (tt,) = struct.unpack(">b", take(1))
                if tt == END:
                    return d
                k = rstr()
                d[k] = payload(tt)
        raise ValueError(t)

    (t,) = struct.unpack(">b", take(1))
    rstr()
    return payload(t)
