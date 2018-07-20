import sys
import codecs
from collections import defaultdict

import simplejson as json
from itertools import chain


def string2hash(s):
    # https: // gist.github.com / hanleybrand / 5224673
    h = 0
    for c in s:
        h = (31 * h + ord(c)) & 0xFFFFFFFF
    return ((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000


def ngrams(s, n):
    for i in range(len(s) - n + 1):
        yield s[i:i + n]


def generate_hash_values(s, hash_size):
    s = s.lower()
    # bigrams = ngrams('^%s$' % s, 2)
    trigrams = ngrams('^%s$' % s, 3)
    for gram in trigrams: # chain(bigrams, trigrams):
        yield string2hash(gram) % hash_size

def generate_definition(entry):
    definition = ''
    for pos, text in entry['english'].items():
        definition += '<b>%s</b> %s ' % (pos, text)

    return definition


def main():
    hash_size = 512
    entries_dict = defaultdict(list)
    for line in sys.stdin:
        entry = json.loads(line)
        hash_values = set(generate_hash_values(entry['title'], hash_size))
        for value in hash_values:
            entries_dict[value].append({
                'title': entry['title'],
                'definition': generate_definition(entry)
            })

    for value, entries in entries_dict.items():
        with codecs.open('data/%03d.js' % value, mode='w', encoding='utf-8') as f:
            index_body = json.dumps(entries, ensure_ascii=False)
            f.write('dict[%d]=%s;' % (value, index_body))

if __name__ == '__main__':
    main()
