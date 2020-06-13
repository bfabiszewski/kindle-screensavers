#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
# kate: indent-mode cstyle; indent-width 4; replace-tabs on;
#
# $Id: kfxmeta.py 15389 2018-09-05 19:41:12Z NiLuJe $
#
# See <http://www.mobileread.com/forums/showpost.php?p=3176029&postcount=89> for the original tool ;).

# python 2.7
from __future__ import (unicode_literals, division, absolute_import, print_function)
import base64
import collections
import datetime
import decimal
import json
import sys
import os
import StringIO
import struct
import getopt
import hashlib

# UTF-8 trickery for paths pilfered from KindleUnpack
from utf8_utils import utf8_argv, add_cp65001_codec, utf8_str
add_cp65001_codec()


'''
Sample program to demonstrate the decoding of data and extraction of metadata from KFX and KDF book files.
The full contents of the input file will be dumped by default. Use the -m option to dump only metadata.

This was developed to document what I have learned so far and to aid others who want to understand
KFX and KDF for their own purposes. It is likely incorrect and incomplete in some areas.

This program does NOT extract protected book content. It does not deal with DRM or encryption. Use of
this tool to aid in content extraction or DRM removal is not sanctioned!



A "metadata.kfx" file is a KFX container file mostly containing book metadata. A file with this name
can (usually) be found in the "book-name.sdr/assets" directory of a Kindle running firmware version
5.6.5 or later. The KFX files found in the "attachables" subdirectory are in the same container format
and mostly hold images. (The main KFX book file holds most of the book content, but cannot be decrypted
by this program.)

A KFX container has a "CONT" header followed by multiple data entities. Each of these has a "ENTY"
header and holds either a binary resource (such as a JPEG image) or packed structured binary data, known
as ION.

A "book.kdf" file, produced by the Amazon Kindle Previewer 3.0 beta or above, is an SQLite database
containing fragments, which are equivalent to KFX entities. Images are kept in separate files.

ION can represent multiple data types and complex structures. Data properties are identified by numbers
and require a symbol table for interpretation. Different symbol tables apply to book data (YJ_symbols)
and encrypted data (ProtectedData).

The full YJ_symbols table needed to decode ION book data is not included here in order to avoid possible
copyright issues. (It is a part of any Amazon software that reads or writes KFX.)

Raw ION files can also be dumped by this program.



Release history:
1.0     Initial release
1.1     Fix string encode/decode problem, Miscellaneous clean up
1.2     Miscellaneous clean up
2.0     Additional ion data types and support for KDF.
'''

__license__   = 'GPL v3'
__copyright__ = '2016, John Howell <jhowell@acm.org>'

VERSION = '2.0.N'


# magic numbers for data structures
CONTAINER_MAGIC = b'CONT'
ENTITY_MAGIC = b'ENTY'
ION_MAGIC = b'\xe0\x01\x00\xea'
DRMION_MAGIC = b'\xeaDRMION\xee'


# ION data types            (comment shows equivalent python data type produced)
DT_NULL = 0                 # None
DT_BOOLEAN = 1              # True/False
DT_POSITIVE_INTEGER = 2     # int
DT_NEGATIVE_INTEGER = 3     # int
DT_FLOAT = 4                # float
DT_DECIMAL = 5              # decimal.Decimal
DT_TIMESTAMP = 6            # datetime.datetime
DT_SYMBOL = 7               # str (using non-unicode to distinguish symbols from strings)
DT_STRING = 8               # unicode
DT_CLOB = 9                 # unicode
DT_BLOB = 10                # str (base 64 encoded)
DT_LIST = 11                # list
DT_S_EXPRESSION = 12        # tuple
DT_STRUCT = 13              # OrderedDict of symbol/value pairs (order is sometimes important)
DT_TYPED_DATA = 14          # dict with 'type', 'id', 'value'


# metadata-related symbols from YJ_symbols
# (non-unicode strings are used to distinguish symbols from character strings in this program)
SYMBOL_TABLE = {
    10: b"language",
    153: b"title",
    154: b"description",
    222: b"author",
    232: b"publisher",
    258: b"metadata",
    307: b"value",
    490: b"book_metadata",
    491: b"categorised_metadata",
    492: b"key",
    495: b"category",
    417: b"bcRawMedia",
    }

# Only dump metadata?
METADATA_ONLY = False
# Only dump cover image?
COVER_ONLY = False




