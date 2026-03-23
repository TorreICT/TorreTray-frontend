from __future__ import annotations

import time
from datetime import datetime

from torretray_pi.config import AppSettings
from torretray_pi.models import Reservation, ReservationFilters

try:
    from escpos.printer import Usb
except Exception:  # pragma: no cover - depends on runtime printer stack
    Usb = None


class PrinterError(RuntimeError):
    """Raised when a print job cannot be completed."""


class PrinterService:
    """Encapsulate USB ticket printing."""

    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings

    def print_ticket(self, reservation: Reservation, filters: ReservationFilters) -> None:
        if Usb is None:
            raise PrinterError("python-escpos non e disponibile in questo ambiente.")

        try:
            printer = Usb(
                self._settings.printer_vendor_id,
                self._settings.printer_product_id,
                self._settings.printer_interface,
            )
            printer.charcode("USA")
            printer.set(height=2, width=2, align="center")
            printer.image(str(self._settings.logo_path))
            time.sleep(0.1)
            printer.text(f"{filters.reservation_type.ticket_title}\n\n")
            printer.set(height=1, width=1, align="center")
            printer.text(
                f"{filters.meal_type.label} - {filters.date.strftime('%d/%m/%Y')}\n"
            )
            printer.text(f"Stampato alle {datetime.now().strftime('%H:%M')}\n\n")
            printer.set(height=2, width=2, align="center")
            printer.text(f"{reservation.name}\n")
            if reservation.diet_label != "-":
                printer.set(height=1, width=1, align="center")
                printer.text(f"{reservation.diet_label}\n")

            printer.set(height=1, width=1, align="left")
            printer.text("\nPreferenze:\n")
            if reservation.preference_lines:
                for line in reservation.preference_lines:
                    printer.text(f"{line}\n")
            else:
                printer.text("Senza preferenze\n")

            printer.text("\n\n")
            printer.cut()
            close = getattr(printer, "close", None)
            if callable(close):
                close()
        except Exception as exc:  # pragma: no cover - depends on hardware
            raise PrinterError(
                "Impossibile completare la stampa del ticket."
            ) from exc
