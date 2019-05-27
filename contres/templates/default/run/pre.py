import os
import random
import subprocess

args = ['#- nothing to do -#']

if __name__=='__main__':
    # build a unique id
    uid = str(hex(int(random.random() * 10e9))[2:10])
    with open('.id', 'w') as f:
        f.write(uid)
    
    print('-' * 40)
    print('This is the preprocessor speaking')
    print('UID: #%s' % uid)
    print('-' * 40)
    
    if not os.path.exists('results'):
        os.makedirs('results')
    res = subprocess.run(args, capture_output=True)
    txt = res.stdout.decode()
    print(txt)

    print('Writing log')
    with open('results/%s_preprocessing.log' % uid, 'w') as log:
        log.write(txt)