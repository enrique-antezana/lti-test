import json
from jwcrypto.jwk import JWK

f = open("jwtRS256.key.pub", "r")
public_key = f.read()
f.close()

jwk_obj = JWK.from_pem(public_key.encode('utf-8'))
public_jwk = json.loads(jwk_obj.export_public())
public_jwk['alg'] = 'RS256'
public_jwk['use'] = 'sig'
public_jwk_str = json.dumps(public_jwk)
print(public_jwk_str)