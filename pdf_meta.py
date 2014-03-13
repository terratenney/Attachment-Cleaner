# -*- coding: utf-8 -*-
"""
Created on Wed Mar 12 18:53:42 2014

@author: zeke
"""

import os

from libzotero.libzotero import LibZotero
from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.generic import NameObject, createStringObject

zp = u'/home/zeke/.zotero/zotero/w5xs38jf.default/'

zot = LibZotero(zp)
cur = zot.conn.cursor()

in_root = '/home/zeke/Documents/articles/'
out_root = '/home/zeke/Documents/articles/updated/'
t_dic = '/home/zeke/tmp/'

flst = os.listdir(in_root)
paths = []

count = 0
for f in zot.index.values():
    if not isinstance(f.fulltext, type(None)):
        print f.fulltext
        if os.path.isfile(f.fulltext):
            p = f.fulltext

            root = '/'.join(p.split('/')[0:-2]) + '/'
            fname = p.split('/')[-1]
            fin = file(p, 'rb')
            try:

                pdf_in = PdfFileReader(fin)

                writer = PdfFileWriter()

                for page in range(pdf_in.getNumPages()):
                    writer.addPage(pdf_in.getPage(page))
                infoDict = writer._info.getObject()
                info = pdf_in.documentInfo
                for key in info:
                    infoDict.update({NameObject(key): createStringObject(info[key])})
                    infoDict.update({NameObject('/Title'): createStringObject(f.format_title())})
                    infoDict.update({NameObject(key): createStringObject(info[key])})
                    infoDict.update({NameObject('/Author'): createStringObject(f.format_author())})
                    infoDict.update({NameObject(key): createStringObject(info[key])})

                    infoDict.update({NameObject('/Date'): createStringObject(f.format_date())})
                    infoDict.update({NameObject(key): createStringObject(info[key])})
                    infoDict.update({NameObject('/Publication'): createStringObject(f.format_publication())})
                    infoDict.update({NameObject(key): createStringObject(info[key])})
                    infoDict.update({NameObject('/Producer'): createStringObject(f.format_publication())})

                    infoDict.update({NameObject(key): createStringObject(info[key])})
                    infoDict.update({NameObject('/Citation'): createStringObject(f.full_format())})
                    if f.format_tags():
                        infoDict.update({NameObject(key): createStringObject(info[key])})
                        infoDict.update({NameObject('/Keywords'): createStringObject(f.format_tags())})

                fout = open(t_dic + fname, 'wb')
                writer.write(fout)
                fin.close()
                fout.close()
                os.rename(t_dic + fname, p)
            except:
                'Doesnt work here'


