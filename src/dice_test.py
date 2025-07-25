import pytest
import lark
from dicetypes import BoolType

from main import grammar, parse_string


@pytest.fixture
def test_parser() -> lark.Lark:
    return lark.Lark(grammar, parser="lalr")


def test_1(test_parser: lark.Lark) -> None:
    text = """let x = flip 0.4 in x"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.4, rel=0.1)

def test_not(test_parser: lark.Lark) -> None:
    text = """let x = flip 0.4 in !x"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.6, rel=0.1)

def test_obs1(test_parser: lark.Lark) -> None:
    text = """let x = flip 0.4 in let y = flip 0.1 in let z = observe x || y in x"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.8695652173913043, rel=0.1)

def test_obs2(test_parser: lark.Lark) -> None:
    text = """let x = flip 0.4 in let y = flip 0.1 in let z = observe x || y in !x"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.13043478260869565, rel=0.1)

def test_tup1(test_parser: lark.Lark) -> None:
    text = """let x = (flip 0.1, flip 0.4) in snd x"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.4, rel=0.1)

def test_nestedtup(test_parser: lark.Lark) -> None:
    text = """let x = (flip 0.1, (flip 0.4, flip 0.7)) in fst (snd x)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.4, rel=0.1)

def test_nestedtup2(test_parser: lark.Lark) -> None:
    text = """let x = (flip 0.1, (flip 0.4, flip 0.7)) in ! fst (snd x)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.6, rel=0.1)

def test_ite1(test_parser: lark.Lark) -> None:
    text = """if flip 0.4 then true else false"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.4, rel=0.1)

def test_ite2(test_parser: lark.Lark) -> None:
    text = """if flip 0.4 then flip 0.6 else false"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.24, rel=0.1)

def test_ite3(test_parser: lark.Lark) -> None:
    text = """if flip 0.4 then let z = observe false in flip 0.6 else false"""
    assert parse_string(text, test_parser)[BoolType(False)] == pytest.approx(1.0, rel=0.1)

def test_int1(test_parser: lark.Lark) -> None:
    text = """let x = discrete(0.1, 0.4, 0.5) in x == int(2, 1)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.4, rel=0.1)

def test_int2(test_parser: lark.Lark) -> None:
    text = """let x = discrete(0.1, 0.4, 0.5) in let z = observe ! (x == int(2, 0)) in x == int(2, 1)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.4444444444444445, rel=0.1)

def test_int3(test_parser: lark.Lark) -> None:
    text = """let x = discrete(0.1, 0.4, 0.5) in let z = observe ! (x == int(2, 0) || x == int(2,1)) in x == int(2, 2)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_int4(test_parser: lark.Lark) -> None:
    text = """let x = discrete(0.1, 0.4, 0.5) in let z = observe ! (x == int(2, 1)) in x == int(2, 2)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.8333333333333334, rel=0.1)

def test_add1(test_parser: lark.Lark) -> None:
    text = """let x = int(3, 0) + int(3, 1) in x == int(3, 1)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_add2(test_parser: lark.Lark) -> None:
    text = """let x = discrete(0.1, 0.4, 0.5) + int(2, 1) in x == int(2, 1)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.1, rel=0.1)

def test_add3(test_parser: lark.Lark) -> None:
    text = """let x = discrete(0.1, 0.4, 0.5) + discrete(1.0, 0.0, 0.0) in x == int(2, 1)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.4, rel=0.1)

def test_add4(test_parser: lark.Lark) -> None:
    text = """let x = discrete(0.25, 0.25, 0.25, 0.25) + discrete(0.25, 0.25, 0.25, 0.25) in x == int(2, 1)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.25, rel=0.1)

def test_add5(test_parser: lark.Lark) -> None:
    text = """
   let x = discrete(0.3, 0.1, 0.2, 0.2, 0.2) in
   let y = discrete(0.1, 0.3, 0.2, 0.2, 0.2) in
   let sum = x + y in
   let z = observe x == int(3, 1) in
   sum == int(3, 1)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.1, rel=0.1)

def test_add6(test_parser: lark.Lark) -> None:
    text = """let x = discrete(0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125)
+ discrete(0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125) in x == int(3, 1)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.125, rel=0.1)

def test_sub1(test_parser: lark.Lark) -> None:
    text = """let x = int(3, 0) - int(3, 1) in x == int(3, 7)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_sub2(test_parser: lark.Lark) -> None:
    text = """let x = discrete(0.1, 0.4, 0.5) - int(2, 1) in x == int(2, 1)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.5, rel=0.1)

def test_sub3(test_parser: lark.Lark) -> None:
    text = """let x = discrete(0.1, 0.4, 0.5) - discrete(0.0, 1.0, 0.0) in x == int(2, 1)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.5, rel=0.1)

