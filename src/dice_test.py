import pytest
import lark

from main import grammar, TreeTransformer, parse_string


@pytest.fixture
def test_parser() -> lark.Lark:
    return lark.Lark(grammar, parser="lalr")


def assert_feq(expected, actual, tolerance=1e-6):
    """Assert that two floating point numbers are approximately equal."""
    assert abs(expected - actual) < tolerance, f"Expected {expected}, got {actual}"


def parse_and_prob(prog, test_parser):
    """Parse and compute probability using the test parser."""
    return parse_string(prog, test_parser)


def parse_optimize_and_prob(prog, test_parser):
    """Parse, optimize and compute probability using the test parser."""
    # Assuming optimization is handled by the same function for now
    return parse_string(prog, test_parser)


class TestDiceExpressions:
    def test_1(self, test_parser):
        prog = "let x = flip 0.4 in x"
        assert_feq(0.4, parse_and_prob(prog, test_parser))
        assert_feq(0.4, parse_optimize_and_prob(prog, test_parser))

    def test_not(self, test_parser):
        prog = "let x = flip 0.4 in !x"
        assert_feq(0.6, parse_and_prob(prog, test_parser))
        assert_feq(0.6, parse_optimize_and_prob(prog, test_parser))

    def test_obs1(self, test_parser):
        prog = "let x = flip 0.4 in let y = flip 0.1 in let z = observe x || y in x"
        assert_feq(0.4 / 0.46, parse_and_prob(prog, test_parser))
        assert_feq(0.4 / 0.46, parse_optimize_and_prob(prog, test_parser))

    def test_obs2(self, test_parser):
        prog = "let x = flip 0.4 in let y = flip 0.1 in let z = observe x || y in !x"
        assert_feq(0.06 / 0.46, parse_and_prob(prog, test_parser))
        assert_feq(0.06 / 0.46, parse_optimize_and_prob(prog, test_parser))

    def test_tup1(self, test_parser):
        prog = "let x = (flip 0.1, flip 0.4) in snd x"
        assert_feq(0.4, parse_and_prob(prog, test_parser))
        assert_feq(0.4, parse_optimize_and_prob(prog, test_parser))

    def test_nestedtup(self, test_parser):
        prog = "let x = (flip 0.1, (flip 0.4, flip 0.7)) in fst (snd x)"
        assert_feq(0.4, parse_and_prob(prog, test_parser))
        assert_feq(0.4, parse_optimize_and_prob(prog, test_parser))

    def test_nestedtup2(self, test_parser):
        prog = "let x = (flip 0.1, (flip 0.4, flip 0.7)) in ! fst (snd x)"
        assert_feq(0.6, parse_and_prob(prog, test_parser))
        assert_feq(0.6, parse_optimize_and_prob(prog, test_parser))

    def test_ite1(self, test_parser):
        prog = "if flip 0.4 then true else false"
        assert_feq(0.4, parse_and_prob(prog, test_parser))
        assert_feq(0.4, parse_optimize_and_prob(prog, test_parser))

    def test_ite2(self, test_parser):
        prog = "if flip 0.4 then flip 0.6 else false"
        assert_feq(0.24, parse_and_prob(prog, test_parser))
        assert_feq(0.24, parse_optimize_and_prob(prog, test_parser))

    def test_ite3(self, test_parser):
        prog = "if flip 0.4 then let z = observe false in flip 0.6 else false"
        assert_feq(0.0, parse_and_prob(prog, test_parser))
        assert_feq(0.0, parse_optimize_and_prob(prog, test_parser))

    def test_int1(self, test_parser):
        prog = "let x = discrete(0.1, 0.4, 0.5) in x == int(2, 1)"
        assert_feq(0.4, parse_and_prob(prog, test_parser))
        assert_feq(0.4, parse_optimize_and_prob(prog, test_parser))

    def test_int2(self, test_parser):
        prog = "let x = discrete(0.1, 0.4, 0.5) in let z = observe ! (x == int(2, 0)) in x == int(2, 1)"
        assert_feq(0.4 / 0.9, parse_and_prob(prog, test_parser))
        assert_feq(0.4 / 0.9, parse_optimize_and_prob(prog, test_parser))

    def test_int3(self, test_parser):
        prog = "let x = discrete(0.1, 0.4, 0.5) in let z = observe ! (x == int(2, 0) || x == int(2,1)) in x == int(2, 2)"
        assert_feq(1.0, parse_and_prob(prog, test_parser))
        assert_feq(1.0, parse_optimize_and_prob(prog, test_parser))

    def test_int4(self, test_parser):
        prog = "let x = discrete(0.1, 0.4, 0.5) in let z = observe ! (x == int(2, 1)) in x == int(2, 2)"
        assert_feq(0.5 / 0.6, parse_and_prob(prog, test_parser))
        assert_feq(0.5 / 0.6, parse_optimize_and_prob(prog, test_parser))

    def test_add1(self, test_parser):
        prog = "let x = int(3, 0) + int(3, 1) in x == int(3, 1)"
        assert_feq(1.0, parse_and_prob(prog, test_parser))
        assert_feq(1.0, parse_optimize_and_prob(prog, test_parser))

    def test_add2(self, test_parser):
        prog = "let x = discrete(0.1, 0.4, 0.5) + int(2, 1) in x == int(2, 1)"
        assert_feq(0.1, parse_and_prob(prog, test_parser))
        assert_feq(0.1, parse_optimize_and_prob(prog, test_parser))

    def test_add3(self, test_parser):
        prog = "let x = discrete(0.1, 0.4, 0.5) + discrete(1.0, 0.0, 0.0) in x == int(2, 1)"
        assert_feq(0.4, parse_and_prob(prog, test_parser))
        assert_feq(0.4, parse_optimize_and_prob(prog, test_parser))

    def test_add4(self, test_parser):
        prog = "let x = discrete(0.25, 0.25, 0.25, 0.25) + discrete(0.25, 0.25, 0.25, 0.25) in x == int(2, 1)"
        assert_feq(0.25, parse_and_prob(prog, test_parser))
        assert_feq(0.25, parse_optimize_and_prob(prog, test_parser))

    def test_add5(self, test_parser):
        prog = """
        let x = discrete(0.3, 0.1, 0.2, 0.2, 0.2) in
        let y = discrete(0.1, 0.3, 0.2, 0.2, 0.2) in
        let sum = x + y in
        let z = observe x == int(3, 1) in
        sum == int(3, 1)"""
        assert_feq(0.1, parse_and_prob(prog, test_parser))
        assert_feq(0.1, parse_optimize_and_prob(prog, test_parser))

    def test_add6(self, test_parser):
        prog = """let x = discrete(0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125)
+ discrete(0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125) in x == int(3, 1)"""
        assert_feq(0.125, parse_and_prob(prog, test_parser))
        assert_feq(0.125, parse_optimize_and_prob(prog, test_parser))

    def test_sub1(self, test_parser):
        prog = "let x = int(3, 0) - int(3, 1) in x == int(3, 7)"
        assert_feq(1.0, parse_and_prob(prog, test_parser))
        assert_feq(1.0, parse_optimize_and_prob(prog, test_parser))

    def test_sub2(self, test_parser):
        prog = "let x = discrete(0.1, 0.4, 0.5) - int(2, 1) in x == int(2, 1)"
        assert_feq(0.5, parse_and_prob(prog, test_parser))
        assert_feq(0.5, parse_optimize_and_prob(prog, test_parser))

    def test_sub3(self, test_parser):
        prog = "let x = discrete(0.1, 0.4, 0.5) - discrete(0.0, 1.0, 0.0) in x == int(2, 1)"
        assert_feq(0.5, parse_and_prob(prog, test_parser))
        assert_feq(0.5, parse_optimize_and_prob(prog, test_parser))

    def test_sub4(self, test_parser):
        prog = """let x = discrete(0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125)
- discrete(0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125) in x == int(3, 1)"""
        assert_feq(0.125, parse_and_prob(prog, test_parser))
        assert_feq(0.125, parse_optimize_and_prob(prog, test_parser))

    def test_op1(self, test_parser):
        prog = """discrete(0.1, 0.2, 0.3, 0.4) < discrete(0.4, 0.3, 0.2, 0.1)"""
        assert_feq(3.0 / 20.0, parse_and_prob(prog, test_parser))
        assert_feq(3.0 / 20.0, parse_optimize_and_prob(prog, test_parser))

    def test_op2(self, test_parser):
        prog = """
        let x = discrete(0.1, 0.2, 0.3, 0.4) in
        let y = discrete(0.4, 0.3, 0.2, 0.1) in
        x <= y"""
        assert_feq(7.0 / 20.0, parse_and_prob(prog, test_parser))
        assert_feq(7.0 / 20.0, parse_optimize_and_prob(prog, test_parser))

    def test_op3(self, test_parser):
        prog = """
        let x = discrete(0.1, 0.2, 0.3, 0.4) in
        let y = discrete(0.4, 0.3, 0.2, 0.1) in
        (x + y) < int(2, 2)"""
        assert_feq(23.0 / 50.0, parse_and_prob(prog, test_parser))
        assert_feq(23.0 / 50.0, parse_optimize_and_prob(prog, test_parser))

    def test_op4(self, test_parser):
        prog = """
        let x = discrete(0.1, 0.2, 0.3, 0.4) in
        let y = discrete(0.4, 0.3, 0.2, 0.1) in
        let tmp = observe (x + y) < int(2, 2) in
        x == y"""
        assert_feq(5.0 / 23.0, parse_and_prob(prog, test_parser))
        assert_feq(5.0 / 23.0, parse_optimize_and_prob(prog, test_parser))

    def test_iff1(self, test_parser):
        prog = "true <=> false"
        assert_feq(0.0, parse_and_prob(prog, test_parser))

    def test_iff2(self, test_parser):
        prog = "false <=> false"
        assert_feq(1.0, parse_and_prob(prog, test_parser))

    def test_iff3(self, test_parser):
        prog = "flip 0.1 <=> flip 0.4"
        assert_feq(0.58, parse_and_prob(prog, test_parser))

    def test_xor1(self, test_parser):
        prog = "true ^ false"
        assert_feq(1.0, parse_and_prob(prog, test_parser))

    def test_xor2(self, test_parser):
        prog = "false ^ false"
        assert_feq(0.0, parse_and_prob(prog, test_parser))

    def test_xor3(self, test_parser):
        prog = "flip 0.1 ^ flip 0.4"
        assert_feq(0.42, parse_and_prob(prog, test_parser))

    def test_mul1(self, test_parser):
        prog = "let x = int(3, 0) * int(3, 1) in x == int(3, 0)"
        assert_feq(1.0, parse_and_prob(prog, test_parser))
        assert_feq(1.0, parse_optimize_and_prob(prog, test_parser))

    def test_mul2(self, test_parser):
        prog = "let x = int(3, 2) * int(3, 2) in x == int(3, 4)"
        assert_feq(1.0, parse_and_prob(prog, test_parser))
        assert_feq(1.0, parse_optimize_and_prob(prog, test_parser))

    def test_mul3(self, test_parser):
        prog = "let x = int(3, 3) * int(3, 3) in x == int(3, 1)"
        assert_feq(1.0, parse_and_prob(prog, test_parser))
        assert_feq(1.0, parse_optimize_and_prob(prog, test_parser))

    def test_mul4(self, test_parser):
        prog = "let x = int(4, 3) * int(4, 3) in x == int(4, 9)"
        assert_feq(1.0, parse_and_prob(prog, test_parser))
        assert_feq(1.0, parse_optimize_and_prob(prog, test_parser))

    def test_mul5(self, test_parser):
        prog = "let x = int(4, 3) * int(4, 3) * int(4, 3) in x == int(4, 11)"
        assert_feq(1.0, parse_and_prob(prog, test_parser))
        assert_feq(1.0, parse_optimize_and_prob(prog, test_parser))

    def test_mul6(self, test_parser):
        prog = "let x = discrete(0.1, 0.4, 0.5, 0.0) * int(2, 2) in x == int(2, 0)"
        assert_feq(0.6, parse_and_prob(prog, test_parser))
        assert_feq(0.6, parse_optimize_and_prob(prog, test_parser))

    def test_leftshift_1(self, test_parser):
        prog = "let x = int(4, 1) in let y = x << 2 in y == int(4, 4)"
        assert_feq(1.0, parse_and_prob(prog, test_parser))

    def test_leftshift_2(self, test_parser):
        prog = "let x = int(4, 1) in let y = x << 5 in y == int(4, 0)"
        assert_feq(1.0, parse_and_prob(prog, test_parser))

    def test_rightshift_1(self, test_parser):
        prog = "let x = int(4, 8) in let y = x >> 2 in y == int(4, 2)"
        assert_feq(1.0, parse_and_prob(prog, test_parser))

    def test_rightshift_2(self, test_parser):
        prog = "let x = int(4, 12) in let y = x >> 1 in y == int(4, 6)"
        assert_feq(1.0, parse_and_prob(prog, test_parser))

    def test_rightshift_3(self, test_parser):
        prog = "let x = int(4, 12) in let y = x >> 5 in y == int(4, 0)"
        assert_feq(1.0, parse_and_prob(prog, test_parser))

    def test_rightshift_4(self, test_parser):
        prog = "let x = int(2, 2) in int(2, 1) == (x >> 1)"
        assert_feq(1.0, parse_and_prob(prog, test_parser))

    def test_rightshift_5(self, test_parser):
        prog = """
let a = int(2,2) in
let _x1 = if ( nth_bit(int(2,1), a)) then true else false in
let _x0 = if ( nth_bit(int(2,0), a)) then _x1 else true in
let b = a in
let _y1 = if ( nth_bit(int(2,1), b)) then true else false in
let _y0 = if ( nth_bit(int(2,1), b >> 1)) then _y1 else true in
_x0 <=> _y0"""
        assert_feq(1.0, parse_and_prob(prog, test_parser))

    def test_unif_1(self, test_parser):
        prog1 = "let u = uniform(4, 0, 10) in u < int(4, 4)"
        prog2 = "let d = discrete(0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1) in d < int(4, 4)"
        assert_feq(
            parse_and_prob(prog1, test_parser), parse_and_prob(prog2, test_parser)
        )
        assert_feq(0.4, parse_and_prob(prog1, test_parser))

    def test_unif_2(self, test_parser):
        prog1 = "let u = uniform(3, 2, 6) in u == int(3, 0)"
        prog2 = "let d = discrete(0., 0., 0.25, 0.25, 0.25, 0.25) in d == int(3, 0)"
        assert_feq(
            parse_and_prob(prog1, test_parser), parse_and_prob(prog2, test_parser)
        )
        assert_feq(0.0, parse_and_prob(prog1, test_parser))

    def test_unif_3(self, test_parser):
        prog1 = "let u = uniform(3, 3, 4) in u == int(3, 3)"
        prog2 = "let d = discrete(0., 0., 0., 1., 0.) in d == int(3, 3)"
        assert_feq(
            parse_and_prob(prog1, test_parser), parse_and_prob(prog2, test_parser)
        )
        assert_feq(1.0, parse_and_prob(prog1, test_parser))

    def test_unif_4(self, test_parser):
        prog = """
        let u = uniform(2, 1, 4) in
        let d = discrete(0., 0.5, 0.25, 0.25) in
        u == d && u < int(2, 3)"""
        assert_feq(0.25, parse_and_prob(prog, test_parser))

    def test_binom_1(self, test_parser):
        prog = "let b = binomial(3, 4, 0.25) in b == int(3, 1)"
        assert_feq(0.421875, parse_and_prob(prog, test_parser))

    def test_binom_2(self, test_parser):
        prog = "let b = binomial(5, 29, 0.5) in b <= int(5, 14)"
        assert_feq(0.5, parse_and_prob(prog, test_parser))

    def test_binom_3(self, test_parser):
        prog = "let b = binomial(3, 0, 0.5) in b == int(3, 0)"
        assert_feq(1.0, parse_and_prob(prog, test_parser))

    def test_binom_4(self, test_parser):
        prog = "let b = binomial(3, 1, 0.3) in b == int(3, 1)"
        assert_feq(0.3, parse_and_prob(prog, test_parser))

    def test_fcall1(self, test_parser):
        prog = """
        fun foo(test: bool) {
          (flip 0.5) && test
        }
        foo(true) && foo(true)"""
        assert_feq(0.25, parse_and_prob(prog, test_parser))
        assert_feq(0.25, parse_optimize_and_prob(prog, test_parser))

    def test_fcall2(self, test_parser):
        prog = """
        fun foo(test: bool) {
          (flip 0.5) && test
        }
        foo(true) && foo(false)"""
        assert_feq(0.0, parse_and_prob(prog, test_parser))
        assert_feq(0.0, parse_optimize_and_prob(prog, test_parser))

    def test_fcall3(self, test_parser):
        prog = """
        fun foo(test: bool) {
          (flip 0.5) && test
        }
        foo(flip 0.5) && foo(flip 0.5)"""
        assert_feq(0.06250, parse_and_prob(prog, test_parser))
        assert_feq(0.06250, parse_optimize_and_prob(prog, test_parser))

    def test_fcall4(self, test_parser):
        prog = """
        fun foo(test: bool) {
          let tmp = observe test in
          true
        }
        let z = flip 0.5 in
        let tmp = foo(z) in
        z"""
        assert_feq(1.0, parse_and_prob(prog, test_parser))
        assert_feq(1.0, parse_optimize_and_prob(prog, test_parser))

    def test_fcall5(self, test_parser):
        prog = """
        fun foo(test1: bool, test2: bool) {
          let k = observe test1 || test2 in
          false
        }
        let f1 = flip 0.4 in
        let f2 = flip 0.1 in
        let tmp = foo(f1, f2) in
        f1"""
        assert_feq(0.4 / 0.46, parse_and_prob(prog, test_parser))
        assert_feq(0.4 / 0.46, parse_optimize_and_prob(prog, test_parser))

    def test_fcall6(self, test_parser):
        prog = """
        fun foo(test1: (bool, bool)) {
          let k = observe (fst test1) || (snd test1) in
          false
        }
        let f1 = flip 0.4 in
        let tmp = foo((f1, flip 0.1)) in f1"""
        assert_feq(0.4 / 0.46, parse_and_prob(prog, test_parser))
        assert_feq(0.4 / 0.46, parse_optimize_and_prob(prog, test_parser))

    def test_fcall7(self, test_parser):
        prog = """
        fun foo(test1: int(2)) {
          let k = observe !(test1 == int(2, 0)) in
          false
        }
        let f1 = discrete(0.1, 0.4, 0.5) in
        let tmp = foo(f1) in f1 == int(2, 1)"""
        assert_feq(0.4 / 0.9, parse_and_prob(prog, test_parser))
        assert_feq(0.4 / 0.9, parse_optimize_and_prob(prog, test_parser))

    def test_nthbit1(self, test_parser):
        prog = """
        let f1 = discrete(0.1, 0.4, 0.3, 0.2) in
        nth_bit(int(2, 1), f1)"""
        assert_feq(0.6, parse_and_prob(prog, test_parser))

    def test_nthbit2(self, test_parser):
        prog = """
        let f1 = discrete(0.1, 0.4, 0.3, 0.2) in
        nth_bit(int(2, 0), f1)"""
        assert_feq(0.5, parse_and_prob(prog, test_parser))

    def test_nthbit3(self, test_parser):
        prog = """
        let a = int(2, 1) in nth_bit(int(2,1), a)"""
        assert_feq(1.0, parse_and_prob(prog, test_parser))

    def test_nthbit4(self, test_parser):
        prog = """
        let a = int(2, 1) in nth_bit(int(2,0), a)"""
        assert_feq(0.0, parse_and_prob(prog, test_parser))

    def test_caesar(self, test_parser):
        prog = """
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
        assert_feq(0.25, parse_and_prob(prog, test_parser))
        assert_feq(0.25, parse_optimize_and_prob(prog, test_parser))

    def test_caesar_iterate(self, test_parser):
        prog = """