def usage(progname):
    print("")
    print("Description:")
    print("  Parse data from a KFX, KDF or ION file and dump as JSON")
    print("Usage:")
    print("  %s -h -m -c infile [cover outdir]" % progname)
    print("Options:")
    print("    -h           print this help message")
    print("    -m           dump only book metadata instead of all file content")
    print("    -c           dump only book cover (in cover outdir) instead of all file content")

def main():
    global METADATA_ONLY
    global COVER_ONLY
    print("KFX Meta v%s" % VERSION)
    argv = utf8_argv()
    progname = os.path.basename(argv[0])
    try:
        opts, args = getopt.getopt(argv[1:], "hmc")
    except getopt.GetoptError as err:
        print(str(err))
        usage(progname)
        sys.exit(2)

    if len(args) < 1:
        usage(progname)
        sys.exit(2)

    for o, _ in opts:
        if o == "-h":
            usage(progname)
            sys.exit(0)
        if o == "-m":
            METADATA_ONLY = True
        if o == "-c":
            COVER_ONLY = True

    if len(args) > 1:
        infile, outdir = args
    else:
        infile = args[0]
        # FIXME: Use default outdir on Kindle?
        outdir = os.path.dirname(infile)

    infile = utf8_str(infile)
    outdir = utf8_str(outdir)
    # NOTE: Except we want unicode (thanks to our future unicode_literals import) ;)
    infile = unicode(infile, "utf-8")
    outdir = unicode(outdir, "utf-8")

    print('Decoding "{}"'.format(infile))

    if infile.endswith('.kdf'):
        data = KDFDatabase(infile).decode()
    else:
        packed_data = read_file(infile)

        if packed_data[0:4] == CONTAINER_MAGIC:
            data = KFXContainer(packed_data).decode()
        elif packed_data[0:4] == ION_MAGIC:
            data = PackedIon(packed_data).decode_list()
        elif packed_data[0:8] == DRMION_MAGIC:
            data = PackedIon(packed_data[8:-8]).decode_list()
        else:
            raise Exception('Input file does not appear to be KFX, KDF or ION')

    if METADATA_ONLY or COVER_ONLY:
        data = extract_metadata(data)

    # NOTE: We only care about the cover (which is assumed to be the first image, bcRawMedia)...
    if COVER_ONLY:
        cover_key = SYMBOL_TABLE[417]
        if not cover_key in data:
            # Hu oh... Failed to find a cover?
            raise StandardError('Failed to extract a cover image!')
        # Put the CDE Key in there, to match what we do in MobiCover...
        if not 'ASIN' in data:
            # Hu oh... No ASIN set?!
            print('No ASIN found!')
            # NOTE: Just in case, print content_id if it exists...
            if 'content_id' in data:
                print("But content_id is {}".format(data["content_id"]))
            # Use the sha1 of the full path of the book, like the Kindle does for legacy files?
            # FIXME: No idea if this still holds true for side-loaded KFX, not that this should be a common workflow...
            # If we're passed a metadata.kfx, get the path of the book itself...
            if os.path.basename(infile) == "metadata.kfx":
                bookpath = os.path.splitext(infile.rsplit('/', 2)[0])[0] + '.kfx'
            else:
                bookpath = infile
            cdekey = hashlib.sha1(os.path.abspath(bookpath)).hexdigest()
        else:
            cdekey = data["ASIN"]
        # NOTE: Assume this'll always be a jpg
        covername = "cover_raw_%s.jpg" % (cdekey)
        print("Extracting cover image to {0:s}".format(covername))
        outimg = os.path.join(outdir, covername)
        coverdata = base64.b64decode(data[cover_key])
        write_file(outimg, coverdata)
    else:
        outfile = os.path.splitext(infile)[0] + '.json'
        write_file(outfile, json_dump(data))
        print('Extracted data to JSON file "%s"' % outfile)




def extract_metadata(container_data):
    metadata = {}

    def add_metadata(_key, _value):
        # handle duplicates by changing the value to a list (allows multiple authors, etc.)
        if _key in metadata:
            if not isinstance(metadata[_key], list):
                if metadata[_key] == _value:
                    return  # already have this value

                metadata[_key] = [metadata[_key]]

            metadata[_key].append(_value)
        else:
            metadata[_key] = _value

    # locate metadata within the book data structures

    for entity in container_data:
        entity_type = entity["type"]
        entity_value = entity["value"]

        if entity_type == b"metadata":
            for key, value in entity_value.items():
                if key in SYMBOL_TABLE.values():
                    add_metadata(key, value)

        elif entity_type == b"book_metadata":
            target = entity_value
            if entity_value.has_key("type") and entity_value["type"] == b"P2":
                target = entity_value["value"]
            for value1 in target[b"categorised_metadata"]:
                for meta in value1[b"metadata"]:
                    add_metadata(meta[b"key"], meta[b"value"])

        elif entity_type == b"bcRawMedia" and entity_type not in metadata:
            metadata[entity_type] = entity_value    # assume first image is the cover

    return metadata