def test_sub4(test_parser: lark.Lark) -> None:
    text = """let x = discrete(0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125)
- discrete(0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125) in x == int(3, 1)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.125, rel=0.1)

def test_op1(test_parser: lark.Lark) -> None:
    text = """
   discrete(0.1, 0.2, 0.3, 0.4) < discrete(0.4, 0.3, 0.2, 0.1)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.15, rel=0.1)

def test_op2(test_parser: lark.Lark) -> None:
    text = """
   let x = discrete(0.1, 0.2, 0.3, 0.4) in
   let y = discrete(0.4, 0.3, 0.2, 0.1) in
   x <= y"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.35, rel=0.1)

def test_op3(test_parser: lark.Lark) -> None:
    text = """
   let x = discrete(0.1, 0.2, 0.3, 0.4) in
   let y = discrete(0.4, 0.3, 0.2, 0.1) in
   (x + y) < int(2, 2)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.46, rel=0.1)

def test_op4(test_parser: lark.Lark) -> None:
    text = """
   let x = discrete(0.1, 0.2, 0.3, 0.4) in
   let y = discrete(0.4, 0.3, 0.2, 0.1) in
   let tmp = observe (x + y) < int(2, 2) in
   x == y"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.21739130434782608, rel=0.1)

def test_iff1(test_parser: lark.Lark) -> None:
    text = """true <=> false"""
    assert parse_string(text, test_parser)[BoolType(False)] == pytest.approx(1.0, rel=0.1)

def test_iff2(test_parser: lark.Lark) -> None:
    text = """false <=> false"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_iff3(test_parser: lark.Lark) -> None:
    text = """flip 0.1 <=> flip 0.4"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.58, rel=0.1)

def test_xor1(test_parser: lark.Lark) -> None:
    text = """true ^ false"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_xor2(test_parser: lark.Lark) -> None:
    text = """false ^ false"""
    assert parse_string(text, test_parser)[BoolType(False)] == pytest.approx(1.0, rel=0.1)

def test_xor3(test_parser: lark.Lark) -> None:
    text = """flip 0.1 ^ flip 0.4"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.42, rel=0.1)

def test_mul1(test_parser: lark.Lark) -> None:
    text = """let x = int(3, 0) * int(3, 1) in x == int(3, 0)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_mul2(test_parser: lark.Lark) -> None:
    text = """let x = int(3, 2) * int(3, 2) in x == int(3, 4)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_mul3(test_parser: lark.Lark) -> None:
    text = """let x = int(3, 3) * int(3, 3) in x == int(3, 1)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_mul4(test_parser: lark.Lark) -> None:
    text = """let x = int(4, 3) * int(4, 3) in x == int(4, 9)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_mul5(test_parser: lark.Lark) -> None:
    text = """let x = int(4, 3) * int(4, 3) * int(4, 3) in x == int(4, 11)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_mul6(test_parser: lark.Lark) -> None:
    text = """let x = discrete(0.1, 0.4, 0.5, 0.0) * int(2, 2) in x == int(2, 0)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.6, rel=0.1)

def test_leftshift_1(test_parser: lark.Lark) -> None:
    text = """let x = int(4, 1) in let y = x << 2 in y == int(4, 4)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_leftshift_2(test_parser: lark.Lark) -> None:
    text = """let x = int(4, 1) in let y = x << 5 in y == int(4, 0)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_rightshift_1(test_parser: lark.Lark) -> None:
    text = """let x = int(4, 8) in let y = x >> 2 in y == int(4, 2)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_rightshift_2(test_parser: lark.Lark) -> None:
    text = """let x = int(4, 12) in let y = x >> 1 in y == int(4, 6)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_rightshift_3(test_parser: lark.Lark) -> None:
    text = """let x = int(4, 12) in let y = x >> 5 in y == int(4, 0)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_rightshift_4(test_parser: lark.Lark) -> None:
    text = """let x = int(2, 2) in int(2, 1) == (x >> 1)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_rightshift_5(test_parser: lark.Lark) -> None:
    text = """
