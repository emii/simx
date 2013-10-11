first=title.find_next_siblings('b', text=u'\u00A5\u00A5')
contenidos=[]
#contenido=soup.new_tag('entry')
#el=first[1].previous_sibling
for el in first:
    contenido = soup.new_tag('entry')
    while el.name != 'br':
        contenido.contents.append(el)
        el=el.next_sibling
    contenidos.append(contenido)
    
#while el.name != 'center':
#    el = el.next_sibling
#    print el.name
#    if el.name=='br':
#        contenidos.append(contenido)
#        contenido=soup.new_tag('entry')
#        #contenido.contents=[]
#    else:
#        contenido.contents.append(el)
#       #continue
#    print 'while'        
#    #br case

#if type(el)==type(contenido):
#    if el.name=='br':
#        print 'br true'
#        br=True
#    else:
#        print 'element is tag'
#        contenido.append(el)
#else:
#    print 'element is string1'
#    contenido.append(el)
#
#while not br:
#    el=el.next_sibling
#    if el is None:
#        continue
#    print el
#    if type(el)==type(contenido):
#        if el.name=='br':
#            print 'element is br'
#            br=True
#        else:
#            print 'element is tag'
#            contenido.append(el)
#    else:
#        print 'element is string2'
#        print el
#        contenido.append(el)