fun sendchar(arg: (int(2), int(2))) {
  let key = fst arg in
  let observation = snd arg in
  let gen = discrete(0.5, 0.25, 0.125, 0.125) in    // sample a foolang character
  let enc = key + gen in                            // encrypt the character
  let tmp = observe observation == enc in
  (key, observation + int(2, 1))
}
// sample a uniform random key: a=0, b=1, c=2, d=3
let key = discrete(0.25, 0.25, 0.25, 0.25) in
// observe the ciphertext cccc
let tmp = iterate(sendchar, (key, int(2, 2)), 4) in
key == int(2, 0)
"""
        assert_feq(0.25, parse_and_prob(prog, test_parser))
        assert_feq(0.25, parse_optimize_and_prob(prog, test_parser))

    def test_burglary(self, test_parser):
        prog = """
        let burglary = flip 0.001 in
        let earthquake = flip 0.002 in
        let alarm = if burglary then if earthquake then flip 0.95 else flip 0.94 else if earthquake then flip 0.29 else flip 0.001 in
        let john = 	if alarm then flip 0.9 else flip 0.05 in
        let mary = 	if alarm then flip 0.7 else flip 0.01 in
        let temp = observe john in
        let temp = observe mary in
        burglary"""
        assert_feq(0.284172, parse_and_prob(prog, test_parser))
        assert_feq(0.284172, parse_optimize_and_prob(prog, test_parser))

    def test_double_flip(self, test_parser):
        prog = """
        let c1 = flip 0.5 in
        let c2 = flip 0.5 in
        c1 && c2
        """
        assert_feq(0.25, parse_and_prob(prog, test_parser))
        assert_feq(0.25, parse_optimize_and_prob(prog, test_parser))

    def test_typecheck_1(self, test_parser):
        prog = """
        let c1 = discrete(0.1, 0.4, 0.5) in
        let c2 = int(2, 1) in
        (c1 == c2) || (c1 != c2)
        """
        assert_feq(1.0, parse_and_prob(prog, test_parser))
        assert_feq(1.0, parse_optimize_and_prob(prog, test_parser))

    # def test_mod_sub(self, test_parser):
    #     prog = """
    #     let c1 = int(3, 0) in
    #     let c2 = int(3, 1) in
    #     (c1 - c2) == int(3, 2)"""
    #     assert_feq(1.0, parse_and_prob(prog, test_parser))
    #     assert_feq(1.0, parse_optimize_and_
