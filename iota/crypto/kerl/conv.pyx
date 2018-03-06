# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals
cimport cython
from libc.stdlib cimport malloc, free


BYTE_HASH_LENGTH = 48
TRIT_HASH_LENGTH = 243

tryte_table = {
        '9': [ 0,  0,  0],  #   0
        'A': [ 1,  0,  0],  #   1
        'B': [-1,  1,  0],  #   2
        'C': [ 0,  1,  0],  #   3
        'D': [ 1,  1,  0],  #   4
        'E': [-1, -1,  1],  #   5
        'F': [ 0, -1,  1],  #   6
        'G': [ 1, -1,  1],  #   7
        'H': [-1,  0,  1],  #   8
        'I': [ 0,  0,  1],  #   9
        'J': [ 1,  0,  1],  #  10
        'K': [-1,  1,  1],  #  11
        'L': [ 0,  1,  1],  #  12
        'M': [ 1,  1,  1],  #  13
        'N': [-1, -1, -1],  # -13
        'O': [ 0, -1, -1],  # -12
        'P': [ 1, -1, -1],  # -11
        'Q': [-1,  0, -1],  # -10
        'R': [ 0,  0, -1],  #  -9
        'S': [ 1,  0, -1],  #  -8
        'T': [-1,  1, -1],  #  -7
        'U': [ 0,  1, -1],  #  -6
        'V': [ 1,  1, -1],  #  -5
        'W': [-1, -1,  0],  #  -4
        'X': [ 0, -1,  0],  #  -3
        'Y': [ 1, -1,  0],  #  -2
        'Z': [-1,  0,  0],  #  -1
        }

# Invert for trit -> tryte lookup
trit_table = {tuple(v): k for k, v in tryte_table.items()}

def trytes_to_trits(trytes):
    trits = []
    for tryte in trytes:
        trits.extend(tryte_table[tryte])

    return trits

def trits_to_trytes(trits):
    trytes = []
    trits_chunks = [trits[i:i + 3] for i in range(0, len(trits), 3)]

    for trit in trits_chunks:
        trytes.extend(trit_table[tuple(trit)])

    return ''.join(trytes)

def convertToTrits(bytes_k):
    return convertToTrits2(bytes_k)

def convertToTrits1(bytes_k):
    bigInt = convertBytesToBigInt(bytes_k)
    trits = convertBigintToBase(bigInt, 3, TRIT_HASH_LENGTH)
    return trits

def convertToTrits2(bytes_k):
    return bytes_to_trits(bytes_k)

@cython.boundscheck(False)
def bytes_to_trits(bytes_k):
    cdef int i

    cdef int len_bytesArray = len(bytes_k)

    bytesArray = <int *>malloc(len_bytesArray*cython.sizeof(int))
    if bytesArray is NULL:
        raise MemoryError()

    for i in range(len_bytesArray):
        bytesArray[i] = bytes_k[i]

    # number sign in MSB
    cdef int signum = (1 if bytesArray[0] >= 0 else -1)

    cdef int sub
    if signum == -1:
        # sub1

        for i in range(len_bytesArray-1, -1, -1):
            sub = (bytesArray[i] & 0xFF) - 1
            bytesArray[i] = (sub if sub <= 0x7F else sub - 0x100)
            if bytesArray[i] != -1:
                break

        # 1-compliment
        for i in range(len_bytesArray):
            bytesArray[i] = ~bytesArray[i]

    for i in range(len_bytesArray):
        bytesArray[i] = bytesArray[i] & 0xFF

    cdef int output[243]
    output[:] = [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,

        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,

        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    ]

    cdef int padded_output[248]
    padded_output[:] = [
        0, 0, 0, 0, 0,

        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,

        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,

        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    ]

    cdef int left_pad = 5
    cdef int[:] padded_output_view = padded_output
    cdef int[:] temp0 = padded_output_view[left_pad:]
    cdef int[:] temp1 = padded_output_view[left_pad-1:-1]
    cdef int[:] temp2 = padded_output_view[left_pad-2:-2]
    cdef int[:] temp3 = padded_output_view[left_pad-5:-5]

    cdef int bai, remainder, value, q
    cdef int count = 0
    for bai in range(len_bytesArray):

        for i in range(243):
            output[i] = temp0[i] + temp1[i] + temp2[i] + temp3[i]

        q = 0
        for i in range(243):
            value = output[i] + q
            if (value > 1) or (value < -1):
                remainder = value % 3
                q = value // 3

                if remainder > 1:
                    remainder = -1
                    q += 1

                output[i] = remainder
            else:
                if q:
                    output[i] = output[i] + q
                q = 0

        count = 0
        negative = False

        if bytesArray[bai] < 0:
            negative = True
            bytesArray[bai] = abs(bytesArray[bai])
        while bytesArray[bai] > 0:
            remainder = bytesArray[bai] % 3
            bytesArray[bai] = bytesArray[bai] // 3

            value = remainder + output[count]

            if value > 1:
                value = value -3
                bytesArray[bai] += 1

            output[count] = value

            count += 1

        for i in range(243):
            padded_output[i+left_pad] = output[i]

        if bai == len_bytesArray:
            break

    if signum == -1:
        for i in range(243):
            output[i] *= -1

    return output

