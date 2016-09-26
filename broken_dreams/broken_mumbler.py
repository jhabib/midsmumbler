import random
import time
import mmap
import os
from collections import defaultdict
from collections import Counter


# def extract_bigrams(start_word=None, file_path=None, output_dict=None):
#     with open(file_path) as file:
#         # print 'searching file...'
#         for line in file:
#             fields = line.split('\t')
#             try:
#                 first, second = fields[0].split(' ')
#             except:
#                 pass
#             if first and start_word < first:
#                 # print 'stopping search for: %s' % start_word
#                 break
#             if second and start_word == first:
#                 output_dict[second] += int(fields[2])
#         file.close()
#     return start_word, output_dict


def get_offsets(mmap_object=None):
    offsets=[]
    for l in iter(mmap_object.readline, ''):
        loc = mmap_object.tell()
        offsets.append(loc)
    return offsets


def get_line_pos(pos=0, mmap_object=None):
    mmap_object.seek(pos)
    line = mmap_object.readline()
    # print line
    return line


def split_line(line):
    fields = line.split('\t')
    f, s = None, None
    fs = fields[0].split(' ')
    if len(fs) == 2:
        f = fs[0]
        s = fs[1]

    # try:
    #     first, second = fields[0].split(' ')
    # except ValueError as ve:
    #     pass
    # print 'first: %s second: %s count: %s' % (first, second, fields[2])
    return f, s, fields[2]


def binary_extract_bigrams(start_word='', file_path='', offsets=[]):
    output_dict = Counter()
    low = 0
    high = len(offsets)
    found = False
    with open(file_path) as fp:
        m = mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ)
        while low <= high and not found:
            current_pos = (low + high) // 2
            seek_to = int(offsets[current_pos])
            line = get_line_pos(seek_to, m)
            first, second, scount = split_line(line)
            if first == start_word:
                # print 'word found. seeking other matches...'
                found = True
                output_dict[second] += int(scount)
                # seek right
                i = current_pos
                while i < len(offsets):
                    i += 1
                    newline = get_line_pos(int(offsets[i]), m)
                    first, second, scount = split_line(newline)
                    if first == start_word:
                        output_dict[second] += int(scount)
                    else:
                        break
                # seek left
                i = current_pos
                while i > 0:
                    i -= 1
                    newline = get_line_pos(int(offsets[i]), m)
                    first, second, scount = split_line(newline)
                    if first == start_word:
                        output_dict[second] += int(scount)
                    else:
                        break
            elif first < start_word:
                # print 'raising low value...'
                low = current_pos + 1
            elif first > start_word:
                # print 'lowering high value...'
                high = current_pos - 1
        m.close()
    return output_dict


def get_line_at_offset(offset, filemap):
    filemap.seek(offset)
    char = filemap.read(1)
    while char != '\n' and filemap.tell() != 1:
        filemap.seek(-2, 1)
        char = filemap.read(1)
    return filemap.readline().rstrip()


def binary_extract_bigrams_bytes(start_word='', file_path=''):
    filesize = os.path.getsize(file_path)

    output_dict = Counter()
    low = 0
    high = filesize
    found = False
    with open(file_path) as fp:
        m = mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ)
        while low <= high and not found:
            current_pos = (low + high) // 2
            # seek_to = current_pos
            line = get_line_at_offset(current_pos, m)
            bytes_read = len(line)
            first, second, scount = split_line(line)
            if first == start_word:
                # print 'word found. seeking other matches...'
                found = True
                output_dict[second] += int(scount)
                # seek right
                i = current_pos
                while i < filesize:
                    i += bytes_read
                    newline = get_line_at_offset(i, m)
                    first, second, scount = split_line(newline)
                    if first == start_word:
                        output_dict[second] += int(scount)
                    else:
                        break
                # seek left
                i = current_pos
                while i > 0:
                    i -= bytes_read
                    newline = get_line_at_offset(i, m)
                    first, second, scount = split_line(newline)
                    if first == start_word:
                        output_dict[second] += int(scount)
                    else:
                        break
            elif first < start_word:
                low = current_pos + bytes_read
            elif first > start_word:
                high = current_pos - bytes_read
        m.close()
    return output_dict


def roulette_selection(input_dict=None):
    f_max = max(input_dict.values())
    items = input_dict.items()
    item_max_index = len(items) - 1
    while True:
        rand_individual = items[random.randint(0, item_max_index)]
        if float(f_max) * random.uniform(0, 1) < rand_individual[1]:
            return rand_individual[0]


def iterative_selection(input_dict=None):
    rand = random.randint(0, sum(input_dict.values()))
    num = 0
    for k, v in input_dict.iteritems():
        num += v
        if rand <= num:
            return k


