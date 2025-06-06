import pytest
import lark
from dicetypes import BoolType, IntType

from main import grammar, TreeTransformer, parse_string
from inference import Inferencer


@pytest.fixture
def test_parser() -> lark.Lark:
    return lark.Lark(grammar, parser="lalr")


def test_always_negative(test_parser: lark.Lark) -> None:
    text = "(true || flip 0.25 ) && !xyz"
    tree = test_parser.parse(text)
    new_tree = TreeTransformer().transform(tree)
    inferencer = Inferencer(new_tree, {"xyz": BoolType(True)})
    assert inferencer.infer()[BoolType(False)] == 1.0


def test_basic_assign(test_parser: lark.Lark) -> None:
    text = """
        let a = flip 0.3 in
        a
    """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(
        0.3, rel=0.02
    )


def test_basic_if(test_parser: lark.Lark) -> None:
    text = "let x = if flip 0.5 then flip 0.25 else true in x"
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(
        0.625, rel=0.02
    )


def test_basic_or(test_parser: lark.Lark) -> None:
    text = "flip 0.33 || flip 0.25"
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(
        0.5, rel=0.02
    )


def test_basic_and(test_parser: lark.Lark) -> None:
    text = """
        let x = flip 0.5 in
        let y = x && flip 0.5 in
        x && y
    """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(
        0.25, rel=0.02
    )


def test_type_check(test_parser: lark.Lark) -> None:
    with pytest.raises(Exception):
        parse_string("true + false", test_parser)
    with pytest.raises(Exception):
        parse_string("true - false", test_parser)
    with pytest.raises(Exception):
        parse_string("true * false", test_parser)
    with pytest.raises(Exception):
        parse_string("true / false", test_parser)
    with pytest.raises(Exception):
        parse_string("int(2, 1) && int(2, 2)", test_parser)
    with pytest.raises(Exception):
        parse_string("int(2, 1) || int(2, 2)", test_parser)
    with pytest.raises(Exception):
        parse_string("!int(2, 1)", test_parser)


def test_int_add(test_parser: lark.Lark) -> None:
    text = "int(3, 5) + int(3, 6)"
    assert parse_string(text, test_parser)[IntType(3, 3)] == 1.0


def test_int_sub(test_parser: lark.Lark) -> None:
    text = "int(3, 5) - int(3, 6)"
    assert parse_string(text, test_parser)[IntType(3, 7)] == 1.0


def test_int_mul(test_parser: lark.Lark) -> None:
    text = "int(3, 5) * int(3, 6)"
    assert parse_string(text, test_parser)[IntType(3, 6)] == 1.0


def test_int_div(test_parser: lark.Lark) -> None:
    text = "int(3, 7) / int(3, 2)"
    assert parse_string(text, test_parser)[IntType(3, 3)] == 1.0


def test_basic_discrete(test_parser: lark.Lark) -> None:
    text = "discrete(0.1, 0.2, 0.3)"
    res = parse_string(text, test_parser)
    assert res[IntType(2, 0)] == pytest.approx(1 / 6, rel=0.2)
    assert res[IntType(2, 1)] == pytest.approx(1 / 3, rel=0.2)
    assert res[IntType(2, 2)] == pytest.approx(1 / 2, rel=0.2)
    assert IntType(2, 3) not in res


def test_basic_uniform(test_parser: lark.Lark) -> None:
    text = "uniform(3, 1, 5)"
    res = parse_string(text, test_parser)
    assert IntType(3, 0) not in res
    assert res[IntType(3, 1)] == pytest.approx(1 / 4, rel=0.2)
    assert res[IntType(3, 2)] == pytest.approx(1 / 4, rel=0.2)
    assert res[IntType(3, 3)] == pytest.approx(1 / 4, rel=0.2)
    assert res[IntType(3, 4)] == pytest.approx(1 / 4, rel=0.2)
    assert IntType(3, 5) not in res
    assert IntType(3, 6) not in res
    assert IntType(3, 7) not in res