let a = int(2,2) in
let _x1 = if ( nth_bit(int(2,1), a)) then true else false in
let _x0 = if ( nth_bit(int(2,0), a)) then _x1 else true in
let b = a in
let _y1 = if ( nth_bit(int(2,1), b)) then true else false in
let _y0 = if ( nth_bit(int(2,1), b >> 1)) then _y1 else true in
_x0 <=> _y0"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_unif_1(test_parser: lark.Lark) -> None:
    text1 = "let u = uniform(4, 0, 10) in u < int(4, 4)"
    text2 = "let d = discrete(0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1) in d < int(4, 4)"
    prob1 = parse_string(text1, test_parser)[BoolType(True)]
    prob2 = parse_string(text2, test_parser)[BoolType(True)]
    assert prob1 == pytest.approx(prob2, rel=0.1)
    assert prob1 == pytest.approx(0.4, rel=0.1)

def test_unif_2(test_parser: lark.Lark) -> None:
    text1 = "let u = uniform(3, 2, 6) in u == int(3, 0)"
    text2 = "let d = discrete(0., 0., 0.25, 0.25, 0.25, 0.25) in d == int(3, 0)"
    prob1 = parse_string(text1, test_parser)[BoolType(False)]
    prob2 = parse_string(text2, test_parser)[BoolType(False)]
    assert prob1 == pytest.approx(prob2, rel=0.1)
    assert prob1 == pytest.approx(1.0, rel=0.1)

def test_unif_3(test_parser: lark.Lark) -> None:
    text1 = "let u = uniform(3, 3, 4) in u == int(3, 3)"
    text2 = "let d = discrete(0., 0., 0., 1., 0.) in d == int(3, 3)"
    prob1 = parse_string(text1, test_parser)[BoolType(True)]
    prob2 = parse_string(text2, test_parser)[BoolType(True)]
    assert prob1 == pytest.approx(prob2, rel=0.1)
    assert prob1 == pytest.approx(1.0, rel=0.1)

def test_unif_4(test_parser: lark.Lark) -> None:
    text = """
    let u = uniform(2, 1, 4) in
    let d = discrete(0., 0.5, 0.25, 0.25) in
    u == d && u < int(2, 3)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.25, rel=0.1)

def test_binom_1(test_parser: lark.Lark) -> None:
    text = """let b = binomial(3, 4, 0.25) in b == int(3, 1)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.421875, rel=0.1)

def test_binom_2(test_parser: lark.Lark) -> None:
    text = """let b = binomial(5, 29, 0.5) in b <= int(5, 14)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.5, rel=0.1)

def test_binom_3(test_parser: lark.Lark) -> None:
    text = """let b = binomial(3, 0, 0.5) in b == int(3, 0)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_binom_4(test_parser: lark.Lark) -> None:
    text = """let b = binomial(3, 1, 0.3) in b == int(3, 1)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.3, rel=0.1)

def test_fcall1(test_parser: lark.Lark) -> None:
    text = """
    fun foo(test: bool) {
      (flip 0.5) && test
    }
    foo(true) && foo(true)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.25, rel=0.1)

def test_fcall2(test_parser: lark.Lark) -> None:
    text = """
    fun foo(test: bool) {
      (flip 0.5) && test
    }
    foo(true) && foo(false)"""
    assert parse_string(text, test_parser)[BoolType(False)] == pytest.approx(1.0, rel=0.1)

def test_fcall3(test_parser: lark.Lark) -> None:
    text = """
    fun foo(test: bool) {
      (flip 0.5) && test
    }
    foo(flip 0.5) && foo(flip 0.5)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.0625, rel=0.1)

def test_fcall4(test_parser: lark.Lark) -> None:
    text = """
    fun foo(test: bool) {
      let tmp = observe test in
      true
    }
    let z = flip 0.5 in
    let tmp = foo(z) in
    z"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_fcall5(test_parser: lark.Lark) -> None:
    text = """
    fun foo(test1: bool, test2: bool) {
      let k = observe test1 || test2 in
      false
    }
    let f1 = flip 0.4 in
    let f2 = flip 0.1 in
    let tmp = foo(f1, f2) in
    f1"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.8695652173913043, rel=0.1)

def test_fcall6(test_parser: lark.Lark) -> None:
    text = """
    fun foo(test1: (bool, bool)) {
      let k = observe (fst test1) || (snd test1) in
      false
    }
    let f1 = flip 0.4 in
    let tmp = foo((f1, flip 0.1)) in f1"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.8695652173913043, rel=0.1)

