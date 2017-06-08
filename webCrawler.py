print "loading..."
import urllib2, shutil, os, time, cookielib

def addQuery(query,dictionary,item,end=','):
    try:
        query = query + '"' + noQuote(dictionary[item]) + '"' + end
        return query

    except:
        query = query + '""' + end
        return query


def addFeature(dic,item,query,end=','):
    found = False
    for key, value in dic.iteritems():
        if value.lower() == item:
            found = True
            break
    if found:
        return query + '1' + end
    else:
        return query + '0' + end

def grabItem(htmlStart,htmlEnd,name,page_source,skip=0,skip2=0,skip3=0,desc=False):
    beginDef = page_source.find(htmlStart)

    if beginDef > -1:
        endDef = page_source[beginDef:].find(htmlEnd)

        if desc:
            return {name: noQuote(page_source[beginDef+skip:beginDef+endDef],skip2,skip3)}
        else:
            return {name: noQuote(noHTML(page_source[beginDef+skip:beginDef+endDef]),skip2,skip3)}

    else:
        return ""

def noHTML(definition):
    command = False
    
    while command is False:
        lessOpen = definition.find('<')
        greatClose = definition.find('>')
        if lessOpen > -1 and greatClose > -1:
            definition = definition[0:lessOpen] + definition[greatClose+1:]
        else:
            command = True

    return definition
            
def noQuote(fraze,skip=0,skipEnd=0):
    fraze = fraze.replace('"', "'")
    fraze = fraze.strip()
    fraze = fraze[skip:len(fraze)-skipEnd]
    fraze = fraze.strip()
    return fraze

