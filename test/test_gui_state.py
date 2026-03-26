from markpickle.config_class import Config
from markpickle.gui.configstate import ConfigState
from markpickle.gui.docstate import DocumentState


def test_config_state_defaults_and_notifies_listeners() -> None:
    state = ConfigState()
    seen: list[Config] = []

    state.register(seen.append)
    new_config = Config()
    new_config.infer_scalar_types = False
    state.set(new_config)

    assert state.config is new_config
    assert seen == [new_config]


def test_config_state_ignores_listener_exceptions() -> None:
    state = ConfigState()
    seen: list[Config] = []

    def bad_listener(_config: Config) -> None:
        raise RuntimeError("boom")

    state.register(bad_listener)
    state.register(seen.append)
    new_config = Config()
    state.set(new_config)

    assert state.config is new_config
    assert seen == [new_config]


def test_document_state_defaults_and_notifies_listeners() -> None:
    state = DocumentState()
    seen: list[str] = []

    state.register(seen.append)
    state.set("# Title")

    assert state.text == "# Title"
    assert seen == ["# Title"]


def test_document_state_ignores_listener_exceptions() -> None:
    state = DocumentState()
    seen: list[str] = []

    def bad_listener(_text: str) -> None:
        raise RuntimeError("boom")

    state.register(bad_listener)
    state.register(seen.append)
    state.set("hello")

    assert state.text == "hello"
    assert seen == ["hello"]