def test_fcall7(test_parser: lark.Lark) -> None:
    text = """
    fun foo(test1: int(2)) {
      let k = observe !(test1 == int(2, 0)) in
      false
    }
    let f1 = discrete(0.1, 0.4, 0.5) in
    let tmp = foo(f1) in f1 == int(2, 1)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.4444444444444445, rel=0.1)

def test_nthbit1(test_parser: lark.Lark) -> None:
    text = """
    let f1 = discrete(0.1, 0.4, 0.3, 0.2) in
    nth_bit(int(2, 1), f1)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.6, rel=0.1)

def test_nthbit2(test_parser: lark.Lark) -> None:
    text = """
    let f1 = discrete(0.1, 0.4, 0.3, 0.2) in
    nth_bit(int(2, 0), f1)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.5, rel=0.1)

def test_nthbit3(test_parser: lark.Lark) -> None:
    text = """
    let a = int(2, 1) in nth_bit(int(2,1), a)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_nthbit4(test_parser: lark.Lark) -> None:
    text = """
    let a = int(2, 1) in nth_bit(int(2,0), a)"""
    assert parse_string(text, test_parser)[BoolType(False)] == pytest.approx(1.0, rel=0.1)

def test_caesar(test_parser: lark.Lark) -> None:
    text = """
    fun sendchar(key: int(2), observation: int(2)) {
      let gen = discrete(0.5, 0.25, 0.125, 0.125) in
      let enc = key + gen in
      observe observation == enc
    }
    let key = discrete(0.25, 0.25, 0.25, 0.25) in
    let tmp = sendchar(key, int(2, 0)) in
    let tmp = sendchar(key, int(2, 1)) in
    let tmp = sendchar(key, int(2, 2)) in
    let tmp = sendchar(key, int(2, 3)) in
    key == int(2, 0)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.25, rel=0.3)

##### This test case is removed because it uses an "iterate" keyword, but idk
##### what that does :(
# def test_caesar_iterate(test_parser: lark.Lark) -> None:
#     text = """
# fun sendchar(arg: (int(2), int(2))) {
#   let key = fst arg in
#   let observation = snd arg in
#   let gen = discrete(0.5, 0.25, 0.125, 0.125) in    // sample a foolang character
#   let enc = key + gen in                            // encrypt the character
#   let tmp = observe observation == enc in
#   (key, observation + int(2, 1))
# }
# // sample a uniform random key: a=0, b=1, c=2, d=3
# let key = discrete(0.25, 0.25, 0.25, 0.25) in
# // observe the ciphertext cccc
# let tmp = iterate(sendchar, (key, int(2, 2)), 4) in
# key == int(2, 0)
# """
#     assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.25, rel=0.1)

