# Keypirinha | A semantic launcher for Windows | http://keypirinha.com

import keypirinha as kp
import keypirinha_util as kpu
from collections import OrderedDict
from .lib.leoparser import LeoParser


class DictLeo(kp.Plugin):
    """
    Translate words with leo online dictionary
    """

    ACTION_DEFAULT = '0_default'
    ACTION_OPEN_LEO = '1_open_in_leo'

    URL_LEO = 'http://dict.leo.org/dictQuery/m-vocab/{language_code}/{item_language}.html?searchLoc=0&lp={language_code}&directN=0&rmWords=off&search={user_query}&resultOrder=basic&multiwordShowSingle=on'

    _languages = {}
    _icons = {}
    _actions = OrderedDict()
    
    _parser = None


    def __init__(self):
        super().__init__()

    def __del__(self):
        self._clean_icons()

    def on_start(self):
        self._parser = LeoParser()
        
        self._read_config()
        
        self._clean_icons()
        self._init_icons()
        
        self._languages.clear()
        self._init_languages()

        self._init_actions()

    def on_catalog(self):
        self._read_config()

        catalog = []
        
        for language_key, language_data in self._languages.items():
            catalog.append(self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label=language_data.keyword,
                short_desc=language_data.description,
                target=language_data.keyword,
                args_hint=kp.ItemArgsHint.REQUIRED,
                hit_hint=kp.ItemHitHint.NOARGS,
                icon_handle=language_data.icon_handle)
            )
                
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
        if initial_item.category() != kp.ItemCategory.KEYWORD:
            return

        suggestions = []
        
        current_language = self._languages[initial_item.target()]

        for leo_translation in self._parser.translate(current_language.language_code, user_input):
            item_icon = self._icons[leo_translation.language]

            suggestions.append(self.create_item(
                category=kp.ItemCategory.EXPRESSION,
                label=leo_translation.caption,
                short_desc=leo_translation.description,
                target=leo_translation.caption,
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.IGNORE,
                icon_handle=item_icon,
                data_bag=kpu.kwargs_encode(
                    language_code=current_language.language_code,
                    item_language=leo_translation.language,
                    user_query=user_input,
                    translation_result=leo_translation.caption
                )
            ))

        self.set_suggestions(suggestions, kp.Match.ANY, kp.Sort.NONE)

    def on_execute(self, item, action):
        if not item and item.category() != kp.ItemCategory.EXPRESSION:
            return
        if not item.data_bag():
            return

        data_bag = kpu.kwargs_decode(item.data_bag())
        if not action or action.name() == self.ACTION_DEFAULT:
            kpu.set_clipboard(data_bag['translation_result'])
        elif action.name() == self.ACTION_OPEN_LEO:
            kpu.web_browser_command(
                url=self.URL_LEO.format(**data_bag),
                execute=True
            )

    def on_events(self, flags):
        if flags & kp.Events.PACKCONFIG:
            self.info("Configuration changed, rebuilding catalog...")
            self.on_catalog()

    def _read_config(self):
        settings = self.load_settings()
        
        proxy_enabled = settings.get_bool("proxy_enabled", "main", False)
        if not proxy_enabled:
            self._parser.set_proxy()
        else:
            proxy_http_url = settings.get_stripped("proxy_http_url", "main", None)
            self._parser.set_proxy(proxy_http_url)

    def _clean_icons(self):
        for key, icon in self._icons.items():
            icon.free()

        self._icons.clear()

    def _init_icons(self):
        self._icons['de'] = self.load_icon('res://DictLeo/icons/icon_de.png')
        self._icons['fr'] = self.load_icon('res://DictLeo/icons/icon_fr.png')
        self._icons['en'] = self.load_icon('res://DictLeo/icons/icon_uk.png')
        self._icons['es'] = self.load_icon('res://DictLeo/icons/icon_es.png')
        self._icons['it'] = self.load_icon('res://DictLeo/icons/icon_it.png')
        self._icons['ru'] = self.load_icon('res://DictLeo/icons/icon_ru.png')
        self._icons['pt'] = self.load_icon('res://DictLeo/icons/icon_pt.png')
        self._icons['pl'] = self.load_icon('res://DictLeo/icons/icon_pl.png')

    def _init_languages(self):
        self._languages['de'] = LanguageEntry(
            keyword='de',
            language_code='ende',
            description='Translate to German or English',
            icon_handle=self._icons['en']
        )

        self._languages['df'] = LanguageEntry(
            keyword='df',
            language_code='frde',
            description='Translate to German or French',
            icon_handle=self._icons['fr']
        )

        self._languages['ds'] = LanguageEntry(
            keyword='ds',
            language_code='esde',
            description='Translate to German or Spanish',
            icon_handle=self._icons['es']
        )

        self._languages['di'] = LanguageEntry(
            keyword='di',
            language_code='itde',
            description='Translate to German or Italian',
            icon_handle=self._icons['it']
        )

        self._languages['dr'] = LanguageEntry(
            keyword='dr',
            language_code='rude',
            description='Translate to German or Russian',
            icon_handle=self._icons['ru']
        )

        self._languages['db'] = LanguageEntry(
            keyword='db',
            language_code='ptde',
            description='Translate to German or Portuguese',
            icon_handle=self._icons['pt']
        )

        self._languages['dp'] = LanguageEntry(
            keyword='dp',
            language_code='plde',
            description='Translate to German or Polish',
            icon_handle=self._icons['pl']
        )

    def _init_actions(self):
        self._actions[self.ACTION_DEFAULT] = self.create_action(
            name=self.ACTION_DEFAULT,
            label='Copy to clipboard',
            short_desc='Copy the selected translation text to the clipboard.'
        )

        self._actions[self.ACTION_OPEN_LEO] = self.create_action(
            name=self.ACTION_OPEN_LEO,
            label='Open translation in Leo',
            short_desc='Shows the translation results on leo.dict.org'
        )

        list_of_actions = list(self._actions.values())
        self.set_actions(kp.ItemCategory.EXPRESSION, list_of_actions)


class LanguageEntry:
    keyword = None
    language_code = None
    description = None
    icon_handle = None

    def __init__(self, keyword, language_code, description, icon_handle):
        self.keyword = keyword
        self.language_code = language_code
        self.description = description
        self.icon_handle = icon_handle
