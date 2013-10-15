
def get_kegg(item='04060')
    url = 'http://rest.kegg.jp/'
    action = 'get'
    db = 'path'
    org = 'hsa'
    formt = 'kgml' 
    write_ = True
    requrl = url+'/'+action+'/'+':'.join([db,org+item])+'/'+formt
    
    keggreq = requests.get(requrl)
    
    root = etree.XML(keggreq.text)
    return root
