from dos_utility.auth.exceptions import (
    EmptyTokenException,
    InvalidTokenKeyException,
    InvalidTokenException,
    TokenExpiredException,
)


def test_empty_token_exception_message():
    exc = EmptyTokenException()
    assert "empty" in str(exc).lower()


def test_invalid_token_key_exception_default_message():
    exc = InvalidTokenKeyException()
    assert str(exc) != ""


def test_invalid_token_key_exception_custom_message():
    exc = InvalidTokenKeyException(msg="custom message")
    assert "custom message" in str(exc)


def test_invalid_token_exception_default_message():
    exc = InvalidTokenException()
    assert str(exc) != ""


def test_invalid_token_exception_custom_message():
    exc = InvalidTokenException(msg="custom message")
    assert "custom message" in str(exc)


def test_token_expired_exception_message():
    exc = TokenExpiredException()
    assert "expired" in str(exc).lower()


def test_exceptions_are_base_exceptions():
    assert issubclass(EmptyTokenException, Exception)
    assert issubclass(InvalidTokenKeyException, Exception)
    assert issubclass(InvalidTokenException, Exception)
    assert issubclass(TokenExpiredException, Exception)