def convertToBytes(trits):
    return convertToBytes2(trits)

def convertToBytes1(trits):
    # print(trits)
    bigInt = convertBaseToBigint(trits, 3)
    bytes_k = convertBigintToBytes(bigInt)
    # print(bytes_k)
    return bytes_k

def convertToBytes2(trits_):
    cdef int *trits
    cdef int len_trits = len(trits_)
    cdef int i, j

    trits = <int *>malloc(len_trits*cython.sizeof(int))
    if trits is NULL:
        raise MemoryError()

    for i in range(len_trits):
        trits[i] = trits_[len_trits - 1 - i]

    cdef int output[48]
    output[:] = [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    ]
    cdef int check_index = 0
    cdef int sign = 0
    cdef int carry = 0
    cdef int value

    for i in range(len_trits):
        if sign == 0 and trits[i] != 0:
            sign = trits[i]
        elif sign == 0 and trits[i] == 0:
            continue
        trits[i] = trits[i] * sign
        carry = 0
        for j in range(48):
            if j > check_index:
                break
            value = (output[j] * 3) + carry
            carry = 0
            if value > 255:
                check_index = max(check_index, j + 1)
                carry = value // 256
                value = value % 256
            elif value < -255:
                check_index = max(check_index, j + 1)
                carry = value // -256
                value = value % -256
            output[j] = value
        output[0] += trits[i]

        for j in range(check_index):
            if trits[i] == 1 and output[j] == 256:
                output[j] = 0
                output[j+1] += 1
            elif trits[i] == -1 and output[j] == -1:
                output[j] = 255
                output[j+1] -= 1
            else:
                break

    free(trits)

    cdef int bytesArray[48]
    # big endian and balanced
    for i in range(48):
        if output[i] <= 0x7F:
            bytesArray[48 - 1 - i] = output[i]
        else:
            bytesArray[48 - 1 - i] = output[i] - 0x100

    cdef int add
    if sign < 0:
        # 1-compliment
        for i in range(48):
            bytesArray[i] = ~bytesArray[i]
        # bytesArray = list(map(lambda x: ~x, bytesArray))

        # add1
        for i in range(47, -1, -1):
            add = (bytesArray[i] & <int>0xFF) + 1
            if add <= 0x7F:
                bytesArray[i] = add
            else:
                bytesArray[i] = add - <int>0x100
            if bytesArray[i] != 0:
                break

    return bytesArray

def convertBytesToBigInt(ba):
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


def convertBigintToBytes(big):
    bytesArrayTemp = [(abs(big) >> pos * 8) % (1 << 8) for pos in
                      range(48)]

    # big endian and balanced
    bytesArray = list(map(lambda x: (x if x <= 0x7F else x - 0x100),
                     reversed(bytesArrayTemp)))

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

def convertBaseToBigint(array, base):
    cdef int i
    cdef int len_array = len(array)

    bigint = 0

    for i in range(len_array):
        bigint += array[i] * (base ** i)

    return bigint

def convertBigintToBase(bigInt, int base, int length):
    cdef int remainder, MAX
    result = []

    is_negative = bigInt < 0
    quotient = abs(bigInt)

    MAX = (base-1) // 2
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

def convert_sign(byte):
    """
    Convert between signed and unsigned bytes
    """
    if byte < 0:
        return 256 + byte
    elif byte > 127:
        return -256 + byte
    return byte
