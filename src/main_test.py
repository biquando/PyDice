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


@pytest.mark.parametrize(
    "text,expected",
    [
        ("flip(0.33) | flip(0.25)", 0.5),
        (
            """
let a = flip(0.3) in
a
    """,
            0.3,
        ),
        (
            """
let x = flip(0.5) in
let y = x & flip(0.5) in
x & y
""",
            0.25,
        ),
    ],
    ids=["test_basic_or", "test_basic_assign", "test_basic_and"],
)
def test_execution(test_parser: lark.Lark, text: str, expected: float) -> None:
    assert parse_string(text, test_parser) == pytest.approx(expected, rel=0.02)
