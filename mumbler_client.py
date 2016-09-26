import requests
import sys
import json
import random
import threading
import Queue
import urllib
from collections import defaultdict


def get_words_from_database(server_url, search_word, shared_queue=None):
    try:
        response = requests.get(''.join([server_url, urllib.quote(search_word, safe='')]))
    except (Exception, UnboundLocalError) as e:
        pass
    try:
        data = json.loads(response.content)
    except (ValueError, UnboundLocalError) as e:
        pass
    else:
        shared_queue.put(data)
        # return data


def iterative_selection(input_dict=None):
    rand = random.randint(0, sum(input_dict.values()))
    num = 0
    for k, v in input_dict.iteritems():
        num += v
        if rand <= num:
            return k


def mumble(start_word, length=5, servers=None):
    if not servers:
        servers = ['http://108.168.233.196:5000/',
                   'http://108.168.233.197:5000/',
                   'http://108.168.233.198:5000/']
    q = Queue.Queue()

    rem_len = length
    chain = start_word

    print '%s'% start_word,

    while rem_len > 1:

        for server in servers:
            t = threading.Thread(target=get_words_from_database, args=(server, start_word, q))
            t.daemon = True
            t.start()
        t.join()

        output_lists = []
        # possibly not safe
        while not q.empty():
            try:
                output_lists.append(q.get())
            except Exception as e:
                pass

        if not output_lists:
            print '\nstart word %s not found. exiting ...' % start_word
            break
        else:
            d = defaultdict(int)
            for output_list in output_lists:
                for item in output_list:
                    d[str(item['SecondWord'])] += item['Count']
            start_word = iterative_selection(d)
            chain = ' '.join([chain, start_word])
        rem_len -= 1
        print '%s' % start_word,
    return chain


if __name__ == '__main__':

    if len(sys.argv) != 3:
        search_term = r"hello"
        chain_length = 5
    else:
        search_term = sys.argv[1]
        chain_length = int(sys.argv[2])

    mumble(search_term, chain_length)
