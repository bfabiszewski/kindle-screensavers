#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# kate: indent-mode cstyle; indent-width 4; replace-tabs on;
#
# $Id: kindleunpack.py 15478 2018-10-08 19:58:19Z NiLuJe $
#
# This is pretty much completely ripped out of the excellent KindleUnpack <http://www.mobileread.com/forums/showthread.php?t=61986> tool ;).

DUMP = False
""" Set to True to dump all possible information. """

EOF_RECORD = chr(0xe9) + chr(0x8e) + "\r\n"
""" The EOF record content. """

K8_BOUNDARY = "BOUNDARY"
""" The section data that divides K8 mobi ebooks. """

CDETYPE_CHECK = False
""" Set to True to make sure we only parse EBOK or PDOC cde types (and optionally MAGZ & NWPR). (Use by the ScreenSavers hack on legacy devices) """

import sys
import os

import locale
import codecs

# Setting setdefaultencoding to 'utf-8' should be fine (no side effects should occur).
#reload(sys)
#sys.setdefaultencoding('utf-8')

from utf8_utils import utf8_argv, add_cp65001_codec, utf8_str
add_cp65001_codec()

import array, struct, imghdr, hashlib, datetime
import getopt

from path import pathof
import path

# import the mobiunpack support libraries
from mobi_uncompress import HuffcdicReader, PalmdocReader, UncompressedReader

def describe(data):
    txtans = ''
    hexans = data.encode('hex')
    for i in data:
        if ord(i) < 32 or ord(i) > 127:
            txtans += '?'
        else:
            txtans += i
    return '"' + txtans + '"' + ' 0x'+ hexans

class unpackException(Exception):
    pass

class fileNames:
    def __init__(self, infile, outdir):
        self.infile = infile
        self.outdir = outdir
        if not path.exists(outdir):
            path.mkdir(outdir)

        self.outbase = os.path.join(outdir, os.path.splitext(os.path.split(infile)[1])[0])

    def getInputFileBasename(self):
        return os.path.splitext(os.path.basename(self.infile))[0]


def datetimefrompalmtime(palmtime):
    if palmtime > 0x7FFFFFFF:
        pythondatetime = datetime.datetime(year=1904,month=1,day=1)+datetime.timedelta(seconds=palmtime)
    else:
        pythondatetime = datetime.datetime(year=1970,month=1,day=1)+datetime.timedelta(seconds=palmtime)
    return pythondatetime

class Sectionizer:
    def __init__(self, filename):
        self.data = open(pathof(filename), 'rb').read()
        self.palmheader = self.data[:78]
        self.palmname = self.data[:32]
        self.ident = self.palmheader[0x3C:0x3C+8]
        self.num_sections, = struct.unpack_from('>H', self.palmheader, 76)
        self.filelength = len(self.data)
        sectionsdata = struct.unpack_from('>%dL' % (self.num_sections*2), self.data, 78) + (self.filelength, 0)
        self.sectionoffsets = sectionsdata[::2]
        self.sectionattributes = sectionsdata[1::2]
        self.sectiondescriptions = ["" for x in range(self.num_sections+1)]
        self.sectiondescriptions[-1] = "File Length Only"
        return

    def dumpsectionsinfo(self):
        print "Section     Offset  Length      UID Attribs Description"
        for i in xrange(self.num_sections):
            print "%3d %3X  0x%07X 0x%05X % 8d % 7d %s" % (i,i, self.sectionoffsets[i], self.sectionoffsets[i+1] - self.sectionoffsets[i], self.sectionattributes[i]&0xFFFFFF, (self.sectionattributes[i]>>24)&0xFF, self.sectiondescriptions[i])
        print "%3d %3X  0x%07X                          %s" % (self.num_sections,self.num_sections, self.sectionoffsets[self.num_sections], self.sectiondescriptions[self.num_sections])

    def setsectiondescription(self, section, description):
        if section < len(self.sectiondescriptions):
            self.sectiondescriptions[section] = description
        else:
            print "Section out of range: %d, description %s" % (section,description)

    def dumppalmheader(self):
        print "Palm Database Header"
        print "Database name: " + repr(self.palmheader[:32])
        dbattributes, = struct.unpack_from('>H', self.palmheader, 32)
        print "Bitfield attributes: 0x%0X" % dbattributes,
        if dbattributes != 0:
            print " ( ",
            if (dbattributes & 2):
                print "Read-only; ",
            if (dbattributes & 4):
                print "Dirty AppInfoArea; ",
            if (dbattributes & 8):
                print "Needs to be backed up; ",
            if (dbattributes & 16):
                print "OK to install over newer; ",
            if (dbattributes & 32):
                print "Reset after installation; ",
            if (dbattributes & 64):
                print "No copying by PalmPilot beaming; ",
            print ")"
        else:
            print ""
        print "File version: %d" % struct.unpack_from('>H', self.palmheader, 34)[0]
        dbcreation, = struct.unpack_from('>L', self.palmheader, 36)
        print "Creation Date: " + str(datetimefrompalmtime(dbcreation))+ (" (0x%0X)" % dbcreation)
        dbmodification, = struct.unpack_from('>L', self.palmheader, 40)
        print "Modification Date: " + str(datetimefrompalmtime(dbmodification))+ (" (0x%0X)" % dbmodification)
        dbbackup, = struct.unpack_from('>L', self.palmheader, 44)
        if dbbackup != 0:
            print "Backup Date: " + str(datetimefrompalmtime(dbbackup))+ (" (0x%0X)" % dbbackup)
        print "Modification No.: %d" % struct.unpack_from('>L', self.palmheader, 48)[0]
        print "App Info offset: 0x%0X" % struct.unpack_from('>L', self.palmheader, 52)[0]
        print "Sort Info offset: 0x%0X" % struct.unpack_from('>L', self.palmheader, 56)[0]
        print "Type/Creator: %s/%s" % (repr(self.palmheader[60:64]), repr(self.palmheader[64:68]))
        print "Unique seed: 0x%0X" % struct.unpack_from('>L', self.palmheader, 68)[0]
        expectedzero, = struct.unpack_from('>L', self.palmheader, 72)
        if expectedzero != 0:
            print "Should be zero but isn't: %d" % struct.unpack_from('>L', self.palmheader, 72)[0]
        print "Number of sections: %d" % struct.unpack_from('>H', self.palmheader, 76)[0]
        return

    def loadSection(self, section):
        before, after = self.sectionoffsets[section:section+2]
        return self.data[before:after]


