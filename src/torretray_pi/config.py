from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path

from torretray_pi.models import MealType, ReservationFilters, ReservationType


WEEKDAY_NAMES = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)


@dataclass(frozen=True)
class ScheduledServiceWindow:
    key: str
    label: str
    meal_type: MealType
    reservation_type: ReservationType
    start_time: time
    end_time: time

    def filters_for(self, target_date: date) -> ReservationFilters:
        return ReservationFilters(
            date=target_date,
            meal_type=self.meal_type,
            reservation_type=self.reservation_type,
        )

    def starts_at(self, target_date: date) -> datetime:
        return datetime.combine(target_date, self.start_time)

    def ends_at(self, target_date: date) -> datetime:
        return datetime.combine(target_date, self.end_time)

    def preload_starts_at(self, target_date: date, preload_minutes: int) -> datetime:
        return self.starts_at(target_date) - timedelta(minutes=preload_minutes)


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


def _get_time(name: str, default: str) -> time:
    value = os.getenv(name, default).strip()
    return datetime.strptime(value, "%H:%M").time()


def _slot_time(slot: str, edge: str, weekday_name: str, default: str) -> time:
    specific_key = f"TORRETRAY_{slot.upper()}_{edge.upper()}_{weekday_name.upper()}"
    base_key = f"TORRETRAY_{slot.upper()}_{edge.upper()}"
    if os.getenv(specific_key):
        return _get_time(specific_key, default)
    return _get_time(base_key, default)


def _load_schedule() -> dict[int, tuple[ScheduledServiceWindow, ...]]:
    defaults = (
        (
            "breakfast",
            "Schiscette da colazione",
            MealType.LUNCH,
            ReservationType.LUNCHBOX,
            "08:00",
            "08:45",
        ),
        (
            "lunch",
            "Vassoi del pranzo",
            MealType.LUNCH,
            ReservationType.TRAY,
            "13:00",
            "14:30",
        ),
        (
            "dinner",
            "Vassoi della cena",
            MealType.DINNER,
            ReservationType.TRAY,
            "20:00",
            "21:00",
        ),
    )

    schedule: dict[int, tuple[ScheduledServiceWindow, ...]] = {}
    for weekday_index, weekday_name in enumerate(WEEKDAY_NAMES):
        windows: list[ScheduledServiceWindow] = []
        for key, label, meal_type, reservation_type, start_default, end_default in defaults:
            windows.append(
                ScheduledServiceWindow(
                    key=key,
                    label=label,
                    meal_type=meal_type,
                    reservation_type=reservation_type,
                    start_time=_slot_time(key, "start", weekday_name, start_default),
                    end_time=_slot_time(key, "end", weekday_name, end_default),
                )
            )
        schedule[weekday_index] = tuple(windows)
    return schedule


@dataclass(frozen=True)
class AppSettings:
    project_root: Path
    image_dir: Path
    api_base_url: str
    request_timeout_seconds: float
    auto_refresh_minutes: int
    preload_minutes: int
    bell_interval_seconds: int
    start_fullscreen: bool
    printer_vendor_id: int
    printer_product_id: int
    printer_interface: int
    schedule_by_weekday: dict[int, tuple[ScheduledServiceWindow, ...]]

    @property
    def logo_path(self) -> Path:
        return self.image_dir / "logo-torre-mono-medium.png"

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

    def resolve_active_service(
        self,
        current_moment: datetime | None = None,
    ) -> ScheduledServiceWindow | None:
        now = current_moment or datetime.now()
        for window in self.schedule_by_weekday.get(now.weekday(), ()):
            if window.preload_starts_at(now.date(), self.preload_minutes) <= now <= window.ends_at(now.date()):
                return window
        return None

    def next_service(
        self,
        current_moment: datetime | None = None,
    ) -> tuple[ScheduledServiceWindow, datetime] | None:
        now = current_moment or datetime.now()
        for day_offset in range(0, 8):
            target_date = now.date() + timedelta(days=day_offset)
            for window in self.schedule_by_weekday.get(target_date.weekday(), ()):
                preload_time = window.preload_starts_at(target_date, self.preload_minutes)
                if preload_time > now:
                    return window, preload_time
        return None


def load_settings() -> AppSettings:
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
        bell_interval_seconds=max(15, _get_int("TORRETRAY_BELL_INTERVAL_SECONDS", 60)),
        start_fullscreen=_get_bool("TORRETRAY_START_FULLSCREEN", True),
        printer_vendor_id=_get_int("TORRETRAY_PRINTER_VENDOR_ID", 0x1FC9),
        printer_product_id=_get_int("TORRETRAY_PRINTER_PRODUCT_ID", 0x2016),
        printer_interface=_get_int("TORRETRAY_PRINTER_INTERFACE", 0),
        schedule_by_weekday=_load_schedule(),
    )