def binary_mumbler(start_word, length=5, input_data=None, input_offsets=None):
    rem_len = length
    chain = start_word
    while rem_len > 1:
        output_dict = binary_extract_bigrams(start_word, input_data, input_offsets)
        if not output_dict.keys():
            print 'start word %s not found. exiting ...' % start_word
            break
        else:
            # start_word = roulette_selection(output_dict)
            start_word = iterative_selection(output_dict)
            # print 'new start word is: %s' % start_word
            chain = ' '.join([chain, start_word])
            # print '%s\n' % chain
        rem_len -= 1

    return chain


def binary_mumbler_bytes(start_word, length=5, input_data=None):
    rem_len = length
    chain = start_word
    while rem_len > 1:
        output_dict = binary_extract_bigrams_bytes(start_word, input_data)
        if not output_dict.keys():
            print 'start word %s not found. exiting ...' % start_word
            break
        else:
            # start_word = roulette_selection(output_dict)
            start_word = iterative_selection(output_dict)
            # print 'new start word is: %s' % start_word
            chain = ' '.join([chain, start_word])
            # print '%s\n' % chain
        rem_len -= 1

    return chain

# ###### TEST ITERATIVE SELECTION
# od = Counter()
# extract_bigrams('financial', 'googlebooks0.csv', od)
# print(od)
#
# for i in xrange(10):
#     d = Counter()
#     print 'Iterative selection...'
#     t = time.time()
#     for i in range(0, 180600):
#         d[iterative_selection(od)] += 1
#     print 'time taken: %s seconds' % str(time.time() - t)
#     print d
#     c = Counter()
#     print 'Roulette selection... '
#     t = time.time()
#     for i in range(0, 180600):
#         c[roulette_selection(od)] += 1
#     print 'time taken: %s seconds' % str(time.time() - t)
#     print c
#     print '\n'
# ###### TEST ITERATIVE SELECTION


########## TEST BINARY SEARCH MUMBLER ##########
print 'reading offsets into memory...'
t = time.time()
with open('googlebooks0_offsets.csv') as offset_file:
    offsets = offset_file.readlines()
print 'time taken to read offsets: %s' % (time.time() - t)

for i in xrange(10):
    print 'mumbling...'
    t = time.time()
    c = binary_mumbler(start_word='itself', length=5, input_data='googlebooks0.csv', input_offsets=offsets)
    tf = time.time()
    print 'chain is: %s' % c
    print 'time taken to mumble: %s\n' % (tf - t)
########## TEST BINARY SEARCH MUMBLER ##########


print '########## NOT USING OFFSETS ##########'
# ########## TEST BINARY SEARCH MUMBLER ##########
# # print 'reading offsets into memory...'
# # t = time.time()
# # with open('googlebooks0_offsets.csv') as offset_file:
# #     offsets = offset_file.readlines()
# # print 'time taken to read offsets: %s' % (time.time() - t)
#
for i in xrange(10):
    print 'mumbling...'
    t = time.time()
    # output = Counter()
    # c = binary_mumbler(start_word='what', length=25, input_data='googlebooks0.csv', input_offsets=offsets,
    #                    output_dict=output)
    c = binary_mumbler_bytes(start_word='itself', length=10, input_data='googlebooks0.csv')
    tf = time.time()
    print 'chain is: %s' % c
    print 'time taken to mumble: %s\n' % (tf - t)
# ########## TEST BINARY SEARCH MUMBLER ##########


########## DO NOT DELETE - INITIAL MUMBLER VERSION ##########
# def mumbler(start_word='', length=5, input_data=None, output_dict=None):
#     rem_len = length
#     chain = start_word
#     while rem_len > 1:
#         extract_bigrams(start_word, input_data, output_dict)
#         if not output_dict.keys():
#             print 'start word %s not found. exiting ...' % start_word
#             break
#         else:
#             start_word = roulette_selection(output_dict)
#             print 'new start word is: %s' % start_word
#         rem_len -= 1
#         chain = ' '.join([chain, start_word])
#         print '%s\n' % chain
#     return chain

######### Test Mumbler
# otd = Counter()
# c = mumbler('financial', 5, 'googlebooks0.csv', otd)
# print 'mumbler chain is: %s\n' % c
######### Test Mumbler
########## DO NOT DELETE - INITIAL MUMBLER VERSION ##########

# with open('allbigrams.dat') as file:
#     print 'searching file...'
#     for line in file:
#         fields = line.split('\t') # line.split('\t')
#         print fields[0].split(' ') # fields[0].split(' ')
#     file.close()
