"""Laptop-only capture transport. No Torch, MediaPipe or model weights are needed."""
from __future__ import annotations

import argparse
import base64
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import stat
import time
import uuid
import zipfile

import paramiko

ROOT = Path(__file__).resolve().parent
EXTRACTORS = ("dwpose", "hybrid", "rtmw", "mediapipe", "rtmw-hand", "rtmdet-hand")
MODELS = ("tcn", "bilstm", "stgcn")


def fingerprint(key):
    return "SHA256:" + base64.b64encode(hashlib.sha256(key.asbytes()).digest()).decode().rstrip("=")


class ConfirmHostKey(paramiko.MissingHostKeyPolicy):
    def __init__(self, known_hosts, confirm):
        self.known_hosts, self.confirm = Path(known_hosts), confirm

    def missing_host_key(self, client, hostname, key):
        value = fingerprint(key)
        if not self.confirm(hostname, value):
            raise paramiko.SSHException("서버 지문 확인을 취소했습니다.")
        self.known_hosts.parent.mkdir(parents=True, exist_ok=True)
        client.get_host_keys().add(hostname, key.get_name(), key)
        client.save_host_keys(str(self.known_hosts))


def load_config(path=None):
    config = json.loads(Path(path or ROOT / "client-config.json").read_text(encoding="utf-8"))
    for key in ("host", "username", "server_script", "server_python"):
        if not isinstance(config.get(key), str) or not config[key].strip():
            raise ValueError(f"연결 설정의 {key} 값을 입력하세요.")
    if not config["server_script"].startswith("/"):
        raise ValueError("서버 프로그램은 전체 경로로 지정하세요.")
    config["port"] = int(config.get("port", 22))
    if not 1 <= config["port"] <= 65535:
        raise ValueError("SSH 포트 번호를 확인하세요.")
    return config


