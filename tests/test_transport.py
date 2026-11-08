import io
import json
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from remote_client import safe_extract, sha256, run_job, ConfirmHostKey


class TransportTests(unittest.TestCase):
    def archive(self, root, names):
        archive = root / "test.zip"
        with zipfile.ZipFile(archive, "w") as bundle:
            for name, contents in names:
                bundle.writestr(name, contents)
        return archive

    def test_path_traversal_is_rejected_before_writing(self):
        for name in ("../escape.txt", "/absolute.txt", "C:/temp/escape", "a\\..\\escape"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                archive = self.archive(root, [("good.txt", "ok"), (name, "bad")])
                with self.assertRaises(ValueError):
                    safe_extract(archive, root / "output")
                self.assertFalse((root / "output").exists())

    def test_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            entry = zipfile.ZipInfo("link")
            entry.create_system = 3
            entry.external_attr = (stat.S_IFLNK | 0o777) << 16
            with zipfile.ZipFile(root / "test.zip", "w") as bundle:
                bundle.writestr(entry, "../target")
            with self.assertRaises(ValueError):
                safe_extract(root / "test.zip", root / "output")

    def test_total_size_limit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = self.archive(root, [("large", "12345")])
            with self.assertRaises(ValueError):
                safe_extract(archive, root / "output", max_bytes=4)

    def test_valid_report_extraction(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = self.archive(root, [("report.html", "보고서"), ("rtmw/keypoints.mp4", "video")])
            safe_extract(archive, root / "output")
            self.assertEqual((root / "output/report.html").read_text(), "보고서")

    def test_host_refusal_does_not_save_key(self):
        import paramiko
        with tempfile.TemporaryDirectory() as temp:
            known = Path(temp) / "known_hosts"
            policy = ConfirmHostKey(known, lambda *_: False)
            with self.assertRaises(paramiko.SSHException):
                policy.missing_host_key(paramiko.SSHClient(), "test", paramiko.RSAKey.generate(1024))
            self.assertFalse(known.exists())

    def test_resume_completed_job_downloads_without_resubmission(self):
        config = dict(host="example", port=22, username="user", server_script="/server.py", server_python="python3")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = self.archive(root, [("report.html", "report"), ("summary.json", "{}")])
            receipt = root / "job.json"
            receipt.write_text(json.dumps(dict(job_id="a" * 32, prepared=True, server=dict(config, server_config=None))))
            state = dict(state="completed", job_dir="/jobs/" + "a" * 32,
                         archive_bytes=archive.stat().st_size, archive_sha256=sha256(archive))
            class SFTP:
                def get(self, remote, local, callback=None):
                    Path(local).write_bytes(archive.read_bytes())
            class FakeConnection:
                actions = []
                def __init__(self, *args, **kwargs):
                    self.sftp = SFTP()
                def command(self, action, job_id=None):
                    self.actions.append(action)
                    return state
                def close(self):
                    pass
            with patch("remote_client.Connection", FakeConnection):
                result = run_job(config, resume=receipt, notify=lambda *_: None)
            self.assertEqual(result.read_text(), "report")
            self.assertEqual(FakeConnection.actions, ["status"])


if __name__ == "__main__":
    unittest.main()