class PackedData:
    '''
    Simplify unpacking of packed binary data structures
    '''

    def __init__(self, data):
        self.buffer = data
        self.offset = 0


    def unpack_one(self, fmt, advance=True):
        return self.unpack_multi(fmt, advance)[0]


    def unpack_multi(self, fmt, advance=True):
        fmt = fmt.encode('ascii')
        result = struct.unpack_from(fmt, self.buffer, self.offset)
        if advance:
            self.advance(struct.calcsize(fmt))
        return result


    def extract(self, size):
        data = self.buffer[self.offset:self.offset + size]
        self.advance(size)
        return data


    def advance(self, size):
        self.offset += size


    def remaining(self):
        return len(self.buffer) - self.offset



class PackedBlock(PackedData):
    '''
    Common header structure of container and entity blocks
    '''

    def __init__(self, data, magic):
        PackedData.__init__(self, data)

        self.magic = self.unpack_one('4s')
        if self.magic != magic:
            raise Exception('%s magic number is incorrect (%s)' % (magic, hexs(self.magic)))

        self.version = self.unpack_one('<H')
        self.header_len = self.unpack_one('<L')



class KFXContainer(PackedBlock):
    '''
    Container file containing data entities
    '''

    def __init__(self, data):
        self.data = data
        PackedBlock.__init__(self, data, CONTAINER_MAGIC)

        self.advance(8)
        self.entities = []

        while True:
            if self.unpack_one('4s', advance=False) == ION_MAGIC:
                break

            entity_id, entity_type, entity_offset, entity_len = self.unpack_multi('<LLQQ')
            entity_start = self.header_len + entity_offset
            self.entities.append(Entity(self.data[entity_start:entity_start + entity_len], entity_type, entity_id))


    def decode(self):
        return [entity.decode() for entity in self.entities]



class Entity(PackedBlock):
    '''
    Data entity inside a container
    '''

    def __init__(self, data, entity_type, entity_id):
        PackedBlock.__init__(self, data, ENTITY_MAGIC)
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.entity_data = data[self.header_len:]


    def decode(self):
        if PackedData(self.entity_data).unpack_one('4s') == ION_MAGIC:
            entity_value = PackedIon(self.entity_data).decode()
        else:
            entity_value = self.entity_data.encode('base64')

        return {"type": property_name(self.entity_type), "id": property_name(self.entity_id), "value": entity_value}



class KDFDatabase(object):
    '''
    SLQite database containing book fragments
    '''

    def __init__(self, filename):
        import sqlite3      # version 3.8.2 or later required

        conn = sqlite3.connect(filename, 30)
        self.fragments = conn.execute('SELECT * FROM fragments;').fetchall()
        conn.close()


    def decode(self):
        fragments_data = []

        for payload_id, payload_type, payload_value in self.fragments:
            if payload_type == "blob" and payload_id != "max_id":
                fragment = PackedIon(StringIO.StringIO(payload_value).read()).decode()
                fragments_data.append({"type": fragment["id"], "id": payload_id.encode('utf8'), "value": fragment["value"]})

        return fragments_data