def sha256(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def save_json(path, value):
    path = Path(path)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def safe_extract(archive, destination, max_bytes=4 * 1024**3):
    """Validate the entire archive before writing any file or following a link."""
    destination = Path(destination).resolve()
    with zipfile.ZipFile(archive) as bundle:
        members = bundle.infolist()
        if len(members) > 10000 or sum(m.file_size for m in members) > max_bytes:
            raise ValueError("결과 압축파일의 크기 제한을 초과했습니다.")
        seen = set()
        for entry in members:
            name = entry.filename
            parts = PurePosixPath(name).parts
            if (not parts or name.startswith("/") or "\\" in name or ":" in name
                    or any(part in (".", "..") or part.endswith((" ", ".")) for part in parts)
                    or stat.S_ISLNK(entry.external_attr >> 16)):
                raise ValueError("안전하지 않은 결과 파일 경로입니다.")
            target = destination.joinpath(*parts).resolve()
            if destination not in target.parents or name.casefold() in seen:
                raise ValueError("중복되거나 범위를 벗어난 결과 경로입니다.")
            seen.add(name.casefold())
        destination.mkdir(parents=True, exist_ok=False)
        try:
            for entry in members:
                path = destination.joinpath(*PurePosixPath(entry.filename).parts)
                if entry.is_dir():
                    path.mkdir(parents=True, exist_ok=True)
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with bundle.open(entry) as source, path.open("xb") as output:
                        shutil.copyfileobj(source, output)
        except Exception:
            shutil.rmtree(destination)
            raise


class Connection:
    def __init__(self, config, *, password=None, key_passphrase=None, confirm_host=None):
        self.config = config
        self.client = paramiko.SSHClient()
        known_hosts = Path(config.get("known_hosts", str(ROOT / "known_hosts"))).expanduser()
        if known_hosts.exists():
            self.client.load_host_keys(str(known_hosts))
        self.client.load_system_host_keys()
        if confirm_host:
            self.client.set_missing_host_key_policy(ConfirmHostKey(known_hosts, confirm_host))
        else:
            self.client.set_missing_host_key_policy(paramiko.RejectPolicy())
        key = config.get("key_filename")
        if key:
            key = str(Path(key).expanduser())
        self.client.connect(config["host"], port=config["port"], username=config["username"],
                            password=password or None, key_filename=key or None,
                            passphrase=key_passphrase or None, timeout=20, auth_timeout=30,
                            banner_timeout=20, allow_agent=True, look_for_keys=not bool(password))
        self.client.get_transport().set_keepalive(20)
        self.sftp = self.client.open_sftp()
        self.sftp.get_channel().settimeout(120)

    def close(self):
        try:
            self.sftp.close()
        finally:
            self.client.close()

    def command(self, action, job_id=None):
        if action not in ("prepare", "submit", "status", "info"):
            raise ValueError("지원하지 않는 서버 명령입니다.")
        arguments = [self.config["server_python"], self.config["server_script"]]
        if self.config.get("server_config"):
            arguments += ["--config", self.config["server_config"]]
        arguments += [action]
        if job_id:
            if not re.fullmatch(r"[0-9a-f]{32}", job_id):
                raise ValueError("작업 번호를 확인하세요.")
            arguments += ["--job-id", job_id]
        stdin, stdout, stderr = self.client.exec_command(shlex.join(arguments), timeout=120)
        stdin.close()
        data, errors = stdout.read(1024 * 1024).decode("utf-8"), stderr.read(65536).decode("utf-8", "replace")
        exit_code = stdout.channel.recv_exit_status()
        try:
            result = json.loads(data)
        except ValueError as exc:
            raise RuntimeError(f"서버 응답을 읽지 못했습니다: {errors[-1000:] or data[-1000:]}") from exc
        if exit_code or "error" in result and "state" not in result:
            raise RuntimeError(result.get("error", errors))
        return result


def receive_result(connection, state, local, notify):
    remote = PurePosixPath(state["job_dir"])
    expected_size, expected_sha = state["archive_bytes"], state["archive_sha256"]
    if type(expected_size) is not int or not 1 <= expected_size <= 4 * 1024**3:
        raise ValueError("서버 결과 파일의 크기를 확인하세요.")
    archive = local / "result.zip"
    if not archive.is_file() or archive.stat().st_size != expected_size or sha256(archive) != expected_sha:
        notify("보고서와 결과 영상 내려받는 중")
        temporary = local / "result.zip.part"
        connection.sftp.get(str(remote / "result.zip"), str(temporary),
                            callback=transfer_progress(notify, "결과 수신"))
        if temporary.stat().st_size != expected_size or sha256(temporary) != expected_sha:
            raise ValueError("받은 결과 파일의 검증에 실패했습니다. 같은 작업을 다시 연결하세요.")
        temporary.replace(archive)
    result = local / "result"
    verification = local / "received.json"
    if not (result / "report.html").is_file() or not verification.is_file() or json.loads(verification.read_text())["sha256"] != expected_sha:
        # Only a staging directory is removed. A previously received report is retained.
        stage = local / "result.unpacking"
        if stage.exists():
            shutil.rmtree(stage)
        safe_extract(archive, stage)
        if not (stage / "report.html").is_file() or not (stage / "summary.json").is_file():
            raise ValueError("서버 결과에 보고서가 없습니다.")
        if result.exists():
            result.rename(local / f"result.previous-{uuid.uuid4().hex[:8]}")
        stage.rename(result)
        save_json(verification, dict(sha256=expected_sha, received_at=datetime.now().isoformat()))
    notify("완료: 보고서와 결과 영상을 노트북에 저장했습니다.")
    return result / "report.html"


def transfer_progress(notify, label):
    last = [-1]
    def callback(done, total):
        percent = int(done * 100 / total) if total else 0
        if percent // 10 != last[0]:
            last[0] = percent // 10
            notify(f"{label}: {percent}%")
    return callback


def run_job(config, *, video=None, extractors=("rtmw",), models=("tcn",),
            timing=None, resume=None, password=None, key_passphrase=None,
            confirm_host=None, notify=print, stop_event=None, poll_seconds=3):
    if resume:
        receipt = Path(resume).resolve()
        local = receipt.parent
        record = json.loads(receipt.read_text(encoding="utf-8"))
        if record["server"] != {key: config.get(key) for key in ("host", "port", "username", "server_script", "server_python", "server_config")}:
            raise ValueError("이 작업을 시작했던 서버 연결 설정을 사용하세요.")
    else:
        video = Path(video).resolve()
        if not video.is_file():
            raise FileNotFoundError(video)
        if any(x not in EXTRACTORS for x in extractors) or any(x not in MODELS for x in models) or not extractors or not models:
            raise ValueError("추출기와 수어 모델을 선택하세요.")
        local = Path(config.get("results_dir", str(ROOT / "results"))).expanduser().resolve() / uuid.uuid4().hex
        local.mkdir(parents=True)
        receipt = local / "job.json"
        record = dict(job_id=local.name, video=str(video), request=dict(version=1, sha256=sha256(video),
                      bytes=video.stat().st_size, extractors=list(dict.fromkeys(extractors)),
                      models=list(dict.fromkeys(models)), capture_timing=timing),
                      server={key: config.get(key) for key in ("host", "port", "username", "server_script", "server_python", "server_config")},
                      prepared=False)
        save_json(receipt, record)
    notify(f"다시 연결할 작업 파일: {receipt}")
    connection = None
    try:
        connection = Connection(config, password=password, key_passphrase=key_passphrase, confirm_host=confirm_host)
        if not record["prepared"]:
            try:
                state = connection.command("prepare", record["job_id"])
            except RuntimeError:
                # The first response may have been lost after prepare succeeded.
                state = connection.command("status", record["job_id"])
            record.update(prepared=True, remote_dir=state["job_dir"])
            save_json(receipt, record)
        state = connection.command("status", record["job_id"])
        if state["state"] == "prepared":
            video = Path(record["video"])
            if not video.is_file() or sha256(video) != record["request"]["sha256"]:
                raise ValueError("전송할 원본 영상이 변경됐거나 없습니다.")
            remote = PurePosixPath(state["job_dir"])
            notify("영상 전송 중")
            connection.sftp.put(str(video), str(remote / "input.video.part"),
                                callback=transfer_progress(notify, "영상 전송"))
            connection.sftp.posix_rename(str(remote / "input.video.part"), str(remote / "input.video"))
            with connection.sftp.file(str(remote / "request.json.part"), "w") as stream:
                stream.write(json.dumps(record["request"], ensure_ascii=False).encode("utf-8"))
            connection.sftp.posix_rename(str(remote / "request.json.part"), str(remote / "request.json"))
            state = connection.command("submit", record["job_id"])
        last_phase = None
        while state["state"] in ("queued", "running"):
            if stop_event and stop_event.is_set():
                raise InterruptedError(f"결과 대기를 중단했습니다. 서버 작업은 계속됩니다. 다시 연결: {receipt}")
            label = f"{state['phase']} ({state.get('completed_steps', 0)}/{state.get('total_steps', '?')})"
            if label != last_phase:
                notify(label)
                last_phase = label
            time.sleep(poll_seconds)
            state = connection.command("status", record["job_id"])
        if state["state"] != "completed":
            try:
                connection.sftp.get(str(PurePosixPath(state["job_dir"]) / "server.log"), str(local / "server.log"))
            except OSError:
                pass
            raise RuntimeError(state.get("error", f"서버 작업 상태: {state['state']}"))
        save_json(local / "server-status.json", state)
        return receive_result(connection, state, local, notify)
    finally:
        if connection:
            connection.close()


def main():
    import getpass
    import webbrowser
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--video", type=Path)
    source.add_argument("--camera", type=int)
    source.add_argument("--resume", type=Path)
    parser.add_argument("--extractors", nargs="+", choices=EXTRACTORS, default=["rtmw"])
    parser.add_argument("--models", nargs="+", choices=MODELS, default=["tcn"])
    parser.add_argument("--password", action="store_true", help="SSH 비밀번호를 저장하지 않고 입력")
    parser.add_argument("--open-report", action="store_true")
    args = parser.parse_args()
    config = load_config(args.config)
    video, timing = args.video, None
    if args.camera is not None:
        from recorder import record_camera
        video, timing = record_camera(args.camera)
        if video is None:
            return
    def confirm(host, value):
        return input(f"새 서버 {host}\n지문 {value}\n서버에서 확인한 지문과 같습니까? [yes/no] ").strip().lower() == "yes"
    result = run_job(config, video=video, timing=timing, resume=args.resume,
                     extractors=args.extractors, models=args.models,
                     password=getpass.getpass("SSH 비밀번호: ") if args.password else None,
                     confirm_host=confirm)
    print(result)
    if args.open_report:
        webbrowser.open(result.as_uri())


if __name__ == "__main__":
    main()
