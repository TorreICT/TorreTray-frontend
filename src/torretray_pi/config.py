from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Iterable

from torretray_pi.models import MealType, ReservationFilters, ReservationType


@dataclass(frozen=True)
class ScheduledServiceWindow:
    date: date
    key: str
    label: str
    meal_type: MealType
    reservation_type: ReservationType
    start_time: time
    end_time: time

    def filters_for(self) -> ReservationFilters:
        return ReservationFilters(
            date=self.date,
            meal_type=self.meal_type,
            reservation_type=self.reservation_type,
        )

    def starts_at(self) -> datetime:
        return datetime.combine(self.date, self.start_time)

    def ends_at(self) -> datetime:
        return datetime.combine(self.date, self.end_time)

    def preload_starts_at(self, preload_minutes: int) -> datetime:
        return self.starts_at() - timedelta(minutes=preload_minutes)


def _load_env_file(project_root: Path) -> None:
    env_path = project_root / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def save_runtime_settings(
    project_root: Path,
    *,
    auto_refresh_minutes: int,
    preload_minutes: int,
    schedule_lookahead_days: int,
    bell_interval_seconds: int,
    bell_muted: bool,
) -> None:
    """Persist the editable runtime settings to the local tray `.env` file."""
    env_path = project_root / ".env"
    updates = {
        "TORRETRAY_AUTO_REFRESH_MINUTES": str(max(1, auto_refresh_minutes)),
        "TORRETRAY_PRELOAD_MINUTES": str(max(0, preload_minutes)),
        "TORRETRAY_SCHEDULE_LOOKAHEAD_DAYS": str(max(1, schedule_lookahead_days)),
        "TORRETRAY_BELL_INTERVAL_SECONDS": str(max(15, bell_interval_seconds)),
        "TORRETRAY_BELL_MUTED": "true" if bell_muted else "false",
    }

    existing_lines = (
        env_path.read_text(encoding="utf-8").splitlines()
        if env_path.exists()
        else []
    )
    updated_lines: list[str] = []
    seen_keys: set[str] = set()

    for raw_line in existing_lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or "=" not in raw_line:
            updated_lines.append(raw_line)
            continue

        key, _value = raw_line.split("=", 1)
        normalized_key = key.strip()
        if normalized_key not in updates:
            updated_lines.append(raw_line)
            continue

        updated_lines.append(f"{normalized_key}={updates[normalized_key]}")
        seen_keys.add(normalized_key)

    for key, value in updates.items():
        if key not in seen_keys:
            updated_lines.append(f"{key}={value}")

    env_path.write_text("\n".join(updated_lines).rstrip() + "\n", encoding="utf-8")
    for key, value in updates.items():
        os.environ[key] = value


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value, 0)


@dataclass(frozen=True)
class AppSettings:
    project_root: Path
    image_dir: Path
    api_base_url: str
    request_timeout_seconds: float
    auto_refresh_minutes: int
    preload_minutes: int
    schedule_lookahead_days: int
    bell_interval_seconds: int
    bell_muted: bool
    start_fullscreen: bool
    printer_vendor_id: int
    printer_product_id: int
    printer_interface: int
    test_now: datetime | None

    @property
    def logo_path(self) -> Path:
        return self.image_dir / "logo-torre-mono-small.png"

    @property
    def footer_logo_path(self) -> Path:
        return self.image_dir / "logo-torre-small.png"

    @property
    def window_icon_path(self) -> Path:
        return self.image_dir / "logo-torre.png"

    @property
    def printer_icon_path(self) -> Path:
        return self.image_dir / "printer.png"

    @property
    def loading_gif_path(self) -> Path:
        return self.image_dir / "upload_2.gif"

    @property
    def bell_sound_path(self) -> Path:
        return self.project_root / "res" / "glass_ping.wav"

    def current_datetime(self) -> datetime:
        return self.test_now or datetime.now()

    def current_date(self) -> date:
        return self.current_datetime().date()


def resolve_active_service(
    schedule_windows: Iterable[ScheduledServiceWindow],
    *,
    current_moment: datetime,
    preload_minutes: int,
) -> ScheduledServiceWindow | None:
    """Return the currently active service window, if any."""
    for window in sorted(
        schedule_windows,
        key=lambda item: item.preload_starts_at(preload_minutes),
    ):
        if window.preload_starts_at(preload_minutes) <= current_moment <= window.ends_at():
            return window
    return None


def next_service(
    schedule_windows: Iterable[ScheduledServiceWindow],
    *,
    current_moment: datetime,
    preload_minutes: int,
) -> tuple[ScheduledServiceWindow, datetime] | None:
    """Return the next upcoming service window and its preload start."""
    for window in sorted(
        schedule_windows,
        key=lambda item: item.preload_starts_at(preload_minutes),
    ):
        preload_time = window.preload_starts_at(preload_minutes)
        if preload_time > current_moment:
            return window, preload_time
    return None


def load_settings(*, test_now_override: datetime | None = None) -> AppSettings:
    project_root = Path(__file__).resolve().parents[2]
    _load_env_file(project_root)

    return AppSettings(
        project_root=project_root,
        image_dir=project_root / "res" / "img",
        api_base_url=os.getenv("TORRETRAY_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/"),
        request_timeout_seconds=float(
            os.getenv("TORRETRAY_REQUEST_TIMEOUT_SECONDS", "10")
        ),
        auto_refresh_minutes=max(1, _get_int("TORRETRAY_AUTO_REFRESH_MINUTES", 5)),
        preload_minutes=max(0, _get_int("TORRETRAY_PRELOAD_MINUTES", 5)),
        schedule_lookahead_days=max(1, _get_int("TORRETRAY_SCHEDULE_LOOKAHEAD_DAYS", 7)),
        bell_interval_seconds=max(15, _get_int("TORRETRAY_BELL_INTERVAL_SECONDS", 60)),
        bell_muted=_get_bool("TORRETRAY_BELL_MUTED", False),
        start_fullscreen=_get_bool("TORRETRAY_START_FULLSCREEN", True),
        printer_vendor_id=_get_int("TORRETRAY_PRINTER_VENDOR_ID", 0x1FC9),
        printer_product_id=_get_int("TORRETRAY_PRINTER_PRODUCT_ID", 0x2016),
        printer_interface=_get_int("TORRETRAY_PRINTER_INTERFACE", 0),
        test_now=test_now_override,
    )
