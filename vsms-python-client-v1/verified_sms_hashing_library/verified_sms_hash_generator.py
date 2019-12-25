# -*- coding: utf-8 -*-
"""This module contains the hash generator for creating hash codes
that can be used to call Verified SMS."""
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from .string_sanitizer import StringSanitizer

class VerifiedSmsHashGenerator(object):
    """
    This class converts SMS message strings into hash values for use
    with the Verified SMS (https://verifiedsms.googleapis.com).
    """
    _string_sanitizer = StringSanitizer()
    _HASH_CODE_LENGTH = 32

    def create_hashes(self, private_key, public_key, message):
        """
        Creates hash codes for the given key pair and message.

        Args:
            private_key (EllipticCurvePrivateKey): Private key of the brand.
            public_key (EllipticCurvePublicKey): Public key of a device.
            message str(): The SMS message

        Returns:
           A :list: List of hash codes for the given parameters.
        """
        results = []
        shared_key = private_key.exchange(ec.ECDH(), public_key)
        hash_codes = self.get_digests(shared_key, message)

        # Add all the hashed bytes as base64 encoded strings to the results
        for hash_code in hash_codes:
            results.append(base64.urlsafe_b64encode(hash_code).decode('utf-8'))

        return results

    def get_digests(self, shared_key, message):
        """
        Returns a list of SMS hash codes for the given argument and SMS message.

        Args:
            shared_key (bytes): The shared secret between
                the brand's private key and device's public key.
            message (str): SMS message segments.

        Returns:
           A :list: List of SMS hash codes for the given arguments.
        """
        results = []
        sanitized_message = self._string_sanitizer.sanitize(message)

        if sanitized_message != message:
            results.append(self._hkdf_for_hmac_sha256(shared_key, sanitized_message))

        results.append(self._hkdf_for_hmac_sha256(shared_key, message))

        return results

    def _hkdf_for_hmac_sha256(self, shared_key, message):
        """
        Calculates hash code by using HKDF and HMAC-SHA-2-256 algorithm using shared secret as the
        input keying material and message bytes as application specific information.

        Args:
            shared_key (bytes): The shared secret between
                the brand's private key and device's public key.
            message (str): SMS message segments.

        Returns:
           A :bytes: The unique hashcode for the message.
        """
        return HKDF(
            algorithm=hashes.SHA256(),
            length=self._HASH_CODE_LENGTH,
            salt=None,
            info=message.encode('UTF-8'),
            backend=default_backend()
        ).derive(shared_key)