class PackedIon(PackedData):
    '''
    Packed structured binary data format
    '''

    def __init__(self, data):
        PackedData.__init__(self, data)


    def decode(self):
        self.check_magic()
        return self.unpack_typed_value()


    def decode_list(self):
        self.check_magic()
        return self.unpack_list(self.remaining())


    def check_magic(self):
        magic = self.unpack_one('4s')
        if magic != ION_MAGIC:
            raise Exception('ION magic number is incorrect (%s)' % hexs(magic))


    def unpack_typed_value(self):
        cmd = self.unpack_one('B')

        data_type = cmd >> 4
        data_len = cmd & 0x0f
        if data_len == 14:
            data_len = self.unpack_unsigned_number()

        #print('cmd=%02x, len=%s: %s' % (cmd, data_len, hexs(self.buffer[self.offset:][:data_len])))

        if data_type == DT_NULL:
            return None

        if data_type == DT_BOOLEAN:
            return data_len != 0  # length is actually value

        if data_type == DT_POSITIVE_INTEGER:
            return self.unpack_unsigned_int(data_len)

        if data_type == DT_NEGATIVE_INTEGER:
            return -self.unpack_unsigned_int(data_len)

        if data_type == DT_FLOAT:
            if data_len == 0:
                return float(0.0)
            return struct.unpack_from(b'>d', self.extract(data_len))[0]     # length must be 8

        if data_type == DT_DECIMAL:
            if data_len == 0:
                return decimal.Decimal(0)
            ion = PackedIon(self.extract(data_len))
            scale = ion.unpack_signed_number()
            magnitude = ion.unpack_signed_int(ion.remaining())
            return decimal.Decimal(magnitude) * (decimal.Decimal(10) ** scale)

        if data_type == DT_TIMESTAMP:
            ion = PackedIon(self.extract(data_len))
            ion.unpack_unsigned_number()        # unknown
            year = ion.unpack_unsigned_number()
            month = ion.unpack_unsigned_number()
            day = ion.unpack_unsigned_number()
            hour = ion.unpack_unsigned_number()
            minute = ion.unpack_unsigned_number()
            second = ion.unpack_unsigned_number()
            ion.unpack_unsigned_number()        # unknown
            return datetime.datetime(year, month, day, hour, minute, second)

        if data_type == DT_SYMBOL:
            return property_name(self.unpack_unsigned_int(data_len))

        if data_type == DT_STRING:
            return self.extract(data_len).decode('utf8')

        if data_type == DT_CLOB:
            return self.extract(data_len).decode('utf8')

        if data_type == DT_BLOB:
            return self.extract(data_len).encode('base64')

        if data_type == DT_LIST:
            return self.unpack_list(data_len)

        if data_type == DT_S_EXPRESSION:
            return tuple(self.unpack_list(data_len))

        if data_type == DT_STRUCT:
            ion = PackedIon(self.extract(data_len))
            result = collections.OrderedDict()

            while (ion.remaining()):
                symbol = property_name(ion.unpack_unsigned_number())
                result[symbol] = ion.unpack_typed_value()

            return result

        if data_type == DT_TYPED_DATA:
            ion = PackedIon(self.extract(data_len))
            result = {}
            result["type"] = property_name(ion.unpack_unsigned_number())
            result["id"] = property_name(ion.unpack_unsigned_number())
            result["value"] = ion.unpack_typed_value()
            return result


        print("encountered unknown data type %d" % data_type)
        self.advance(data_len)
        return None


    def unpack_list(self, length):
        ion = PackedIon(self.extract(length))
        result = []

        while (ion.remaining()):
            result.append(ion.unpack_typed_value())

        return result


    def unpack_unsigned_number(self):
        # variable length numbers, MSB first, 7 bits per byte, last byte is flagged by MSb set
        number = 0
        while (True):
            byte = self.unpack_one('B')
            number = (number << 7) | (byte & 0x7f)
            if byte >= 0x80:
                return number


    def unpack_signed_number(self):
        # single byte only, variable length not supported
        value = self.unpack_one('B')
        if (value & 0x80) == 0:
            raise Exception('encountered multi-byte signed number')
        if (value & 0x40):
            return -(value & 0x3f)
        return (value & 0x7f)


    def unpack_unsigned_int(self, length):
        # unsigned big-endian (MSB first)
        return struct.unpack_from(b'>Q', chr(0)*(8-length) + self.extract(length))[0]


    def unpack_signed_int(self, length):
        # signed big-endian (MSB first)
        if length == 0:
            return 0

        first_byte = self.unpack_one('B', advance=False)
        if (first_byte & 0x80) != 0:
            self.advance(1)
            # NOTE: Wild attempt at fixing errors on some side-loaded KFX built with KPR >= 3.24.0?
            #       struct.error: unpack_from requires a buffer of at least 8 bytes
            return -struct.unpack_from(b'>Q', chr(0)*(8-length) + chr(first_byte & 0x7f) + self.extract(length-1))[0]

        return self.unpack_unsigned_int(length)



def property_name(property_number):
    return SYMBOL_TABLE.get(property_number, b"P%d" % property_number)


def hexs(string, sep=' '):
    return sep.join('%02x' % ord(b) for b in string)


class IonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)

        if type(o).__name__ == "datetime":
            return o.isoformat()

        return super(IonEncoder, self).default(o)


def json_dump(data):
    return json.dumps(data, indent=2, separators=(',', ': '), cls=IonEncoder)


def read_file(filename):
    with open(filename, 'rb') as of:
        return of.read()


def write_file(filename, data):
    with open(filename, 'wb') as of:
        of.write(data)


main()