def sortedHeaderKeys(mheader):
    hdrkeys = sorted(mheader.keys(), key=lambda akey: mheader[akey][0])
    return hdrkeys

class MobiHeader:
    # all values are packed in big endian format
    palmdoc_header = {
            'compression_type'  : (0x00, '>H', 2),
            'fill0'             : (0x02, '>H', 2),
            'text_length'       : (0x04, '>L', 4),
            'text_records'      : (0x08, '>H', 2),
            'max_section_size'  : (0x0a, '>H', 2),
            'read_pos   '       : (0x0c, '>L', 4),
    }

    mobi6_header = {
            'compression_type'  : (0x00, '>H', 2),
            'fill0'             : (0x02, '>H', 2),
            'text_length'       : (0x04, '>L', 4),
            'text_records'      : (0x08, '>H', 2),
            'max_section_size'  : (0x0a, '>H', 2),
            'crypto_type'       : (0x0c, '>H', 2),
            'fill1'             : (0x0e, '>H', 2),
            'magic'             : (0x10, '4s', 4),
            'header_length (from MOBI)'     : (0x14, '>L', 4),
            'type'              : (0x18, '>L', 4),
            'codepage'          : (0x1c, '>L', 4),
            'unique_id'         : (0x20, '>L', 4),
            'version'           : (0x24, '>L', 4),
            'metaorthindex'     : (0x28, '>L', 4),
            'metainflindex'     : (0x2c, '>L', 4),
            'index_names'       : (0x30, '>L', 4),
            'index_keys'        : (0x34, '>L', 4),
            'extra_index0'      : (0x38, '>L', 4),
            'extra_index1'      : (0x3c, '>L', 4),
            'extra_index2'      : (0x40, '>L', 4),
            'extra_index3'      : (0x44, '>L', 4),
            'extra_index4'      : (0x48, '>L', 4),
            'extra_index5'      : (0x4c, '>L', 4),
            'first_nontext'     : (0x50, '>L', 4),
            'title_offset'      : (0x54, '>L', 4),
            'title_length'      : (0x58, '>L', 4),
            'language_code'     : (0x5c, '>L', 4),
            'dict_in_lang'      : (0x60, '>L', 4),
            'dict_out_lang'     : (0x64, '>L', 4),
            'min_version'       : (0x68, '>L', 4),
            'first_resc_offset' : (0x6c, '>L', 4),
            'huff_offset'       : (0x70, '>L', 4),
            'huff_num'          : (0x74, '>L', 4),
            'huff_tbl_offset'   : (0x78, '>L', 4),
            'huff_tbl_len'      : (0x7c, '>L', 4),
            'exth_flags'        : (0x80, '>L', 4),
            'fill3_a'           : (0x84, '>L', 4),
            'fill3_b'           : (0x88, '>L', 4),
            'fill3_c'           : (0x8c, '>L', 4),
            'fill3_d'           : (0x90, '>L', 4),
            'fill3_e'           : (0x94, '>L', 4),
            'fill3_f'           : (0x98, '>L', 4),
            'fill3_g'           : (0x9c, '>L', 4),
            'fill3_h'           : (0xa0, '>L', 4),
            'unknown0'          : (0xa4, '>L', 4),
            'drm_offset'        : (0xa8, '>L', 4),
            'drm_count'         : (0xac, '>L', 4),
            'drm_size'          : (0xb0, '>L', 4),
            'drm_flags'         : (0xb4, '>L', 4),
            'fill4_a'           : (0xb8, '>L', 4),
            'fill4_b'           : (0xbc, '>L', 4),
            'first_content'     : (0xc0, '>H', 2),
            'last_content'      : (0xc2, '>H', 2),
            'unknown0'          : (0xc4, '>L', 4),
            'fcis_offset'       : (0xc8, '>L', 4),
            'fcis_count'        : (0xcc, '>L', 4),
            'flis_offset'       : (0xd0, '>L', 4),
            'flis_count'        : (0xd4, '>L', 4),
            'unknown1'          : (0xd8, '>L', 4),
            'unknown2'          : (0xdc, '>L', 4),
            'srcs_offset'       : (0xe0, '>L', 4),
            'srcs_count'        : (0xe4, '>L', 4),
            'unknown3'          : (0xe8, '>L', 4),
            'unknown4'          : (0xec, '>L', 4),
            'fill5'             : (0xf0, '>H', 2),
            'traildata_flags'   : (0xf2, '>H', 2),
            'ncx_index'         : (0xf4, '>L', 4),
            'unknown5'          : (0xf8, '>L', 4),
            'unknown6'          : (0xfc, '>L', 4),
            'datp_offset'       : (0x100, '>L', 4),
            'unknown7'          : (0x104, '>L', 4),
            'Unknown    '       : (0x108, '>L', 4),
            'Unknown    '       : (0x10C, '>L', 4),
            'Unknown    '       : (0x110, '>L', 4),
            'Unknown    '       : (0x114, '>L', 4),
            'Unknown    '       : (0x118, '>L', 4),
            'Unknown    '       : (0x11C, '>L', 4),
            'Unknown    '       : (0x120, '>L', 4),
            'Unknown    '       : (0x124, '>L', 4),
            'Unknown    '       : (0x128, '>L', 4),
            'Unknown    '       : (0x12C, '>L', 4),
            'Unknown    '       : (0x130, '>L', 4),
            'Unknown    '       : (0x134, '>L', 4),
            'Unknown    '       : (0x138, '>L', 4),
            'Unknown    '       : (0x11C, '>L', 4),
    }

    mobi8_header = {
            'compression_type'  : (0x00, '>H', 2),
            'fill0'             : (0x02, '>H', 2),
            'text_length'       : (0x04, '>L', 4),
            'text_records'      : (0x08, '>H', 2),
            'max_section_size'  : (0x0a, '>H', 2),
            'crypto_type'       : (0x0c, '>H', 2),
            'fill1'             : (0x0e, '>H', 2),
            'magic'             : (0x10, '4s', 4),
            'header_length (from MOBI)'     : (0x14, '>L', 4),
            'type'              : (0x18, '>L', 4),
            'codepage'          : (0x1c, '>L', 4),
            'unique_id'         : (0x20, '>L', 4),
            'version'           : (0x24, '>L', 4),
            'metaorthindex'     : (0x28, '>L', 4),
            'metainflindex'     : (0x2c, '>L', 4),
            'index_names'       : (0x30, '>L', 4),
            'index_keys'        : (0x34, '>L', 4),
            'extra_index0'      : (0x38, '>L', 4),
            'extra_index1'      : (0x3c, '>L', 4),
            'extra_index2'      : (0x40, '>L', 4),
            'extra_index3'      : (0x44, '>L', 4),
            'extra_index4'      : (0x48, '>L', 4),
            'extra_index5'      : (0x4c, '>L', 4),
            'first_nontext'     : (0x50, '>L', 4),
            'title_offset'      : (0x54, '>L', 4),
            'title_length'      : (0x58, '>L', 4),
            'language_code'     : (0x5c, '>L', 4),
            'dict_in_lang'      : (0x60, '>L', 4),
            'dict_out_lang'     : (0x64, '>L', 4),
            'min_version'       : (0x68, '>L', 4),
            'first_resc_offset' : (0x6c, '>L', 4),
            'huff_offset'       : (0x70, '>L', 4),
            'huff_num'          : (0x74, '>L', 4),
            'huff_tbl_offset'   : (0x78, '>L', 4),
            'huff_tbl_len'      : (0x7c, '>L', 4),
            'exth_flags'        : (0x80, '>L', 4),
            'fill3_a'           : (0x84, '>L', 4),
            'fill3_b'           : (0x88, '>L', 4),
            'fill3_c'           : (0x8c, '>L', 4),
            'fill3_d'           : (0x90, '>L', 4),
            'fill3_e'           : (0x94, '>L', 4),
            'fill3_f'           : (0x98, '>L', 4),
            'fill3_g'           : (0x9c, '>L', 4),
            'fill3_h'           : (0xa0, '>L', 4),
            'unknown0'          : (0xa4, '>L', 4),
            'drm_offset'        : (0xa8, '>L', 4),
            'drm_count'         : (0xac, '>L', 4),
            'drm_size'          : (0xb0, '>L', 4),
            'drm_flags'         : (0xb4, '>L', 4),
            'fill4_a'           : (0xb8, '>L', 4),
            'fill4_b'           : (0xbc, '>L', 4),
            'fdst_offset'       : (0xc0, '>L', 4),
            'fdst_flow_count'   : (0xc4, '>L', 4),
            'fcis_offset'       : (0xc8, '>L', 4),
            'fcis_count'        : (0xcc, '>L', 4),
            'flis_offset'       : (0xd0, '>L', 4),
            'flis_count'        : (0xd4, '>L', 4),
            'unknown1'          : (0xd8, '>L', 4),
            'unknown2'          : (0xdc, '>L', 4),
            'srcs_offset'       : (0xe0, '>L', 4),
            'srcs_count'        : (0xe4, '>L', 4),
            'unknown3'          : (0xe8, '>L', 4),
            'unknown4'          : (0xec, '>L', 4),
            'fill5'             : (0xf0, '>H', 2),
            'traildata_flags'   : (0xf2, '>H', 2),
            'ncx_index'         : (0xf4, '>L', 4),
            'fragment_index'    : (0xf8, '>L', 4),
            'skeleton_index'    : (0xfc, '>L', 4),
            'datp_offset'       : (0x100, '>L', 4),
            'guide_index'       : (0x104, '>L', 4),
            'Unknown    '       : (0x108, '>L', 4),
            'Unknown    '       : (0x10C, '>L', 4),
            'Unknown    '       : (0x110, '>L', 4),
            'Unknown    '       : (0x114, '>L', 4),
            'Unknown    '       : (0x118, '>L', 4),
            'Unknown    '       : (0x11C, '>L', 4),
            'Unknown    '       : (0x120, '>L', 4),
            'Unknown    '       : (0x124, '>L', 4),
            'Unknown    '       : (0x128, '>L', 4),
            'Unknown    '       : (0x12C, '>L', 4),
            'Unknown    '       : (0x130, '>L', 4),
            'Unknown    '       : (0x134, '>L', 4),
            'Unknown    '       : (0x138, '>L', 4),
            'Unknown    '       : (0x11C, '>L', 4),
    }

    palmdoc_header_sorted_keys = sortedHeaderKeys(palmdoc_header)
    mobi6_header_sorted_keys = sortedHeaderKeys(mobi6_header)
    mobi8_header_sorted_keys = sortedHeaderKeys(mobi8_header)

    id_map_strings = {
        1 : 'Drm Server Id',
        2 : 'Drm Commerce Id',
        3 : 'Drm Ebookbase Book Id',
        100 : 'Creator',
        101 : 'Publisher',
        102 : 'Imprint',
        103 : 'Description',
        104 : 'ISBN',
        105 : 'Subject',
        106 : 'Published',
        107 : 'Review',
        108 : 'Contributor',
        109 : 'Rights',
        110 : 'SubjectCode',
        111 : 'Type',
        112 : 'Source',
        113 : 'ASIN',
        114 : 'versionNumber',
        117 : 'Adult',
        118 : 'Price',
        119 : 'Currency',
        122 : 'fixed-layout',
        123 : 'book-type',
        124 : 'orientation-lock',
        126 : 'original-resolution',
        127 : 'zero-gutter',
        128 : 'zero-margin',
        129 : 'K8(129)_Masthead/Cover_Image',
        132 : 'RegionMagnification',
        200 : 'DictShortName',
        208 : 'Watermark',
        501 : 'Document Type',
        502 : 'last_update_time',
        503 : 'Updated_Title',
        504 : 'ASIN_(504)',
        508 : 'Title file-as',
        517 : 'Creator file-as',
        522 : 'Publisher file-as',
        524 : 'Language_(524)',
        525 : 'primary-writing-mode',
        527 : 'page-progression-direction',
        528 : 'Unknown_Logical_Value_(528)',
        529 : 'Original_Source_Description_(529)',
        534 : 'Unknown_(534)',
        535 : 'Kindlegen_BuildRev_Number',
    }
    id_map_values = {
        115 : 'sample',
        116 : 'StartOffset',
        121 : 'K8(121)_Boundary_Section',
        125 : 'K8(125)_Count_of_Resources_Fonts_Images',
        131 : 'K8(131)_Unidentified_Count',
        201 : 'CoverOffset',
        202 : 'ThumbOffset',
        203 : 'Has Fake Cover',
        204 : 'Creator Software',
        205 : 'Creator Major Version',
        206 : 'Creator Minor Version',
        207 : 'Creator Build Number',
        401 : 'Clipping Limit',
        402 : 'Publisher Limit',
        404 : 'Text to Speech Disabled',
        406 : 'Rental_Indicator',
    }
    id_map_hexstrings = {
        209 : 'Tamper Proof Keys (hex)',
        300 : 'Font Signature (hex)',
        403 : 'Unknown_(403) (hex)',
        405 : 'Unknown_(405) (hex)',
        407 : 'Unknown_(407) (hex)',
        450 : 'Unknown_(450) (hex)',
        451 : 'Unknown_(451) (hex)',
        452 : 'Unknown_(452) (hex)',
        453 : 'Unknown_(453) (hex)',
    }

    def __init__(self, sect, sectNumber):
        self.sect = sect
        self.start = sectNumber
        self.header = self.sect.loadSection(self.start)
        if len(self.header)>20 and self.header[16:20] == 'MOBI':
            self.sect.setsectiondescription(0,"Mobipocket Header")
            self.palm = False
        elif self.sect.ident == 'TEXtREAd':
            self.sect.setsectiondescription(0, "PalmDOC Header")
            self.palm = True
        else:
            raise unpackException('Unknown File Format')

        self.records, = struct.unpack_from('>H', self.header, 0x8)
        # set defaults in case this is a PalmDOC
        self.title = self.sect.palmname
        self.length = len(self.header)-16
        self.type = 3
        self.codepage = 1252
        self.codec = 'windows-1252'
        self.unique_id = 0
        self.version = 0
        self.hasExth = False
        self.exth = ''
        self.exth_offset = self.length + 16
        self.exth_length = 0
        self.crypto_type = 0
        self.firstnontext = self.start+self.records + 1
        self.firstresource = self.start+self.records + 1
        self.metaOrthIndex = 0xffffffff
        self.mlstart = self.sect.loadSection(self.start+1)[:4]

        # set up for decompression/unpacking
        self.compression, = struct.unpack_from('>H', self.header, 0x0)
        if self.compression == 0x4448:
            reader = HuffcdicReader()
            huffoff, huffnum = struct.unpack_from('>LL', self.header, 0x70)
            huffoff = huffoff + self.start
            self.sect.setsectiondescription(huffoff,"Huffman Compression Seed")
            reader.loadHuff(self.sect.loadSection(huffoff))
            for i in xrange(1, huffnum):
                self.sect.setsectiondescription(huffoff+i,"Huffman CDIC Compression Seed %d" % i)
                reader.loadCdic(self.sect.loadSection(huffoff+i))
            self.unpack = reader.unpack
        elif self.compression == 2:
            self.unpack = PalmdocReader().unpack
        elif self.compression == 1:
            self.unpack = UncompressedReader().unpack
        else:
            raise unpackException('invalid compression type: 0x%4x' % self.compression)

        if self.palm:
            return

        self.length, self.type, self.codepage, self.unique_id, self.version = struct.unpack('>LLLLL', self.header[20:40])
        codec_map = {
            1252 : 'windows-1252',
            65001: 'utf-8',
        }
        if self.codepage in codec_map.keys():
            self.codec = codec_map[self.codepage]

        # title
        toff, tlen = struct.unpack('>II', self.header[0x54:0x5c])
        tend = toff + tlen
        self.title=self.header[toff:tend]

        exth_flag, = struct.unpack('>L', self.header[0x80:0x84])
        self.hasExth = exth_flag & 0x40
        self.exth_offset = self.length + 16
        self.exth_length = 0
        if self.hasExth:
            self.exth_length, = struct.unpack_from('>L', self.header, self.exth_offset+4)
            self.exth_length = ((self.exth_length + 3)>>2)<<2 # round to next 4 byte boundary
            self.exth = self.header[self.exth_offset:self.exth_offset+self.exth_length]

        #self.mlstart = self.sect.loadSection(self.start+1)
        #self.mlstart = self.mlstart[0:4]
        self.crypto_type, = struct.unpack_from('>H', self.header, 0xC)

        # Start sector for additional files such as images, fonts, resources, etc
        # Can be missing so fall back to default set previously
        ofst, = struct.unpack_from('>L', self.header, 0x6C)
        if ofst != 0xffffffff:
            self.firstresource = ofst + self.start
        ofst, = struct.unpack_from('>L', self.header, 0x50)
        if ofst != 0xffffffff:
            self.firstnontext = ofst + self.start

        if self.isPrintReplica():
            return

        if self.version < 8:
            # Dictionary metaOrthIndex
            self.metaOrthIndex, = struct.unpack_from('>L', self.header, 0x28)
            if self.metaOrthIndex != 0xffffffff:
                self.metaOrthIndex += self.start

        # handle older headers without any ncxindex info and later
        # specifically 0xe4 headers
        if self.length + 16 < 0xf8:
            return

    def dump_exth(self):
        # determine text encoding
        codec=self.codec
        if (not self.hasExth) or (self.exth_length) == 0 or (self.exth == ''):
            return
        num_items, = struct.unpack('>L', self.exth[8:12])
        pos = 12
        print "Key Size Decription                     Value"
        for _ in range(num_items):
            id, size = struct.unpack('>LL', self.exth[pos:pos+8])
            contentsize = size-8
            content = self.exth[pos + 8: pos + size]
            if id in MobiHeader.id_map_strings.keys():
                exth_name = MobiHeader.id_map_strings[id]
                print '{0: >3d} {1: >4d} {2: <30s} {3:s}'.format(id, contentsize, exth_name, unicode(content, codec).encode("utf-8"))
            elif id in MobiHeader.id_map_values.keys():
                exth_name = MobiHeader.id_map_values[id]
                if size == 9:
                    value, = struct.unpack('B',content)
                    print '{0:3d} byte {1:<30s} {2:d}'.format(id, exth_name, value)
                elif size == 10:
                    value, = struct.unpack('>H',content)
                    print '{0:3d} word {1:<30s} 0x{2:0>4X} ({2:d})'.format(id, exth_name, value)
                elif size == 12:
                    value, = struct.unpack('>L',content)
                    print '{0:3d} long {1:<30s} 0x{2:0>8X} ({2:d})'.format(id, exth_name, value)
                elif size == 16:
                    hival, = struct.unpack('>L',content[0:4])
                    loval, = struct.unpack('>L',content[0:4])
                    value = hival*0x100000000 + loval
                    print '{0:3d}   LL {1:<30s} 0x{2:0>16X} ({2:d})'.format(id, exth_name, value)
                else:
                    print '{0: >3d} {1: >4d} {2: <30s} (0x{3:s})'.format(id, contentsize, "Bad size for "+exth_name, content.encode('hex'))
            elif id in MobiHeader.id_map_hexstrings.keys():
                exth_name = MobiHeader.id_map_hexstrings[id]
                print '{0:3d} {1:4d} {2:<30s} 0x{3:s}'.format(id, contentsize, exth_name, content.encode('hex'))
            else:
                exth_name = "Unknown EXTH ID {0:d}".format(id)
                print "{0: >3d} {1: >4d} {2: <30s} 0x{3:s}".format(id, contentsize, exth_name, content.encode('hex'))
            pos += size
        return

    def dumpheader(self):
        # first 16 bytes are not part of the official mobiheader
        # but we will treat it as such
        # so section 0 is 16 (decimal) + self.length in total == at least 0x108 bytes for Mobi 8 headers
        print "Dumping section %d, Mobipocket Header version: %d, total length %d" % (self.start,self.version, self.length+16)
        self.hdr = {}
        # set it up for the proper header version
        if self.version == 0:
            self.mobi_header = MobiHeader.palmdoc_header
            self.mobi_header_sorted_keys = MobiHeader.palmdoc_header_sorted_keys
        elif self.version < 8:
            self.mobi_header = MobiHeader.mobi6_header
            self.mobi_header_sorted_keys = MobiHeader.mobi6_header_sorted_keys
        else:
            self.mobi_header = MobiHeader.mobi8_header
            self.mobi_header_sorted_keys = MobiHeader.mobi8_header_sorted_keys

        # parse the header information
        for key in self.mobi_header_sorted_keys:
            (pos, format, tot_len) = self.mobi_header[key]
            if pos < (self.length + 16):
                val, = struct.unpack_from(format, self.header, pos)
                self.hdr[key] = val

        if 'title_offset' in self.hdr:
            title_offset = self.hdr['title_offset']
            title_length = self.hdr['title_length']
        else:
            title_offset = 0
            title_length = 0
        if title_offset == 0:
            title_offset = len(self.header)
            title_length = 0
            self.title = self.sect.palmname
        else:
            self.title = self.header[title_offset:title_offset+title_length]
            # title record always padded with two nul bytes and then padded with nuls to next 4 byte boundary
            title_length = ((title_length+2+3)>>2)<<2

        self.extra1 = self.header[self.exth_offset+self.exth_length:title_offset]
        self.extra2 = self.header[title_offset+title_length:]


        print "Mobipocket header from section %d" % self.start
        print "     Offset  Value Hex Dec        Description"
        for key in self.mobi_header_sorted_keys:
            (pos, format, tot_len) = self.mobi_header[key]
            if pos < (self.length + 16):
                if key != 'magic':
                    fmt_string = "0x{0:0>3X} ({0:3d}){1: >" + str(9-2*tot_len) +"s}0x{2:0>" + str(2*tot_len) + "X} {2:10d} {3:s}"
                else:
                    fmt_string = "0x{0:0>3X} ({0:3d}){2:>11s}            {3:s}"
                print fmt_string.format(pos, " ",self.hdr[key], key)
        print ""

        if self.exth_length > 0:
            print "EXTH metadata, offset %d, padded length %d" % (self.exth_offset,self.exth_length)
            self.dump_exth()
            print ""

        if len(self.extra1) > 0:
            print "Extra data between EXTH and Title, length %d" % len(self.extra1)
            print self.extra1.encode('hex')
            print ""

        if title_length > 0:
            print "Title in header at offset %d, padded length %d: '%s'" %(title_offset,title_length,self.title)
            print ""

        if len(self.extra2) > 0:
            print "Extra data between Title and end of header, length %d" % len(self.extra2)
            print  self.extra2.encode('hex')
            print ""

    def isPrintReplica(self):
        return self.mlstart[0:4] == "%MOP"

    def isK8(self):
        return self.start != 0 or self.version == 8

    def isEncrypted(self):
        return self.crypto_type != 0

    def isDictionary(self):
        return self.metaOrthIndex != 0xffffffff

    def decompress(self, data):
        return self.unpack(data)

    def getMetaData(self):

        def addValue(name, value):
            if name not in self.metadata:
                self.metadata[name] = [value]
            else:
                self.metadata[name].append(value)

        self.metadata = {}
        codec=self.codec
        if self.hasExth:
            extheader=self.exth
            _length, num_items = struct.unpack('>LL', extheader[4:12])
            extheader = extheader[12:]
            pos = 0
            for _ in range(num_items):
                id, size = struct.unpack('>LL', extheader[pos:pos+8])
                content = extheader[pos + 8: pos + size]
                if id in MobiHeader.id_map_strings.keys():
                    name = MobiHeader.id_map_strings[id]
                    addValue(name, unicode(content, codec).encode('utf-8'))
                elif id in MobiHeader.id_map_values.keys():
                    name = MobiHeader.id_map_values[id]
                    if size == 9:
                        value, = struct.unpack('B',content)
                        addValue(name, str(value))
                    elif size == 10:
                        value, = struct.unpack('>H',content)
                        addValue(name, str(value))
                    elif size == 12:
                        value, = struct.unpack('>L',content)
                        addValue(name, str(value))
                    else:
                        addValue(name, content.encode('hex'))
                elif id in MobiHeader.id_map_hexstrings.keys():
                    name = MobiHeader.id_map_hexstrings[id]
                    addValue(name, content.encode('hex'))
                else:
                    name = str(id) + ' (hex)'
                    addValue(name, content.encode('hex'))
                pos += size
        return self.metadata


