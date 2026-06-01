"""Audio device discovery helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class AudioDevice:
    index: int
    name: str
    max_input_channels: int
    max_output_channels: int
    default_samplerate: float
    hostapi: int

    @property
    def is_input(self) -> bool:
        return self.max_input_channels > 0


def _sounddevice():
    try:
        import sounddevice as sd
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "sounddevice is not installed. Run `pip install -r requirements.txt` "
            "and make sure PortAudio is available on your OS."
        ) from exc
    return sd


def list_devices() -> list[AudioDevice]:
    """Return all audio devices known to sounddevice."""

    sd = _sounddevice()
    raw_devices = sd.query_devices()
    devices: list[AudioDevice] = []
    for index, raw in enumerate(raw_devices):
        devices.append(
            AudioDevice(
                index=index,
                name=str(raw.get("name", "")),
                max_input_channels=int(raw.get("max_input_channels", 0)),
                max_output_channels=int(raw.get("max_output_channels", 0)),
                default_samplerate=float(raw.get("default_samplerate", 0.0)),
                hostapi=int(raw.get("hostapi", -1)),
            )
        )
    return devices


def input_devices() -> list[AudioDevice]:
    return [device for device in list_devices() if device.is_input]


def resolve_input_device(device_index: Optional[str | int]) -> Optional[int]:
    """Resolve CLI input into a sounddevice index.

    `None` and `auto` both mean "let sounddevice use the OS default input".
    """

    if device_index is None:
        return None
    if isinstance(device_index, str) and device_index.strip().lower() == "auto":
        return None
    try:
        index = int(device_index)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Device index must be an integer or 'auto', got {device_index!r}") from exc

    matching = [device for device in list_devices() if device.index == index]
    if not matching:
        raise ValueError(f"No audio device exists at index {index}")
    if not matching[0].is_input:
        raise ValueError(f"Audio device {index} is not an input device")
    return index


def format_devices(devices: Iterable[AudioDevice]) -> str:
    lines = [
        "Index | Input | Output | Default Hz | Name",
        "------+-------+--------+------------+------------------------------",
    ]
    for device in devices:
        lines.append(
            f"{device.index:>5} | "
            f"{device.max_input_channels:>5} | "
            f"{device.max_output_channels:>6} | "
            f"{device.default_samplerate:>10.0f} | "
            f"{device.name}"
        )
    return "\n".join(lines)


def print_input_devices() -> None:
    print(format_devices(input_devices()))
