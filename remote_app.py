"""Small Windows-friendly launcher for recording, SSH transfer and report retrieval."""
from __future__ import annotations

import json
from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser

from remote_client import ROOT, EXTRACTORS, MODELS, load_config, run_job, save_json


class App:
    def __init__(self, window):
        self.window = window
        self.events = queue.Queue()
        self.stop = threading.Event()
        self.busy, self.last_report = False, None
        window.title("SMS 원격 수어 분석")
        window.geometry("900x780")
        window.minsize(760, 640)
        pane = ttk.Frame(window, padding=20)
        pane.pack(fill="both", expand=True)
        ttk.Label(pane, text="노트북 촬영 → GPU 서버 분석 → 보고서 받기", font=("맑은 고딕", 18, "bold")).pack(anchor="w")
        ttk.Label(pane, text="노트북은 촬영과 전송만 수행합니다. 모델과 키포인트 처리는 서버에서 실행합니다.").pack(anchor="w", pady=(6, 12))
        self.config_path = ROOT / "client-config.json"
        example = ROOT / "client-config.example.json"
        config = json.loads((self.config_path if self.config_path.exists() else example).read_text(encoding="utf-8"))
        self.config = config
        server = ttk.LabelFrame(pane, text="1. 서버 연결", padding=10)
        server.pack(fill="x")
        self.fields = {}
        for row, (key, label, default) in enumerate([
            ("host", "서버 주소", ""), ("port", "SSH 포트", "22"), ("username", "사용자 이름", "your-user"),
            ("server_script", "서버 프로그램 위치", "/path/to/workspace/sms-demo/sms-remote/server.py"),
            ("key_filename", "SSH 개인키 (선택)", ""),
        ]):
            ttk.Label(server, text=label).grid(row=row, column=0, sticky="w", pady=2)
            value = tk.StringVar(value=str(config.get(key, default)))
            self.fields[key] = value
            ttk.Entry(server, textvariable=value).grid(row=row, column=1, sticky="ew", padx=8, pady=2)
        server.columnconfigure(1, weight=1)
        self.password, self.passphrase = tk.StringVar(), tk.StringVar()
        ttk.Label(server, text="SSH 비밀번호").grid(row=5, column=0, sticky="w")
        ttk.Entry(server, textvariable=self.password, show="*").grid(row=5, column=1, sticky="ew", padx=8)
        ttk.Label(server, text="개인키 암호 (선택)").grid(row=6, column=0, sticky="w")
        ttk.Entry(server, textvariable=self.passphrase, show="*").grid(row=6, column=1, sticky="ew", padx=8)
        ttk.Label(server, text="비밀번호와 개인키 암호는 파일에 저장하지 않습니다.").grid(row=7, column=0, columnspan=2, sticky="w", pady=3)
        source = ttk.LabelFrame(pane, text="2. 입력", padding=10)
        source.pack(fill="x", pady=8)
        self.mode, self.video, self.camera = tk.StringVar(value="camera"), tk.StringVar(), tk.StringVar(value="0")
        ttk.Radiobutton(source, text="웹캠 촬영", variable=self.mode, value="camera").grid(row=0, column=0, sticky="w")
        ttk.Label(source, text="카메라 번호").grid(row=0, column=1, sticky="w")
        ttk.Spinbox(source, from_=0, to=9, textvariable=self.camera, width=5).grid(row=0, column=2)
        ttk.Radiobutton(source, text="저장된 영상", variable=self.mode, value="video").grid(row=1, column=0, sticky="w")
        ttk.Entry(source, textvariable=self.video).grid(row=1, column=1, sticky="ew", padx=8)
        ttk.Button(source, text="선택", command=self.browse_video).grid(row=1, column=2)
        ttk.Label(source, text="촬영 창에서 Space 시작 → 수어 수행 → Space 종료. 최대 60초, 30fps.").grid(row=2, column=0, columnspan=3, sticky="w", pady=5)
        source.columnconfigure(1, weight=1)
        choices = ttk.LabelFrame(pane, text="3. 서버에서 실행할 분석", padding=10)
        choices.pack(fill="x")
        self.extractors, self.models = {}, {}
        labels = dict(dwpose="DWPose-L", hybrid="hybrid", rtmw="RTMW-x 384", mediapipe="MediaPipe (CPU)",
                      **{"rtmw-hand": "RTMW + Hand", "rtmdet-hand": "RTMDet-Hand"})
        for i, name in enumerate(EXTRACTORS):
            value = tk.BooleanVar(value=name == "rtmw")
            self.extractors[name] = value
            ttk.Checkbutton(choices, text=labels[name], variable=value).grid(row=i//3, column=i%3, sticky="w", padx=8)
        for i, name in enumerate(MODELS):
            value = tk.BooleanVar(value=name == "tcn")
            self.models[name] = value
            ttk.Checkbutton(choices, text=name.upper(), variable=value).grid(row=2, column=i, sticky="w", padx=8, pady=(8, 0))
        actions = ttk.Frame(pane)
        actions.pack(fill="x", pady=12)
        self.start_button = ttk.Button(actions, text="촬영·전송·분석 시작", command=self.start)
        self.start_button.pack(side="left")
        self.resume_button = ttk.Button(actions, text="기존 작업 다시 연결", command=self.resume)
        self.resume_button.pack(side="left", padx=8)
        self.open_button = ttk.Button(actions, text="받은 보고서 열기", command=self.open_report, state="disabled")
        self.open_button.pack(side="left")
        self.log = tk.Text(pane, height=9, wrap="word", state="disabled")
        self.log.pack(fill="both", expand=True)
        window.protocol("WM_DELETE_WINDOW", self.close)
        window.after(100, self.poll)

    def browse_video(self):
        filename = filedialog.askopenfilename(filetypes=[("동영상", "*.mp4 *.avi *.mov *.mkv"), ("모든 파일", "*")])
        if filename:
            self.video.set(filename)
            self.mode.set("video")

    def notify(self, text):
        self.events.put(("log", str(text)))

    def confirm_host(self, host, fingerprint):
        response, ready = [], threading.Event()
        self.events.put(("host", (host, fingerprint, response, ready)))
        while not ready.wait(.2):
            if self.stop.is_set():
                return False
        return response[0]

    def start(self):
        self.launch()

    def resume(self):
        path = filedialog.askopenfilename(initialdir=ROOT / "results", title="이전 작업의 job.json 선택",
                                          filetypes=[("작업 파일", "job.json")])
        if path:
            self.launch(Path(path))

    def launch(self, resume=None):
        if self.busy:
            return
        try:
            config = dict(self.config)
            config.update({key: value.get().strip() for key, value in self.fields.items()})
            config.setdefault("server_python", "/usr/bin/python3")
            save_json(self.config_path, config)
            config = load_config(self.config_path)
            names = [name for name, value in self.extractors.items() if value.get()]
            models = [name for name, value in self.models.items() if value.get()]
            mode, video, camera = self.mode.get(), self.video.get(), int(self.camera.get())
            if not resume and (not names or not models):
                raise ValueError("추출기와 수어 모델을 각각 하나 이상 선택하세요.")
            if not resume and mode == "video" and not Path(video).is_file():
                raise ValueError("분석할 영상 파일을 선택하세요.")
        except Exception as exc:
            messagebox.showerror("설정 확인", str(exc))
            return
        password, passphrase = self.password.get(), self.passphrase.get()
        self.password.set("")
        self.passphrase.set("")
        self.stop.clear()
        self.busy = True
        self.start_button.configure(state="disabled")
        self.resume_button.configure(state="disabled")
        def work():
            try:
                source, timing = video, None
                if not resume and mode == "camera":
                    from recorder import record_camera
                    self.notify("촬영 창에서 Space를 눌러 시작·종료하세요.")
                    source, timing = record_camera(camera)
                    if source is None:
                        self.notify("촬영을 취소했습니다.")
                        return
                report = run_job(config, video=source, timing=timing, resume=resume,
                                 extractors=names, models=models, password=password, key_passphrase=passphrase,
                                 confirm_host=self.confirm_host, notify=self.notify, stop_event=self.stop)
                self.events.put(("report", report))
            except Exception as exc:
                self.events.put(("error", str(exc)))
            finally:
                self.events.put(("idle", None))
        threading.Thread(target=work, daemon=True).start()

    def poll(self):
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind == "host":
                    host, fingerprint, response, ready = payload
                    response.append(messagebox.askyesno("처음 연결하는 서버",
                        f"서버: {host}\n지문: {fingerprint}\n\n서버에서 확인한 SSH 지문과 같은 경우에만 연결하세요. 이 서버를 신뢰하고 저장할까요?"))
                    ready.set()
                elif kind in ("log", "error"):
                    self.log.configure(state="normal")
                    self.log.insert("end", payload + "\n")
                    self.log.see("end")
                    self.log.configure(state="disabled")
                    if kind == "error":
                        messagebox.showerror("작업 확인", payload + "\n\n연결 문제라면 기존 작업 다시 연결에서 위에 표시된 job.json을 선택하세요.")
                elif kind == "report":
                    self.last_report = Path(payload)
                    self.open_button.configure(state="normal")
                    self.open_report()
                elif kind == "idle":
                    self.busy = False
                    self.start_button.configure(state="normal")
                    self.resume_button.configure(state="normal")
        except queue.Empty:
            pass
        self.window.after(100, self.poll)

    def open_report(self):
        if self.last_report:
            webbrowser.open(self.last_report.resolve().as_uri())

    def close(self):
        if self.busy and not messagebox.askyesno("창 닫기", "창을 닫아도 이미 시작한 서버 분석은 계속됩니다. 나중에 기존 작업 다시 연결로 결과를 받을 수 있습니다. 닫을까요?"):
            return
        self.stop.set()
        self.window.destroy()


if __name__ == "__main__":
    window = tk.Tk()
    App(window)
    window.mainloop()
