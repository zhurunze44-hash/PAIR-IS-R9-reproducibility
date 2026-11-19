"""Merge independently compiled documents without destination-name collisions."""
from pathlib import Path
import json
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject, ArrayObject, TextStringObject, NameObject

ROOT=Path(__file__).resolve().parents[1]

def namespace_destinations(reader, prefix):
    mapping={str(name):prefix+str(name) for name in reader.named_destinations}
    root=reader.trailer['/Root']
    names=root.get('/Names')
    if names is not None:
        tree=names.get_object().get('/Dests')
        def rename_tree(node):
            node=node.get_object()
            if '/Names' in node:
                pairs=node['/Names']
                for i in range(0,len(pairs),2):pairs[i]=TextStringObject(mapping[str(pairs[i])])
            if '/Limits' in node:
                node[NameObject('/Limits')]=ArrayObject([TextStringObject(mapping[str(v)]) for v in node['/Limits']])
            for child in node.get('/Kids',[]):rename_tree(child)
        if tree is not None:rename_tree(tree)
    if '/Dests' in root:
        old=root['/Dests'];new=DictionaryObject()
        for key,value in old.items():
            new[NameObject('/'+mapping.get(str(key).lstrip('/'),prefix+str(key).lstrip('/')))]=value
        root[NameObject('/Dests')]=new
    seen=set()
    def retarget(obj):
        obj=obj.get_object() if hasattr(obj,'get_object') else obj
        if not isinstance(obj,(DictionaryObject,ArrayObject)) or id(obj) in seen:return
        seen.add(id(obj))
        if isinstance(obj,DictionaryObject):
            for key in ['/Dest','/D']:
                value=obj.get(key)
                if isinstance(value,str) and str(value) in mapping:
                    obj[NameObject(key)]=TextStringObject(mapping[str(value)])
            for value in list(obj.values()):retarget(value)
        else:
            for value in obj:retarget(value)
    retarget(root)
    # PdfReader caches the name tree; invalidate after the in-memory rename.
    reader._named_destinations_cache=None
    return mapping

main=PdfReader(ROOT/'PAIR_KBS_Main.pdf');supp=PdfReader(ROOT/'PAIR_KBS_Supplement.pdf')
expected={}
for reader,prefix,offset in [(main,'main::',0),(supp,'supp::',len(main.pages))]:
    expected.update({prefix+str(name):offset+reader.get_destination_page_number(dest) for name,dest in reader.named_destinations.items()})
    namespace_destinations(reader,prefix)
writer=PdfWriter()
writer.append(main,outline_item='Main manuscript')
writer.append(supp,outline_item='Supplementary information')
writer.add_metadata({'/Title': main.metadata.title, '/Author': main.metadata.author})
path=ROOT/'PAIR_KBS_Complete.pdf'
with path.open('wb') as handle:writer.write(handle)
check=PdfReader(path)
actual={str(name):check.get_destination_page_number(dest) for name,dest in check.named_destinations.items()}
assert actual==expected, 'Merged destinations do not preserve standalone page targets'
links=0
for page in check.pages:
    for ref in page.get('/Annots',[]):
        obj=ref.get_object();action=obj.get('/A')
        target=obj.get('/Dest')
        if action is not None and action.get_object().get('/S')=='/GoTo':target=action.get_object().get('/D')
        if isinstance(target,str):assert str(target) in actual;links+=1
receipt={'status':'PASS_NAMESPACED_PDF_LINKS','named_destinations':len(actual),'string_internal_links_checked':links,'main_pages':len(main.pages),'supplement_pages':len(supp.pages),'complete_pages':len(check.pages),'all_destination_pages_match_standalone':True}
(ROOT/'revision_audit/PDF_LINK_QA.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt))
