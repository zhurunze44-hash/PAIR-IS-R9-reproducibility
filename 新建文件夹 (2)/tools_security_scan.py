#!/usr/bin/env python3
"""Fail-closed primitive safety scan; false-negative-free security is NOT guaranteed.
Use together with manual rights/privacy review before private upload.
"""
import re,sys,hashlib
from pathlib import Path
r=Path(sys.argv[1]).resolve();blocked=[];n=0
# Safely allow only explicitly hash-indexed files under data/permitted/.
permitted={}
pmanifest=r/'data'/'PERMITTED_PUBLIC_MANIFEST.json'
if pmanifest.is_file():
 import json,hashlib
 try:
  for entry in json.loads(pmanifest.read_text()).get('files',[]):
   permitted[entry['public_relative_path']]=entry['sha256']
 except Exception:
  blocked.append('malformed permitted public manifest')
ext_block={'.pem','.key','.p12','.pfx','.sqlite','.db','.env','.parquet','.h5','.hdf5','.pt','.pth','.npy','.npz'}
for p in r.rglob('*'):
 if not p.is_file() or '.git' in p.parts:continue
 n+=1
 rel=p.relative_to(r).as_posix()
 if any(s in rel.lower() for s in ('private_inventory','original_native_staged','credentials','access_token','passwords','personal_data')):
  blocked.append('restricted name '+rel)
 if p.suffix.lower() in ext_block or (p.name.startswith('.env')):
  if rel.startswith('data/permitted/') and rel in permitted:
   if hashlib.sha256(p.read_bytes()).hexdigest() != permitted[rel]:
    blocked.append('approved data SHA mismatch '+rel)
  else:
   blocked.append('restricted extension '+rel)
 if p.stat().st_size>90*1024*1024:blocked.append('oversize '+rel)
 if p.suffix.lower() in ('.md','.json','.yml','.yaml','.py','.sh','.txt','.tex','.bib','.csv','.cff') and p.stat().st_size<4*1024**2:
  t=p.read_text(errors='replace')
  rules=(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',r'ghp_[A-Za-z0-9]{30,}',
         r'github_pat_[A-Za-z0-9_]{40,}',r'(?i)authorization:\s*bearer\s+[A-Za-z0-9]{16,}')
  if any(re.search(x,t) for x in rules):blocked.append('potential credential '+rel)
print('SAFETY_SCAN',n,'files', 'HOLD '+repr(blocked) if blocked else 'PASS_AUTOMATIC_SCREEN_ONLY')
if blocked:sys.exit(4)