def test_burglary(test_parser: lark.Lark) -> None:
    text = """
    let burglary = flip 0.001 in
    let earthquake = flip 0.002 in
    let alarm = if burglary then if earthquake then flip 0.95 else flip 0.94 else if earthquake then flip 0.29 else flip 0.001 in
    let john = 	if alarm then flip 0.9 else flip 0.05 in
    let mary = 	if alarm then flip 0.7 else flip 0.01 in
    let temp = observe john in
    let temp = observe mary in
    burglary"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.284172, rel=0.3)

def test_alarm(test_parser: lark.Lark) -> None:
    text = """
    let earthquake  = flip 0.0001 in
    let burglary  = flip 0.001 in
    let alarm  = earthquake || burglary in
    let phoneWorking  = if earthquake then flip 0.7 else flip 0.99 in
    let maryWakes  = if alarm then
        (if earthquake then flip 0.8 else flip 0.6)
        else flip 0.2 in
    let called  = (maryWakes && phoneWorking) in
    let tmp = observe called in
    burglary
    """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(2969983.0 / 992160802.0, rel=0.3)

def test_murder(test_parser: lark.Lark) -> None:
    text = """
    fun mystery() {
        let aliceDunnit  = flip 0.3 in
        let withGun = if aliceDunnit then flip 0.03 else flip 0.8 in
        (aliceDunnit, withGun)
    }

    fun gunFoundAtScene(gunFound: bool) {
        let res = mystery() in
        let aliceDunnit = fst res in
        let withGun = snd res in
        let obs = if withGun then gunFound else !gunFound in
        let tmp = observe obs in
        aliceDunnit
    }

    gunFoundAtScene(true)
    """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(9.0 / 569.0, rel=0.3)

def test_evidence1(test_parser: lark.Lark) -> None:
    text = """
    let evidence = flip 0.5 in
    let coin  = flip 0.5 in
    if evidence then
        let tmp = observe coin in evidence
        else evidence
    """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0 / 3.0, rel=0.1)

def test_evidence2(test_parser: lark.Lark) -> None:
    text = """
    let evidence = flip 0.5 in
        if evidence then
            let coin1  = flip 0.5 in
            let tmp = observe coin1 in
            coin1
        else
            flip 0.5
    """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(2.0 / 3.0, rel=0.1)

def test_grass(test_parser: lark.Lark) -> None:
    text = """
    let cloudy  = flip 0.5 in
    let rain  = if cloudy then flip 0.8 else flip 0.2 in
    let sprinkler  = if cloudy then flip 0.1 else flip 0.5 in
    let temp1  = flip 0.7 in
    let wetRoof  = (temp1 && rain) in
    let temp2  = flip 0.9 in
    let temp3  = flip 0.9 in
    let wetGrass  = ((temp2 && rain) || ( temp3 && sprinkler)) in
    let tmp = observe wetGrass in
    rain
    """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(509.0 / 719.0, rel=0.1)

def test_cancer(test_parser: lark.Lark) -> None:
    text = """
    let Pollution = discrete(0.500000,0.400000,0.100000) in
    let Smoker = flip 0.300000 in
    let Cancer =
     if ((Pollution == int(2, 2))) then
      (if (Smoker) then (flip 0.030000) else (flip 0.0010000))
     else (if ((Pollution == int(2, 1))) then
       (if (Smoker) then (flip 0.030000) else (flip 0.0010000))
     else (if (Smoker) then (flip 0.050000) else (flip 0.020000))) in
    let Dyspnoea = if (Cancer) then (flip 0.650000) else (flip 0.300000) in
    let Xray = if (Cancer) then (flip 0.900000) else (flip 0.200000) in
    Xray
    """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(42709.0 / 200000.0, rel=0.1)

def test_caesar_2(test_parser: lark.Lark) -> None:
    text = """
    fun drawChar(key: int(5), observation: int(5)) {
        let drawnChar = discrete(0.08167, 0.01492, 0.02782, 0.04253, 0.04378, 0.02228, 0.02015, 0.06094, 0.06966, 0.0153, 0.0772, 0.04025, 0.02406, 0.06749, 0.07507, 0.01929, 0.00095, 0.05987, 0.06327, 0.09056, 0.02758, 0.00978, 0.02360, 0.00150, 0.01974, 0.00074) in
        let encrypted = key + drawnChar  in
        observe observation == encrypted
    }
    let key1  = discrete(0.038461538,0.038461538,0.038461538,0.038461538,0.038461538,0.038461538,0.038461538,0.038461538,0.038461538,0.038461538,0.038461538,0.038461538,0.038461538,0.038461538,0.038461538,0.038461538,0.038461538,0.038461538,0.038461538,0.038461538,0.038461538,0.038461538,0.038461538,0.038461538,0.038461538,0.038461538) in
    let a = drawChar(key1, int(5, 6)) in
    key1 == int(5, 5)
    """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1113032.0 / 315312455.0, abs=0.1)

### This test is removed because it's just too big
# def test_alarm_2(test_parser: lark.Lark) -> None:
#     text = """
#     ...
#     """
#     assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.281037656, rel=0.1)

### This test is removed because it's just too big
# def test_pmc1(test_parser: lark.Lark) -> None:
#     text = """
#     ...
#     """
#     assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1023.0 / 2048.0, rel=0.1)

### This test is removed because it's just too big
# def test_pmc2(test_parser: lark.Lark) -> None:
#     text = """
#     ...
#     """
#     assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(31.0 / 64.0, rel=0.1)

def test_double_flip(test_parser: lark.Lark) -> None:
    text = """
    let c1 = flip 0.5 in
    let c2 = flip 0.5 in
    c1 && c2
    """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.25, rel=0.1)

def test_typecheck_1(test_parser: lark.Lark) -> None:
    text = """
    let c1 = discrete(0.1, 0.4, 0.5) in
    let c2 = int(2, 1) in
    (c1 == c2) || (c1 != c2)
    """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_mod_sub(test_parser: lark.Lark) -> None:
    text = """
    let c1 = int(3, 0) in
    let c2 = int(3, 1) in
    (c1 - c2) == int(3, 7)"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_coin(test_parser: lark.Lark) -> None:
    text = """let coin1 = if flip 0.5 then int(6, 10) else int(6, 25) in
