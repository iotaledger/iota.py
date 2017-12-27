# coding=utf-8
from __future__ import absolute_import, division, print_function, \
  unicode_literals

from unittest import TestCase

from six import binary_type, text_type

from iota import Address, AddressChecksum, AsciiTrytesCodec, Hash, Tag, \
  TryteString, TrytesDecodeError, TransactionTrytes, TransactionHash


# noinspection SpellCheckingInspection
class TryteStringConvertBytesTestCase(TestCase):
  def test_transaction_hash(self):
    txh = TransactionHash(b'CHVXYIMWTDHTBXGEUMNSAS9WMLNSGNYGI9NGKUMCQAZONLMYLQXFVBKNVLATTLWNCNFNBNIPJULFA9999')
    bytes_ = (b'\xe8\xf2\xedu\xa4">\x05>V\xd5\xb4\x1c\xaet\xa08\x8d\xc8\x1c\x8b=@\x1f'
             b'\x11\xfd\x87x\xfb\xaa\xac\xa1d_t\xc1J\xa4\x17\xa2\x89\x8c\xd3\x1dj!\x00'
             b'\x00\x00')
    self.assertEqual(txh.as_bytes(), bytes_)
    self.assertEqual(TransactionHash.from_bytes(bytes_), txh)

  def test_tag(self):
    tag = Hash(b'EXAMPLE')
    bytes_ = (b'\xb4T\xa1\xa0\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
              b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
              b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

    self.assertEqual(tag.as_bytes(), bytes_)
    self.assertEqual(Hash.from_bytes(bytes_), tag)

  def test_transaction_trytes(self):
    txt = TransactionTrytes(
      (b'BVWUTCNFCTBHZHF9HPLVUGWOPHYQYEIBWDPAXNGZTKXWXXZD9GATQKDQOGQZKGNYCFMGYJ'
       b'9BCCFU9JYTKDYLRRZOXSYZGLTODYEXAYWMDZOSREGLOYJMINYEKVVUEHHUDMQNVOBIDJGH'
       b'LRVONVFPMFUMFWKXEQG9YVOBUXCWFBVASSAWHJQATDHHUKQORNJLNOEYDKIRYOT9APCJFK'
       b'GP99IJDHD9BMEVS9JGJJOZXFVJKHHJ9HDEWJUTCPT9CNVEZLXLDKKWCEZ9ZNMUYEGSQVTM'
       b'SFMW9DGALROMSXUGRAUCEJQG9BDEXEEMNSKGFEFSFNUWIGPUMETHMDGHSGFHKBFEBCBEPI'
       b'XTVHLIKVEPK9WNXSACJNKTONWLFJLEPFIWBCKJZPYP9VHKJTRTNORKOETDDTZPJDXLVPTK'
       b'LT99RIQSFBC9PDXEOSLOKXTBQSUXFKGZCQSMQRRUVQYEG9JDGFKLAKPZA9QDF9OLORFURS'
       b'KQLFWEKCNPM9XAE9HXV9QVKUFUADBXIWEKDLHNFLZ9CFSSSIMLLHQMGXJOAPGCSGIAWOQM'
       b'BWURGABAETJLLGRCFURCSXHPHLWITZFEDKXJIVCGIEAHJRFRWERLYULRLXBHVMZISUGQZT'
       b'OONMV9SXGTALLYVLI9VZOXKOLKAWTLJNRPGPGTIACCQCNHHUROBBEAERNKAA9WSSGXR9LP'
       b'X9GKKZTKUYM9XBVBVKCZFX9K9NPDDBYPZPGSTFYCDDFXRHQRHDDPWWRQTSNPKZTMDMXSRE'
       b'INPIQBGUXT9IOIMGEA9TFTHFACNPPBZWAIAATNIK9CSSI9BMYVIXCLLFRIPXQUL9VMOSBZ'
       b'YWXQCGYIWQJHDCJKLJBPVXULGNFYHCHHKAIHALEQBOIKKSWOE9ZMXNVAJLKYVBFGEPYPVY'
       b'PXCIHUUKNJPNQASXXFBIND9XOTU9JQNKNUTGNYLGUICKSJDBISZVMDOZKRIBPCAMYBBFTG'
       b'TYHYMFPLXJVCGWLOSA9NZRSWIJZYKWHYXYDUGNGYI999VQUAT9NJTUJAYBKBUN9CUUIGMU'
       b'9SQAHLVDYBDVTZMHIGBJMEWBNUHQLWAIARCUJJBTTTHUSLAUEMAUQIFEQNV9KQYZJFXXXF'
       b'SIOKQBTGMAMRSFIHEDKUZVUSOCTGQQZBHVUFDFYRLQXLTDCOTHWXOAJDLNKPWXAUKWQXQP'
       b'GY9IXMDWHZJUFWBQVTBNHO9XUPKLWHMPIAYMRSLWVBAMYMTUKFHTOFQIWLWXLGYUUWXJHE'
       b'RTGUGGSKUYOUZKFUXDRFEBSM9PPWCUVOKSBBXCZGPTKNPFCEOVDTCMFXYCRJXH9VFLANDF'
       b'XZEGJVFNNGQMIM9DYBHKRQLDYGDAUXVKDFKZEWDHZUTTOLRVY9XGEFVRHTCOEHGPT9A9SO'
       b'YRSLCNKOBYZCTSIYRDN9CQHZRAVEAHDTOUWS9SCUTYXKJGXW9DDVUYBKL9VCTJGWUDTMZH'
       b'XRNHVGCGWMDLMFXEKWFEGGFGXLBX9YUFQPDUMNPAAXNWPRQWKUCUCXMQMNPAUNOFXCQQNX'
       b'GHQWMLZHPMKDZEJRRZNMLMSQ9UWEIPQATAIEUCTNZQYNXWSQPJQCQ9XFAHQOSAYWVMQVIF'
       b'JPPKUGFBJKVUVLWQVIFCUIMQHKGFSZIGZFIQZJECUCHXAWYDM9PYXPLWPPHXTZ9CVRYXZQ'
       b'HUHLSLJ9IVAWWWJGPXTKDUYARLOHGMSAWSMPFAXJTJNB9PTRGVMYQEVPDOKKHTOPOILMBR'
       b'QB9MWYGHEHRBJLDVCHHQBYPALXEAGQYQRSAFYKUYAJBXMGVMBHRR9RISZRZVJYOMYTDUJO'
       b'EIEDRBWOBFZSSIUXK99RXDYAEGAH9ROJWTETQUHYJYAJVG9CKUHRANRUBJYXGPSXVKKXPS'
       b'BGWKBRGFXFZNOHXNSFPIPAZHCMCKGAUJRXGCCOKLFRXNCXJGGJZNONSCYRIBWKGYIMUPBW'
       b'FBLERFFNXPMGTGLEHHHSEYBVC9VONAYLNZWIRLINAXLLQXPDYSBWACVQHHRCEZCWYYPXWN'
       b'KWZSMYPNAMYOOUOCIYYZOODLUB9ES9Q9BMRHTXMUKDPUWWBAWKIZWSGN9XKUHAJWGRKRHS'
       b'HUPKAUPPQPMRSJJFHBPDQGWTY9DYFEMEIBJ9RXYSYMDHNRPQVZ9HWOFVT9I9CDNYYCKDM9'
       b'TQQFVZCHWJMNQWZV9KPWCHICGJZXKE9GSUDXZYUAPLHAKAHYHDXNPHENTERYMMBQOPSQID'
       b'ENXKLKCEYCPVTZQLEEJVYJZV9BWU999999999999999999999999999QRFM99999999999'
       b'999999999999SUYEEXD99999999999A99999999SSSFJDJAJ9HBHQSDSGZQIRUYXIQTSMC'
       b'JZUDBRQXTWVDMDAAWALGPXAZUXGF9ATJJ9BQHMHORGF9VBHBAZSGVAWACCHIGS9CCPXJYJ'
       b'KOWAA9YERRVGIHRVKPMSKOLQGGYENRIXZXRKHJDDKKPPZBOVEUWMDEBVA9999OBDZAJUQM'
       b'ZXX9RAQO9CYLLIONKQWRSTYDPRJKIWTHXOAWAZUII9QRLAML9BXCXTGYREN9IIDRNDQ999'
       b'99999999999999999999999999999999999999999999999999999999YZTZAFBXOBRHZM'
       b'XZG9OUBFJMOBL'))
    bytes_ = (b'n\xf3\xbf\x97\x11\xc2\xe7\xad9\xe5\xe0\xd7\xc4\xf5\x99\xd23,?E\x9e\xb0*\xf9/\xa7\xe4\xe2\x0c?'
        b'7\x90(\xa5\xc3\xf4\xd5+\x1argY6\t7\xfao\xc0w\xfa\xb3\xdc\xdc\xb7\xe3\x15\xc5`\xa9\xe7'
        b'\xcbE(\xae\xe7*X.Y\r+,w\xf0+\xed@v\x8a\xf0\x0euoJ\x0c\xf0\x87\xaa1:'
        b'f\xc2b\x914\x02j\x8a\xcbN\xf4\x14\x169\x06\xe1\xce\x06e\xc7\xcd\xf0\xdb\x88[\xda)j!\xb2'
        b'\xad\xea\tF\x1ee\xd1\xffQvi\x01na\xb6\x1bg]\xd9\xf7\xd5@\xc8]\xe5\xbc\xde[\xea\x9e'
        b'\xf9\xb8\xcf\xea$k:\xd1\x1a\xea\xaf\x8b^\xa8A\xdd\x9fs\xa7\xd7\xff\xce\x04\xb3`\xe9\xc9\x07\x02\x19'
        b' 4\x02n\x0f,q+`\xb6\x10\xba\x9a\x9cP\xd1>1\xdey@#\x14JA\xc1\x149`M'
        b'3\x9fo?\xa1\x9f\x0b\xa3\xe1\x13Z\x8eA\x8a\xd8\xbb\x1f1\xa4\xcb\x119\xce\x9d\xc8PF&\xec\xbe'
        b'\xa2\x93\x98;\\\xc2\xc9n\xe6x\x8daB\xff\xaf\xee\xe7\x14\x030\xe6\xb4\xe7\x98\xba\x9a\xa7I\xf6e'
        b'\xec\xb8\xb5\xf2\xe4\xc7\xe0\xa8A\x1b^8\\\xb3\xa1\x1a\xaf!\x06\xdc\x98\xa6\xef\xb5\xf0#\xde;\xb9\x99'
        b'\rH-\xe5I\xfeb 4\x15\xbb\xe6\x9d\xbe(\xf1\xdan\xff\t\xba\x13kp\xf14C\x18.\x9d'
        b'X9S\x95\x8br\x96\xee<7\xb2\xc3[v\xb1\xb2\xef\x18\xa7iD\xa0\xca\xf5\x9a\xbc\xe9\n\xf2@'
        b'\x9d\xb3]\xa6\x95,H\xfbjH\xa7Ig\xfe\xbb\xc4\x92\xc1\xa3)\xd7\x1bG\xc3Rv\xd2\x0cR\xf5'
        b'\xa3!h&\xa3j\x9e5;\xbf\xec\x0cT\xe2\x8c\xed\xef\x918`-\x8bq\t\x949<\xfd\xff\xa1'
        b"\xfd\xc4g5 \xec\r\xa6\xd4n \xf8\xb5\xaf\x04\xbd\\\x13\xc8M;.b\x1ap\x12\xae\xed\x93'"
        b'\xce\xa2\xae,\x96\x99\xf0<(\xbc\xe8*\x9d\xde\xa9\xcc\xef\xc0\x00\xddx\x9b\x04\xc1<\x17\x0b\x97/\x0e'
        b'\x93\x03\x0c7\xd8fQ9N6x\xd2\xb8\tp\x06k\xe1G#\xd3\xbc\x96\xf8\x92\xa6\x18\xd1\xca\xa5'
        b'\xef\r[\\\xce\x9e\xaa\xeeC\xa2\xaa\x1e\xedsQ#\xd3\xa8\xb1\xc9g\x8c\x8b\x02k\xa7\xcf\x1c\xd4\xf2'
        b'1c/\xbf0\xec\xa4\tKK\xcfV\x892\xb8\xac\xc1R_\x00\x93JP\xa9)\xda\xbf\x9b\xf9C'
        b'\xfa\xb9\xbcv\x06\xbbkw\x955\xe6\x15FT\xf28\xc1=\xc3it\xd0#YL\xc4k\x0f\x02\x8b'
        b'\xff\x96P\xef\xa9\xe0\xd2H#\xc4+\xf0\t\x00\xd3G\xb1\xfe\x0e\xecX\xcb\xb5\x16\x8e\xff\xcb\xfag\xce'
        b"\x1b2Hx\\\x11p\x99u\x08\xc5[\xa1\xa4\x8c\xdf\xe3\xe0\x01\x04\x18\x15\xce\xc2/\x17\xb6'\x9dw"
        b'R\xe19\xea)\xfe\xf0\xa8Z\xb5\xf75\xf8\x8c\xaa8e\r\r\xe7S\x9c\xbc\xcek>\x919\xc3\xa3'
        b'5i\xc8rc\xae\xf1\xf6\xc5U\x8bF\xab-ZU\x89\xa1\xab\x03a\xe1\xa5\x9a\xd1\x00\xe8y\xa3\xfa'
        b'[\xc0\x11b\x99\x8c\xb7\xff\xc9+\xd4G\xd7k\xee\r\xe7\xe01T\xf2C\x9c:>\xdb\xa8\x9d\xd3\xe4'
        b'\xd6\xfb\xc8\xab\xcd0-\x14=" \xecE\xab:\xa9\x0c3;9\x04\xbf\xf3\xcb\xaaq\x0f\xb1\xb8?'
        b"+\xcf\x99W\x0f\xcf:Y:\xc7\tW\xe2R4'*7\xe2`\\\xaa\x89;bm\x04\xce\xb5f"
        b'\xdct\xefs\x03\xe31\re\x93FIP\x99\x92\x0cA\xff\xc7\x10\xd5\xdc\xec\x95\xeag\xbd\x1bQ\x91'
        b'\xfe\xe7\x1f)\x8c\xefP<N\xfe\xba\xfc\xe8\xc6\xafm_H:\xdb\xda\xf8\xe8\xcb\xc3\xa6^\xb6\xf4$'
        b'p>\x11\\R\x19\x14\xc5\xc9:\xd5H\xfd\x87\xd6X\xc4tU(\xe7;\xf5/\xd1d\xe7B\xf7\xee'
        b'\xa94 f+\x05\xb0\x88\x9c\xdc\xa2\xceT\x08tb+\x05\x8e\xdb\xe7\xe8\x90\xe1\xec\x92t\xf1iq'
        b'w\xac\\\xf7\xabqx\x98\xfd\x8e\x0f\xa0\x11<QV\xb7\x89\xe4\xa8\xe1\x172VG\xe2\xe5!\xc7\x91'
        b'\x13\xa9\xd2\xf2\xf09\xd4\x8d\xce\xb6XfL\xf0\xe0b\x1a\x1d\xfa\xd7E\xd5d\xf4\xd3\xfeS\xdb\xcd\x1d'
        b"K\x18\x08\xc6]\x04\xbfHh\xc6\x8d\xe8\xde\x00\xd4\xc1\xa6\xa6Y\x17\xbc'\x01\xd6\x95\xa3Y\xd1\xa5a"
        b'UJ\xaf\xbbhw\x13Er\xa4\x04Y\x14\x89\x01+5\xd5\xd7\x91\xd5a\x8bg>,\x90Z\xd7\xb0'
        b',Q\xe0\xc8\xc8J-\x1e(L\xc7\xa9\xcc0l\x91U\xa8\xe35\x06\xd0!\xec\x1c\x07ts\xd5I'
        b'\xf7\xffN\xdd\x94\xd3\xd4-\xf2e?\x97\x05a\xb0\x96\x8b7\x1a\xe7\xcd3\x01\xafiK-"\x18\xaf'
        b'\x0f\xa4+\xde\x9c\xf1\xd4T\xd6\x07\xb8\xce\x08\xb1\xab0o\xe4\xd1\xe7\xd2AI\xb4\xcc\xa4\x16\xc1\x135'
        b'\x93\x8a\xe8\x0ebM\x10\xac\x1e^r\x0b\x15\xe6>T\x8bp\x06\xa5\x17\x18g\\\x93\x8a\xb4\xcd\xe5\x15'
        b'2gP^\x8d\xdd<\xd3\xb1\xb5\xda\x9c\xd7=n\xea\xc8\xbb\xcfW\x19l\x8a\x05O\x89\xdc\t#\x8e'
        b'\xb0$\xaa\xc7\\\xb7\x96\x03\xd4\xdb\x19\x18\xea\xb8\xed\xc8\xa5\x8a\x9fNr\xc8)u\xad\xdb\x92\x03L\xf6'
        b'\xa3\x0b\xce\x02`\xfd\xf6W\xb3>G\xcew\xdf\xda2\xb2b\xeeE<\xf3\xa6\xce#\xcd>-\x95\xbb'
        b'Y\x8d\r\xc4\x8d\x9a\r8]\xebX \xc0\xa4\xecl\xfa/\xa1\xcb[\x00G\xb7j\xbc\x8e\xc12\xf5'
        b'\xe5\xf521\xff\x03o*\xed9^\x04\xde\xe1\xd5P\xc7Y\xa1\x90\xf6\xfbr\xd8\xe8\x1c@\xef\xa61'
        b'\xca\xe9"\xe2\xfa\x07Fjc\xe6\xaa\'\x91\x8d0)\x0e\xeby\xb6\x91\x10\xe1\'\x99\xa5p\\`\x1a'
        b'a\x99\xa6\xa0a\xd6\x19O\xfe\x96\xee\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf6b\x04'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe8\xec\x99I\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\xb8'
        b"\x13b'%\x1eH\xe74!\xc2\xadNH\xf9P,8\x1f\xef?\x13\xdc\xa5\xdagx\n\x95\x03C"
        b'\xa4\xb2\xca\xc7\x13\t\x14\x1f\x12\xdb\xd7\x97\xc1\x13\xd3\xe7X\xf7\xc2C\xdcR\xb8T"\xff\x1c\xa4oY'
        b'\xbaD\t\xca\x0f\xac\xc5\xcb\xb211\xbc\xba\xd2<\xd1\xbe\xab\xb8\xfd\xae\xf0p%A1\xf3\xb1\x9f\xcc'
        b'h\xbc\x14\x16\x00\x00\xafV\xf8\x1c\x9er\xae\xf7\xaf\xe6\xdb\x1bO%\x97)\x92\xae.J\x9e\x12"\xdf'
        b'\xde\xf8\x05\x17\xfdO\t\xe2im%\x12N\xa6=\xfe\xbd\xfc\t\r\x88\xe9\xff\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xca\xac\xf5'
        b'\xb0\x07\x93\x02\xc6u\xe2\x15\x940cx*$')

    self.assertEqual(txt.as_bytes(), bytes_)
    self.assertEqual(TransactionTrytes.from_bytes(bytes_), txt)

  def test_address(self):
    address = Address(b'KPWCHICGJZXKE9GSUDXZYUAPLHAKAHYHDXNPHENTERYMMBQOPSQIDENXKLKCEYCPVTZQLEEJVYJZV9BWU')
    bytes_ = (b'\xd5\xf3IZf\xfa3\x10?I\x0b\xf6OSh#rH\xe3\r\x8a\xda\xbf\xbd'
              b'\x05Jy\xe7,\xb4\xf6\xbc\x8d3\xd4\x1f\xcfZ\xcf\xde\xe21 CYk\xae'
              b'\xdd\xfa')

    self.assertEqual(address.as_bytes(), bytes_)
    self.assertEqual(Address.from_bytes(bytes_), bytes_)

  def test_tryte_string(self):
    ts = TryteString(b'HELLOIOTA')
    bytes_0 = b''
    bytes_10 = b'\x9c%'
    bytes_27 = b'\x9c%\x98\xb8;\x00'

    # as_bytes length indicate how many trits want to convert to bytes
    self.assertEqual(ts.as_bytes(length=0), bytes_0)
    self.assertEqual(ts.as_bytes(length=10), bytes_10)
    self.assertEqual(ts.as_bytes(length=27), bytes_27)
    self.assertEqual(ts.as_bytes(), bytes_27)
    with self.assertRaises(IndexError):
      ts.as_bytes(length=28)
    with self.assertRaises(IndexError):
      ts.as_bytes(length=48)

    # from_bytes length indicate how may trits you want to convert to, it will
    # then convert trits to tryte string
    self.assertEqual(TryteString.from_bytes(bytes_0, length=0), TryteString(b''))
    self.assertEqual(TryteString.from_bytes(bytes_0, length=10), TryteString(b'9999'))
    self.assertEqual(TryteString.from_bytes(bytes_0, length=27), TryteString(b'999999999'))

    self.assertEqual(TryteString.from_bytes(bytes_10, length=0), TryteString(b''))
    self.assertEqual(TryteString.from_bytes(bytes_10, length=1), TryteString(b'Z'))
    self.assertEqual(TryteString.from_bytes(bytes_10, length=10), TryteString(b'HEL9'))
    self.assertEqual(TryteString.from_bytes(bytes_10, length=27), TryteString(b'HEL999999'))

    self.assertEqual(TryteString.from_bytes(bytes_27, length=0), TryteString(b''))
    self.assertEqual(TryteString.from_bytes(bytes_10, length=1), TryteString(b'Z'))
    self.assertEqual(TryteString.from_bytes(bytes_27, length=10), TryteString(b'HEL9'))
    self.assertEqual(TryteString.from_bytes(bytes_27, length=27), TryteString(b'HELLOIOTA'))
    self.assertEqual(TryteString.from_bytes(bytes_27, length=48), TryteString(b'HELLOIOTA9999999'))

    # from_bytes can auto triming trailing 9 when not providing length
    self.assertEqual(TryteString.from_bytes(bytes_27), TryteString(b'HELLOIOTA'))

  def test_empty_tryte_string(self):
    ts = TryteString(b'')

    self.assertEqual(ts.as_bytes(), b'')
    self.assertEqual(ts.as_bytes(length=0), b'')
    with self.assertRaises(IndexError):
      ts.as_bytes(length=1)

    self.assertEqual(TryteString.from_bytes(b''), TryteString(b''))
    self.assertEqual(TryteString.from_bytes(b'', length=1), TryteString(b'9'))
    self.assertEqual(TryteString.from_bytes(b'', length=2), TryteString(b'9'))
    self.assertEqual(TryteString.from_bytes(b'', length=3), TryteString(b'9'))
    self.assertEqual(TryteString.from_bytes(b'', length=4), TryteString(b'99'))
    self.assertEqual(TryteString.from_bytes(b'', length=5), TryteString(b'99'))
    self.assertEqual(TryteString.from_bytes(b'', length=6), TryteString(b'99'))
    self.assertEqual(TryteString.from_bytes(b'', length=7), TryteString(b'999'))
    self.assertEqual(TryteString.from_bytes(b'', length=8), TryteString(b'999'))
    self.assertEqual(TryteString.from_bytes(b'', length=9), TryteString(b'999'))
    self.assertEqual(TryteString.from_bytes(b'', length=10), TryteString(b'9999'))
    self.assertEqual(TryteString.from_bytes(b'', length=11), TryteString(b'9999'))
    self.assertEqual(TryteString.from_bytes(b'', length=12), TryteString(b'9999'))
    self.assertEqual(TryteString.from_bytes(b'', length=13), TryteString(b'99999'))


# noinspection SpellCheckingInspection
class TryteStringTestCase(TestCase):
  def test_ascii_bytes(self):
    """
    Getting an ASCII representation of a TryteString, as bytes.
    """
    self.assertEqual(
      binary_type(TryteString(b'HELLOIOTA')),
      b'HELLOIOTA',
    )

  def test_ascii_str(self):
    """
    Getting an ASCII representation of a TryteString, as a unicode
    string.
    """
    self.assertEqual(
      text_type(TryteString(b'HELLOIOTA')),
      'HELLOIOTA',
    )

  def test_comparison(self):
    """
    Comparing TryteStrings for equality.
    """
    trytes1 = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')
    trytes2 = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')
    trytes3 = TryteString(
      b'CCPCBDVC9DTCEAKDXC9D9DEARCWCPCBDVCTCEAHDWCTCEAKDCDFD9DSCSA',
    )

    self.assertTrue(trytes1 == trytes2)
    self.assertFalse(trytes1 != trytes2)

    self.assertFalse(trytes1 == trytes3)
    self.assertTrue(trytes1 != trytes3)

    self.assertTrue(trytes1 is trytes1)
    self.assertFalse(trytes1 is not trytes1)

    self.assertFalse(trytes1 is trytes2)
    self.assertTrue(trytes1 is not trytes2)

    self.assertFalse(trytes1 is trytes3)
    self.assertTrue(trytes1 is not trytes3)

    # Comparing against strings is also allowed.
    self.assertTrue(trytes1 == b'RBTC9D9DCDQAEASBYBCCKBFA')
    self.assertFalse(trytes1 != b'RBTC9D9DCDQAEASBYBCCKBFA')
    self.assertFalse(trytes3 == b'RBTC9D9DCDQAEASBYBCCKBFA')
    self.assertTrue(trytes3 != b'RBTC9D9DCDQAEASBYBCCKBFA')

    self.assertTrue(trytes1 == 'RBTC9D9DCDQAEASBYBCCKBFA')
    self.assertFalse(trytes1 != 'RBTC9D9DCDQAEASBYBCCKBFA')
    self.assertFalse(trytes3 == 'RBTC9D9DCDQAEASBYBCCKBFA')
    self.assertTrue(trytes3 != 'RBTC9D9DCDQAEASBYBCCKBFA')

    # Ditto for bytearrays.
    self.assertTrue(trytes1 == bytearray(b'RBTC9D9DCDQAEASBYBCCKBFA'))
    self.assertFalse(trytes1 != bytearray(b'RBTC9D9DCDQAEASBYBCCKBFA'))
    self.assertFalse(trytes3 == bytearray(b'RBTC9D9DCDQAEASBYBCCKBFA'))
    self.assertTrue(trytes3 != bytearray(b'RBTC9D9DCDQAEASBYBCCKBFA'))

  # noinspection PyTypeChecker
  def test_comparison_error_wrong_type(self):
    """
    Attempting to compare a TryteString with something that is not a
    TrytesCompatible.
    """
    trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

    with self.assertRaises(TypeError):
      # TryteString is not a numeric type, so comparing against a
      # numeric value doesn't make any sense.
      # noinspection PyStatementEffect
      trytes == 42

    # Identity comparison still works though.
    self.assertFalse(trytes is 'RBTC9D9DCDQAEASBYBCCKBFA')
    self.assertTrue(trytes is not 'RBTC9D9DCDQAEASBYBCCKBFA')

  def test_bool_cast(self):
    """
    Casting a TryteString as a boolean.
    """
    # Empty TryteString evaluates to False.
    self.assertIs(bool(TryteString(b'')), False)

    # TryteString that is nothing but padding also evaluates to False.
    self.assertIs(bool(TryteString(b'9')), False)
    self.assertIs(bool(TryteString(b'', pad=1024)), False)

    # A single non-padding tryte evaluates to True.
    self.assertIs(bool(TryteString(b'A')), True)
    self.assertIs(bool(TryteString(b'9'*1024 + b'Z')), True)

  def test_container(self):
    """
    Checking whether a TryteString contains a sequence.
    """
    trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

    self.assertTrue(trytes in trytes)
    self.assertTrue(TryteString(b'RBTC9D') in trytes)
    self.assertTrue(TryteString(b'DQAEAS') in trytes)
    self.assertTrue(TryteString(b'CCKBFA') in trytes)

    self.assertFalse(TryteString(b'9RBTC9D9DCDQAEASBYBCCKBFA') in trytes)
    self.assertFalse(TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA9') in trytes)
    self.assertFalse(TryteString(b'RBTC9D9DCDQA9EASBYBCCKBFA') in trytes)
    self.assertFalse(TryteString(b'X') in trytes)

    # Any TrytesCompatible value will work here.
    self.assertTrue(b'EASBY' in trytes)
    self.assertTrue('EASBY' in trytes)
    self.assertFalse(b'QQQ' in trytes)
    self.assertFalse('QQQ' in trytes)
    self.assertTrue(bytearray(b'CCKBF') in trytes)
    self.assertFalse(bytearray(b'ZZZ') in trytes)

  def test_container_error_wrong_type(self):
    """
    Checking whether a TryteString contains a sequence with an
    incompatible type.
    """
    trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

    with self.assertRaises(TypeError):
      # TryteString is not a numeric type, so this makes about as much
      # sense as ``16 in b'Hello, world!'``.
      # noinspection PyStatementEffect,PyTypeChecker
      16 in trytes

    with self.assertRaises(TypeError):
      # This is too ambiguous.  Is this a list of trit values that can
      # appar anywhere in the tryte sequence, or does it have to match
      # a tryte exactly?
      # noinspection PyStatementEffect,PyTypeChecker
      [0, 1, 1, 0, -1, 0] in trytes

    with self.assertRaises(TypeError):
      # This makes more sense than the previous example, but for
      # consistency, we will not allow checking for trytes inside
      # of a TryteString.
      # noinspection PyStatementEffect,PyTypeChecker
      [[0, 0, 0], [1, 1, 0]] in trytes

    with self.assertRaises(TypeError):
      # Did I miss something? When did we get to DisneyLand?
      # noinspection PyStatementEffect,PyTypeChecker
      None in trytes

  def test_concatenation(self):
    """
    Concatenating TryteStrings with TrytesCompatibles.
    """
    trytes1 = TryteString(b'RBTC9D9DCDQA')
    trytes2 = TryteString(b'EASBYBCCKBFA')

    concat = trytes1 + trytes2
    self.assertIsInstance(concat, TryteString)
    self.assertEqual(binary_type(concat), b'RBTC9D9DCDQAEASBYBCCKBFA')

    # You can also concatenate a TryteString with any TrytesCompatible.
    self.assertEqual(
      binary_type(trytes1 + b'EASBYBCCKBFA'),
      b'RBTC9D9DCDQAEASBYBCCKBFA',
    )

    self.assertEqual(
      binary_type(trytes1 + 'EASBYBCCKBFA'),
      b'RBTC9D9DCDQAEASBYBCCKBFA',
    )

    self.assertEqual(
      binary_type(trytes1 + bytearray(b'EASBYBCCKBFA')),
      b'RBTC9D9DCDQAEASBYBCCKBFA',
    )

  def test_concatenation_error_wrong_type(self):
    """
    Attempting to concatenate a TryteString with something that is not
    a TrytesCompatible.
    """
    trytes = TryteString(b'RBTC9D9DCDQA')

    with self.assertRaises(TypeError):
      # TryteString is not a numeric type, so adding a numeric value
      # doesn't make any sense.
      trytes += 42

    with self.assertRaises(TypeError):
      # What is this I don't even..
      trytes += None

  def test_slice_accessor(self):
    """
    Taking slices of a TryteString.
    """
    ts = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

    self.assertEqual(ts[4], TryteString(b'9'))
    self.assertEqual(ts[:4], TryteString(b'RBTC'))
    self.assertEqual(ts[:-4], TryteString(b'RBTC9D9DCDQAEASBYBCC'))
    self.assertEqual(ts[4:], TryteString(b'9D9DCDQAEASBYBCCKBFA'))
    self.assertEqual(ts[-4:], TryteString(b'KBFA'))
    self.assertEqual(ts[4:-4:4], TryteString(b'9CEY'))

    with self.assertRaises(IndexError):
      # noinspection PyStatementEffect
      ts[42]

    # To match the behavior of built-in types, TryteString will allow
    # you to access a slice that occurs after the end of the sequence.
    # There's nothing in it, of course, but you can access it.
    self.assertEqual(ts[42:43], TryteString(b''))

  def test_slice_mutator(self):
    """
    Modifying slices of a TryteString.
    """
    ts = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

    ts[4] = TryteString(b'A')
    self.assertEqual(ts, TryteString(b'RBTCAD9DCDQAEASBYBCCKBFA'))

    ts[:4] = TryteString(b'BCDE')
    self.assertEqual(ts, TryteString(b'BCDEAD9DCDQAEASBYBCCKBFA'))

    # The lengths do not have to be the same...
    ts[:-4] = TryteString(b'EFGHIJ')
    self.assertEqual(ts, TryteString(b'EFGHIJKBFA'))

    # ... unless you are trying to set a single tryte.
    with self.assertRaises(ValueError):
      ts[4] = TryteString(b'99')

    # Any TrytesCompatible value will work.
    ts[3:-3] = b'FOOBAR'
    self.assertEqual(ts, TryteString(b'EFGFOOBARBFA'))

    # I have no idea why you would ever need to do this, but I'm not
    # going to judge, either.
    ts[2:-2:2] = b'IOTA'
    self.assertEqual(ts, TryteString(b'EFIFOOTAABFA'))

    with self.assertRaises(IndexError):
      ts[42] = b'9'

    # To match the behavior of built-in types, TryteString will allow
    # you to modify a slice that occurs after the end of the sequence.
    ts[42:43] = TryteString(b'9')
    self.assertEqual(ts, TryteString(b'EFIFOOTAABFA9'))

  def test_iter_chunks(self):
    """
    Iterating over a TryteString in constant-size chunks.
    """
    trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

    self.assertListEqual(
      list(trytes.iter_chunks(9)),

      [
        TryteString(b'RBTC9D9DC'),
        TryteString(b'DQAEASBYB'),
        # The final chunk is padded as necessary.
        TryteString(b'CCKBFA999'),
      ],
    )

  def test_init_from_unicode_string(self):
    """
    Initializing a TryteString from a unicode string.
    """
    trytes1 = TryteString('RBTC9D9DCDQAEASBYBCCKBFA')
    trytes2 = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')

    self.assertEqual(trytes1, trytes2)

  def test_init_from_unicode_string_error_not_ascii(self):
    """
    Attempting to initialize a TryteString from a unicode string that
    contains non-ASCII characters.
    """
    with self.assertRaises(UnicodeEncodeError):
      TryteString('¡Hola, IOTA!')

  def test_init_from_tryte_string(self):
    """
    Initializing a TryteString from another TryteString.
    """
    trytes1 = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')
    trytes2 = TryteString(trytes1)

    self.assertFalse(trytes1 is trytes2)
    self.assertTrue(trytes1 == trytes2)

  def test_init_from_tryte_string_error_wrong_subclass(self):
    """
    Initializing a TryteString from a conflicting subclass instance.

    This restriction does not apply when initializing a TryteString
    instance; only subclasses.
    """
    tag = Tag(b'RBTC9D9DCDQAEASBYBCCKBFA')

    with self.assertRaises(TypeError):
      # When initializing a subclassed TryteString, you have to use the
      # same type (or a generic TryteString).
      Address(tag)

    # If you are 110% confident that you know what you are doing, you
    # can force the conversion by casting as a generic TryteString
    # first.
    addy = Address(TryteString(tag))

    self.assertEqual(
      binary_type(addy),

      b'RBTC9D9DCDQAEASBYBCCKBFA9999999999999999'
      b'99999999999999999999999999999999999999999',
    )

  def test_init_padding(self):
    """
    Apply padding to ensure a TryteString has a minimum length.
    """
    trytes = TryteString(
      trytes =
        b'ZJVYUGTDRPDYFGFXMKOTV9ZWSGFK9CFPXTITQL'
        b'QNLPPG9YNAARMKNKYQO9GSCSBIOTGMLJUFLZWSY',

      pad = 81,
    )

    self.assertEqual(
      binary_type(trytes),

      # Note the additional Tryte([-1, -1, -1]) values appended to the
      #   end of the sequence (represented in ASCII as '9').
      b'ZJVYUGTDRPDYFGFXMKOTV9ZWSGFK9CFPXTITQLQN'
      b'LPPG9YNAARMKNKYQO9GSCSBIOTGMLJUFLZWSY9999'
    )

  def test_init_from_tryte_string_with_padding(self):
    """
    Initializing a TryteString from another TryteString, and padding
    the new one to a specific length.
    """
    trytes1 = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')
    trytes2 = TryteString(trytes1, pad=27)

    self.assertFalse(trytes1 is trytes2)
    self.assertFalse(trytes1 == trytes2)

    self.assertEqual(binary_type(trytes2), b'RBTC9D9DCDQAEASBYBCCKBFA999')

  def test_init_error_invalid_characters(self):
    """
    Attempting to reset a TryteString with a value that contains
    invalid characters.
    """
    with self.assertRaises(ValueError):
      TryteString(b'not valid')

  # noinspection PyTypeChecker
  def test_init_error_int(self):
    """
    Attempting to reset a TryteString from an int.
    """
    with self.assertRaises(TypeError):
      TryteString(42)

  def test_length(self):
    """
    Just like byte strings, TryteStrings have length.
    """
    self.assertEqual(len(TryteString(b'RBTC')), 4)
    self.assertEqual(len(TryteString(b'RBTC', pad=81)), 81)

  def test_iterator(self):
    """
    Just like byte strings, you can iterate over TryteStrings.
    """
    self.assertListEqual(
      list(TryteString(b'RBTC')),
      [b'R', b'B', b'T', b'C'],
    )

    self.assertListEqual(
      list(TryteString(b'RBTC', pad=6)),
      [b'R', b'B', b'T', b'C', b'9', b'9'],
    )

  def test_string_conversion(self):
    """
    A TryteString can be converted into an ASCII representation.
    """
    self.assertEqual(
      binary_type(TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA')),

      # Note that the trytes are NOT converted into bytes!
      b'RBTC9D9DCDQAEASBYBCCKBFA',
    )

  def test_as_bytes_partial_sequence_errors_strict(self):
    """
    Attempting to convert an odd number of trytes into bytes using the
    `as_bytes` method with errors='strict'.
    """
    trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA9')

    with self.assertRaises(TrytesDecodeError):
      trytes.as_bytes(errors='strict')

  def test_as_bytes_partial_sequence_errors_ignore(self):
    """
    Attempting to convert an odd number of trytes into bytes using the
    `as_bytes` method with errors='ignore'.
    """
    trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA9')

    self.assertEqual(
      trytes.as_bytes(errors='ignore'),

      # The extra tryte is ignored.
      b'Hello, IOTA!',
    )

  def test_as_bytes_partial_sequence_errors_replace(self):
    """
    Attempting to convert an odd number of trytes into bytes using the
    `as_bytes` method with errors='replace'.
    """
    trytes = TryteString(b'RBTC9D9DCDQAEASBYBCCKBFA9')

    self.assertEqual(
      trytes.as_bytes(errors='replace'),

      # The extra tryte is replaced with '?'.
      b'Hello, IOTA!?',
    )

  def test_as_bytes_non_ascii_errors_strict(self):
    """
    Converting a sequence of trytes into bytes using the `as_bytes`
    method yields non-ASCII characters, and errors='strict'.
    """
    trytes = TryteString(b'ZJVYUGTDRPDYFGFXMK')

    with self.assertRaises(TrytesDecodeError):
      trytes.as_bytes(errors='strict')

  def test_as_bytes_non_ascii_errors_ignore(self):
    """
    Converting a sequence of trytes into bytes using the `as_bytes`
    method yields non-ASCII characters, and errors='ignore'.
    """
    trytes = TryteString(b'ZJVYUGTDRPDYFGFXMK')

    self.assertEqual(
      trytes.as_bytes(errors='ignore'),
      b'\xd2\x80\xc3',
    )

  def test_as_bytes_non_ascii_errors_replace(self):
    """
    Converting a sequence of trytes into bytes using the `as_bytes`
    method yields non-ASCII characters, and errors='replace'.
    """
    trytes = TryteString(b'ZJVYUGTDRPDYFGFXMK')

    self.assertEqual(
      trytes.as_bytes(errors='replace'),
      b'??\xd2\x80??\xc3??',
    )

  def test_as_string(self):
    """
    Converting a sequence of trytes into a Unicode string.
    """
    trytes = TryteString(b'LH9GYEMHCF9GWHZFEELHVFOEOHNEEEWHZFUD')

    self.assertEqual(trytes.as_string(), '你好，世界！')

  def test_as_string_strip(self):
    """
    Strip trailing padding from a TryteString before converting.
    """
    # Note odd number of trytes!
    trytes = TryteString(b'LH9GYEMHCF9GWHZFEELHVFOEOHNEEEWHZFUD9999999999999')

    self.assertEqual(trytes.as_string(), '你好，世界！')

  def test_as_string_no_strip(self):
    """
    Prevent stripping trailing padding when converting to string.
    """
    trytes = TryteString(b'LH9GYEMHCF9GWHZFEELHVFOEOHNEEEWHZFUD999999999999')

    self.assertEqual(
      trytes.as_string(strip_padding=False),
      '你好，世界！\x00\x00\x00\x00\x00\x00',
    )

  def test_as_string_not_utf8_errors_strict(self):
    """
    The tryte sequence does not represent a valid UTF-8 sequence, and
    errors='strict'.
    """
    # Chop off a couple of trytes to break up a multi-byte sequence.
    trytes = TryteString.from_string('你好，世界！')[:-2]

    # Note the exception type.  The trytes were decoded to bytes
    # successfully; the exception occurred while trying to decode the
    # bytes into Unicode code points.
    with self.assertRaises(UnicodeDecodeError):
      trytes.as_string('strict')

  def test_as_string_not_utf8_errors_ignore(self):
    """
    The tryte sequence does not represent a valid UTF-8 sequence, and
    errors='ignore'.
    """
    # Chop off a couple of trytes to break up a multi-byte sequence.
    trytes = TryteString.from_string('你好，世界！')[:-2]

    self.assertEqual(
      trytes.as_string('ignore'),
      '你好，世界',
    )

  def test_as_string_not_utf8_errors_replace(self):
    """
    The tryte sequence does not represent a valid UTF-8 sequence, and
    errors='replace'.
    """
    # Chop off a couple of trytes to break up a multi-byte sequence.
    trytes = TryteString.from_string('你好，世界！')[:-2]

    self.assertEqual(
      trytes.as_string('replace'),

      # Note that the replacement character is the Unicode replacement
      # character, not '?'.
      '你好，世界�',
    )

  def test_as_trytes_single_tryte(self):
    """
    Converting a single-tryte TryteString into a sequence of tryte
    values.
    """
    # Fortunately, there's only 27 possible tryte configurations, so
    # it's not too painful to test them all.
    self.assertDictEqual(
      {
        chr(c): TryteString(chr(c).encode('ascii')).as_trytes()
          for c in AsciiTrytesCodec.alphabet.values()
      },

      {
        '9': [[ 0,  0,  0]],  #   0
        'A': [[ 1,  0,  0]],  #   1
        'B': [[-1,  1,  0]],  #   2
        'C': [[ 0,  1,  0]],  #   3
        'D': [[ 1,  1,  0]],  #   4
        'E': [[-1, -1,  1]],  #   5
        'F': [[ 0, -1,  1]],  #   6
        'G': [[ 1, -1,  1]],  #   7
        'H': [[-1,  0,  1]],  #   8
        'I': [[ 0,  0,  1]],  #   9
        'J': [[ 1,  0,  1]],  #  10
        'K': [[-1,  1,  1]],  #  11
        'L': [[ 0,  1,  1]],  #  12
        'M': [[ 1,  1,  1]],  #  13
        'N': [[-1, -1, -1]],  # -13 (overflow)
        'O': [[ 0, -1, -1]],  # -12
        'P': [[ 1, -1, -1]],  # -11
        'Q': [[-1,  0, -1]],  # -10
        'R': [[ 0,  0, -1]],  #  -9
        'S': [[ 1,  0, -1]],  #  -8
        'T': [[-1,  1, -1]],  #  -7
        'U': [[ 0,  1, -1]],  #  -6
        'V': [[ 1,  1, -1]],  #  -5
        'W': [[-1, -1,  0]],  #  -4
        'X': [[ 0, -1,  0]],  #  -3
        'Y': [[ 1, -1,  0]],  #  -2
        'Z': [[-1,  0,  0]],  #  -1
      },
    )

  def test_as_trytes_mulitple_trytes(self):
    """
    Converting a multiple-tryte TryteString into a sequence of
    tryte values.
    """
    self.assertListEqual(
      TryteString(b'ZJVYUGTDRPDYFGFXMK').as_trytes(),

      [
        [-1,  0,  0],
        [ 1,  0,  1],
        [ 1,  1, -1],
        [ 1, -1,  0],
        [ 0,  1, -1],
        [ 1, -1,  1],
        [-1,  1, -1],
        [ 1,  1,  0],
        [ 0,  0, -1],
        [ 1, -1, -1],
        [ 1,  1,  0],
        [ 1, -1,  0],
        [ 0, -1,  1],
        [ 1, -1,  1],
        [ 0, -1,  1],
        [ 0, -1,  0],
        [ 1,  1,  1],
        [-1,  1,  1],
      ],
    )

  def test_as_trits_single_tryte(self):
    """
    Converting a single-tryte TryteString into a sequence of trit
    values.
    """
    # Fortunately, there's only 27 possible tryte configurations, so
    # it's not too painful to test them all.
    self.assertDictEqual(
      {
        chr(c): TryteString(chr(c).encode('ascii')).as_trits()
          for c in AsciiTrytesCodec.alphabet.values()
      },

      {
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
        'N': [-1, -1, -1],  # -13 (overflow)
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
      },
    )

  def test_as_trits_multiple_trytes(self):
    """
    Converting a multiple-tryte TryteString into a sequence of trit
    values.
    """
    self.assertListEqual(
      TryteString(b'ZJVYUGTDRPDYFGFXMK').as_trits(),

      [
        -1,  0,  0,
         1,  0,  1,
         1,  1, -1,
         1, -1,  0,
         0,  1, -1,
         1, -1,  1,
        -1,  1, -1,
         1,  1,  0,
         0,  0, -1,
         1, -1, -1,
         1,  1,  0,
         1, -1,  0,
         0, -1,  1,
         1, -1,  1,
         0, -1,  1,
         0, -1,  0,
         1,  1,  1,
        -1,  1,  1,
      ],
    )

  def test_random(self):
    """
    Generating a random sequence of trytes.
    """
    trytes = TryteString.random(Hash.LEN)

    # It is (hopefully!) impossible to predict what the actual trytes
    # will be, but at least we can verify that the correct number were
    # generated!
    self.assertEqual(len(trytes), Hash.LEN)

  def test_from_bytes(self):
    """
    Converting a sequence of bytes into a TryteString.
    """
    self.assertEqual(
      binary_type(TryteString.from_bytes(b'Hello, IOTA!')),
      b'RBTC9D9DCDQAEASBYBCCKBFA',
    )

  def test_from_string(self):
    """
    Converting a Unicode string into a TryteString.
    """
    self.assertEqual(
      binary_type(TryteString.from_string('你好，世界！')),
      b'LH9GYEMHCF9GWHZFEELHVFOEOHNEEEWHZFUD',
    )

  def test_from_trytes(self):
    """
    Converting a sequence of tryte values into a TryteString.
    """
    trytes = [
      [0, 0, -1],
      [-1, 1, 0],
      [-1, 1, -1],
      [0, 1, 0],
      [0, 0, 0],
      [1, 1, 0],
      [0, 0, 0],
      [1, 1, 0],
      [0, 1, 0],
      [1, 1, 0],
      [-1, 0, -1],
      [1, 0, 0],
      [-1, -1, 1],
      [1, 0, 0],
      [1, 0, -1],
      [-1, 1, 0],
      [1, -1, 0],
      [-1, 1, 0],
      [0, 1, 0],
      [0, 1, 0],
      [-1, 1, 1],
      [-1, 1, 0],
      [0, -1, 1],
      [1, 0, 0],
    ]

    self.assertEqual(
      binary_type(TryteString.from_trytes(trytes)),
      b'RBTC9D9DCDQAEASBYBCCKBFA',
    )

  def test_from_trits(self):
    """
    Converting a sequence of trit values into a TryteString.
    """
    trits = [
      0, 0, -1,
      -1, 1, 0,
      -1, 1, -1,
      0, 1, 0,
      0, 0, 0,
      1, 1, 0,
      0, 0, 0,
      1, 1, 0,
      0, 1, 0,
      1, 1, 0,
      -1, 0, -1,
      1, 0, 0,
      -1, -1, 1,
      1, 0, 0,
      1, 0, -1,
      -1, 1, 0,
      1, -1, 0,
      -1, 1, 0,
      0, 1, 0,
      0, 1, 0,
      -1, 1, 1,
      -1, 1, 0,
      0, -1, 1,
      1, 0, 0,
    ]

    self.assertEqual(
      binary_type(TryteString.from_trits(trits)),
      b'RBTC9D9DCDQAEASBYBCCKBFA',
    )

  def test_from_trits_wrong_length_padded(self):
    """
    Automatically padding a sequence of trit values with length not
    divisible by 3 so that it can be converted into a TryteString.
    """
    trits = [
      0, 0, -1,
      -1, 1, 0,
      -1, 1, -1,
      0, 1, # 0, <- Oops, did you lose something?
    ]

    self.assertEqual(
      binary_type(TryteString.from_trits(trits)),
      b'RBTC',
    )


# noinspection SpellCheckingInspection
class AddressTestCase(TestCase):
  def test_init_automatic_pad(self):
    """
    Addresses are automatically padded to 81 trytes.
    """
    addy = Address(
      b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
      b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC'
    )

    self.assertEqual(
      binary_type(addy),

      # Note the extra 9's added to the end.
      b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
      b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC9999',
    )

    # This attribute will make more sense once we start working with
    # address checksums.
    self.assertEqual(
      binary_type(addy.address),

      b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
      b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC9999',
    )

    # Checksum is not generated automatically.
    self.assertIsNone(addy.checksum)

  def test_init_error_too_long(self):
    """
    Attempting to create an address longer than 81 trytes.
    """
    with self.assertRaises(ValueError):
      Address(
        # Extra padding at the end is not ignored.
        # If it's an address (without checksum), then it must be 81
        # trytes exactly.
        b'JVMTDGDPDFYHMZPMWEKKANBQSLSDTIIHAYQUMZOK'
        b'HXXXGJHJDQPOMDOMNRDKYCZRUFZROZDADTHZC99999'
      )

  def test_init_with_checksum(self):
    """
    Creating an address with checksum already attached.
    """
    addy = Address(
      b'RVORZ9SIIP9RCYMREUIXXVPQIPHVCNPQ9HZWYKFWYWZRE'
      b'9JQKG9REPKIASHUUECPSQO9JT9XNMVKWYGVAFOXM9MUBX'
    )

    self.assertEqual(
      binary_type(addy),

      b'RVORZ9SIIP9RCYMREUIXXVPQIPHVCNPQ9HZWYKFWYWZRE'
      b'9JQKG9REPKIASHUUECPSQO9JT9XNMVKWYGVAFOXM9MUBX',
    )

    self.assertEqual(
      binary_type(addy.address),

      b'RVORZ9SIIP9RCYMREUIXXVPQIPHVCNPQ9HZWYKFWYWZRE'
      b'9JQKG9REPKIASHUUECPSQO9JT9XNMVKWYGVA',
    )

    self.assertEqual(
      binary_type(addy.checksum),
      b'FOXM9MUBX',
    )

  def test_init_error_checksum_too_long(self):
    """
    Attempting to create an address longer than 90 trytes.
    """
    with self.assertRaises(ValueError):
      Address(
        # Extra padding at the end is not ignored.
        # If it's a checksummed address, then it must be 90 trytes
        # exactly.
        b'RVORZ9SIIP9RCYMREUIXXVPQIPHVCNPQ9HZWYKFWYWZRE'
        b'9JQKG9REPKIASHUUECPSQO9JT9XNMVKWYGVAFOXM9MUBX9'
      )

  def test_checksum_valid(self):
    """
    An address is created with a valid checksum.
    """
    addy = Address(
      b'RVORZ9SIIP9RCYMREUIXXVPQIPHVCNPQ9HZWYKFWYWZRE'
      b'9JQKG9REPKIASHUUECPSQO9JT9XNMVKWYGVAITCOXAQSD',
    )

    self.assertTrue(addy.is_checksum_valid())

    self.assertEqual(
      binary_type(addy.with_valid_checksum()),

      b'RVORZ9SIIP9RCYMREUIXXVPQIPHVCNPQ9HZWYKFWYWZRE'
      b'9JQKG9REPKIASHUUECPSQO9JT9XNMVKWYGVAITCOXAQSD',
    )

  def test_checksum_invalid(self):
    """
    An address is created with an invalid checksum.
    """
    trytes = (
      b'IGKUOZGEFNSVJXETLIBKRSUZAWMYSVDPMHGQPCETEFNZP'
      b'XSJLZMBLAWDRLUBWPIPKFNEPADIWMXMYYRKQ'
    )

    addy = Address(
      trytes + b'XYYNAFRMB' # <- Last tryte s/b 'A'.
    )

    self.assertFalse(addy.is_checksum_valid())

    self.assertEqual(
      binary_type(addy.with_valid_checksum()),

      b'IGKUOZGEFNSVJXETLIBKRSUZAWMYSVDPMHGQPCETEFNZP'
      b'XSJLZMBLAWDRLUBWPIPKFNEPADIWMXMYYRKQXYYNAFRMA',
    )

  def test_checksum_null(self):
    """
    An address is created without a checksum.
    """
    trytes = (
      b'ZKIUDZXQYQAWSHPKSAATJXPAQZPGYCDCQDRSMWWCGQJNI'
      b'PCOORMDRNREDUDKBMUYENYTFVUNEWDBAKXMV'
    )

    addy = Address(trytes)

    self.assertFalse(addy.is_checksum_valid())

    self.assertEqual(
      binary_type(addy.with_valid_checksum()),

      b'ZKIUDZXQYQAWSHPKSAATJXPAQZPGYCDCQDRSMWWCGQJNI'
      b'PCOORMDRNREDUDKBMUYENYTFVUNEWDBAKXMVJJJGBARPB',
    )

  def test_with_checksum_attributes(self):
    """
    :py:meth:`Address.with_valid_checksum` also copies attributes such
    as key index and balance.
    """
    addy =\
      Address(
        trytes =
          b'ZKIUDZXQYQAWSHPKSAATJXPAQZPGYCDCQDRSMWWCGQJNI'
          b'PCOORMDRNREDUDKBMUYENYTFVUNEWDBAKXMV',

        key_index = 42,
        balance   = 86,
      )

    checked = addy.with_valid_checksum()

    self.assertEqual(checked.key_index, 42)
    self.assertEqual(checked.balance, 86)


# noinspection SpellCheckingInspection
class AddressChecksumTestCase(TestCase):
  def test_init_happy_path(self):
    """
    Creating a valid address checksum.
    """
    self.assertEqual(binary_type(AddressChecksum(b'FOXM9MUBX')), b'FOXM9MUBX')

  def test_init_error_too_short(self):
    """
    Attempting to create an address checksum shorter than 9 trytes.
    """
    with self.assertRaises(ValueError):
      AddressChecksum(b'FOXM9MUB')

  def test_init_error_too_long(self):
    """
    Attempting to create an address checksum longer than 9 trytes.
    """
    with self.assertRaises(ValueError):
      # Extra padding characters are not ignored.
      # If it's an address checksum, it must be 9 trytes exactly.
      AddressChecksum(b'FOXM9MUBX9')


# noinspection SpellCheckingInspection
class TagTestCase(TestCase):
  def test_init_automatic_pad(self):
    """
    Tags are automatically padded to 27 trytes.
    """
    tag = Tag(b'COLOREDCOINS')

    self.assertEqual(binary_type(tag), b'COLOREDCOINS999999999999999')

  def test_init_error_too_long(self):
    """
    Attempting to create a tag longer than 27 trytes.
    """
    with self.assertRaises(ValueError):
      # 28 chars = no va.
      Tag(b'COLOREDCOINS9999999999999999')
