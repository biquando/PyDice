import pytest
import lark
from dicetypes import BoolType, IntType

from main import grammar, TreeTransformer, parse_string, parse_string_compile
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


def test_nested_consistent_assign(test_parser: lark.Lark) -> None:
    text = "let x = flip 0.5 in let y = !x in y && !x"
    assert parse_string_compile(text, test_parser)[BoolType(True)] == pytest.approx(
        0.5, rel=0.02
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


def test_logic_precedence(test_parser: lark.Lark) -> None:
    text = "flip 0.5 || flip 0.5 && flip 0.2"
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(
        0.55, rel=0.02
    )


def test_NOT_precedence(test_parser: lark.Lark) -> None:
    text = "!flip 0.1 && flip 0.5 && !(flip 0.5 || flip 0.5 )"
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(
        0.1125, rel=0.02
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
    with pytest.raises(Exception):
        parse_string("int(2, 1) < true", test_parser)
    with pytest.raises(Exception):
        parse_string("int(2, 1) ^ true", test_parser)
    with pytest.raises(Exception):
        parse_string("int(2, 1) <=> true", test_parser)
    with pytest.raises(Exception):
        parse_string("int(3, 1) > int(3,2) > int(3,3)", test_parser)


def test_implies(test_parser: lark.Lark) -> None:
    text = "flip 0.1 -> flip 0.5"
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(
        0.95, rel=0.02
    )


def test_iff(test_parser: lark.Lark) -> None:
    text = "flip 0.25 <=> flip 0.25"
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(
        0.6875, rel=0.1
    )


def test_xor(test_parser: lark.Lark) -> None:
    text = "flip 0.75 ^ flip 0.25"
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(
        0.625, rel=0.1
    )


def test_int_equals(test_parser: lark.Lark) -> None:
    text = "int(3,5) == int(3,5)"
    assert parse_string(text, test_parser)[BoolType(True)] == 1.0


def test_int_not_equals(test_parser: lark.Lark) -> None:
    text = "int(3,5) != int(3,6)"
    assert parse_string(text, test_parser)[BoolType(True)] == 1.0


def test_int_equals_and_bool(test_parser: lark.Lark) -> None:
    text = "(int(3,5) == int(3,5)) && flip 0.5"
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(
        0.5, rel=0.1
    )


def test_int_equals_bool(test_parser: lark.Lark) -> None:
    text = "int(3,5) == flip 0.5"
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


def test_int_precedence(test_parser: lark.Lark) -> None:
    text = "int(10,4) * int(10,2) + int(10,10) / ( int(10,5) - int(10,3) )"
    print(parse_string(text, test_parser))
    assert parse_string(text, test_parser)[IntType(10, 13)] == 1.0


def test_int_bool(test_parser: lark.Lark) -> None:
    text = "if flip 0.5 then int(3,1) else int(10,2)"
    res = parse_string(text, test_parser)
    assert res[IntType(3, 1)] == pytest.approx(0.5, rel=0.1)
    assert res[IntType(10, 2)] == pytest.approx(0.5, rel=0.1)


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


def test_no_arg_function(test_parser: lark.Lark) -> None:
    text = "fun flip_coin(){ flip 0.5 } flip_coin()"
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(
        0.5, rel=0.1
    )


def test_1_arg_function(test_parser: lark.Lark) -> None:
    text = (
        "fun flip_coin( a : bool ){ if a then flip 0.5 else true} flip_coin( flip 0.5 )"
    )
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(
        0.75, rel=0.1
    )


def test_3_arg_function(test_parser: lark.Lark) -> None:
    text = """
    fun flip_coin( a : bool, b : int( 4 ), c : bool ){ 
    if b > int(4,5) then a || c else a && c
    } 
    flip_coin( flip 0.5, int(4,10), flip 0.5 )
    """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(
        0.75, rel=0.1
    )


def test_3_arg_function_dependent(test_parser: lark.Lark) -> None:
    text = """
    fun flip_coin( a : bool, b : bool, c : bool ){ 
    if b then a else c
    } 
    let x = flip 0.5 in flip_coin(x, x, !x)
    """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)


def test_incorrect_function_type_args(test_parser: lark.Lark) -> None:
    with pytest.raises(Exception):
        text = """
        "fun flip_coin( a : bool ){
        if a then flip 0.5 else true
        }
        flip_coin( int(4,10) )
        """
        parse_string(text, test_parser)


def test_incorrect_function_length_args(test_parser: lark.Lark) -> None:
    with pytest.raises(Exception):
        text = """
        "fun flip_coin( a : bool ){
        if a then flip 0.5 else true
        }
        flip_coin( true, false )
        """
        parse_string(text, test_parser)


def test_2_functions(test_parser: lark.Lark) -> None:
    text = """
    fun flip_coin( a : bool ){
    if a then flip 0.5 else true
    }
    fun flip_coin2( a : bool ){
    if !a then flip 0.5 else false
    }
    flip_coin( flip 0.9 ) && flip_coin2( flip 0.1 )
    """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(
        0.2475, rel=0.1
    )


def test_call_in_call(test_parser: lark.Lark) -> None:
    text = """
    fun flip_coin( a : bool ){
    if a then flip 0.5 else true
    }
    fun flip_coin2( a : bool ){
    if !a then flip 0.5 else false
    }
    flip_coin2( flip_coin (flip 0.9))
    """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.225, rel=0.1)


