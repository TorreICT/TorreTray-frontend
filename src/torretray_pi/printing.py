from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime

from torretray_pi.config import AppSettings
from torretray_pi.models import Reservation, ReservationFilters

try:
    from escpos.printer import Usb
except Exception:  # pragma: no cover - depends on runtime printer stack
    Usb = None


class PrinterError(RuntimeError):
    """Raised when a print job cannot be completed."""


@dataclass(frozen=True)
class TicketPreview:
    title: str
    meal_line: str
    printed_at_line: str
    name: str
    diet_label: str | None
    preference_lines: list[str]


class PrinterService:
    """Encapsulate USB ticket printing."""

    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings

    def build_ticket_preview(
        self,
        reservation: Reservation,
        filters: ReservationFilters,
        *,
        printed_at: datetime | None = None,
    ) -> TicketPreview:
        timestamp = printed_at or self._settings.current_datetime()
        return TicketPreview(
            title=filters.reservation_type.ticket_title,
            meal_line=f"{filters.meal_type.label} - {filters.date.strftime('%d/%m/%Y')}",
            printed_at_line=f"Stampato alle {timestamp.strftime('%H:%M')}",
            name=reservation.name,
            diet_label=reservation.diet_label if reservation.diet_label != "-" else None,
            preference_lines=reservation.preference_lines or ["Senza preferenze"],
        )

    def print_ticket(self, reservation: Reservation, filters: ReservationFilters) -> None:
        if Usb is None:
            raise PrinterError("python-escpos non e disponibile in questo ambiente.")

        try:
            ticket = self.build_ticket_preview(reservation, filters)
            printer = Usb(
                self._settings.printer_vendor_id,
                self._settings.printer_product_id,
                self._settings.printer_interface,
            )
            printer.charcode("USA")
            printer.set(height=2, width=2, align="center")
            printer.image(str(self._settings.logo_path))
            time.sleep(0.1)
            printer.text(f"{ticket.title}\n\n")
            printer.set(height=1, width=1, align="center")
            printer.text(f"{ticket.meal_line}\n")
            printer.text(f"{ticket.printed_at_line}\n\n")
            printer.set(height=2, width=2, align="center")
            printer.text(f"{ticket.name}\n")
            if ticket.diet_label is not None:
                printer.set(height=1, width=1, align="center")
                printer.text(f"{ticket.diet_label}\n")

            printer.set(height=1, width=1, align="left")
            printer.text("\nPreferenze:\n")
            for line in ticket.preference_lines:
                printer.text(f"{line}\n")

            printer.text("\n\n")
            printer.cut()
            close = getattr(printer, "close", None)
            if callable(close):
                close()
        except Exception as exc:  # pragma: no cover - depends on hardware
            raise PrinterError(
                "Impossibile completare la stampa del ticket."
            ) from exc
