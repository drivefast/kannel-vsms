# -*- coding: utf-8 -*-
import unittest
import base64

from verified_sms_hashing_library import verified_sms_hash_generator

class TestVerifiedSmsHashFunctionV1(unittest.TestCase):
    _SECRET = bytearray([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    _HMACSHA256_LENGTH = 32

    _HELLO_WORLD = u'Hello, world!'
    _HELLO_WORLD_HASH = u'mSmxaqH5TXKaFGxKS8TOy8V2Ja1ZyoULfEa0dbrbKto='

    _HELLO_WORLD_NEW_LINES = u'Hello,\r\nworld!'
    _HELLO_WORLD_NEW_LINES_HASH = u'mPoCKZP1zshcaaD6aXY1DrzzHca4XZ_c2EM_vx0KejQ='

    _MESSAGE_WITH_UNICODE_SPACE = u'Hello,\r\n\u3000wörld!'
    _MESSAGE_WITH_UNICODE_SPACE_HASH_1 = u'mSmxaqH5TXKaFGxKS8TOy8V2Ja1ZyoULfEa0dbrbKto='
    _MESSAGE_WITH_UNICODE_SPACE_HASH_2 = u'ahezUooFUZDMXDGCe6Jo3amqJa03Mcr94dDn0dkK4TI='

    _ACCENTED_CHARACTERS = u'Hello, world! This is ÉèéìÑñÖ'
    _ACCENTED_CHARACTERS_REPLACED = u'Hello, world! This is EeeiNnO'
    _ACCENTED_CHARACTERS_HASH = u'FkfnSHOjwnB2jCxm1XrnYGPkz_-94e4PRT9AgtFUVr8='
    _ACCENTED_CHARACTERS_REPLACED_HASH = u'hfjEj6ZBWpNucIEYzbMPmpBZohQbYrICi0rGJfwGgJ0='

    _ACCENTED_CHARACTERS_IN_URL = u'Click this ÜRL HTTP://example.org/Éèéì\u3000ÑñÖ to register.'
    _ACCENTED_CHARACTERS_IN_URL_REPLACED = (u'Click this URL '
                                            'HTTP://example.org/Éèéì NnO to register.')
    _ACCENTED_CHARACTERS_IN_URL_HASH = u'Dmy-b2GmvZgAmTDEhnpnVFgxPcsND_0YXAUydgRe_1Q='
    _ACCENTED_CHARACTERS_IN_URL_REPLACED_HASH = u'2OOaiceVP78UJofZ9vVsDlkvbCv6aQArQWinyimN_MI='

    _MESSAGE_WITH_CHARACTERS_THAT_DONT_FIT_7BIT = (u'~!@#$%^&*()_+|}|{":":<?>?><>?>,/.'
                                                   '/./,\';\',[]\[][=-0=-0-987654321`1`1234567890-')
    _MESSAGE_WITH_CHARACTERS_THAT_DONT_FIT_7BIT_TRANSLATED = (u'~!@#$%^&*()_+|}|{":":<?>?><>?>'
                                                              ',/././,\';\',[]\[][=-0=-0-987654321'
                                                              '\'1\'1234567890-')
    _MESSAGE_WITH_CHARACTERS_THAT_DONT_FIT_7BIT_HASH = (u'D2kJxWi-HR-wANxrfCW0ts0x6rOeFkDH3'
                                                        'GvGy2A2T4M=')
    _MESSAGE_WITH_CHARACTERS_THAT_DONT_FIT_7BIT_TRANSLATED_HASH = (u'8oSdDPYafObGEBvaIGp2s3'
                                                                   'bS8nRlr1tu6v3j7gk9EKU=')

    _MESSAGE_WITH_BACKTICKS = u'te````st'
    _MESSAGE_WITH_BACKTICKS_REPLACED = u'te\'\'\'\'st'
    _MESSAGE_WITH_BACKTICKS_HASH = u'mHLZHhcgP04soshExFzKwFUUTafARcGIErBGt_VRxBU='
    _MESSAGE_WITH_BACKTICKS_REPLACED_HASH = u'Ir9thjpnlsR3ACRRw_Kp88m0jisL0cwqBhCdy7fgXkE='

    _MESSAGE_WITH_ACCENTED_CHARACTERS_IN_DOMAIN = (u'Accènted characters aren\'t expected to be '
                                                   'replaced in domain names: Bücher.org')
    _MESSAGE_WITH_ACCENTED_CHARACTERS_IN_DOMAIN_NOT_REPLACED = (u'Accented characters aren\'t '
                                                                'expected to be replaced in domain '
                                                                'names: Bücher.org')
    _MESSAGE_WITH_ACCENTED_CHARACTERS_IN_DOMAIN_HASH = (u'7Y-MNRzxhrunOcqrJMtA1s0xPijehy'
                                                        'TOmThgktIR-Qw=')
    _MESSAGE_WITH_ACCENTED_CHARACTERS_IN_DOMAIN_NOT_REPLACED_HASH = (u'ak6Mov6JUqoHNpp1D5NjX3aos'
                                                                     '4c5eESsBtzoUET_S8Y=')

    _MESSAGE_IS_URL_WITH_ACCENTED_CHARACTERS = u'httpS://example.org/Éèéì\u3000ÑñÖ'
    _MESSAGE_IS_URL_WITH_ACCENTED_CHARACTERS_REPLACED = u'httpS://example.org/Éèéì NnO'
    _MESSAGE_IS_URL_WITH_ACCENTED_CHARACTERS_HASH = u'kq-Z8MUgCzBdbKR1HC6_0NUe038xlA7wLmyzXdVY1EU='
    _MESSAGE_IS_URL_WITH_ACCENTED_CHARACTERS_REPLACED_HASH = (u'2tepgBjQ0k2i7F6V4Us2vQeQmKK8'
                                                              'tpaBghV1BGwPGms=')

    _hash_generator = verified_sms_hash_generator.VerifiedSmsHashGenerator()

    def to_base64(self, hashes):
        results = []
        for value in hashes:
            results.append(base64.urlsafe_b64encode(value).decode('utf-8'))

        return results

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

    def test_duplicates_for_not_munged_message(self):
        hash_codes = self._hash_generator.get_digests(self._SECRET, self._HELLO_WORLD)

        self.assertTrue(len(hash_codes) == 1)
        self.assertTrue(self.contains_exactly(self._HELLO_WORLD_HASH, self.to_base64(hash_codes)))

    def test_new_line_normalization(self):
        hash_codes = self._hash_generator.get_digests(self._SECRET, self._HELLO_WORLD_NEW_LINES)

        self.assertTrue(len(hash_codes) == 2)
        self.assertTrue(self.contains_exactly(
            [self._HELLO_WORLD_HASH, self._HELLO_WORLD_NEW_LINES_HASH],
            self.to_base64(hash_codes)))

    def test_two_hash_codes_with_sanitized_message(self):
        hash_codes = self._hash_generator.get_digests(
            self._SECRET,
            self._MESSAGE_WITH_UNICODE_SPACE)

        self.assertTrue(len(hash_codes) == 2)
        self.assertTrue(self.contains_exactly(
            [self._MESSAGE_WITH_UNICODE_SPACE_HASH_1, self._MESSAGE_WITH_UNICODE_SPACE_HASH_2],
            self.to_base64(hash_codes)))

    def test_accented_characters(self):
        with_changed_characters = self._hash_generator.get_digests(
            self._SECRET,
            self._ACCENTED_CHARACTERS)
        without_changed_characters = self._hash_generator.get_digests(
            self._SECRET,
            self._ACCENTED_CHARACTERS_REPLACED)

        self.assertTrue(self.contains_exactly(
            [self._ACCENTED_CHARACTERS_REPLACED_HASH, self._ACCENTED_CHARACTERS_HASH],
            self.to_base64(with_changed_characters)))

        self.assertTrue(self.contains_exactly(
            self._ACCENTED_CHARACTERS_REPLACED_HASH,
            self.to_base64(without_changed_characters)))

    def test_accented_characters_are_not_replaced_in_http_url(self):
        with_changed_characters = self._hash_generator.get_digests(
            self._SECRET,
            self._ACCENTED_CHARACTERS_IN_URL)
        without_changed_characters = self._hash_generator.get_digests(
            self._SECRET,
            self._ACCENTED_CHARACTERS_IN_URL_REPLACED)

        self.assertTrue(self.contains_exactly(
            [self._ACCENTED_CHARACTERS_IN_URL_REPLACED_HASH, self._ACCENTED_CHARACTERS_IN_URL_HASH],
            self.to_base64(with_changed_characters)))

        self.assertTrue(self.contains_exactly(
            self._ACCENTED_CHARACTERS_IN_URL_REPLACED_HASH,
            self.to_base64(without_changed_characters)))

    def test_accented_characters_are_not_replaced_in_https_url_when_message_is_url(self):
        with_changed_characters = self._hash_generator.get_digests(
            self._SECRET,
            self._MESSAGE_IS_URL_WITH_ACCENTED_CHARACTERS)
        without_changed_characters = self._hash_generator.get_digests(
            self._SECRET,
            self._MESSAGE_IS_URL_WITH_ACCENTED_CHARACTERS_REPLACED)

        self.assertTrue(
            self.contains_exactly([self._MESSAGE_IS_URL_WITH_ACCENTED_CHARACTERS_REPLACED_HASH,
                                   self._MESSAGE_IS_URL_WITH_ACCENTED_CHARACTERS_HASH],
                                  self.to_base64(with_changed_characters)))

        self.assertTrue(
            self.contains_exactly(self._MESSAGE_IS_URL_WITH_ACCENTED_CHARACTERS_REPLACED_HASH,
                                  self.to_base64(without_changed_characters)))

    def test_accented_characters_are_not_replaced_in_domain_name(self):
        with_changed_characters = self._hash_generator.get_digests(
            self._SECRET,
            self._MESSAGE_WITH_ACCENTED_CHARACTERS_IN_DOMAIN)
        without_changed_characters = self._hash_generator.get_digests(
            self._SECRET,
            self._MESSAGE_WITH_ACCENTED_CHARACTERS_IN_DOMAIN_NOT_REPLACED)

        self.assertTrue(
            self.contains_exactly([self._MESSAGE_WITH_ACCENTED_CHARACTERS_IN_DOMAIN_NOT_REPLACED_HASH,
                                   self._MESSAGE_WITH_ACCENTED_CHARACTERS_IN_DOMAIN_HASH],
                                   self.to_base64(with_changed_characters)))

        self.assertTrue(
            self.contains_exactly(self._MESSAGE_WITH_ACCENTED_CHARACTERS_IN_DOMAIN_NOT_REPLACED_HASH,
                                  self.to_base64(without_changed_characters)))

    def test_back_ticks(self):
        with_changed_characters = self._hash_generator.get_digests(
            self._SECRET,
            self._MESSAGE_WITH_BACKTICKS)
        without_changed_characters = self._hash_generator.get_digests(
            self._SECRET,
            self._MESSAGE_WITH_BACKTICKS_REPLACED)

        self.assertTrue(
            self.contains_exactly([self._MESSAGE_WITH_BACKTICKS_REPLACED_HASH,
                                   self._MESSAGE_WITH_BACKTICKS_HASH],
                                  self.to_base64(with_changed_characters)))

        self.assertTrue(
            self.contains_exactly(self._MESSAGE_WITH_BACKTICKS_REPLACED_HASH,
                                  self.to_base64(without_changed_characters)))

    def test_7bit_translation(self):
        with_changed_characters = self._hash_generator.get_digests(
            self._SECRET,
            self._MESSAGE_WITH_CHARACTERS_THAT_DONT_FIT_7BIT)
        without_changed_characters = self._hash_generator.get_digests(
            self._SECRET,
            self._MESSAGE_WITH_CHARACTERS_THAT_DONT_FIT_7BIT_TRANSLATED)

        self.assertTrue(
            self.contains_exactly([self._MESSAGE_WITH_CHARACTERS_THAT_DONT_FIT_7BIT_TRANSLATED_HASH,
                                   self._MESSAGE_WITH_CHARACTERS_THAT_DONT_FIT_7BIT_HASH],
                                  self.to_base64(with_changed_characters)))

        self.assertTrue(
            self.contains_exactly(self._MESSAGE_WITH_CHARACTERS_THAT_DONT_FIT_7BIT_TRANSLATED_HASH,
                                  self.to_base64(without_changed_characters)))

if __name__ == '__main__':
    unittest.main()