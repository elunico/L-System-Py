from lsystem import *

class Alphabet(AlphabetEnum):
    A = 'A'
    B = 'B'

rc = RuleConverter(Alphabet, '@', '@')

l = LSystem(
    Axiom([Alphabet.A]),
    [
        rc.convert(Alphabet.A, '@B@@B@'),
        rc.convert(Alphabet.B, '@B@', '@A@', ''),
    ]
)

for i in l.expand():
    print("".join(map(str, i)))
    input()