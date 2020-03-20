from typing import List, Dict


BYTE_HASH_LENGTH = 48
TRIT_HASH_LENGTH = 243

tryte_table: Dict[str, List[int]] = {
    '9': [0, 0, 0],  # 0
    'A': [1, 0, 0],  # 1
    'B': [-1, 1, 0],  # 2
    'C': [0, 1, 0],  # 3
    'D': [1, 1, 0],  # 4
    'E': [-1, -1, 1],  # 5
    'F': [0, -1, 1],  # 6
    'G': [1, -1, 1],  # 7
    'H': [-1, 0, 1],  # 8
    'I': [0, 0, 1],  # 9
    'J': [1, 0, 1],  # 10
    'K': [-1, 1, 1],  # 11
    'L': [0, 1, 1],  # 12
    'M': [1, 1, 1],  # 13
    'N': [-1, -1, -1],  # -13
    'O': [0, -1, -1],  # -12
    'P': [1, -1, -1],  # -11
    'Q': [-1, 0, -1],  # -10
    'R': [0, 0, -1],  # -9
    'S': [1, 0, -1],  # -8
    'T': [-1, 1, -1],  # -7
    'U': [0, 1, -1],  # -6
    'V': [1, 1, -1],  # -5
    'W': [-1, -1, 0],  # -4
    'X': [0, -1, 0],  # -3
    'Y': [1, -1, 0],  # -2
    'Z': [-1, 0, 0],  # -1
}

# Invert for trit -> tryte lookup
trit_table = {tuple(v): k for k, v in tryte_table.items()}


def trytes_to_trits(trytes: str) -> List[int]:
    trits = []
    for tryte in trytes:
        trits.extend(tryte_table[tryte])

    return trits


def trits_to_trytes(trits: List[int]) -> str:
    trytes = []
    trits_chunks = [trits[i:i + 3] for i in range(0, len(trits), 3)]

    for trit in trits_chunks:
        trytes.extend(trit_table[tuple(trit)])

    return ''.join(trytes)


def convertToTrits(bytes_k: List[int]) -> List[int]:
    bigInt = convertBytesToBigInt(bytes_k)
    trits = convertBigintToBase(bigInt, 3, TRIT_HASH_LENGTH)
    return trits


def convertToBytes(trits: List[int]) -> List[int]:
    bigInt = convertBaseToBigint(trits, 3)
    bytes_k = convertBigIntToBytes(bigInt)
    return bytes_k


def convertBytesToBigInt(ba: List[int]) -> int:
    # copy of array
    bytesArray = list(map(lambda x: x, ba))

    # number sign in MSB
    signum = (1 if bytesArray[0] >= 0 else -1)

    if signum == -1:
        # sub1
        for pos in reversed(range(len(bytesArray))):
            sub = (bytesArray[pos] & 0xFF) - 1
            bytesArray[pos] = (sub if sub <= 0x7F else sub - 0x100)
            if bytesArray[pos] != -1:
                break

        # 1-compliment
        bytesArray = list(map(lambda x: ~x, bytesArray))

    # sum magnitudes and set sign
    return sum((x & 0xFF) << pos * 8 for (pos, x) in
               enumerate(reversed(bytesArray))) * signum


def convertBigIntToBytes(big: int) -> List[int]:
    bytesArrayTemp = [(abs(big) >> pos * 8) % (1 << 8) for pos in
                      range(48)]

    # big endian and balanced
    bytesArray = list(map(
        lambda x: (x if x <= 0x7F else x - 0x100),
        reversed(bytesArrayTemp)
    ))

    if big < 0:
        # 1-compliment
        bytesArray = list(map(lambda x: ~x, bytesArray))

        # add1
        for pos in reversed(range(len(bytesArray))):
            add = (bytesArray[pos] & 0xFF) + 1
            bytesArray[pos] = (add if add <= 0x7F else add - 0x100)
            if bytesArray[pos] != 0:
                break

    return bytesArray


def convertBaseToBigint(array: List[int], base: int) -> int:
    bigint = 0

    for i in range(len(array)):
        bigint += array[i] * (base ** i)

    return bigint


def convertBigintToBase(bigInt: int, base: int, length: int) -> List[int]:
    result = []

    is_negative = bigInt < 0
    quotient = abs(bigInt)

    MAX = (base - 1) // 2
    if is_negative:
        MAX = base // 2

    for i in range(length):
        quotient, remainder = divmod(quotient, base)

        if remainder > MAX:
            # Lend 1 to the next place so we can make this digit negative.
            quotient += 1
            remainder -= base

        if is_negative:
            remainder = remainder * -1

        result.append(remainder)

    return result


def convert_sign(byte: int) -> int:
    """
    Convert between signed and unsigned bytes.
    """
    if byte < 0:
        return 256 + byte
    elif byte > 127:
        return -256 + byte
    return byte
