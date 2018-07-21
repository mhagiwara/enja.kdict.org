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


def iterate_wiktionary_data(io):
    for line in io:
        entry = json.loads(line)
        definition = generate_definition(entry)
        yield (entry['title'], definition)

def iterate_ejdict_data(io):
    for line in io:
        fields = line.strip().split('\t')
        if len(fields) != 2:
            print('Invalid number of fields: %s' % line)
            continue

        title, definition = fields
        yield (title, definition)


def main():
    hash_size = 512
    entries_dict = defaultdict(list)
    all_titles = set()

    wiktionary_file = open(sys.argv[1])
    wiktionary_iter = iterate_wiktionary_data(wiktionary_file)

    ejdict_file = open(sys.argv[2])
    ejdict_iter = iterate_ejdict_data(ejdict_file)

    for title, definition in chain(wiktionary_iter, ejdict_iter):
        if title in all_titles:
            continue
        all_titles.add(title)

        hash_values = set(generate_hash_values(title, hash_size))
        for value in hash_values:
            entries_dict[value].append({
                'title': title,
                'definition': definition
            })

    for value, entries in entries_dict.items():
        with codecs.open('data/%03d.js' % value, mode='w', encoding='utf-8') as f:
            index_body = json.dumps(entries, ensure_ascii=False)
            f.write('dict[%d]=%s;' % (value, index_body))

    ejdict_file.close()
    wiktionary_file.close()

    print('Total # of words = %d' % len(all_titles))

if __name__ == '__main__':
    main()
