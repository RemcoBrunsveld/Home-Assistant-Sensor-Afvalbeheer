"""
Custom collector for manually entered waste collection dates.
"""
import logging
from datetime import datetime

from ..base import WasteCollector
from ...models import WasteCollection

_LOGGER = logging.getLogger(__name__)


class CustomCollector(WasteCollector):
    """
    Collector that uses manually entered dates instead of an API.
    """

    WASTE_TYPE_MAPPING = {}

    def __init__(self, hass, waste_type, dates, custom_mapping):
        # Pass minimal values to base class (no address needed)
        super().__init__(hass, "custom", "", "", "", custom_mapping)
        self.waste_type = waste_type
        self.dates = dates or []

    @property
    def _auth_store_key(self):
        """Custom collector doesn't need auth storage."""
        return f"afvalbeheer.custom_{self.waste_type}"

    async def update(self):
        """Load manually entered dates into the collections repository."""
        self.collections.remove_all()
        waste_type_slug = self.waste_type.lower().replace(" ", "-")

        for date_str in self.dates:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                collection = WasteCollection.create(
                    date=date,
                    waste_type=self.waste_type,
                    waste_type_slug=waste_type_slug,
                )
                self.collections.add(collection)
            except (ValueError, TypeError) as e:
                _LOGGER.warning("Invalid date '%s' for custom collector: %s", date_str, e)
