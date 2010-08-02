"""Request to the Gatherer site"""
import re
import httplib2
import logging
import urllib

from constants import settings_url, settings_header, params, base_url

class CardRequest(object):

    def __init__(self, options, special=False):
        self.options = options
        self.special = special
        
    def _get_url_fragments(self, options):
        fragments = []
        for opt, value in options.items():
            if value:
                sep = re.compile('[,]+')
                value = sep.split(value)
                frag = '%s=' % opt
                frag += ('%s[%s]' * (len(value))) % \
                    tuple(self._get_modifiers(value))
                fragments.append(frag)
        return fragments

    def _get_modifiers(self, lst):
        modifiers = re.compile('^([!=|<>]+)')
        results = []
        for item in lst:
            matches = modifiers.match(item)
            if matches:
                modifier_char = '+' + matches.group(0)
                if modifier_char == '+|':
                    modifier_char = '|'
                item = modifiers.sub('', item)
            else:
                modifier_char = '+'
            results.extend([modifier_char, item])
        return results

    @property
    def url_fragments(self):
        return self._get_url_fragments(self.options)

    @property
    def special_fragment(self):
        return self.special and '&special=true' or ''

    @property
    def url(self):
        return base_url + '&'.join(self.url_fragments) + self.special_fragment

    def send(self):
        http = httplib2.Http()
        try:
            response, content = http.request(settings_url, 'POST', 
                                             headers=settings_header,
                                             body=urllib.urlencode(params))
        except httplib2.ServerNotFoundError as ex:
            logging.warning(ex)
            return False
        card_header = headers = {'Cookie': response['set-cookie']}

        response, content = http.request(self.url, 'GET', headers=headers)


        
