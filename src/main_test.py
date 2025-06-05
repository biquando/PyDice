import pytest
import lark
from dicetypes import BoolType, IntType

from main import grammar, TreeTransformer, parse_string
from inference import Inferencer


@pytest.fixture
def test_parser() -> lark.Lark:
    return lark.Lark(grammar, parser="lalr")


def test_always_negative(test_parser: lark.Lark) -> None:
    text = "(true | flip(0.25)) & !xyz"
    tree = test_parser.parse(text)
    new_tree = TreeTransformer().transform(tree)
    inferencer = Inferencer(new_tree, {"xyz": BoolType(True)})
    assert inferencer.infer()[BoolType(False)] == 1.0


def test_basic_assign(test_parser: lark.Lark) -> None:
    text = """
        let a = flip(0.3) in
        a
    """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.3, rel=0.02)


def test_basic_if(test_parser: lark.Lark) -> None:
    text = "let x = if flip(0.5) then flip(0.25) else true in x"
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.625, rel=0.02)


def test_basic_or(test_parser: lark.Lark) -> None:
    text = "flip(0.33) | flip(0.25)"
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.5, rel=0.02)


def test_basic_and(test_parser: lark.Lark) -> None:
    text = """
        let x = flip(0.5) in
        let y = x & flip(0.5) in
        x & y
    """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.25, rel=0.02)


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
        parse_string("int(2, 1) & int(2, 2)", test_parser)
    with pytest.raises(Exception):
        parse_string("int(2, 1) | int(2, 2)", test_parser)
    with pytest.raises(Exception):
        parse_string("!int(2, 1)", test_parser)
    with pytest.raises(Exception):
        parse_string("int(2, 1) < true", test_parser)
    with pytest.raises(Exception):
        parse_string("int(2, 1) ^ true", test_parser)
    with pytest.raises(Exception):
        parse_string("int(2, 1) <-> true", test_parser)

def test_implies(test_parser: lark.Lark) -> None:
    text = "flip(0.1) -> flip(0.5)"
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.95, rel=0.02)

def test_iff(test_parser: lark.Lark) -> None:
    text = "flip(0.25) <-> flip(0.25)"
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.6875, rel=0.1)

def test_xor(test_parser: lark.Lark) -> None:
    text = "flip(0.75) ^ flip(0.25)"
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.625, rel=0.1)

def test_int_equals(test_parser: lark.Lark) -> None:
    text = "int(3,5) == int(3,5)"
    assert parse_string(text, test_parser)[BoolType(True)] == 1.0

def test_int_not_equals(test_parser: lark.Lark) -> None:
    text = "int(3,5) != int(3,6)"
    assert parse_string(text, test_parser)[BoolType(True)] == 1.0

def test_int_equals_and_bool(test_parser: lark.Lark) -> None:
    text = "(int(3,5) == int(3,5)) & flip( 0.5 )"
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.5, rel=0.1)

def test_int_equals_bool(test_parser: lark.Lark) -> None:
    text = "int(3,5) == flip(0.5)"
    assert parse_string(text, test_parser)[BoolType(False)] == 1.0

def test_int_less_than(test_parser: lark.Lark) -> None:
    text = "int(3,5) < int(3,7)"
    text2 = "int(3,7) < int(3,7)"
    text3 = "int(3,7) <= int(3,7)"
    assert parse_string(text, test_parser)[BoolType(True)] == 1.0
    assert parse_string(text2, test_parser)[BoolType(False)] == 1.0
    assert parse_string(text3, test_parser)[BoolType(True)] == 1.0

def test_int_greater_than(test_parser: lark.Lark) -> None:
    text = "int(3,7) > int(3,5)"
    text2 = "int(3,7) > int(3,7)"
    text3 = "int(3,7) >= int(3,7)"
    assert parse_string(text, test_parser)[BoolType(True)] == 1.0
    assert parse_string(text2, test_parser)[BoolType(False)] == 1.0
    assert parse_string(text3, test_parser)[BoolType(True)] == 1.0

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
    assert res[IntType(2, 0)] == pytest.approx(1/6, rel=0.2)
    assert res[IntType(2, 1)] == pytest.approx(1/3, rel=0.2)
    assert res[IntType(2, 2)] == pytest.approx(1/2, rel=0.2)
    assert IntType(2, 3) not in res
