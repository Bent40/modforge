"""Minimal NBT writer/reader (Java edition, big-endian, gzip) for vanilla structure files. No dependencies."""
import gzip
import struct

END, BYTE, SHORT, INT, LONG, FLOAT, DOUBLE, BYTE_ARRAY, STRING, LIST, COMPOUND, INT_ARRAY, LONG_ARRAY = range(13)


class Int(int):
    pass


class Byte(int):
    pass


def _tag_of(v):
    if isinstance(v, Byte) or isinstance(v, bool):
        return BYTE
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
            return struct.unpack(">b", take(1))[0]
        if t == SHORT:
            return struct.unpack(">h", take(2))[0]
        if t == INT:
            return struct.unpack(">i", take(4))[0]
        if t == LONG:
            return struct.unpack(">q", take(8))[0]
        if t == FLOAT:
            return struct.unpack(">f", take(4))[0]
        if t == DOUBLE:
            return struct.unpack(">d", take(8))[0]
        if t == STRING:
            return rstr()
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
