from .webrequest import get_opener

import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


XML_TAG_SEARCH = 'search'

XML_TAG_LEFT_WORD = 'hitWordCntLeft'
XML_TAG_RIGHT_WORD = 'hitWordCntRight'

XML_TAG_ENTRY = 'entry'
XML_TAG_WORD = 'word'
XML_TAG_WORDS = 'words'

LEO_SUGGESTION_SERVICE = 'http://dict.leo.org/dictQuery/m-query/conf/{language_code}/query.conf/strlist.json?q={query}'
LEO_TRANSLATION_SERVICE = 'http://dict.leo.org/dictQuery/m-vocab/{language_code}/query.xml?tolerMode=nof&lp={language_code}&lang=de&rmWords=off&rmSearch=on&search={query}&searchLoc=0&resultOrder=basic&multiwordShowSingle=on&pos=0&sectLenMax=16&n=1'


class LeoParser:

    _url_opener = None

    def __init__(self):
        self._url_opener = get_opener()

    def set_proxy(self, proxy_url=None):
        self._url_opener = get_opener(proxy_url)

    def translate(self, language_code, search_text):
        result_list = []
        
        secure_search_text = urllib.parse.quote(search_text)
        suggest_request = LEO_TRANSLATION_SERVICE.format(
            query=secure_search_text,
            language_code=language_code
        )
        
        with self._url_opener.open(suggest_request) as response:
            root = ET.fromstring(response.read())
            
            left_hit_count = root.find(XML_TAG_SEARCH).get(XML_TAG_LEFT_WORD)
            right_hit_count = root.find(XML_TAG_SEARCH).get(XML_TAG_RIGHT_WORD)
            
            for entry in root.iter(XML_TAG_ENTRY):
                left_text = entry[0].find(XML_TAG_WORDS).find(XML_TAG_WORD).text
                left_language = entry[0].get('lang')
                
                right_text = entry[1].find(XML_TAG_WORDS).find(XML_TAG_WORD).text
                right_language = entry[1].get('lang')
                
                if left_hit_count > right_hit_count:
                    new_item = TranslatedEntry(right_text, left_text, right_language)
                    result_list.append(new_item)
                else:
                    new_item = TranslatedEntry(left_text, right_text, left_language)
                    result_list.append(new_item)
                    
        return result_list


class TranslatedEntry:

    caption = None
    description = None
    language = None

    def __init__(self, caption, description, language):
        self.caption = caption
        self.description = description
        self.language = language