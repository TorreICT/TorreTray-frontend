from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from PyQt5 import QtCore, QtWidgets

try:
    from PyQt5 import QtMultimedia
except ImportError:  # pragma: no cover - optional at runtime
    QtMultimedia = None

if sys.platform.startswith("win"):
    import winsound
else:  # pragma: no cover - platform-specific
    winsound = None


class BellPlayer(QtCore.QObject):
    """Play the bell sound with the best available backend."""

    def __init__(self, *, sound_path: Path, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._sound_path = sound_path
        self._sound_effect = None

        if QtMultimedia is not None:
            effect = QtMultimedia.QSoundEffect(self)
            effect.setSource(QtCore.QUrl.fromLocalFile(str(sound_path)))
            effect.setVolume(0.9)
            self._sound_effect = effect

    def ring(self) -> None:
        if self._sound_effect is not None:
            self._sound_effect.play()
            return

        if winsound is not None:
            winsound.PlaySound(
                str(self._sound_path),
                winsound.SND_ASYNC | winsound.SND_FILENAME,
            )
            return

        for player in ("aplay", "paplay", "ffplay"):
            executable = shutil.which(player)
            if executable is None:
                continue
            command = [executable, str(self._sound_path)]
            if player == "ffplay":
                command = [
                    executable,
                    "-nodisp",
                    "-autoexit",
                    "-loglevel",
                    "quiet",
                    str(self._sound_path),
                ]
            subprocess.Popen(  # noqa: S603
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return

        QtWidgets.QApplication.beep()
