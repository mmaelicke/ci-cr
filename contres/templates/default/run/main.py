import subprocess

args = ['#- nothing to do -#']


if __name__=='__main__':
    # get uid
    with open('.id', 'r') as f:
        uid = f.read()
        
    print('-' * 40)
    print('Main Analysis script')
    print('UID: #%s' % uid)
    print('-' * 40)
    
    res = subprocess.run(args, capture_output=True)
    txt = res.stdout.decode()
    print(txt)
    
    print('Finished. Writing log')
    with open('results/%s_main.log' % uid, 'w') as log:
        log.write(txt)
