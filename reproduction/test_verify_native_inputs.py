import hashlib,tempfile,unittest
from pathlib import Path
from verify_native_inputs import verify,resolved_path,SCHEMA
class NativePins(unittest.TestCase):
    def test_exact_and_wrong_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);src=root/"input";src.mkdir();(src/"a.tsv").write_bytes(b"original\n")
            pin={"schema_version":SCHEMA,"artifacts":[{"id":"A001","claims":["K1"],"name":"a.tsv","size_bytes":9,"sha256":hashlib.sha256(b"original\n").hexdigest()}]}
            loc={"schema_version":SCHEMA,"roots":{"source":str(src)},"locations":{"A001":{"root":"source","relative_path":"a.tsv"}}}
            ok=verify(pin,loc,root/"out1");self.assertEqual(ok["status"],"PASS_ALL_PINNED_INPUT_BYTES_ONLY")
            self.assertEqual(ok["scientific_replay_status"],"NOT_EXECUTED")
            pin["artifacts"][0]["sha256"]="0"*64
            bad=verify(pin,loc,root/"out2");self.assertEqual(bad["status"],"HOLD_MISSING_OR_CHANGED_INPUTS")
            self.assertEqual((src/"a.tsv").read_bytes(),b"original\n")
    def test_escape_and_source_overwrite_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with self.assertRaises(ValueError):resolved_path({"source":str(root)},{"root":"source","relative_path":"../secret"})
            with self.assertRaises(ValueError):
                verify({"schema_version":SCHEMA,"artifacts":[{"id":"x"}]},
                       {"schema_version":SCHEMA,"roots":{"source":str(root)},"locations":{}},root/"new")
if __name__=="__main__":unittest.main()
