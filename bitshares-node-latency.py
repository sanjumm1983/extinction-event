# Python3
#
# Returns list of live tested Bitshares nodes sorted by latency
#
# (BTS) litepresence1

def nodes(timeout=3, pings=10):  # Public Nodes List

    # timeout is seconds to ping until abort per websocket
    # pings is number of websockets to ping  until abort (0 none, 999 all)

    from multiprocessing import Process, Value, Array
    from bitshares.blockchain import Blockchain
    from bitshares import BitShares
    import requests
    import time

    include = ['wss://relinked.com/ws',]

    exclude = ['wss://valen-tin.fr:8090/ws', 
        'wss://japan.bitshares.apasia.tech/ws',
        'wss://us-ny.bitshares.apasia.tech/ws',
        'wss://bitshares.apasia.tech/ws',
        'wss://altcap.io/ws',]

    # web scraping methods
    def clean(raw):
        return ((raw.replace('"'," ")).replace("'"," ")).replace(',',' ')
    def parse(cleaned):
        return [ t for t in cleaned.split() if t.startswith('wss') ]
    def validate(parsed):
        return [i for i in parsed if (('test' not in i) and ('fake' not in i))]
    #ping the blockchain and return latency
    def ping(n,num,arr):
        start = time.time()
        Blockchain(bitshares_instance=BitShares(n))
        num.value = time.time() - start

    
    begin = time.time()
    print ('=====================================')
    print(('found %s nodes stored in script' % len(include))) 
    urls = []
    # scrape from github
    git = 'https://raw.githubusercontent.com'
    url = git+'/bitshares/bitshares-ui/staging/app/api/apiConfig.js'
    urls.append(url)
    url = git+'/bitshares/bitshares-ui/master/app/api/apiConfig.js'
    urls.append(url)
    url = git+'/CryptoBridge/cryptobridge-ui/'
    url += 'e5214ad63a41bd6de1333fd98d717b37e1a52f77/app/api/apiConfig.js'
    urls.append(url)
    # use pastebin as failsafe backup
    url = 'https://pastebin.com'
    url += '/raw/YCsHRwgS'
    urls.append(url)

    # searched selected sites for Bitshares nodes
    validated = []
    for u in urls:
        try:
            raw = requests.get(u).text
            v = validate(parse(clean(raw)))
            print(('found %s nodes at %s' % (len(v),u[:65])))
            validated += v
        except:
            print(('failed to connect to %s' % u)) 
            pass
    if len(exclude):
        exclude = sorted(exclude)
        print ('remove %s bad nodes' % len(exclude))
        validated = [i for i in validated if i not in exclude]
    validated = sorted(list(set(validated)))


    print ('=====================================')
    print(('found %s total nodes - no duplicates' % len(validated)))
    print ('=====================================')
    print (validated)
    pings = min(pings, len(validated))
    
    if pings: # attempt to contact each websocket
        print ('=====================================')
        print ('searching for %s nodes max timeout %s' % (pings,timeout))
        print ('process estimate %.1f minutes' % (timeout*len(validated)/60.0))
        print ('pinging nodes to find best latency')
        print ('=====================================')
        pinged, timed, down = [], [], []
        # use multiprocessing module to enforce timeout
        for n in validated:
            if len(pinged) < pings:
                num = Value('d', 999999.99)
                arr = Array('i', list(range(0)))
                p = Process(target=ping, args=(n, num, arr))
                p.start()
                p.join(timeout)
                if p.is_alive():
                    p.terminate()
                    p.join()
                    down.append(n)
                else:
                    pinged.append(n)
                    timed.append(num.value)
                print(('ping: ',n,' latency: ', ('%.2f'% num.value)))
        # sort websockets by latency 
        pinged = [x for _,x in sorted(zip(timed,pinged))]
        timed = sorted(timed)
        unknown = sorted(list(set(validated).difference(pinged+down)))
        print('')
        print((len(pinged) ,'of', len(validated), 
            'nodes are active with latency less than', timeout))
        print(('fastest node', pinged[0], 'with latency', ('%.2f'%timed[0])))

        if len(exclude):
            print('')
            print ('excluded nodes:')
            print('')
            for i in range(len(exclude)):
                print(('XXXX', exclude[i]))

        if len(unknown):
            print('')
            print ('not tested nodes:')
            print('')
            for i in range(len(unknown)):
                print(('????', unknown[i]))
        if len(down):
            print('')
            print ('DOWN nodes:')
            print('')
            for i in range(len(down)):
                print(('DOWN', down[i]))
        if len(pinged):
            print ('')
            print ('UP nodes:')
            print ('')
            for i in range(len(pinged)):
                print((('%.2f'%timed[i]), pinged[i]))
        ret = pinged
    else:
        ret = validated
    print ('')
    print (ret)
    print ('')
    print(('elapsed', ('%.2f' %(time.time()-begin))))
    return ret
    
nodes()
