"""
blocklist.py
...

This file just contains the blocklist set used to store revoked JWTs. It will be imported by 
app and the logout resource so that tokens can be added to it and checked against it when the user
logs out or makes a request with a JWT.
"""
BLOCKLIST = set()