def test_call_in_def(test_parser: lark.Lark) -> None:
    text = """
    fun flip_coin( a : bool ){
    if a then flip 0.5 else flip_coin2 (flip 0.5)
    }
    fun flip_coin2( a : bool ){
    if !a then flip 0.5 else false
    }
    flip_coin2( flip_coin (flip 0.9))
    """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.2625, rel=0.1)


def test_recursive_function(test_parser: lark.Lark) -> None:
    text = """
    fun flip_coin(){
    if flip 0.5 then true else flip_coin()
    }
    flip_coin()
    """
    assert parse_string(text, test_parser)[BoolType(True)] == 1.0


def test_basic_observe(test_parser: lark.Lark) -> None:
    text = """
    let x = flip 0.5 in
    let tmp = observe x in
    x
    """
    assert parse_string(text, test_parser)[BoolType(True)] == 1.0


def test_xy_observe(test_parser: lark.Lark) -> None:
    text = """
    let x = flip 0.2 in
    let y = flip 0.6 in
    let tmp = observe !y in
    x || y
    """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(
        0.2, rel=0.05
    )
    assert parse_string(text, test_parser)[BoolType(False)] == pytest.approx(
        0.8, rel=0.05
    )


def test_comment(test_parser: lark.Lark) -> None:
    text = """
    let x = flip 0.5 in  // This is a comment!
    x
    """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.5, rel=0.05)
    assert parse_string(text, test_parser)[BoolType(False)] == pytest.approx(0.5, rel=0.05)


def test_nthbit1(test_parser: lark.Lark) -> None:
    text = "let f1 = discrete(0.1, 0.4, 0.3, 0.2) in nth_bit(int(2, 1), f1)"
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.6, rel=0.1)


def test_nthbit2(test_parser: lark.Lark) -> None:
    text = "let f1 = discrete(0.1, 0.4, 0.3, 0.2) in nth_bit(int(2, 0), f1)"
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.5, rel=0.1)


def test_nthbit3(test_parser: lark.Lark) -> None:
    text = "let a = int(2, 1) in nth_bit(int(2,1), a)"
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)


def test_nthbit4(test_parser: lark.Lark) -> None:
    text = "let a = int(2, 1) in nth_bit(int(2,0), a)"
    assert parse_string(text, test_parser)[BoolType(False)] == pytest.approx(1.0, rel=0.1)


# this test case is explained in section 3.2.2 of the paper
def test_func_observe(test_parser: lark.Lark) -> None:
    text = """
    fun f( x : bool ){
    let y = x || flip 0.5 in let z = observe y in y
    }
    let x = flip 0.1 in let obs = f(x) in x
    """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.1818, rel=0.05)


def test_flip_compiled(test_parser: lark.Lark) -> None:
    text = "flip 0.33"
    assert parse_string_compile(text, test_parser)[BoolType(True)] == pytest.approx(
        0.33, rel=1e-6
    )


