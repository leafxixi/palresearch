#!/usr/bin/env python2
# -*- coding: utf-8 -*-  
import argparse
import struct
import os
import demkf
import utilcommon
from ctypes import *
from PIL import Image, ImageDraw

args=None

def deRLE(input):
    dll=cdll.LoadLibrary(utilcommon.getPallibPath())
    width,height = struct.unpack("<hh",input[0:4])
    length=width*height
    ArrayType = c_int16 * length
    buffer = ArrayType()
    memset(buffer,args.transparent_palette_index,length)
    dll.decoderle(input,c_void_p(addressof(buffer)),width,width,height,0,0)
    return width,height,string_at(buffer,width*height)

def process():
    pat = demkf.deMKF(args.palette,args.palette_id)
    if len(pat) > 768:
        pat=pat[0:768]
    pat="".join([chr(ord(x)*4) for x in pat])
    
    width,height,buffer = deRLE(args.rle.read())
    
    if args.saveraw:
        open(args.output.name+".raw","wb").write(buffer)
    
    im=Image.frombytes("P", (width,height), buffer)
    im.putpalette(pat)
    
    if args.transparent:
        mask=Image.new('L', im.size, color=255)
        draw=ImageDraw.Draw(mask) 
        for x in range(0,width): 
            for y in range(0,height):
                if im.getpixel((x,y)) == args.transparent_palette_index:
                    draw.point( (x,y), fill=0)
        im.putalpha(mask)
    
    if args.show:
        im.show(); 
    
    if args.output:
        im.save(args.output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='tool for converting RLE to palette BMP/PNG')
    parser.add_argument('rle', type=argparse.FileType('rb'),
                       help='rle file to decode')
    parser.add_argument('-o','--output',type=argparse.FileType('wb'),
                       help='resulting bmp')
    parser.add_argument('-p', '--palette', type=argparse.FileType('rb'), required=True, 
                       help='PAT file')
    parser.add_argument('-i', '--palette_id', type=int, default=0,
                       help='palette id')
    parser.add_argument('-d', '--transparent_palette_index', default=0xff,
                       help='palette id')
    parser.add_argument('--show', action='store_true', default=False,
                       help='show decoded image')
    parser.add_argument('--transparent', action='store_true', default=False,
                       help='output transparent as alpha zero - ~10x expensive, and not available in bmp target, and will REQUANTIZE palatte, which will deny the output picture from reimporting EXACTLY any more, leaving only viewable. Turned off by default')
    parser.add_argument('--saveraw', action='store_true', default=False,
                       help='save decoded raw data')

    args = parser.parse_args()
    if not args.show and args.output == None:
        print "Either Show or Specify output filename"
    else:
        process()