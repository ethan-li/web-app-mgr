from dataclasses import dataclass, field
from typing import Dict, List, Optional, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from .base_app import BaseApp


@dataclass
class AppMetadata:
    """Metadata for a registered application type."""
    type_name: str          # e.g. "image_processor"
    display_name: str       # e.g. "Image Processor"
    description: str        # Short description shown in the grid tile
    icon: str               # FontAwesome icon class, e.g. "fas fa-image"
    color_from: str         # CSS gradient start color
    color_to: str           # CSS gradient end color
    enabled: bool = True

    def to_dict(self) -> Dict:
        return {
            "type_name": self.type_name,
            "display_name": self.display_name,
            "description": self.description,
            "icon": self.icon,
            "color_from": self.color_from,
            "color_to": self.color_to,
            "enabled": self.enabled,
        }


class AppRegistry:
    """
    Static application catalog: holds metadata for all registered app types.
    Decoupled from the dynamic AppManager (which manages runtime instances).
    """

    def __init__(self):
        self._registry: Dict[str, AppMetadata] = {}

    def register(self, metadata: AppMetadata) -> None:
        """Register an app type with its metadata."""
        self._registry[metadata.type_name] = metadata

    def get_metadata(self, type_name: str) -> Optional[AppMetadata]:
        """Return metadata for a given type name, or None if not found."""
        return self._registry.get(type_name)

    def get_enabled_apps(self) -> List[AppMetadata]:
        """Return a list of all enabled app metadata entries, sorted by display_name."""
        return sorted(
            [m for m in self._registry.values() if m.enabled],
            key=lambda m: m.display_name,
        )

    def get_all_metadata(self) -> Dict[str, AppMetadata]:
        """Return a copy of the full registry dict."""
        return self._registry.copy()

    def to_dict_list(self) -> List[Dict]:
        """Serialize enabled apps to a list of dicts (for JSON API responses)."""
        return [m.to_dict() for m in self.get_enabled_apps()]