def test_and_compiled(test_parser: lark.Lark) -> None:
    text = "flip 0.33 && flip 0.67"
    assert parse_string_compile(text, test_parser)[BoolType(True)] == pytest.approx(
        0.2211, rel=1e-6
    )


def test_orcompiled(test_parser: lark.Lark) -> None:
    text = "flip 0.33 || flip 0.67"
    assert parse_string_compile(text, test_parser)[BoolType(True)] == pytest.approx(
        0.7789, rel=1e-6
    )


def test_if_compiled(test_parser: lark.Lark) -> None:
    text = "if flip 0.5 then flip 0.4 else flip 0.9"
    assert parse_string_compile(text, test_parser)[BoolType(True)] == pytest.approx(
        0.65, rel=1e-6
    )


def test_basic_assign_compiled(test_parser: lark.Lark) -> None:
    text = """
        let a = flip 0.3 in
        a
    """
    assert parse_string_compile(text, test_parser)[BoolType(True)] == pytest.approx(
        0.3, rel=1e-6
    )


def test_consistent_assign_compiled(test_parser: lark.Lark) -> None:
    text = "let x = flip 0.5 in if x then x else !x"
    assert parse_string_compile(text, test_parser)[BoolType(True)] == pytest.approx(
        1.0, rel=1e-6
    )


def test_nested_assign_compiled(test_parser: lark.Lark) -> None:
    text = "let x = flip 0.5 in let y = flip 0.5 in if x && y then flip 0.8 else flip 0.1"
    assert parse_string_compile(text, test_parser)[BoolType(True)] == pytest.approx(
        0.275, rel=1e-6
    )


def test_nested_consistent_assign_compiled(test_parser: lark.Lark) -> None:
    text = "let x = flip 0.5 in let y = !x in y && !x"
    assert parse_string_compile(text, test_parser)[BoolType(True)] == pytest.approx(
        0.5, rel=1e-6
    )

def test_nested_consistent_assign_advanced_compiled(test_parser: lark.Lark) -> None:
    text = "let x = flip 0.5 in let y = flip 0.3 in let z = y && x in !z && x"
    assert parse_string_compile(text, test_parser)[BoolType(True)] == pytest.approx(
        0.35, rel=1e-6
    )

def test_no_arg_function_compiled(test_parser: lark.Lark) -> None:
    text = "fun flip_coin(){ flip 0.5 } flip_coin()"
    assert parse_string_compile(text, test_parser)[BoolType(True)] == pytest.approx(0.5, rel=1e-6)


def test_1_arg_function_compiled(test_parser: lark.Lark) -> None:
    text = "fun flip_coin( a : bool ){ if a then flip 0.5 else true} flip_coin( flip 0.5 )"
    assert parse_string_compile(text, test_parser)[BoolType(True)] == pytest.approx(0.75, rel=1e-6)


def test_3_arg_function_compiled(test_parser: lark.Lark) -> None:
    text = """
    fun flip_coin( a : bool, b : bool, c : bool ){ 
    if b then a || c else a && c
    } 
    flip_coin( flip 0.5, flip 0.9, flip 0.5 )
    """
    assert parse_string_compile(text, test_parser)[BoolType(True)] == pytest.approx(0.7, rel=1e-6)



def test_3_arg_function_dependent_compiled(test_parser: lark.Lark) -> None:
    text = """
    fun flip_coin( a : bool, b : bool, c : bool ){ 
    if b then a else c
    } 
    let x = flip 0.5 in flip_coin(x, x, !x)
    """
    assert parse_string_compile(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=1e-6)


def test_incorrect_function_length_args_compiled(test_parser: lark.Lark) -> None:
    with pytest.raises(Exception):
        text = """
        "fun flip_coin( a : bool ){
        if a then flip 0.5 else true
        }
        flip_coin( true, false )
        """
        parse_string_compile(text, test_parser)


def test_2_functions_compiled(test_parser: lark.Lark) -> None:
    text = """
    fun flip_coin( a : bool ){
    if a then flip 0.5 else true
    }
    fun flip_coin2( a : bool ){
    if !a then flip 0.5 else false
    }
    flip_coin( flip 0.9 ) && flip_coin2( flip 0.1 )
    """
    assert parse_string_compile(text, test_parser)[BoolType(True)] == pytest.approx(0.2475, rel=1e-6)


