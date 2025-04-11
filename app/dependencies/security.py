"""
Security module for JWT token validation.

This module handles JWT token validation using JWKS (JSON Web Key Sets)
from Azure AD B2C, providing authentication services for the API.
"""

import os

import jwt
import requests
from dotenv import load_dotenv
from jwt.algorithms import RSAAlgorithm

load_dotenv()


async def fetch_jwks():
    """Fetch JSON Web Key Set from the authentication provider."""
    base_uri = os.getenv("KINDE_URI")
    if not base_uri:
        raise ValueError("KINDE_URI is not defined in .env")

    jwks_uri = f"{base_uri.rstrip('/')}/.well-known/jwks"
    try:
        response = requests.get(jwks_uri, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error fetching JWKS: {str(e)}") from e


async def get_public_keys():
    """Fetch and parse public keys from JWKS endpoint."""
    public_keys = {}
    jwks = await fetch_jwks()

    try:
        for jwk in jwks["keys"]:
            kid = jwk["kid"]
            public_keys[kid] = RSAAlgorithm.from_jwk(jwk)
        return public_keys
    except (KeyError, jwt.InvalidKeyError) as e:
        raise RuntimeError(f"Error parsing JWK: {str(e)}") from e


class TokenValidator:
    """Handles JWT token validation using public keys."""

    def __init__(self):
        self.public_keys = None

    async def validate_token(self, token: str):
        """Validate and decode the provided JWT token using public keys."""
        try:
            # Initialize public keys if not already done
            if self.public_keys is None:
                self.public_keys = await get_public_keys()

            # Get the key ID from token header
            token_headers = jwt.get_unverified_header(token)
            if "kid" not in token_headers:
                raise jwt.InvalidTokenError("No 'kid' in token header")

            kid = token_headers["kid"]
            if kid not in self.public_keys:
                raise jwt.InvalidTokenError(f"Key ID '{kid}' not found in JWKS")

            # Decode and validate the token
            key = self.public_keys[kid]
            payload = jwt.decode(
                token,
                key=key,
                algorithms=["RS256"],
                options={"verify_aud": False},  # Add other options as needed
            )
            return payload

        except jwt.ExpiredSignatureError as exc:
            raise jwt.InvalidTokenError("Token has expired") from exc
        except jwt.InvalidTokenError as e:
            raise jwt.InvalidTokenError(f"Invalid token: {str(e)}") from e
        except Exception as e:
            raise jwt.InvalidTokenError(f"Token validation failed: {str(e)}")