def process_all_mobi_headers(files, sect, mhlst, K8Boundary, k8only=False):
    # Keep track of our status straight away, in case a combo file has a cover in the M7 part, but not the KF8 part...
    got_cover = False

    for mh in mhlst:

        if mh.isK8():
            sect.setsectiondescription(mh.start,"KF8 Header")
            mhname = os.path.join(files.outdir,"header_K8.dat")
            print "Processing K8 section of book..."
        elif mh.isPrintReplica():
            raise unpackException('Unsupported file format (Print Replica)')
        else:
            if mh.version == 0:
                sect.setsectiondescription(mh.start, "PalmDoc Header".format(mh.version))
            else:
                sect.setsectiondescription(mh.start,"Mobipocket {0:d} Header".format(mh.version))
            mhname = os.path.join(files.outdir,"header.dat")
            print "Processing Mobipocket {0:d} section of book...".format(mh.version)

        if DUMP:
            # write out raw mobi header data
            open(pathof(mhname), 'wb').write(mh.header)

        # process each mobi header
        if mh.isEncrypted():
            print "Book is encrypted"

        # Abort if it's a dictionary
        if CDETYPE_CHECK:
            if mh.isDictionary():
                # Don't raise an exception, it's annoying as hell when looking up stuff in verbose mode
                #raise unpackException('This is a dictionary')
                print "This is a dictionary"

        # build up the metadata
        metadata = mh.getMetaData()
        metadata['Title'] = [unicode(mh.title, mh.codec).encode("utf-8")]
        metadata['Codec'] = [mh.codec]
        metadata['UniqueID'] = [str(mh.unique_id)]
        if not DUMP:
            print "Mobi Version:", mh.version
            print "Codec:", mh.codec
            print "Title:", mh.title
            if 'Updated_Title'  in mh.metadata:
                print "EXTH Title:", str(mh.metadata['Updated_Title'][0])
            if mh.compression == 0x4448:
                print "Huffdic compression"
            elif mh.compression == 2:
                print "Palmdoc compression"
            elif mh.compression == 1:
                print "No compression"
        else:
            mh.dumpheader()

        # Abort if it's not an EBOK or PDOC
        if CDETYPE_CHECK:
            # Do we want to parse periodicals, too?
            if path.exists('/mnt/us/linkss/periodicals'):
                cdetypechk_list = ['EBOK', 'PDOC', 'MAGZ', 'NWPR']
                cdetypechk_error = 'File is neither a book, a periodical, nor a personal document'
            else:
                cdetypechk_list = ['EBOK', 'PDOC']
                cdetypechk_error = 'File is neither a book nor a personal document'
            if not 'Document Type' in metadata:
                # Files built by KindleGen don't have a CDE Type set yet...
                print "No CDE Type in EXTH!"
            elif metadata['Document Type'][0] not in cdetypechk_list:
                raise unpackException(cdetypechk_error)

        # process additional sections that represent images, resources, fonts, and etc
        print "Unpacking cover image"
        beg = mh.firstresource
        # Apparently, some content producers ship stuff with broken metadata on the Kindle Store...
        # Worst case scenario, always assume that the first resource is the cover, our checks later on will make sure we end up with an image or nothing
        coverindex = beg
        brokencover = False
        if 'CoverOffset' in metadata:
            # Some pretty old MOBI files rely on a NULL pointer to discard this field, honor it
            if int(metadata['CoverOffset'][0]) != 0xffffffff:
                coverindex += int(metadata['CoverOffset'][0])
            else:
                print "Warning: EXTH CoverOffset is a null pointer, discarding it and assuming the first resource in section {0:d} is the cover!".format(coverindex)
                brokencover = True
        else:
            print "Warning: could not determine cover location (CoverOffset missing from EXTH), assuming the first resource in section {0:d} is the cover!".format(coverindex)
            brokencover = True
        end = sect.num_sections
        if beg < K8Boundary:
            # then we're processing the first part of a combination file
            end = K8Boundary
        for i in xrange(beg, end):
            data = sect.loadSection(i)
            type = data[0:4]
            if type in ["FLIS", "FCIS", "FDST", "DATP"]:
                sect.setsectiondescription(i,"Type {0:s}".format(type))
                continue
            elif type == "SRCS":
                sect.setsectiondescription(i,"Zipped Source Files")
                continue
            elif type == "CMET":
                sect.setsectiondescription(i,"Kindlegen log")
                continue
            elif type == "FONT":
                fontname = "font%05d" % i
                sect.setsectiondescription(i,"Font {0:s}".format(fontname))
                continue
            elif type == "RESC":
                sect.setsectiondescription(i,"K8 RESC section")
                continue

            if data == EOF_RECORD:
                sect.setsectiondescription(i,"End Of File")
                continue

            # Make sure it's the cover!
            if i == coverindex:
                # if reach here should be an image but double check to make sure
                # Get the proper file extension
                imgtype = imghdr.what(None, data)
                # imghdr only checks for JFIF or Exif JPEG files. Apparently, there are some
                # with only the magic JPEG bytes out there...
                # ImageMagick handle those, so, do it too.
                if imgtype is None and data[0:2] == b'\xFF\xD8':
                    # Get last non-null bytes
                    last = len(data)
                    while (data[last-1:last] == b'\x00'):
                        last-=1
                    # Be extra safe, check the trailing bytes, too.
                    if data[last-2:last] == b'\xFF\xD9':
                        imgtype = "jpeg"
                if imgtype is None:
                    print "Warning: Section %s does not contain a recognised resource" % i
                    sect.setsectiondescription(i,"Mysterious Section, first four bytes %s" % describe(data[0:4]))
                    if DUMP:
                        fname = "unknown%05d.dat" % i
                        outname= os.path.join(files.outdir, fname)
                        open(pathof(outname), 'wb').write(data)
                        sect.setsectiondescription(i,"Mysterious Section, first four bytes %s extracting as %s" % (describe(data[0:4]), fname))
                else:
                    if brokencover and imgtype is not "jpeg":
                        # If we're playing the guessing game, try a tiny bit harder to look for the first image that might actually be a cover.
                        # Some periodicals have an unrelated gif in the first section, so look for the first JPEG instead...
                        coverindex += 1
                        print "First resource in that section did not appear to be the cover image, now looking in section {0:d} . . .".format(coverindex)
                        continue
                    else:
                        imgname = "image%05d.%s" % (i, imgtype)
                        # Put the CDE Key in there, to help ID the file for the ScreenSavers cache on legacy devices...
                        if not 'ASIN' in metadata:
                            # No exth 113, use the sha1 of the full path, like the Kindle
                            cdekey = hashlib.sha1(os.path.abspath(files.infile)).hexdigest()
                        else:
                            cdekey = metadata['ASIN'][0]
                        covername = "cover_raw_%s.%s" % (cdekey, imgtype)
                        print "Extracting cover image: {0:s} as {1:s} from section {2:d}".format(imgname,covername,i)
                        outimg = os.path.join(files.outdir, covername)
                        open(pathof(outimg), 'wb').write(data)
                        sect.setsectiondescription(i,"Image {0:s}".format(imgname))
                        # Yay, got a cover!
                        got_cover = True
            else:
                continue

    # Die if we couldn't extract a cover at all...
    if not got_cover:
        raise unpackException('Failed to extract a cover image!')

    return


