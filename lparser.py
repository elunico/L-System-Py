import collections
import re

from lsystem import WeightedReplacement, Rule, WeightedRule, LSystem, Axiom, AlphabetEnum
from enum import auto

comma_sep = re.compile(r'\s*?,\s*')
space_sep = re.compile(r'(\s+)')
literal_terminal = re.compile(r'[\w_|:\n]')


# this is here to prevent static type error and code cleanup from removing imports
class GenAlphabet(AlphabetEnum):
    A = auto()

class BufFile:
    def __init__(self, f):
        self.f = f
        self.buf = collections.deque()

    def read(self, n):
        if self.buf:
            content = ''.join(self.buf.pop() for _ in range(min(n, len(self.buf))))
            if len(content) == n:
                return content
            else:
                return content + self.f.read(n - len(content))
        else:
            return self.f.read(n)

    def unget(self, c):
        self.buf.appendleft(c)


class LParser:
    def __init__(self, filename: str):
        self.filename = filename

    def _consume_to_line_end(self, f):
        res = []
        c = f.read(1)
        while c != '\n':
            res.append(c)
            c = f.read(1)
        f.unget(c)
        return ''.join(res)

    def _consume_until_r(self, f, reg):
        res = []
        x = f.read(1)
        while not (reg.match(x)):
            if x != '\n':
                res.append(x)
            x = f.read(1)
        f.unget(x)
        return ''.join(res)

    def _consume_until(self, f, *c):
        c = set(c)
        res = []
        x = f.read(1)
        while x not in c:
            if x != '\n':
                res.append(x)
            x = f.read(1)
        f.unget(x)
        return ''.join(res)

    def parse(self):
        with open(self.filename) as raw_f:
            f = BufFile(raw_f)
            letters = axiom = None
            replacements = collections.defaultdict(list)

            while True:
                c = f.read(1)
                if c == '':
                    break
                if c == '#':
                    self._consume_to_line_end(f)
                if c == '\n':
                    continue

                if c == '%':
                    letters = self.consume_alphabet(f)

                if c == '@':
                    axiom = self.consume_axiom(axiom, f)

                if c == '$':
                    pattern = self.consume_pattern(f, letters)

                if c == '=':
                    while True:
                        repl_parts = []
                        while True:
                            c = self.consume_replacement_case(f, repl_parts)

                            if c == '|' or c == '~' or c == ':' or c == '~' or c == '':
                                break

                        if c == ':':
                            c, weight = self.consume_weight(f)
                            replacements[pattern].append(WeightedReplacement(repl_parts, weight))
                            # clear the case until the |
                            self._consume_until(f, '|', '~')
                            if (c := f.read(1)) == '~': # discard | but not ~
                                f.unget(c)

                        else:
                            replacements[pattern].append(repl_parts)

                        if c == '~' or c == '':
                            break

        if letters is None:
            raise ValueError("No alphabet specified. Use % to specify the alphabet")
        if axiom is None:
            raise ValueError(
                "No axiom specified. Use @ to specify the axiom start and end and commas to separate letters in the axiom")

        axiom, rules = self.transform_parse_result(axiom, letters, replacements)

        return GenAlphabet, LSystem(Axiom(axiom), rules, warn=False)

    def transform_parse_result(self, axiom, letters, replacements):
        if not all(i in replacements for i in letters):
            print("Warning: letters without rules will be treated as terminal symbols")
        # before returning, give back the actual constants
        axiom = [GenAlphabet[i] for i in axiom]
        rules = []
        for pattern, repls in replacements.items():
            pattern = GenAlphabet[pattern]
            if isinstance(repls[0], WeightedReplacement):
                rules.append(WeightedRule(pattern, repls))
            else:
                rules.append(Rule(pattern, repls))
        return axiom, rules

    def consume_replacement_case(self, f, repl_parts):
        c = f.read(1)
        if c == '"':
            repl = self.consume_literal(f)
            repl_parts.append(repl)
        elif c.isalnum() or c == '_':
            f.unget(c)
            repl = self.consume_letter(f)
            repl_parts.append(repl)
        elif c == '':
            return c
        return c

    def consume_alphabet(self, f):
        alphabet = self._consume_until(f, '#', '$', '@', '~')
        letters = comma_sep.split(alphabet)
        cls_str = f'class GenAlphabet(AlphabetEnum):\n' + '\n'.join(
            f'\t{i} = auto()' for i in letters) + '\n'
        exec(cls_str, globals(), globals())
        return letters

    def consume_axiom(self, axiom, f):
        axiom_str = self._consume_until(f, '@')
        f.read(1)  # discard terminal @ sign
        axiom = comma_sep.split(axiom_str)
        return axiom

    def consume_pattern(self, f, letters):
        pattern = self._consume_until(f, '=').strip()
        if letters is not None and pattern not in letters:
            raise ValueError(f"Invalid pattern: {pattern}. Add {pattern} to alphabet or fix pattern")
        return pattern

    def consume_weight(self, f):
        w = ''
        while True:
            c = f.read(1)
            if not c.isdigit() and not c == '.':
                break
            w += c
        if '.' in w:
            weight = float(w)
        else:
            weight = int(w)
        return c, weight

    def consume_letter(self, f):
        letter = self._consume_until(f, ' ', '\n', ':', '|')
        repl = GenAlphabet[letter]
        return repl

    def consume_literal(self, f):
        literal = self._consume_until(f, '"')
        # ignore bar separator
        self._consume_until_r(f, literal_terminal)
        repl = literal
        return repl


p = LParser('lang-sys.lsys')
cls, system = p.parse()
print(system)
g = system.expand()
for i in g:
    print(''.join(map(str, i)))
    input()
