# Keypirinha | A semantic launcher for Windows | http://keypirinha.com

import keypirinha as kp
import keypirinha_util as kpu
from .lib import leoparser

class DictLeo(kp.Plugin):
    """
    Translate words with leo online dictionary
    """
    
    KEYWORDS_AND_CODES = {}
    ICONS = {}
    ACTIONS = {}
    
    ACTION_DEFAULT = 'default'
    
    parser = None
    proxy = None

    def __init__(self):
        super().__init__()
        

    def __del__(self):
        self._clean_icons()
        

    def on_start(self):
        self.parser = leoparser.LeoParser()
        
        self._read_config()
        
        self._clean_icons()
        
        self.ICONS['de'] = self.load_icon('res://DictLeo/icons/icon_de.png')
        self.ICONS['fr'] = self.load_icon('res://DictLeo/icons/icon_fr.png')
        self.ICONS['en'] = self.load_icon('res://DictLeo/icons/icon_uk.png')
        self.ICONS['es'] = self.load_icon('res://DictLeo/icons/icon_es.png')
        self.ICONS['it'] = self.load_icon('res://DictLeo/icons/icon_it.png')
        self.ICONS['ru'] = self.load_icon('res://DictLeo/icons/icon_ru.png')
        self.ICONS['pt'] = self.load_icon('res://DictLeo/icons/icon_pt.png')
        self.ICONS['pl'] = self.load_icon('res://DictLeo/icons/icon_pl.png')
        
        self.KEYWORDS_AND_CODES.clear()
        
        self.KEYWORDS_AND_CODES['de'] = leoparser.LanguageEntry('de', 'ende', 'Translate to German or English', self.ICONS['en'])
        self.KEYWORDS_AND_CODES['df'] = leoparser.LanguageEntry('df', 'frde', 'Translate to German or French', self.ICONS['fr'])
        self.KEYWORDS_AND_CODES['ds'] = leoparser.LanguageEntry('ds', 'esde', 'Translate to German or Spanish', self.ICONS['es'])
        self.KEYWORDS_AND_CODES['di'] = leoparser.LanguageEntry('di', 'itde', 'Translate to German or Italian', self.ICONS['it'])
        self.KEYWORDS_AND_CODES['dr'] = leoparser.LanguageEntry('dr', 'rude', 'Translate to German or Russian', self.ICONS['ru'])
        self.KEYWORDS_AND_CODES['db'] = leoparser.LanguageEntry('db', 'ptde', 'Translate to German or Portuguese', self.ICONS['pt'])
        self.KEYWORDS_AND_CODES['dp'] = leoparser.LanguageEntry('dp', 'plde', 'Translate to German or Polish', self.ICONS['pl'])
        
        self.ACTIONS[self.ACTION_DEFAULT] = self.create_action(name=self.ACTION_DEFAULT, label='Copy to clipboard', short_desc='Copy the selected translation text to the clipboard.')
        
        self.set_actions(kp.ItemCategory.EXPRESSION, list(self.ACTIONS.values()))


    def on_catalog(self):
        self._read_config()
        catalog = []
        
        for languageKey, languageData in self.KEYWORDS_AND_CODES.items():
            catalog.append(self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label=languageData.keyword,
                short_desc=languageData.description,
                target=languageData.keyword,
                args_hint=kp.ItemArgsHint.REQUIRED,
                hit_hint=kp.ItemHitHint.NOARGS,
                icon_handle=languageData.iconHandle))
                
        self.set_catalog(catalog)


    def on_suggest(self, user_input, initial_item, current_item):
        if len(user_input) == 0:
            return
        if not initial_item:
            return
        
        # avoid flooding Leo with too much unnecessary queries in
        # case user is still typing her search
        if self.should_terminate(0.250):
            return
        if initial_item and initial_item.category() != kp.ItemCategory.KEYWORD:
            return

        suggestions = []
        
        languageData = self.KEYWORDS_AND_CODES[initial_item.target()]
        
        for resultItem in self.parser.on_translate(languageData.languageCode, user_input):
            itemIcon = self.ICONS[resultItem.language]
            suggestions.append(self.create_item(
                category=kp.ItemCategory.EXPRESSION,
                label=resultItem.caption,
                short_desc=resultItem.description,
                target=resultItem.caption,
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.IGNORE,
                icon_handle=itemIcon,
                data_bag=str(resultItem.caption)))

        self.set_suggestions(suggestions, kp.Match.ANY, kp.Sort.NONE)


    def on_execute(self, item, action):
        if not item and item.category() != kp.ItemCategory.EXPRESSION:
            return
        
        if not action or action.name() == self.ACTION_DEFAULT:
            kpu.set_clipboard(item.label())


    def on_events(self, flags):
        if flags & kp.Events.PACKCONFIG:
            self.info("Configuration changed, rebuilding catalog...")
            self.on_catalog()


    def _read_config(self):
        settings = self.load_settings()
        
        proxy_enabled = settings.get_bool("proxy_enabled", "main", False)
        proxy_http_url = settings.get_stripped("proxy_http_url", "main", None)
        proxy_https_url = settings.get_stripped("proxy_https_url", "main", None)
        
        if proxy_enabled == False:
            self.proxy = leoparser.ProxyData(proxy_enabled)
        else:
            self.proxy = leoparser.ProxyData(proxy_enabled, proxy_http_url, proxy_https_url)
        
        self.parser.set_proxy(self.proxy)
    
    
    def _clean_icons(self):
        for key, icon in self.ICONS.items():
            icon.free()

        self.ICONS.clear()
