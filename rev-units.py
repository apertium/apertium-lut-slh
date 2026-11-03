#!/usr/bin/env python3
"""Stream filter for generating with a reversed generator (*.autogen-rev.hfst).

The lut and slh generators read prefixes before the lemma, but the prefixes
are only decided by tags after the lemma, so hfst-proc searches the whole
prefix lattice. Reversed generators read the tags and stem first.

Used twice in modes.xml, around hfst-proc:
  before: each lexical unit ^lemma<tag1><tag2>$ becomes
          [@rev@]^<tag2><tag1>ammel$[@/rev@]
  after:  the generated (reversed) form between the markers is reversed back
          and the markers are removed.
Units marked unknown (*), untranslated (@) or ungenerated (#) are left alone.
Superblanks [..] pass through hfst-proc unchanged, which keeps the markers.
"""

import re
import sys

OPEN, CLOSE = '[@rev@]', '[@/rev@]'
TOKEN = re.compile(r'<[^>]*>|\\.|.', re.S)
UNIT = re.compile(r'(\\.)|(\[(?:\\.|[^\]\\])*\])|\^((?:\\.|[^$\\])*)\$', re.S)
MARKED = re.compile(re.escape(OPEN) + r'(.*?)' + re.escape(CLOSE), re.S)


def reverse(s):
    return ''.join(reversed(TOKEN.findall(s)))


def wrap(m):
    escaped, blank, unit = m.groups()
    if unit is None or unit[:1] in ('*', '@', '#'):
        return m.group(0)
    return OPEN + '^' + reverse(unit) + '$' + CLOSE


def unwrap(m):
    form = m.group(1)
    if form[:1] in ('#', '@', '*'):
        return form[0] + reverse(form[1:])
    return reverse(form)


def convert(text):
    if OPEN in text:
        return MARKED.sub(unwrap, text)
    return UNIT.sub(wrap, text)


def main():
    stdin = open(sys.stdin.fileno(), 'r', encoding='utf-8', newline='')
    if '-z' in sys.argv[1:]:          # null-flush: answer each \0-terminated chunk
        chunk = []
        while True:
            c = stdin.read(1)
            if c in ('\0', ''):
                sys.stdout.write(convert(''.join(chunk)))
                if c == '':
                    break
                sys.stdout.write('\0')
                sys.stdout.flush()
                chunk = []
            else:
                chunk.append(c)
        sys.stdout.flush()
        return
    for line in stdin:
        sys.stdout.write(convert(line))
        sys.stdout.flush()


if __name__ == '__main__':
    main()
