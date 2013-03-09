#!/usr/bin/python
# ------------------------------------------------------------------------------
# File: scrape_i386.py
# Date: March 2013
# Purpose: Standalone executable to scrape Intel instruction reference
# Description: Expects the Intel instruction reference in text form to be in 
#   the current directory.  The text form of the PDF can be generated with the
#   following command:
#
#       pdftotext -layout -enc Latin1 intel_ref.pdf intel_ref.txt
#
#   The pdftotext utility is distributed with xpdf.
# ------------------------------------------------------------------------------
import re
import subprocess
import os
import sqlite3

class InstDoc:
    def __init__(self, page_num):
        self.mnemonic = 'unknown'
        self.short_help = 'uninitialized'
        self.long_help = ''
        self.page_start = page_num
        self.num_pages = 1

        # used in stream filtering of long help
        self.prev_line = ''
        self.page_num_pattern = re.compile('^\s*[0-9]+-[0-9]+ Vol\..*$')

    def update_long(self, line):

        if self.page_num_pattern.match(line):
            return

        if line.strip() == '':
            return

        if line.startswith('\x0c'):
            return

        if self.mnemonic in line and self.short_help in line:
            return

        line = line.strip()

        if line[0].isupper() and (self.prev_line.endswith('.') or self.prev_line.endswith('.)')):
            self.long_help += '\n'

        self.prev_line = line
        self.long_help += self.prev_line + '\n'

    def gen_png(self, directory, name):
        
        try:
            os.makedirs(directory)
        except OSError:
            pass

        subprocess.check_call('pdftoppm -png -f %d -l %d intel_ref.pdf %s' % (self.page_start, self.page_start+self.num_pages-1, os.path.join(directory, name)), shell=True)

    def gen_pdf(self, directory, name):
        try:
            os.makedirs(directory)
        except OSError:
            pass

        subprocess.check_call('pdftk intel_ref.pdf cat %d-%d output %s.pdf' % (self.page_start, self.page_start+self.num_pages-1, os.path.join(directory, name)), shell=True)


    mnemonic = property()
    short_help = property()
    long_help = property()

# read in text file and extract pages
with open('intel_ref.latin', 'r') as f:
    txt = f.read()
    pages = txt.split('\f')

# states
STATE_FIND_START         = 1
STATE_FIND_SUBCODES      = 2
STATE_FIND_DESC          = 3
STATE_GATHER_DESC        = 4

state = STATE_FIND_START

inst_docs = []
desc_start = re.compile(r'^\s*Description.*$')
desc_end = re.compile(r'^\s*Operation.*$')
inst_ref = re.compile(r'^\s*INSTRUCTION SET REFERENCE.*$')
inst_start = re.compile(r'^(?P<mnemonic>[A-Z]+[a-zA-Z/0-9 ]*)\s*-+\s*(?P<short_help>.*)$')

for (page_num, page) in enumerate(pages):

    lines = page.split('\n')

    if state == STATE_FIND_START:
        if inst_ref.match(lines[0]):

            # we already know what the first line looks like, so skip it
            for i in range(1,len(lines)):

                line = lines[i]
                inst_match = inst_start.match(line)

                # ignore empty lines
                if line == '':
                    continue
                # NOTE: The only exception when 'Opcode' did not appear within the next
                #       two lines was for 'MOVS/MOVSB/MOVSW/MOVSD/MOVSQ', which I manually
                #       fixed up by deleting some empty lines in the input file.
                elif inst_match and 'Opcode' in '\n'.join(lines[i+1:i+2]):
                    cur_inst = InstDoc(page_num+1)
                    cur_inst.mnemonic = inst_match.group('mnemonic')
                    cur_inst.short_help = inst_match.group('short_help')
                    inst_docs.append(cur_inst)
                    state = STATE_FIND_DESC
                else:
                    break
            
    # ignore the rest of the page if we're still seeking
    if state != STATE_FIND_START:
    
        cur_inst.num_pages += 1

        for i in range(1,len(lines)):
            line = lines[i]

            if state == STATE_FIND_DESC:
                desc_match = desc_start.match(line)
                if desc_match:
                    state = STATE_GATHER_DESC
                    continue
            elif state == STATE_GATHER_DESC:
                if desc_end.match(line):
                    state = STATE_FIND_START
                    break
                else:
                    cur_inst.update_long(line)

db = "instdoc.db"
connection=sqlite3.connect(db)
cursor=connection.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS instdoc (id INTEGER PRIMARY KEY, platform TEXT, mnemonic TEXT, short TEXT, long TEXT)')
connection.commit()

f = open('def.py', 'w')
f.write('instructions = {\n')

for inst in inst_docs:

    cursor.execute('INSERT INTO instdoc VALUES(null, ?, ?, ?, ?)', ('i386', inst.mnemonic, inst.short_help.decode('latin-1'), inst.long_help.decode('latin-1')))

    f.write("\t'%s' : ( '%s',\n'''%s'''),\n" % (inst.mnemonic, inst.short_help, inst.long_help))
    print '%s -- %s (page %d, count %d)\n' % (inst.mnemonic, inst.short_help, inst.page_start, inst.num_pages)
    #for line in inst.long_help.split('\n'):
    #    print '\t%s' % line

    #name = inst.mnemonic.replace('/', '_').replace(' ','')
    #inst.gen_pdf('./pdf', name)

f.write('}\n')
connection.commit()
cursor.close()
