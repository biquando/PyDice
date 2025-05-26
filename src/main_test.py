import pytest
import lark

from main import grammar, TreeTransformer, parse_string
from inference import Inferencer


@pytest.fixture
def test_parser() -> lark.Lark:
    return lark.Lark(grammar, parser="lalr")


def test_always_negative(test_parser: lark.Lark) -> None:
    text = "(true | flip(0.25)) & !xyz"
    tree = test_parser.parse(text)
    new_tree = TreeTransformer().transform(tree)
    inferencer = Inferencer(new_tree, {"xyz": True})
    assert inferencer.infer() == 0.0


def test_basic_assign(test_parser: lark.Lark) -> None:
    text = """
        let a = flip(0.3) in
        a
    """
    assert parse_string(text, test_parser) == pytest.approx(0.3, rel=0.02)


def test_basic_or(test_parser: lark.Lark) -> None:
    text = "flip(0.33) | flip(0.25)"
    assert parse_string(text, test_parser) == pytest.approx(0.5, rel=0.02)


def test_basic_and(test_parser: lark.Lark) -> None:
    text = """
        let x = flip(0.5) in
        let y = x & flip(0.5) in
        x & y
    """
    assert parse_string(text, test_parser) == pytest.approx(0.25, rel=0.02)


def test_basic_if(test_parser: lark.Lark) -> None:
    text = "x = if flip(0.5) then flip(0.25) else true; x"
    assert parse_string(text, test_parser) == pytest.approx(0.625, rel=0.02)