def main():
    pageInt = 0
    item = 0

    hdr = {'User-Agent': 'Mozilla/5.0'}
    
    while pageInt < 3500:
        x = 1
        newBegin = 0
        dic = dict()
        pageLink = 0
        newStart = 0
        response = ""
        while 1:
            try:
                req = urllib2.Request("http://www.wta.org/go-hiking/hikes?b_start:int=" + str(pageInt), headers=hdr)
                response = urllib2.urlopen(req)
                break
            except:
                time.sleep(1)
                print "Trying to reconnect..."
                
        page = response.read()

        pageLink = page[newStart:].find('<a class="listitem-title" title="Read the full hike" href="')
        endDef = page[newStart+pageLink:].find('">')
        
        theLink = page[newStart+pageLink+59:newStart+pageLink+endDef]

        newStart = newStart+pageLink+endDef

        print "\nScraping...\n"
        while pageLink > -1:
            while 1:
                try:
                    req2 = urllib2.Request(theLink, headers=hdr)
                    response = urllib2.urlopen(req2)
                    page_source = response.read()
                    print 'Processing item ' + str(item)

                    #Name
                    dic.update(grabItem('<h1 class="documentFirstHeading">','</h1>','name',page_source))

                    #Distance
                    dic.update(grabItem('<div id="distance">','</span>','distance',page_source))

                    #Gain
                    dic.update(grabItem('Gain: ','</span>','gain',page_source,5))

                    #Highest Point
                    dic.update(grabItem('Highest Point:','</span>','highest',page_source,14))

                    #Pass Name
                    dic.update(grabItem('<div id="pass-required-info" class="alert">','</a>','pass_name',page_source,0,13,9))

                    #Description
                    dic.update(grabItem('<div id="hike-body-text" class="grid_9 omega">','</div>','description',page_source,46,0,0,True))

                    #Driving Directions
                    dic.update(grabItem('<div id="driving-directions">','</div>','directions',page_source,0,18))

                    #Latitude
                    dic.update(grabItem('<div class="latlong">','</span>','lat',page_source,0,13)) 

                    #Longitude
                    dic.update(grabItem('<div class="latlong">','<a class','long',page_source,0,23)) 

                    #Features First
                    dic.update(grabItem('<div class="feature grid_1 alpha " data-title="','">','features0',page_source,47))

                    #Features Only
                    dic.update(grabItem('<div class="feature grid_1 alpha omega" data-title="','">','features0',page_source,52))

                    #Features Others
                    beginDef = page_source[newBegin:].find('<div class="feature grid_1  " data-title="')
                    endDef = 0
                    newBegin = 0
                    while beginDef > -1:
                        newBegin = beginDef + endDef + newBegin
                        
                        beginDef = page_source[newBegin:].find('<div class="feature grid_1  " data-title="')
                    
                        endDef = page_source[newBegin+beginDef:].find('">')

                        dic.update({'features'+str(x): noQuote(page_source[newBegin+beginDef+42:newBegin+beginDef+endDef])})

                        x=x+1

                    #Features end
                    beginDef = page_source.find('<div class="feature grid_1  omega" data-title="')

                    if beginDef > -1:
                        endDef = page_source[beginDef:].find('">')

                        dic.update({'features'+str(x-1): noQuote(page_source[beginDef+47:beginDef+endDef])})

                    #Image
                    beginDef = page_source.find('<!-- The image itself -->')

                    if beginDef > -1:
                        endDef = page_source[beginDef:].find('/>')
                        beginDef2 = page_source[beginDef:].find('src="')
                        endDef2 = page_source[beginDef+beginDef2+5:].find('"')

                        dic.update({'image': noQuote(page_source[beginDef+beginDef2+5:beginDef+beginDef2+endDef2+5])})

                    #Pass Link
                    beginDef = page_source.find('<div id="pass-required-info" class="alert">')

                    if beginDef > -1:
                        endDef = page_source[beginDef:].find('</div>')
                        beginDef2 = page_source[beginDef:].find('href="')
                        endDef2 = page_source[beginDef+6+beginDef2:].find('"')

                        dic.update({'pass_link': noQuote(page_source[beginDef+beginDef2+6:beginDef+beginDef2+endDef2+6])})
                    break

                except:
                    time.sleep(1)
                    print 'Trying to reconnect'

            #Query Main Trail
            file = open('diclog.txt', "a")
            query = "INSERT INTO `db558719382`.`trail` (`id`, `name`, `length`, `gain`, `elevation`, `description`, `latitude`, `longitude`, `directions`, `pass_required`, `pass_name`, `pass_link`, `type`, `country`) VALUES ("
            query = query + str(item) +','
            query = addQuery(query,dic,'name')
            query = addQuery(query,dic,'distance')
            query = addQuery(query,dic,'gain')
            query = addQuery(query,dic,'highest')
            query = addQuery(query,dic,'description')
            query = addQuery(query,dic,'lat')
            query = addQuery(query,dic,'long')
            query = addQuery(query,dic,'directions')
            try:
                if dic['pass_name']:
                    query = query + '"1",'
                else:
                    query = query + '"0",'
            except:
                query = query + '"0",'
            query = addQuery(query,dic,'pass_name')
            query = addQuery(query,dic,'pass_link')
            query = query + '2,'
            query = query + '1);\n\n'    

            file.write(query)
            file.close()

            #Query Trail Media
            file = open('diclog.txt', "a")
            query = "INSERT INTO `db558719382`.`trail_media` (`id`, `trail_id`, `image_main`) VALUES (NULL,"
            query = query + str(item) +','
            query = addQuery(query,dic,'image',');\n\n')

            file.write(query)
            file.close()

            #Query Trail Media
            file = open('diclog.txt', "a")
            query = "INSERT INTO `db558719382`.`trail_features` (`id`, `trail_id`, `coastline`, `rivers`, `lakes`, `waterfalls`, `old_growth`, `fall_foilage`, `flowers`, `mountain_views`, `summits`, `wild_life`, `ridge_passes`, `campsites`, `kid_friendly`, `dogs_allowed`) VALUES (NULL,"
            query = query + str(item) +','

            query = addFeature(dic,'coast',query)
            query = addFeature(dic,'rivers',query)
            query = addFeature(dic,'lakes',query)
            query = addFeature(dic,'waterfalls',query)
            query = addFeature(dic,'old growth',query)
            query = addFeature(dic,'fall foliage',query)
            query = addFeature(dic,'wildflowers/meadows',query)
            query = addFeature(dic,'mountain views',query)
            query = addFeature(dic,'summits',query)
            query = addFeature(dic,'wildlife',query)
            query = addFeature(dic,'ridges/passes',query)
            query = addFeature(dic,'established campsites',query)
            query = addFeature(dic,'good for kids',query)
            query = addFeature(dic,'dogs allowed on leash',query,');\n\n')

            file.write(query)
            file.close()
            

            pageLink = page[newStart:].find('<a class="listitem-title" title="Read the full hike" href="')
            endDef = page[newStart+pageLink:].find('">')
            
            theLink = page[newStart+pageLink+59:newStart+pageLink+endDef]

            newStart = newStart+pageLink+endDef

            item=item+1
            dic = dict()
        pageInt = pageInt + 30

    print "DONE!!!"
    raw_input()

main()
