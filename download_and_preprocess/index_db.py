import sqlite3 as sq
import pickle
import cPickle as cp
import sys
import os
import time

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print 'enter database directory path'
    else:
        db_path_prefix = sys.argv[1]
        db_names = ['gpfs1_bigrams.db',
                     'gpfs2_bigrams.db',
                     'gpfs3_bigrams.db'
                     ]

        for name in db_names:
            db_path = os.path.join(db_path_prefix, name)
            print db_path
            with sq.connect(db_path) as conn:
                try:
                    print 'creating index ... '
                    cur = conn.cursor()
                    cur.execute("CREATE INDEX index_SecondWord ON bigram_counts (SecondWord)")
                    conn.commit()
                except sq.Error as e:
                    if conn:
                        conn.rollback()
                    print 'error occurred: %s' % e.args[0]
                    sys.exit(1)

