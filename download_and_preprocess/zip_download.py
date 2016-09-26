import time
import sys
import os
import pickle
import mmap
from StringIO import StringIO
from zipfile import ZipFile
from urllib import urlopen 
from collections import OrderedDict



def generate_filenames(prefix, low, high):
	filenames = []
	low = int(low)
	high = int(high)

	for i in range(low, high+1, 1):
		filename = ''.join([prefix, str(i), '.csv'])
		filenames.append(filename)

	return filenames


def generate_url(uri_base='', filename='', archive_type='.zip'):
	return ''.join([uri_base, filename, archive_type])


def download_file(uri, filename):
	url = urlopen(uri)
	odic = OrderedDict()
	with ZipFile(StringIO(url.read())) as zipfile:
		with zipfile.open(filename) as f:
			for line in f:
				fields = line.rstrip().split('\t')
				try:
					# only keep standard English characters
					k = fields[0].encode('utf8').decode('ascii').lower()
				except UnicodeDecodeError as e:
					continue
				else:
					v = int(fields[2])
					if k in odic:
						odic[k] += v
					else:
						odic[k] = v
	return odic

def save_file(input_data, output_file):
	with open(output_file, 'wb') as of:
		pickle.dump(input_data, of)

if __name__ == '__main__':

	if len(sys.argv) != 3:
		print 'enter the start and end files'
	else:

		start = sys.argv[1]
		end = sys.argv[2]

		names = generate_filenames('googlebooks-eng-all-2gram-20090715-', start, end)

		ub = 'http://storage.googleapis.com/books/ngrams/books/'
		at = '.zip'

		target_dir=''
		for i, name in enumerate(names):
			url_str = generate_url(ub, name, at)
			print 'downloading and pasring file from %s\n' % (url_str)
			this_dict = download_file(url_str, name)

			output_filename = ''.join(['bigrams-', str(i), '.txt'])
			print 'writing file... %s' % (output_filename)
			with open(output_filename, 'wb') as outputfile:
				pickle.dump(this_dict, outputfile)

