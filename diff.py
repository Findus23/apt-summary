from difflib import SequenceMatcher

COLOR_BLUE = '\033[34m'
ENDC = '\033[0m'


def get_diff(a: str, b: str) -> str:
    sm = SequenceMatcher(None, a, b)
    output = []
    for opcode, a0, a1, b0, b1 in sm.get_opcodes():
        if opcode == 'equal':
            output.append(a[a0:a1])
        elif opcode in ['insert', 'replace']:
            output.append(COLOR_BLUE + b[b0:b1] + ENDC)
        elif opcode == 'delete':
            ...
            # output.append("<del>" + seqm.a[a0:a1] + "</del>")
        else:
            raise RuntimeError("unexpected opcode")
    return ''.join(output)


if __name__ == '__main__':
    a = "Wort"
    b = "Woort"

    print(get_diff(a, b))
