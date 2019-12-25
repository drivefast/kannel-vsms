# -*- coding: utf-8 -*-
"""This module finds URLs within a string and creates UrlAndRange objects to reflect matches."""
import re
from .urlextract.urlextract_core import URLExtract

class UrlFinder(object):
    """
    A utility to find URLs in a given string.
    """

    _EMAIL_REGEX = re.compile(r'[^@]+@[^@]+\.[^@]+')

    _DEFAULT_SCHEMA = 'http://'

    _supported_schemas = [_DEFAULT_SCHEMA, 'https://', 'rtsp://']

    def find(self, source):
        """
        Takes a source, finds URLs that start with supported schemas and returns a list of URLs
        with their ranges.

        Args:
            source (str): Source string to search URLs for.

        Returns:
           A :list: URLs and their ranges in the source string.
        """
        result = []
        extractor = URLExtract()
        extractor.set_stop_chars_right({'>', "'", '\x0c', '\n', '\x0b',
                                        ';', '"', '\r', '<', ' ', '\t', u'\u3000'})
        matches = extractor.find_urls(source)

        for match in matches:
            url = source[match['start']:match['end']]

            # Do not add email addresses to list of URLs
            if not self._EMAIL_REGEX.findall(url):
                url = self.make_url(url)
                result.append(UrlAndRange(url, match['start'], match['end']))

        return result

    def make_url(self, url):
        """
        Makes URL from a given string, prepending it with default schema if
        needed. Schema is always in lower case.

        Args:
            url (str): URL to build.

        Returns:
           A :str: URL with schema.
        """
        has_prefix = False
        for schema in self._supported_schemas:
            if re.match(schema, url, re.I):
                has_prefix = True
                # Fix capitalization if necessary
                if not re.match(schema, url):
                    url = schema + url[len(schema):]
                break

        if has_prefix:
            return url

        return self._DEFAULT_SCHEMA + url


class UrlAndRange(object):
    """
    A utility object to old the url, start and end locations.
    """
    def __init__(self, url, start, end=False):
        self.url = url
        self.start = start

        if not end:
            self.end = len(url) + start
        else:
            self.end = end

    def interval_contains(self, index):
        return self.start <= index <= self.end

    def to_string(self):
        return 'UrlAndRange{url=\'' + self.url + '\', start=' + str(self.start) + '}'

    def __eq__(self, other):
        return self.url == other.url and self.start == other.start

    def __ne__(self, other):
        return not self.__eq__(other)