def test_call_in_call_compiled(test_parser: lark.Lark) -> None:
    text = """
    fun flip_coin( a : bool ){
    if a then flip 0.5 else true
    }
    fun flip_coin2( a : bool ){
    if !a then flip 0.5 else false
    }
    flip_coin2( flip_coin (flip 0.9))
    """
    assert parse_string_compile(text, test_parser)[BoolType(True)] == pytest.approx(0.225, rel=1e-6)

def test_call_in_def_compiled(test_parser: lark.Lark) -> None:
    text = """
    fun flip_coin( a : bool ){
    if a then flip 0.5 else flip_coin2 (flip 0.5)
    }
    fun flip_coin2( a : bool ){
    if !a then flip 0.5 else false
    }
    flip_coin2( flip_coin (flip 0.9))
    """
    assert parse_string_compile(text, test_parser)[BoolType(True)] == pytest.approx(0.2625, rel=1e-6)


def test_recursive_function_compiled(test_parser: lark.Lark) -> None:
    with pytest.raises(Exception):
        text = """
        fun flip_coin(){
        if flip 0.5 then true else flip_coin()
        }
        flip_coin()
        """
        parse_string_compile(text, test_parser)


def test_mutual_recursion_compiled(test_parser: lark.Lark) -> None:
    with pytest.raises(Exception):
        text = """
        fun flip_coin( a : bool ){
        if a then flip 0.5 else flip_coin2 (flip 0.5)
        }
        fun flip_coin2( a : bool ){
        if !a then flip_coin(flip 0.5) else false
        }
        flip_coin2( flip_coin (flip 0.9))
        """
        parse_string_compile(text, test_parser)


def test_basic_observe_compiled(test_parser: lark.Lark) -> None:
    text = """
    let x = flip 0.5 in
    let tmp = observe x in
    x
    """
    assert parse_string_compile(text, test_parser)[BoolType(True)] == 1.0


def test_xy_observe_compiled(test_parser: lark.Lark) -> None:
    text = """
    let x = flip 0.2 in
    let y = flip 0.6 in
    let tmp = observe !y in
    x || y
    """
    assert parse_string_compile(text, test_parser)[BoolType(True)] == pytest.approx(0.2, rel=0.05)
    assert parse_string_compile(text, test_parser)[BoolType(False)] == pytest.approx(0.8, rel=0.05)


# this test case is explained in section 3.2.2 of the paper
def test_func_observe_compiled(test_parser: lark.Lark) -> None:
    text = """
    fun f( x : bool ){
    let y = x || flip 0.5 in let z = observe y in y
    }
    let x = flip 0.1 in let obs = f(x) in x
    """
    assert parse_string_compile(text, test_parser)[BoolType(True)] == pytest.approx(0.1818, rel=0.05)


def test_tuple(test_parser: lark.Lark) -> None:
    text = "let x = (flip 0.1, flip 0.4) in snd x"
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(
        0.4, rel=1e-2
    )


def test_nested_tuple(test_parser: lark.Lark) -> None:
    text = "let x = (flip 0.1, (flip 0.4, flip 0.7)) in fst (snd x)"
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(
        0.4, rel=1e-2
    )


def test_list_empty(test_parser: lark.Lark) -> None:
    text = """
        let xs = [] : list(bool) in
        (length xs) == int(4, 0)
    """
    assert parse_string(text, test_parser)[BoolType(True)] == 1.0


def test_list_head(test_parser: lark.Lark) -> None:
    text = "let xs = [flip 0.3, flip 0.2, flip 0.8] in head xs"
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(
        0.3, rel=1e-2
    )


def test_list_tail(test_parser: lark.Lark) -> None:
    text = "let xs = [flip 0.3, flip 0.2, flip 0.8] in head (tail (tail xs))"
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(
        0.8, rel=1e-2
    )


def test_list_length(test_parser: lark.Lark) -> None:
    text = "let xs = [flip 0.3, flip 0.2, flip 0.8] in length xs"
    assert parse_string(text, test_parser)[IntType(4, 3)] == 1.0
