from csv import DictReader
from os.path import dirname, join
from random import randrange
from unittest import TestCase

from sha3 import keccak_384

from iota.crypto.kerl import Kerl
from iota.crypto.kerl.conv import convertToBytes, convertToTrits, \
  trits_to_trytes, trytes_to_trits


class TestKerl(TestCase):
    def test_correct_hash_function(self):
        k = keccak_384()
        k.update('Message'.encode('utf-8'))

        self.assertEqual(
          k.hexdigest(),

          '0c8d6ff6e6a1cf18a0d55b20f0bca160d0d1c914a5e842f3'
          '707a25eeb20a279f6b4e83eda8e43a67697832c7f69f53ca',
        )

    def test_correct_first(self):
        inp = (
          'EMIDYNHBWMBCXVDEFOFWINXTERALUKYYPPHKP9JJ'
          'FGJEIUY9MUDVNFZHMMWZUYUSWAIOWEVTHNWMHANBH'
        )

        trits = trytes_to_trits(inp)

        kerl = Kerl()
        kerl.absorb(trits)
        trits_out = []
        kerl.squeeze(trits_out)

        trytes_out = trits_to_trytes(trits_out)

        self.assertEqual(
          trytes_out,

          'EJEAOOZYSAWFPZQESYDHZCGYNSTWXUMVJOVDWUNZ'
          'JXDGWCLUFGIMZRMGCAZGKNPLBRLGUNYWKLJTYEAQX',
        )

    def test_output_greater_243(self):
        inp = (
          '9MIDYNHBWMBCXVDEFOFWINXTERALUKYYPPHKP9JJ'
          'FGJEIUY9MUDVNFZHMMWZUYUSWAIOWEVTHNWMHANBH'
        )

        trits = trytes_to_trits(inp)

        kerl = Kerl()
        kerl.absorb(trits)
        trits_out = []
        kerl.squeeze(trits_out, length=486)

        trytes_out = trits_to_trytes(trits_out)

        self.assertEqual(
          trytes_out,

          'G9JYBOMPUXHYHKSNRNMMSSZCSHOFYOYNZRSZMAAYWDYEIMVVOGKPJB'
          'VBM9TDPULSFUNMTVXRKFIDOHUXXVYDLFSZYZTWQYTE9SPYYWYTXJYQ'
          '9IFGYOLZXWZBKWZN9QOOTBQMWMUBLEWUEEASRHRTNIQWJQNDWRYLCA',
        )

    def test_input_greater_243(self):
        inp = (
          'G9JYBOMPUXHYHKSNRNMMSSZCSHOFYOYNZRSZMAAYWDYEIMVVOGKPJB'
          'VBM9TDPULSFUNMTVXRKFIDOHUXXVYDLFSZYZTWQYTE9SPYYWYTXJYQ'
          '9IFGYOLZXWZBKWZN9QOOTBQMWMUBLEWUEEASRHRTNIQWJQNDWRYLCA'
        )

        trits = trytes_to_trits(inp)

        kerl = Kerl()
        kerl.absorb(trits)
        trits_out = []
        kerl.squeeze(trits_out, length=486)

        trytes_out = trits_to_trytes(trits_out)

        self.assertEqual(
          trytes_out,

          'LUCKQVACOGBFYSPPVSSOXJEKNSQQRQKPZC9NXFSMQNRQCGGUL9OHVV'
          'KBDSKEQEBKXRNUJSRXYVHJTXBPDWQGNSCDCBAIRHAQCOWZEBSNHIJI'
          'GPZQITIBJQ9LNTDIBTCQ9EUWKHFLGFUVGGUWJONK9GBCDUIMAYMMQX',
        )


    def test_all_bytes(self):
        for i in range(-128, 128):
            in_bytes = [i] * 48
            trits = convertToTrits(in_bytes)
            out_bytes = convertToBytes(trits)

            self.assertEqual(in_bytes, out_bytes)

    def test_random_trits(self):
        in_trits = [randrange(-1,2) for _ in range(243)]
        in_trits[242] = 0
        in_bytes = convertToBytes(in_trits)
        out_trits = convertToTrits(in_bytes)

        self.assertEqual(in_trits, out_trits)

    def test_generate_trytes_hash(self):
        filepath =\
          join(
            dirname(__file__),
            'test_vectors/generate_trytes_and_hashes.csv',
          )

        with open(filepath,'r') as f:
            reader = DictReader(f)
            for count, line in enumerate(reader):
                trytes = line['trytes']
                hashes = line['Kerl_hash']

                trits = trytes_to_trits(trytes)

                kerl = Kerl()
                kerl.absorb(trits)
                trits_out = []
                kerl.squeeze(trits_out)

                trytes_out = trits_to_trytes(trits_out)

                self.assertEqual(
                  hashes,
                  trytes_out,

                  msg =
                    'line {count}: {hashes} != {trytes}'.format(
                      count = count + 2,
                      hashes = hashes,
                      trytes = trytes_out,
                    ),
                )

    def test_generate_multi_trytes_and_hash(self):
        filepath =\
          join(
            dirname(__file__),
            'test_vectors/generate_multi_trytes_and_hash.csv',
          )

        with open(filepath,'r') as f:
            reader = DictReader(f)
            for count, line in enumerate(reader):
                trytes = line['multiTrytes']
                hashes = line['Kerl_hash']

                trits = trytes_to_trits(trytes)

                kerl = Kerl()
                kerl.absorb(trits)
                trits_out = []
                kerl.squeeze(trits_out)

                trytes_out = trits_to_trytes(trits_out)

                self.assertEqual(
                  hashes,
                  trytes_out,

                  msg =
                    'line {count}: {hashes} != {trytes}'.format(
                      count = count + 2,
                      hashes = hashes,
                      trytes = trytes_out,
                    ),
                )

    def test_generate_trytes_and_multi_squeeze(self):
        filepath =\
          join(
            dirname(__file__),
            'test_vectors/generate_trytes_and_multi_squeeze.csv',
          )

        with open(filepath,'r') as f:
            reader = DictReader(f)
            for count, line in enumerate(reader):
                trytes = line['trytes']
                hashes1 = line['Kerl_squeeze1']
                hashes2 = line['Kerl_squeeze2']
                hashes3 = line['Kerl_squeeze3']

                trits = trytes_to_trits(trytes)

                kerl = Kerl()
                kerl.absorb(trits)

                trits_out = []
                kerl.squeeze(trits_out)
                trytes_out = trits_to_trytes(trits_out)

                self.assertEqual(
                  hashes1,
                  trytes_out,

                  msg =
                    'line {count}: {hashes} != {trytes}'.format(
                      count = count + 2,
                      hashes = hashes1,
                      trytes = trytes_out,
                    ),
                )

                trits_out = []
                kerl.squeeze(trits_out)
                trytes_out = trits_to_trytes(trits_out)

                self.assertEqual(
                  hashes2,
                  trytes_out,

                  msg =
                    'line {count}: {hashes} != {trytes}'.format(
                      count = count + 2,
                      hashes = hashes2,
                      trytes = trytes_out,
                    ),
                )

                trits_out = []
                kerl.squeeze(trits_out)
                trytes_out = trits_to_trytes(trits_out)

                self.assertEqual(
                  hashes3,
                  trytes_out,

                  msg =
                    'line {count}: {hashes} != {trytes}'.format(
                      count = count + 2,
                      hashes = hashes3,
                      trytes = trytes_out,
                    ),
                )
