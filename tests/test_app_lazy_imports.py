from miniflux_tui.config import Config
from miniflux_tui.ui.app import (
    MinifluxTUI,
    _load_entry_list_screen_cls,
    _load_status_screen_cls,
)


def build_config() -> Config:
    return Config(
        server_url="https://example.com",
        api_key="dummy-key",
        allow_invalid_certs=False,
    )


def test_lazy_entry_list_import():
    entry_cls = _load_entry_list_screen_cls()
    assert entry_cls.__name__ == "EntryListScreen"


def test_lazy_status_import():
    status_cls = _load_status_screen_cls()
    assert status_cls.__name__ == "StatusScreen"


def test_app_initializes_without_eager_screens():
    app = MinifluxTUI(config=build_config())
    assert app._entry_list_screen_cls is None  # type: ignore[attr-defined]
    assert app._status_screen_cls is None  # type: ignore[attr-defined]
