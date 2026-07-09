"""Tests for JWT authentication helpers."""

from __future__ import annotations

import os
import unittest

from auth import (
    AuthError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


class TestAuth(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["JWT_SECRET"] = "test-secret-key"

    def test_password_hash_and_verify(self) -> None:
        password_hash = hash_password("secure-password")
        self.assertTrue(verify_password("secure-password", password_hash))
        self.assertFalse(verify_password("wrong-password", password_hash))

    def test_create_and_decode_access_token(self) -> None:
        token = create_access_token(1, "user@example.com")
        payload = decode_access_token(token)
        self.assertEqual(payload["sub"], "1")
        self.assertEqual(payload["email"], "user@example.com")

    def test_missing_jwt_secret_raises(self) -> None:
        os.environ.pop("JWT_SECRET", None)
        with self.assertRaises(AuthError):
            create_access_token(1, "user@example.com")


if __name__ == "__main__":
    unittest.main()
