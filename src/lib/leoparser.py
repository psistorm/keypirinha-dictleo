import urllib.request
import xml.etree.ElementTree as ET

class ProxyData:
    
    proxy_enabled = False
    proxy_http_url = None
    proxy_https_url = None

    def __init__(self, proxy_enabled, proxy_http_url = None, proxy_https_url = None):
        self.proxy_enabled = proxy_enabled
        self.proxy_http_url = proxy_http_url
        self.proxy_https_url = proxy_https_url



class TranslatedEntry:
    
    caption = None
    description = None
    language = None
    
    def __init__(self, caption, description, language):
        self.caption = caption
        self.description = description
        self.language = language


class LeoParser:

    LEO_QUERY_TEMPLATE = "{{query}}"
    LEO_TRANSLATIONCODE_TEMPLATE = "{{translationCode}}"

    LEO_SUGGESTION_SERVICE = "http://dict.leo.org/dictQuery/m-query/conf/ende/query.conf/strlist.json?q={{query}}"
    LEO_TRANSLATION_SERVICE = "http://dict.leo.org/dictQuery/m-vocab/{{translationCode}}/query.xml?tolerMode=nof&lp={{translationCode}}&lang=de&rmWords=off&rmSearch=on&search={{query}}&searchLoc=0&resultOrder=basic&multiwordShowSingle=on&pos=0&sectLenMax=16&n=1"

    urlOpener = None

    def __init__(self):
    	self.urlOpener = urllib.request.build_opener()

    def set_proxy(self, proxyData):
        if proxyData.proxy_enabled:
            proxy = urllib.request.ProxyHandler({'http' : proxyData.proxy_http_url, 'https' : proxyData.proxy_https_url})
            self.urlOpener = urllib.request.build_opener(proxy)          
        else:
            self.urlOpener = urllib.request.build_opener()
            
            
    def on_translate(self, languageCode, searchText):
        resultList = []
        
        secureSearchText = urllib.parse.quote(searchText)
        suggestRequest = self.LEO_TRANSLATION_SERVICE.replace(self.LEO_QUERY_TEMPLATE, secureSearchText)
        suggestRequest = suggestRequest.replace(self.LEO_TRANSLATIONCODE_TEMPLATE, languageCode)
        
        with self.urlOpener.open(suggestRequest) as response:
            root = ET.fromstring(response.read())
            
            leftHitCount = root.find('search').get('hitWordCntLeft')
            rightHitCount = root.find('search').get('hitWordCntRight')
            
            for entry in root.iter('entry'):
                leftText = entry[0].find('words').find('word').text
                leftLanguage = entry[0].get('lang')
                
                rightText = entry[1].find('words').find('word').text
                rightLanguage = entry[1].get('lang')
                
                if (leftHitCount > rightHitCount):
                    newItem = TranslatedEntry(rightText, leftText, rightLanguage)
                    resultList.append(newItem)
                else:
                    newItem = TranslatedEntry(leftText, rightText, leftLanguage)
                    resultList.append(newItem)
                    
        return resultList
        
        

class LanguageEntry:

    keyword = None
    languageCode = None
    description = None
    iconHandle = None
    
    def __init__(self, keyword, languageCode, description, iconHandle):
        self.keyword = keyword
        self.languageCode = languageCode
        self.description = description
        self.iconHandle = iconHandle