def unpackBook(infile, outdir, dodump=False):
    global DUMP
    if DUMP or dodump:
        DUMP = True

    infile = utf8_str(infile)
    outdir = utf8_str(outdir)

    files = fileNames(infile, outdir)

    # process the PalmDoc database header and verify it is a mobi
    sect = Sectionizer(infile)
    if sect.ident != 'BOOKMOBI' and sect.ident != 'TEXtREAd':
        raise unpackException('Invalid file format')
    if DUMP:
        sect.dumppalmheader()
    else:
        print "Palm DB type: %s, %d sections." % (sect.ident,sect.num_sections)

    # scan sections to see if this is a compound mobi file (K8 format)
    # and build a list of all mobi headers to process.
    mhlst = []
    mh = MobiHeader(sect,0)
    # if this is a mobi8-only file hasK8 here will be true
    mhlst.append(mh)
    K8Boundary = -1

    if mh.isK8():
        print "Unpacking a KF8 book..."
        hasK8 = True
    else:
        # This is either a Mobipocket 7 or earlier, or a combi M7/KF8
        # Find out which
        hasK8 = False
        for i in xrange(len(sect.sectionoffsets)-1):
            before, after = sect.sectionoffsets[i:i+2]
            if (after - before) == 8:
                data = sect.loadSection(i)
                if data == K8_BOUNDARY:
                    sect.setsectiondescription(i,"Mobi/KF8 Boundary Section")
                    mh = MobiHeader(sect,i+1)
                    hasK8 = True
                    mhlst.append(mh)
                    K8Boundary = i
                    break
        if hasK8:
            print "Unpacking a Combination M{0:d}/KF8 book...".format(mh.version)
        else:
            print "Unpacking a Mobipocket {0:d} book...".format(mh.version)

    process_all_mobi_headers(files, sect, mhlst, K8Boundary, False)
    if DUMP:
        sect.dumpsectionsinfo()
    return

