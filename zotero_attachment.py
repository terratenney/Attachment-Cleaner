#!/usr/bin/env python
import sqlite3
import os
import os.path
from collections import Counter


class zotero_cleaner(object):
    """
    This is a simple tool that checks if an item attachment is a file in your storage directory and deletes
    the record if it is not. Options include cleaning the pdf directory for duplicate files (by name only) and
    removing duplicate attachments. Only checks for .pdf's not stored in the Zotero default 'storage' directory.
    You can use Zotfile to rename all files, then run this program, and finally rename all attachments after cleaning
    to use Zotero default directory. May cause issues if you have multiple sync'd machines without full-paths (not relative paths)
    """

    attachment_query = u"""
            select items.itemID, itemAttachments.path, itemAttachments.itemID
            from items, itemAttachments
            where items.itemID = itemAttachments.sourceItemID
            """

    def __init__(self, zotero_path, file_path):
        """
        Zotero Path is where the zotero.sqlite database is stored

        File Path is where your pdf attachments are stored. Note all pdf's need to be housed
        in base directory.
        """

        assert (isinstance(zotero_path, unicode))
        print(u"zotero_path = %s" % zotero_path)
        # Set paths
        self.zotero_path = zotero_path
        self.storage_path = os.path.join(self.zotero_path, u"storage")
        self.zotero_database = os.path.join(self.zotero_path, u"zotero.sqlite")
        self.file_path = file_path
        self.attachment_ext = u".pdf"
        self.con = sqlite3.connect(self.zotero_database)
        self.cur = self.con.cursor()


    def check_attachments(self, attachment_query=attachment_query):
        self.cur.execute(attachment_query)
        qs = []

        for rec in self.cur.fetchall():
            path = rec[1]
            if not isinstance(path, type(None)):
                if not path.startswith('storage:'):
                    if not os.path.isfile(path):
                        qs.append({'itemID': rec[0], 'path': rec[1], 'attachID': rec[2]})

        print "Found %s attachments that do not have corresponding files in %s \n" % (len(qs), self.file_path)

        self._nflst = qs

    def clean_file_folder(self):
        """
        Assumes that duplicate pdf's are stored with identical names but with 1-2-3-4-etc.
        at the end to differentiate. If an original exists (e.g., file.pdf) and a duplicate (e.g., file1.pdf)
        the duplicate will be removed. Use with caution. No way to recover deleted files.

        """
        flst = os.listdir(self.file_path)
        dlst = []
        for f in flst:
            if f.endswith('1.pdf') or f.endswith('2.pdf') or f.endswith('3.pdf') or f.endswith('4.pdf') \
                or f.endswith('5.pdf') or f.endswith('6.pdf') or f.endswith('7.pdf') or f.endswith('8.pdf') \
                or f.endswith('9.pdf'):
                o_name = f[0:-5] + '.pdf'
                if os.path.isfile(self.file_path + o_name):
                    print "Found duplicate for file '%s' with '%s' \n" % (o_name, f)
                    dlst.append(self.file_path + o_name)

            print
            print "Found %s duplicate files." % len(dlst)
            print
            answer = raw_input("Do you want to delete them? (y/n)")
            print answer
            print type(answer)
            if answer == 'n':
                print "No files deleted...goodbye"
                break
            elif answer == 'y':
                for f in dlst:
                    print "Deleting: %s " % f
                    os.remove(f)

    def remove_duplicate_attachments(self):
        paths = {}
        tests = []
        con = self.con
        cur = self.cur
        qs = self._nflst

        for rec in qs:
            if paths.has_key(rec['path'][0:-6]):
                paths[rec['path'][0:-6]].append(rec[2])
            else:
                paths[rec['path'][0:-6]] = [rec[2]]
            tests.append(rec['path'][0:-6])

        counts = Counter(tests)

        for k, v in counts.items():
            if v > 1:
                print '%s many duplicate %s attachments' % (k, len(v))
                count = 0
                for itemid in paths[k[0:-6]]:
                    cur.execute(
                        'select itemAttachments.path from itemAttachments where itemAttachments.itemID=%s;' % itemid)
                    res = cur.fetchall()
                    if not os.path.isfile(res[0]):
                        cur.execute('DELETE from itemAttachments where itemAttachments.itemID=%s;' % itemid)
                        con.commit()
                    if count > 0:
                        print 'deleting attachment %s with path %s' % (itemid, res[0])
                        cur.execute('DELETE from itemAttachments where itemAttachments.itemID=%s;' % itemid)
                        con.commit()
                    else:
                        continue
                    count += 1

    def run(self):
        self.clean_file_folder()
        self.check_attachments()
        self.remove_duplicate_attachments()
        self.con.commit()
        self.con.close()


if __name__ == '__main__':
    zp = u'/home/zeke/.zotero/zotero/w5xs38jf.default/'
    fp = u'/home/zeke/Documents/articles/'

    z = zotero_cleaner(zp, fp)
    z.run()