let coin2 = if flip 0.5 then int(6, 10) else int(6, 25) in
let s1 = if flip(0.8) then coin1 else int(6, 0) in
let s2 = if flip 0.8 then coin2 + s1 else s1 in
let candy = s2 >= int(6, 15) in
let tmp = observe candy in
coin1 == int(6, 10)
"""
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.45, rel=0.1)

def test_recursion(test_parser: lark.Lark) -> None:
    text = """
    fun f() {
        flip 0.5
    }

    fun flip_n(n: int(4)): bool {
        if n == int(4, 0) then true else f() && flip_n(n - int(4, 1))
    }

    flip_n(int(4, 3))
    """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.5 ** 3., rel=0.1)

def test_caesar_recursive(test_parser: lark.Lark) -> None:
    text = """
    fun sendchar(key: int(2), observation: int(2)) {
      let gen = discrete(0.5, 0.25, 0.125, 0.125) in
      let enc = key + gen in
      observe observation == enc
    }
    fun loop(key: int(2), observation: int(2)): bool {
      let tmp = sendchar(key, observation) in
      if observation == int(2, 3)
        then true
        else loop(key, observation + int(2, 1))
    }
    let key = discrete(0.25, 0.25, 0.25, 0.25) in
    let tmp = loop(key, int(2, 0)) in
    key == int(2, 0)
  """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.25, abs=0.1)

def test_factorial(test_parser: lark.Lark) -> None:
    text = """
    fun fac(n: int(7)): int(7) {
      if n == int(7, 0) then int(7, 1) else n * fac(n - int(7, 1))
    }
    fac(int(7, 5)) == int(7, 120)
  """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_fibonacci(test_parser: lark.Lark) -> None:
    text = """
    fun fib(n: int(7)): int(7) {
      if n < int(7, 2) then n else fib(n - int(7, 1)) + fib(n - int(7, 2))
    }
    fib(int(7, 11)) == int(7, 89)
  """
    assert parse_string(text, test_parser, 1000)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_list(test_parser: lark.Lark) -> None:
    text = """
    let xs = [true, false, false] in
    (head xs) && !(head (tail xs)) && !(head (tail (tail xs)))
  """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_length(test_parser: lark.Lark) -> None:
    text = """
    let xs = [true, false, false] in
    (length xs) == int(4, 3)
  """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_empty(test_parser: lark.Lark) -> None:
    text = """
    let xs = [] : list(bool) in
    (length xs) == int(4, 0)
  """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

def test_list_recursion(test_parser: lark.Lark) -> None:
    text = """
    fun index(n: int(2), xs: list(bool)): bool {
      if n == int(2, 0) then
        head xs
      else
        index(n - int(2, 1), tail xs)
    }
    let xs = [true, false, false] in
    !index(int(2, 2), xs) && !index(int(2, 1), xs) && index(int(2, 0), xs)
  """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(1.0, rel=0.1)

### This test is removed because it's just too big
# def test_list_distribution(test_parser: lark.Lark) -> None:
#     text = """
#     ...
#     """
#     assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(..., rel=0.1)

def test_list_ex(test_parser: lark.Lark) -> None:
    text = """
    let xs = [flip 0.2, flip 0.4] in
    let ys = if flip 0.5 then (head xs) :: xs else tail xs in
    head ys
  """
    assert parse_string(text, test_parser)[BoolType(True)] == pytest.approx(0.30000000000000004, rel=0.1)

def test_lte_name(test_parser: lark.Lark) -> None:
    text1 = "uniform(3, 0, 8) <= uniform(3, 0, 8)"
    text2 = "let a = uniform(3, 0, 8) in let b = uniform(3, 0, 8) in a <= b"
    prob1 = parse_string(text1, test_parser)[BoolType(True)]
    prob2 = parse_string(text2, test_parser)[BoolType(True)]
    assert prob1 == pytest.approx(prob2, rel=0.2)

def test_lt_name(test_parser: lark.Lark) -> None:
    text1 = "uniform(3, 0, 8) < uniform(3, 0, 8)"
    text2 = "let a = uniform(3, 0, 8) in let b = uniform(3, 0, 8) in a < b"
    prob1 = parse_string(text1, test_parser)[BoolType(True)]
    prob2 = parse_string(text2, test_parser)[BoolType(True)]
    assert prob1 == pytest.approx(prob2, rel=0.2)

### This test is removed because we don't support bdd_exists
# def test_bdd(test_parser: lark.Lark) -> None:
#     ...
