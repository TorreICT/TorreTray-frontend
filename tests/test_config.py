from __future__ import annotations

import unittest
from datetime import date, datetime, time
from pathlib import Path
import shutil

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from torretray_pi.config import (  # noqa: E402
    ScheduledServiceWindow,
    next_service,
    resolve_active_service,
    save_runtime_settings,
)
from torretray_pi.models import MealType, ReservationType  # noqa: E402


def build_window() -> ScheduledServiceWindow:
    return ScheduledServiceWindow(
        date=date(2026, 3, 24),
        key="lunch",
        label="Pranzo 24/03",
        meal_type=MealType.LUNCH,
        reservation_type=ReservationType.TRAY,
        start_time=time(13, 0),
        end_time=time(14, 0),
    )


class ConfigTimingTests(unittest.TestCase):
    def test_loading_and_bell_start_times_are_independent(self) -> None:
        window = build_window()

        self.assertEqual(
            window.loading_starts_at(30),
            datetime(2026, 3, 24, 12, 30),
        )
        self.assertEqual(
            window.bell_starts_at(10),
            datetime(2026, 3, 24, 12, 50),
        )

    def test_active_service_and_next_service_use_loading_time_before_meal(self) -> None:
        window = build_window()

        self.assertIsNone(
            resolve_active_service(
                [window],
                current_moment=datetime(2026, 3, 24, 12, 39),
                loading_time_before_meal=20,
            )
        )
        self.assertIsNotNone(
            resolve_active_service(
                [window],
                current_moment=datetime(2026, 3, 24, 12, 40),
                loading_time_before_meal=20,
            )
        )
        self.assertEqual(
            next_service(
                [window],
                current_moment=datetime(2026, 3, 24, 12, 0),
                loading_time_before_meal=20,
            ),
            (window, datetime(2026, 3, 24, 12, 40)),
        )

    def test_save_runtime_settings_migrates_legacy_preload_key(self) -> None:
        temp_dir = Path(__file__).resolve().parent / "_tmp_config_test"
        try:
            temp_dir.mkdir(exist_ok=True)
            project_root = temp_dir
            env_path = project_root / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "TORRETRAY_PRELOAD_MINUTES=5",
                        "TORRETRAY_AUTO_REFRESH_MINUTES=5",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            save_runtime_settings(
                project_root,
                auto_refresh_minutes=7,
                loading_time_before_meal=25,
                bell_time_before_meal=10,
                schedule_lookahead_days=3,
                bell_interval_seconds=45,
                bell_muted=True,
            )

            contents = env_path.read_text(encoding="utf-8")
            self.assertIn("TORRETRAY_LOADING_TIME_BEFORE_MEAL=25", contents)
            self.assertIn("TORRETRAY_BELL_TIME_BEFORE_MEAL=10", contents)
            self.assertNotIn("TORRETRAY_PRELOAD_MINUTES", contents)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
