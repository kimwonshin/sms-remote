"""Webcam recording only; model processing happens on the remote GPU computer."""
from datetime import datetime
import json
import math
from pathlib import Path
import sys
import time


def record_camera(camera=0, destination=None, max_frames=1800):
    import cv2
    root = Path(__file__).resolve().parent / "recordings"
    root.mkdir(exist_ok=True)
    destination = Path(destination or root / f"camera-{datetime.now():%Y%m%d-%H%M%S-%f}.avi")
    if destination.exists():
        raise FileExistsError("기존 녹화 파일은 덮어쓰지 않습니다.")
    capture = cv2.VideoCapture(camera, cv2.CAP_DSHOW) if sys.platform == "win32" else cv2.VideoCapture(camera)
    if not capture.isOpened() and sys.platform == "win32":
        capture.release()
        capture = cv2.VideoCapture(camera)
    writer = None
    window = "SMS Remote - SPACE: start/finish | q: quit"
    try:
        if not capture.isOpened():
            raise RuntimeError("웹캠을 열 수 없습니다. 카메라 번호와 권한을 확인하세요.")
        capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        capture.set(cv2.CAP_PROP_FPS, 30)
        reported = float(capture.get(cv2.CAP_PROP_FPS))
        stamps, active, slot = [], False, -1
        while True:
            ok, frame = capture.read()
            timestamp = time.monotonic()
            if not ok:
                raise RuntimeError("웹캠 프레임을 읽지 못했습니다.")
            if active:
                next_slot = int((timestamp - stamps[0]) * 30 + .25) if stamps else 0
                if next_slot > slot:
                    if writer is None:
                        h, w = frame.shape[:2]
                        writer = cv2.VideoWriter(str(destination), cv2.VideoWriter_fourcc(*"MJPG"), 30, (w, h))
                        if not writer.isOpened():
                            raise RuntimeError("영상 저장 파일을 만들 수 없습니다.")
                    # Mirror only the preview, preserving anatomical left/right in the input.
                    writer.write(frame)
                    stamps.append(timestamp)
                    slot = next_slot
            fps = (len(stamps)-1)/(stamps[-1]-stamps[0]) if len(stamps) > 1 else 0
            view = cv2.flip(frame, 1)
            label = f"REC {len(stamps)} frames | {fps:.1f} fps | SPACE: finish" if active else "SPACE: start | q: quit"
            cv2.putText(view, label, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, .55, (0, 220, 0), 2, cv2.LINE_AA)
            cv2.imshow(window, view)
            key = cv2.waitKey(1) & 255
            if key in (27, ord("q")) or cv2.getWindowProperty(window, cv2.WND_PROP_VISIBLE) < 1:
                return None, None
            finish = active and (key == 32 or len(stamps) >= max_frames)
            if key == ord("r"):
                if writer:
                    writer.release()
                writer, stamps, active, slot = None, [], False, -1
            if key == 32 and not active and not finish:
                active = True
            if finish:
                if len(stamps) < 2:
                    continue
                writer.release()
                writer = None
                timing = dict(captured_frames=len(stamps), capture_fps=round(fps, 3),
                              camera_reported_fps=reported if math.isfinite(reported) else None,
                              capture_duration_seconds=round(stamps[-1]-stamps[0]+1/30, 4),
                              max_frame_gap_ms=round(max(b-a for a,b in zip(stamps, stamps[1:]))*1000, 3))
                destination.with_suffix(".timing.json").write_text(json.dumps(timing, indent=2), encoding="utf-8")
                if not 27 <= fps <= 33:
                    raise ValueError(f"실제 촬영 속도가 {fps:.1f}fps입니다. 30fps 지원과 조명을 확인하세요. 녹화 원본은 보존했습니다.")
                return destination, timing
    finally:
        if writer:
            writer.release()
        capture.release()
        cv2.destroyAllWindows()
