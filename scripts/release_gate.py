#!/usr/bin/env python3
"""Fail closed if a claimed complete original-source reproduction package is absent."""
import argparse,json,hashlib,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--verify',action='store_true');a=p.parse_args()
r=Path(a.root).resolve();m=r/'native_export_manifest.json'
needed=['K562_PRODUCER','K562_ENCODER','ENCODE','REPLOGLE','CTRP','GDSC','FIGURE_INPUTS']
issues=[]
if not m.is_file():issues.append('MISSING native_export_manifest.json')
else:
 obj=json.loads(m.read_text());arr=obj.get('files',[])
 for key in needed:
  eligible=[x for x in arr if x.get('domain')==key and x.get('release_status')=='APPROVED_PUBLIC' and x.get('origin')=='ORIGINAL_NATIVE']
  if not eligible:issues.append('MISSING authenticated original public files for '+key)
 for x in arr:
  if x.get('release_status')!='APPROVED_PUBLIC':continue
  rel=x.get('staged_relative_path','');fp=(r/rel).resolve()
  if not rel or not fp.is_relative_to(r) or not fp.is_file(): issues.append('invalid/missing path '+str(rel));continue
  h=hashlib.sha256(fp.read_bytes()).hexdigest()
  if h!=x.get('sha256'):issues.append('hash mismatch '+str(rel))
 if not obj.get('explicit_redistribution_licence_audit',False):issues.append('public distribution rights not certified')
 if not obj.get('original_producer_identity_audit',False):issues.append('producer identity was not certified')
print(json.dumps({'gate':'PASS' if not issues else 'HOLD','issues':issues},indent=2,ensure_ascii=False))
if issues:sys.exit(3)
