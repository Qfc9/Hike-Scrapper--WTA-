print("loading...")
import urllib.parse
import urllib.request
import shutil, os, time
import ssl

context = ssl._create_unverified_context()

def addQuery(query,dictionary,item,end=','):
    try:
        query = query + '"' + noQuote(dictionary[item]) + '"' + end
        return query

    except:
        query = query + '""' + end
        return query


def addFeature(dic,item,query,end=','):
    found = False
    for key in dic:
        if dic[key].lower() == item:
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
    item = 5

    allFeatures = ['coast', 'rivers', 'lakes', 'waterfalls', 'old growth', 'fall foliage', 'wildflowers/meadows', 'mountain views', 
    'summits', 'wildlife', 'ridges/passes', 'established campsites', 'dogs allowed on leash', 'dogs not allowed', 'good for kids']

    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    
    while pageInt < 3500:
        x = 1
        newBegin = 0
        dic = dict()
        pageLink = 0
        newStart = 0
        page = None
        while 1:
            try:
                req = urllib.request.Request("http://www.wta.org/go-hiking/hikes?b_start:int=" + str(pageInt), None, hdr)
                page = str(urllib.request.urlopen(req, context=context).read())
                break
            except:
                time.sleep(1)
                print( "Trying to reconnect...")
                
        # page = response

        pageLink = page[newStart:].find('<a class="listitem-title" title="Read the full hike" href="')
        endDef = page[newStart+pageLink:].find('">')
        
        theLink = page[newStart+pageLink+59:newStart+pageLink+endDef]

        newStart = newStart+pageLink+endDef

        print( "\nScraping...\n")
        while pageLink > -1:
            while 1:
                try:
                    req2 = urllib.request.Request(theLink, headers=hdr)
                    page_source = str(urllib.request.urlopen(req2, context=context).read())
                    print( 'Processing item ' + str(item))

                    #Name
                    dic.update(grabItem('<h1 class="documentFirstHeading">','</h1>','name',page_source))

                    #Distance
                    dic.update(grabItem('<div id="distance">',' miles','distance',page_source, 34))

                    #Gain
                    dic.update(grabItem('Gain: ','</span>','gain',page_source,5))

                    #Highest Point
                    dic.update(grabItem('Highest Point:','</span>','highest',page_source,14))

                    #Pass Name
                    dic.update(grabItem('<a title="Learn more about the various types of recreation passes in Washington" href="https://www.wta.org/hiking-info/passes/passes-and-permit-info">','</a>','pass_name',page_source, 150))

                    #Description
                    dic.update(grabItem('<div id="hike-body-text" class="grid_9 omega">','</div>','description',page_source,46,0,0,True))

                    #Driving Directions
                    dic.update(grabItem('Driving Directions','</p>\\n','directions',page_source,40))

                    #Latitude
                    dic.update(grabItem('Co-ordinates:','</span>','lat',page_source,13)) 

                    #Longitude
                    dic.update(grabItem(',\\n                          <span>','</span>','long',page_source,35)) 

                    #Features First
                    # dic.update(grabItem('<div class="feature grid_1 alpha " data-title="','">','features0',page_source,47))

                    # #Features Only
                    # dic.update(grabItem('<div class="feature grid_1 alpha omega" data-title="','">','features0',page_source,52))

                    #Features Others
                    beginDef = page_source[newBegin:].find('<div id="hike-features">')
                    endDef = 0
                    newBegin = 0
                    x = 0
                    while beginDef > -1:
                        newBegin = beginDef + endDef + newBegin
                        
                        beginDef = page_source[newBegin:].find('data-title="')
                    
                        endDef = page_source[newBegin+beginDef:].find('">')

                        dic.update({'features'+str(x): noQuote(page_source[newBegin+beginDef+12:newBegin+beginDef+endDef])})

                        x=x+1

                    # #Features end
                    # beginDef = page_source.find('<div class="feature grid_1  omega" data-title="')

                    # if beginDef > -1:
                    #     endDef = page_source[beginDef:].find('">')

                    #     dic.update({'features'+str(x-1): noQuote(page_source[beginDef+47:beginDef+endDef])})

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
                    print( 'Trying to reconnect')

            #Query Main Trail
            file = open('diclog.txt', "a")
            query = "INSERT INTO `db731590944`.`trails` (`id`, `name`, `latitude`, `longitude`, `directions`, `gain`, `distance`, `pass`) VALUES ("
            query = query + str(item) +','
            query = addQuery(query,dic,'name')
            query = addQuery(query,dic,'lat')
            query = addQuery(query,dic,'long')
            query = addQuery(query,dic,'directions')
            query = addQuery(query,dic,'gain')
            query = addQuery(query,dic,'distance')

            passInfo = '""'
            try:
                if dic['pass_name'] == "Northwest Forest Pass":
                    passInfo = '2'
                elif dic['pass_name'] == "National Park Pass":
                    passInfo = '1'
            except:
                pass

            query += passInfo
            query += ');\n\n'    

            file.write(query)
            file.close()

            #Query Trail Media
            file = open('diclog.txt', "a")
            query = "INSERT INTO `db731590944`.`trail_media` (`trail_id`, `link`, `type`) VALUES ("
            query = query + str(item) +','
            query = addQuery(query,dic,'image',', 1);\n\n')

            file.write(query)
            file.close()

            #Query Trail Media
            query = ''
            for key in dic:
                if dic[key].lower() in allFeatures:

                    query += "INSERT INTO `db731590944`.`trail_features` (`trail_id`, `feature_id`) VALUES ("
                    query += str(item) +','
                    query += str(allFeatures.index(dic[key].lower()) + 1)
                    query += ");\n"


            file = open('diclog.txt', "a")
            file.write(query)
            file.close()
            

            pageLink = page[newStart:].find('<a class="listitem-title" title="Read the full hike" href="')
            endDef = page[newStart+pageLink:].find('">')
            
            theLink = page[newStart+pageLink+59:newStart+pageLink+endDef]

            newStart = newStart+pageLink+endDef

            item=item+1
            dic = dict()
            exit()
        pageInt = pageInt + 30

    print( "DONE!!!")
    raw_input()

main()