def usage(progname):
    print ""
    print "Description:"
    print "  Unpack the cover from a Kindle/MobiPocket ebook"
    print "  into the specified output folder."
    print "Usage:"
    print "  %s -d -k -h infile [outdir]" % progname
    print "Options:"
    print "    -d           dump headers and other info to output and extra files"
    print "    -k           make sure the file is a book or personal document"
    print "    -h           print this help message"


def main():
    global DUMP
    global CDETYPE_CHECK
    print "MobiCover 0.4.N (ripped out of kindleunpack v0.66b)"
    print "   Based on initial version Copyright © 2009 Charles M. Hannum <root@ihack.net>"
    print "   Extensions / Improvements Copyright © 2009-2014 P. Durrant, K. Hendricks, S. Siebert, fandrieu, DiapDealer, nickredding, tkeo."
    print "   This program is free software: you can redistribute it and/or modify"
    print "   it under the terms of the GNU General Public License as published by"
    print "   the Free Software Foundation, version 3."

    argv = utf8_argv()
    progname = os.path.basename(argv[0])
    try:
        opts, args = getopt.getopt(argv[1:], "hdk")
    except getopt.GetoptError, err:
        print str(err)
        usage(progname)
        sys.exit(2)

    if len(args) < 1:
        usage(progname)
        sys.exit(2)

    for o, a in opts:
        if o == "-d":
            DUMP = True
        if o == "-k":
            CDETYPE_CHECK = True
        if o == "-h":
            usage(progname)
            sys.exit(0)

    if len(args) > 1:
        infile, outdir = args
    else:
        infile = args[0]
        # FIXME: Use default outdir on Kindle?
        outdir = os.path.dirname(infile)

    infileext = os.path.splitext(infile)[1].upper()
    if infileext not in ['.MOBI', '.PRC', '.AZW', '.AZW3', '.POBI']:
        print "Error: first parameter must be a Kindle/Mobipocket ebook."
        return 1

    try:
        print 'Unpacking Book...'
        unpackBook(infile, outdir)
        print 'Completed'

    except ValueError, e:
        print "Error: %s" % e
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
