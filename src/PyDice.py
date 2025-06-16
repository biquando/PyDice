import argparse
import sys
import lark

from main import grammar, TreeTransformer
from inference import Inferencer
from compiler import PyEdaCompiler


def parse_string(text: str, parser: lark.Lark, num_its: int=10000) -> dict:
    ast = parser.parse(text)
    ir = TreeTransformer().transform(ast)
    inferencer = Inferencer(ir, num_iterations=num_its, seed=0)
    return inferencer.infer()


def parse_string_compile(text: str, parser: lark.Lark) -> dict:
    ast = parser.parse(text)
    ir = TreeTransformer().transform(ast)
    compiled_tree = PyEdaCompiler(ir)
    return compiled_tree.infer()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bdd", action="store_true", help="enable bdd computation")
    ap.add_argument("-n", "--num-its", type=int, default=10000, help="number of sampling iterations (default 10000)")
    ap.add_argument("input_file", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input file")

    args = ap.parse_args()

    # print(args.bdd)
    # print(args.num_its)
    # print(args.input_file)

    prog = args.input_file.read()
    parser = lark.Lark(grammar, parser="lalr")

    if args.bdd:
        print(parse_string_compile(prog, parser))
    else:
        print(parse_string(prog, parser, args.num_its))

    args.input_file.close()

if __name__ == "__main__":
    main()
