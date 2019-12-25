# -*- coding: utf-8 -*-
import unittest

from verified_sms_hashing_library.url_finder import UrlFinder
from verified_sms_hashing_library.url_finder import UrlAndRange

class TestUrlFinderV1(unittest.TestCase):
    _url_finder = UrlFinder()

    def contains_exactly(self, match_value, collection):
        count = 0
        if isinstance(match_value, list):
            if len(match_value) != len(collection):
                return False

            for i in range(0, len(collection)):
                if match_value[i] != collection[i]:
                    return False

            return True
        else:
            for value in collection:
                if match_value == value:
                    count += 1

            return count == len(collection)

    def test_find_without_urls(self):
        self.assertTrue(not self._url_finder.find('123  123'))
        self.assertTrue(not self._url_finder.find('123 hTTps:// 123'))

    def test_find_with_schemas(self):
        self.assertTrue(self.contains_exactly(UrlAndRange('https://A', 4),
                                              self._url_finder.find('123 hTTps://A 123')))

        self.assertTrue(self.contains_exactly(UrlAndRange('https://google.com', 0),
                                              self._url_finder.find('hTTps://google.com')))

        self.assertTrue(self.contains_exactly(
            [UrlAndRange('https://google.com', 0),
             UrlAndRange('http://google.com', 19)],
            self._url_finder.find('hTTps://google.com hTTp://google.com')))

        self.assertTrue(self.contains_exactly(
            [UrlAndRange('https://google.com', 1),
             UrlAndRange('https://google.com/path/file?param=value', 22)],
            self._url_finder.find(' hTTps://google.com   https://google.com/path/file?param=value ')))

    def test_find_with_emails(self):
        string_to_test = ('Emails like someuser@google.com aren\'t recognized as '
                          'URLs, example@domain.org as well.')

        self.assertTrue(not self._url_finder.find(string_to_test))

    def test_find_without_schemas(self):
        string_to_test = ('The domain googleapis.com is owned and operated by Google. This domain '
                          'is used by programs to talk to Google services. Subdomains. '
                          'storage.googleapis.com – This is the service that hosts Google Cloud '
                          'Storage.')

        self.assertTrue(self.contains_exactly(
            [UrlAndRange('http://googleapis.com', 11),
             UrlAndRange('http://storage.googleapis.com', 131)],
            self._url_finder.find(string_to_test)))

        string_to_test = 'The domain googleapis.com:443 is owned and operated by Google.'

        self.assertTrue(self.contains_exactly(
            UrlAndRange('http://googleapis.com:443', 11),
            self._url_finder.find(string_to_test)))

    def test_find_with_internationalized_domains(self):
        string_to_test = ('IDNA encoding may be illustrated using the example domain Bücher.org.')

        self.assertTrue(self.contains_exactly(
            UrlAndRange('http://Bücher.org', 58),
            self._url_finder.find(string_to_test)))

        string_to_test = ('IDNA encoding may be illustrated using the '
                          'example domain https://Bücher.org.')

        self.assertTrue(self.contains_exactly(
            UrlAndRange('https://Bücher.org', 58),
            self._url_finder.find(string_to_test)))

        string_to_test = ('δοκιμή.net. https://δοκιμή.net is an example of a '
                          'domain with Greek name.')

        self.assertTrue(self.contains_exactly(
            [UrlAndRange('http://δοκιμή.net', 0),
             UrlAndRange('https://δοκιμή.net', 12)],
            self._url_finder.find(string_to_test)))

    def test_find_with_punycode(self):
        string_to_test = 'xn--bcher-kva.org'

        self.assertTrue(self.contains_exactly(
            UrlAndRange('http://xn--bcher-kva.org', 0),
            self._url_finder.find(string_to_test)))

if __name__ == '__main__':
    unittest.main()
