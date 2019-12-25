# -*- coding: utf-8 -*-
"""Sanitizer for SMS messages that normalizes whitespaces and replaces
accent characters with their ISO-8859-1 equivalents."""
import re
from .url_finder import UrlFinder

class StringSanitizer(object):
    """
    Sanitizer for V1 that normalizes whitespaces and replaces
    accent characters with their ISO-8859-1 equivalents.
    """

    _TRIM_AND_REPEATED_SPACES = re.compile('^ +| +$|( )+')

    # Possible data munging characters substitutions for accents.
    _accents = {
        u'Å': 'A',
        u'å': 'a',
        u'Ä': 'A',
        u'ä': 'a',
        u'à': 'a',
        u'Ç': 'C',
        u'É': 'E',
        u'è': 'e',
        u'é': 'e',
        u'ì': 'i',
        u'Ñ': 'N',
        u'ñ': 'n',
        u'Ö': 'O',
        u'ö': 'o',
        u'ò': 'o',
        u'Ø': 'O',
        u'ø': 'o',
        u'Ü': 'U',
        u'ü': 'u',
        u'ù': 'u'
    }

    # Possible data munging characters substitutions for whitespaces.
    _whitespaces = {
        u'\u0000': ' ',
        u'\u0001': ' ',
        u'\u0002': ' ',
        u'\u0003': ' ',
        u'\u0004': ' ',
        u'\u0005': ' ',
        u'\u0006': ' ',
        u'\u0007': ' ',
        u'\u0008': ' ',
        u'\u0009': ' ',
        '\n': ' ',
        u'\u000B': ' ',
        u'\u000C': ' ',
        '\r': ' ',
        u'\u000E': ' ',
        u'\u000F': ' ',
        u'\u0011': ' ',
        u'\u0012': ' ',
        u'\u0013': ' ',
        u'\u0014': ' ',
        u'\u0015': ' ',
        u'\u0016': ' ',
        u'\u0017': ' ',
        u'\u0018': ' ',
        u'\u0019': ' ',
        u'\u001A': ' ',
        u'\u001B': ' ',
        u'\u001C': ' ',
        u'\u001D': ' ',
        u'\u001E': ' ',
        u'\u001F': ' ',

        u'\u007F': ' ', # Non-printable delete character.

        # C1 Control characters.
        # Source: https://en.wikipedia.org/wiki/List_of_Unicode_characters,
        # https://en.wikipedia.org/wiki/Whitespace_character
        u'\u0080': ' ', # Padding Character
        u'\u0081': ' ', # High Octet Preset
        u'\u0082': ' ', # Break Permitted Here
        u'\u0083': ' ', # No Break Here
        u'\u0084': ' ', # Index
        u'\u0085': ' ', # Next Line
        u'\u0086': ' ', # Start of Selected Area
        u'\u0087': ' ', # End of Selected Area
        u'\u0088': ' ', # Character Tabulation Set
        u'\u0089': ' ', # Character Tabulation
        u'\u008A': ' ', # Line Tabulation Set
        u'\u008B': ' ', # Partial Line Forward
        u'\u008C': ' ', # Partial Line Backward
        u'\u008D': ' ', # Reverse Line Feed
        u'\u008E': ' ', # Single-Shift Two
        u'\u008F': ' ', # Single-Shift Three
        u'\u0090': ' ', # Device Control String
        u'\u0091': ' ', # Private Use 1
        u'\u0092': ' ', # Private Use 2
        u'\u0093': ' ', # Set Transmit State
        u'\u0094': ' ', # Cancel character
        u'\u0095': ' ', # Message Waiting
        u'\u0096': ' ', # Start of Protected Area
        u'\u0097': ' ', # End of Protected Area
        u'\u0098': ' ', # Start of String
        u'\u0099': ' ', # Single Graphic Character
        u'\u009A': ' ', # Single Character Intro Introducer
        u'\u009B': ' ', # Control Sequence Introducer
        u'\u009C': ' ', # String Terminator
        u'\u009D': ' ', # Operating System Command
        u'\u009E': ' ', # Private Message
        u'\u009F': ' ', # Application Program Command
        u'\u00A0': ' ', # Non-breaking space
        u'\u1680': ' ', # ogham space mark
        u'\u180E': ' ', # mongolian vowel separator

        # Other unicode whitespaces.
        # Source': https://en.wikipedia.org/wiki/Whitespace_character
        u'\u2000': ' ', # en quad
        u'\u2001': ' ', # em quad
        u'\u2002': ' ', # en space
        u'\u2003': ' ', # em space
        u'\u2004': ' ', # three-per-em space
        u'\u2005': ' ', # four-per-em space
        u'\u2006': ' ', # six-per-em space
        u'\u2007': ' ', # figure space
        u'\u2008': ' ', # punctuation space
        u'\u2009': ' ', # thin space
        u'\u200A': ' ', # hair space
        u'\u200B': ' ', # zero width space
        u'\u200C': ' ', # zero width non-joiner
        u'\u200D': ' ', # zero width joiner
        u'\u2028': ' ', # line separator
        u'\u2029': ' ', # paragraph separator
        u'\u202F': ' ', # narrow no-break space
        u'\u205F': ' ', # medium mathematical space
        u'\u2060': ' ', # word joiner
        u'\u3000': ' ', # ideographic space
        u'\uFEFF': ' ', # zero width non-breaking space
    }

    _seven_bit_characters_translation_table = {
        u'\u0060': u'\u0027',
        u'\u00A2': u'\u0063',
        u'\u00A6': u'\u007C',
        u'\u00A8': u'\u0022',
        u'\u00A9': u'\u0063',
        u'\u00AB': u'\u003C',
        u'\u00AC': u'\u002D',
        u'\u00AE': u'\u0052',
        u'\u00AF': u'\u002D',
        u'\u00B0': u'\u006F',
        u'\u00B1': u'\u003F',
        u'\u00B4': u'\u0027',
        u'\u00B6': u'\u003F',
        u'\u00B7': u'\u002E',
        u'\u00B8': u'\u002C',
        u'\u00BB': u'\u003E',
        u'\u00C0': u'\u0041',
        u'\u00C1': u'\u0041',
        u'\u00C2': u'\u0041',
        u'\u00C3': u'\u0041',
        u'\u00C8': u'\u0045',
        u'\u00CA': u'\u0045',
        u'\u00CB': u'\u0045',
        u'\u00CC': u'\u0049',
        u'\u00CD': u'\u0049',
        u'\u00CE': u'\u0049',
        u'\u00CF': u'\u0049',
        u'\u00D0': u'\u0044',
        u'\u00D2': u'\u004F',
        u'\u00D3': u'\u004F',
        u'\u00D4': u'\u004F',
        u'\u00D5': u'\u004F',
        u'\u00D7': u'\u0078',
        u'\u00D9': u'\u0055',
        u'\u00DA': u'\u0055',
        u'\u00DB': u'\u0055',
        u'\u00DD': u'\u0059',
        u'\u00DE': u'\u0054',
        u'\u00E1': u'\u0061',
        u'\u00E2': u'\u0061',
        u'\u00E3': u'\u0061',
        u'\u00E7': u'\u00C7',
        u'\u00EA': u'\u0065',
        u'\u00EB': u'\u0065',
        u'\u00ED': u'\u0069',
        u'\u00EE': u'\u0069',
        u'\u00EF': u'\u0069',
        u'\u00F0': u'\u0064',
        u'\u00F3': u'\u006F',
        u'\u00F4': u'\u006F',
        u'\u00F5': u'\u006F',
        u'\u00F7': u'\u002F',
        u'\u00FA': u'\u0075',
        u'\u00FB': u'\u0075',
        u'\u00FD': u'\u0079',
        u'\u00FE': u'\u0074',
        u'\u00FF': u'\u0079',
        u'\u0100': u'\u0041',
        u'\u0101': u'\u0061',
        u'\u0102': u'\u0041',
        u'\u0103': u'\u0061',
        u'\u0104': u'\u0041',
        u'\u0105': u'\u0061',
        u'\u0106': u'\u0043',
        u'\u0107': u'\u0063',
        u'\u0109': u'\u0063',
        u'\u010A': u'\u0043',
        u'\u010B': u'\u0063',
        u'\u010C': u'\u0043',
        u'\u010D': u'\u0063',
        u'\u010E': u'\u0044',
        u'\u010F': u'\u0064',
        u'\u0110': u'\u0044',
        u'\u0111': u'\u0064',
        u'\u0112': u'\u0045',
        u'\u0113': u'\u0065',
        u'\u0114': u'\u0045',
        u'\u0115': u'\u0065',
        u'\u0116': u'\u0045',
        u'\u0117': u'\u0065',
        u'\u0118': u'\u0045',
        u'\u0119': u'\u0065',
        u'\u011A': u'\u0045',
        u'\u011B': u'\u0065',
        u'\u011C': u'\u0047',
        u'\u011D': u'\u0067',
        u'\u011E': u'\u0047',
        u'\u011F': u'\u0067',
        u'\u0120': u'\u0047',
        u'\u0121': u'\u0067',
        u'\u0122': u'\u0047',
        u'\u0123': u'\u0067',
        u'\u0124': u'\u0048',
        u'\u0125': u'\u0068',
        u'\u0126': u'\u0048',
        u'\u0127': u'\u0068',
        u'\u0128': u'\u0049',
        u'\u0129': u'\u0069',
        u'\u012A': u'\u0049',
        u'\u012B': u'\u0069',
        u'\u012C': u'\u0049',
        u'\u012D': u'\u0069',
        u'\u012E': u'\u0049',
        u'\u012F': u'\u0069',
        u'\u0130': u'\u0049',
        u'\u0131': u'\u0069',
        u'\u0132': u'\u0049',
        u'\u0133': u'\u006A',
        u'\u0134': u'\u004A',
        u'\u0135': u'\u006A',
        u'\u0136': u'\u004B',
        u'\u0137': u'\u006B',
        u'\u0138': u'\u006B',
        u'\u0139': u'\u004C',
        u'\u013A': u'\u006C',
        u'\u013B': u'\u004C',
        u'\u013C': u'\u006C',
        u'\u013D': u'\u004C',
        u'\u013E': u'\u006C',
        u'\u013F': u'\u004C',
        u'\u0140': u'\u006C',
        u'\u0141': u'\u004C',
        u'\u0142': u'\u006C',
        u'\u0143': u'\u004E',
        u'\u0144': u'\u006E',
        u'\u0145': u'\u004E',
        u'\u0146': u'\u006E',
        u'\u0147': u'\u004E',
        u'\u0148': u'\u006E',
        u'\u0149': u'\u006E',
        u'\u014A': u'\u004E',
        u'\u014B': u'\u006E',
        u'\u014C': u'\u004F',
        u'\u014D': u'\u006F',
        u'\u014E': u'\u004F',
        u'\u014F': u'\u006F',
        u'\u0150': u'\u004F',
        u'\u0151': u'\u006F',
        u'\u0152': u'\u004F',
        u'\u0153': u'\u006F',
        u'\u0154': u'\u0052',
        u'\u0155': u'\u0072',
        u'\u0156': u'\u0052',
        u'\u0157': u'\u0072',
        u'\u0158': u'\u0052',
        u'\u0159': u'\u0072',
        u'\u015A': u'\u0053',
        u'\u015B': u'\u0073',
        u'\u015C': u'\u0053',
        u'\u015D': u'\u0073',
        u'\u015E': u'\u0053',
        u'\u015F': u'\u0073',
        u'\u0160': u'\u0053',
        u'\u0161': u'\u0073',
        u'\u0162': u'\u0054',
        u'\u0163': u'\u0074',
        u'\u0164': u'\u0054',
        u'\u0165': u'\u0074',
        u'\u0166': u'\u0054',
        u'\u0167': u'\u0074',
        u'\u0168': u'\u0055',
        u'\u0169': u'\u0075',
        u'\u016A': u'\u0055',
        u'\u016B': u'\u0075',
        u'\u016E': u'\u0055',
        u'\u016F': u'\u0075',
        u'\u0170': u'\u0055',
        u'\u0171': u'\u0075',
        u'\u0172': u'\u0055',
        u'\u0173': u'\u0075',
        u'\u0174': u'\u0057',
        u'\u0175': u'\u0077',
        u'\u0176': u'\u0059',
        u'\u0177': u'\u0079',
        u'\u0178': u'\u0059',
        u'\u0179': u'\u005A',
        u'\u017A': u'\u007A',
        u'\u017B': u'\u005A',
        u'\u017C': u'\u007A',
        u'\u017D': u'\u005A',
        u'\u017E': u'\u007A',
        u'\u017F': u'\u0066',
        u'\u0181': u'\u0042',
        u'\u018A': u'\u0044',
        u'\u018F': u'\u0045',
        u'\u0192': u'\u003F',
        u'\u0198': u'\u004B',
        u'\u0199': u'\u006B',
        u'\u01A0': u'\u004F',
        u'\u01A1': u'\u006F',
        u'\u01AF': u'\u0055',
        u'\u01B0': u'\u0075',
        u'\u01B3': u'\u0059',
        u'\u01B4': u'\u0079',
        u'\u0253': u'\u0062',
        u'\u0257': u'\u0064',
        u'\u0259': u'\u0065',
        u'\u02BB': u'\u0027',
        u'\u02BC': u'\u0027',
        u'\u02BD': u'\u0027',
        u'\u02D9': u'\u0027',
        u'\u02DD': u'\u0022',
        u'\u037E': u'\u003B',
        u'\u0386': u'\u0041',
        u'\u0387': u'\u002E',
        u'\u0388': u'\u0045',
        u'\u0389': u'\u0048',
        u'\u038A': u'\u0049',
        u'\u038C': u'\u004F',
        u'\u038E': u'\u0059',
        u'\u038F': u'\u03A9',
        u'\u0390': u'\u0049',
        u'\u0391': u'\u0041',
        u'\u0392': u'\u0042',
        u'\u0395': u'\u0045',
        u'\u0396': u'\u005A',
        u'\u0397': u'\u0048',
        u'\u0399': u'\u0049',
        u'\u039A': u'\u004B',
        u'\u039C': u'\u004D',
        u'\u039D': u'\u004E',
        u'\u039F': u'\u004F',
        u'\u03A1': u'\u0050',
        u'\u03A4': u'\u0054',
        u'\u03A5': u'\u0059',
        u'\u03A7': u'\u0058',
        u'\u03AA': u'\u0049',
        u'\u03AB': u'\u0059',
        u'\u03AC': u'\u0041',
        u'\u03AD': u'\u0045',
        u'\u03AE': u'\u0048',
        u'\u03AF': u'\u0049',
        u'\u03B0': u'\u0059',
        u'\u03B1': u'\u0041',
        u'\u03B2': u'\u0042',
        u'\u03B3': u'\u0393',
        u'\u03B4': u'\u0394',
        u'\u03B5': u'\u0045',
        u'\u03B6': u'\u005A',
        u'\u03B7': u'\u0048',
        u'\u03B8': u'\u0398',
        u'\u03B9': u'\u0049',
        u'\u03BA': u'\u004B',
        u'\u03BB': u'\u039B',
        u'\u03BC': u'\u004D',
        u'\u03BD': u'\u004E',
        u'\u03BE': u'\u039E',
        u'\u03BF': u'\u004F',
        u'\u03C0': u'\u03A0',
        u'\u03C1': u'\u0050',
        u'\u03C2': u'\u03A3',
        u'\u03C3': u'\u03A3',
        u'\u03C4': u'\u0054',
        u'\u03C5': u'\u0059',
        u'\u03C6': u'\u03A6',
        u'\u03C7': u'\u0058',
        u'\u03C8': u'\u03A8',
        u'\u03C9': u'\u03A9',
        u'\u03CA': u'\u0049',
        u'\u03CB': u'\u0059',
        u'\u03CC': u'\u004F',
        u'\u03CD': u'\u0059',
        u'\u03CE': u'\u03A9',
        u'\u1E62': u'\u0053',
        u'\u1E63': u'\u0073',
        u'\u1EB8': u'\u0045',
        u'\u1EB9': u'\u0065',
        u'\u1ECA': u'\u0049',
        u'\u1ECB': u'\u0069',
        u'\u1ECC': u'\u004F',
        u'\u1ECD': u'\u006F',
        u'\u1EE4': u'\u0055',
        u'\u2010': u'\u002D',
        u'\u2013': u'\u002D',
        u'\u2014': u'\u002D',
        u'\u201A': u'\u0027',
        u'\u201C': u'\u0022',
        u'\u201D': u'\u0022',
        u'\u201E': u'\u0022',
        u'\u2020': u'\u002B',
        u'\u2021': u'\u002B',
        u'\u2022': u'\u002E',
        u'\u2026': u'\u002E',
        u'\u2030': u'\u0025',
        u'\u2039': u'\u003C',
        u'\u203A': u'\u003E',
        u'\u20A3': u'\u0023',
        u'\u20A4': u'\u0023',
        u'\u20B1': u'\u0023',
        u'\u2122': u'\u003F',
        u'\u221A': u'\u003F',
        u'\u221E': u'\u003F',
        u'\u2248': u'\u003F',
        u'\u2260': u'\u003F',
        u'\u2264': u'\u003C',
        u'\u2265': u'\u003E'
    }

    # All possible data munging characters substitutions.
    _substitutions = {}
    _substitutions.update(_accents)
    _substitutions.update(_whitespaces)
    _substitutions.update(_seven_bit_characters_translation_table)

    _url_finder = UrlFinder()

    def sanitize(self, message_or_segment):
        """
        Method to sanitize a given SMS message or segment.

        Args:
            message_or_segment (str): SMS message or segment to sanitize to.

        Returns:
           A :str: Sanitized message or segment.
        """
        urls_and_ranges = self._url_finder.find(message_or_segment)

        # Create sanitized builder only if there are substitution characters.
        in_url = False
        i = 0
        sanitized_builder = None

        for current in message_or_segment:
            is_whitespace = current.isspace() or current in self._whitespaces

            # If current character is the last characters of HTTP or HTTPS scheme then treat current
            # sequence as URL.
            if not in_url and not is_whitespace and self.is_inside_url(urls_and_ranges, i):
                in_url = True

            # If inside URL and whitespace is seen then stop treat current sequence as URL.
            if in_url and is_whitespace:
                in_url = False

            # Do not replace accents if inside URL.
            if in_url and current in self._accents:
                replacement = None
            else:
                replacement = self._substitutions.get(current)

            if replacement is not None:
                # Create sanitized builder.
                if sanitized_builder is None:
                    sanitized_builder = message_or_segment[0:i]

                sanitized_builder += replacement
            elif sanitized_builder is not None:
                sanitized_builder += current

            i += 1

        if sanitized_builder is not None:
            message_or_segment = sanitized_builder

        return self._TRIM_AND_REPEATED_SPACES.sub(' ', message_or_segment.strip())

    def is_inside_url(self, urls_and_ranges, index):
        """
        Checks if a given index is inside of the given URL ranges.

        Args:
            urls_and_ranges (object): URLs and their ranges.

        Returns:
           A :bool: Whether a given index is inside of on of the given URL ranges.
        """
        for url_and_range in urls_and_ranges:
            if url_and_range.interval_contains(index):
                return True

        return False
