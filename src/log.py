indentDepth = 0


def indent(s, nspaces: int = 2):
    s = str(s)
    lines = s.split("\n")

    global indentDepth
    indentDepth += nspaces
    indented_lines = [indentDepth * " " + line for line in lines]
    indentDepth -= nspaces

    return "\n".join(indented_lines)
