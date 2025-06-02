from lsystem import AlphabetEnum, WeightedReplacement, WeightedRule, LeafRule, Rule, LSystem, Axiom

# new alphabet for this file. The system only checks for == so anything can be used as an alphabet as long as
# 1) replacements are made of iterables of the same type as patterns
# 2) they can be compared meaningfully with ==

class Alphabet(AlphabetEnum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'

wc = WeightedRule(
    Alphabet.C,
    [
        WeightedReplacement([Alphabet.D, Alphabet.B], 0.165),
        WeightedReplacement([Alphabet.B, Alphabet.A], 0.165),
        WeightedReplacement([Alphabet.C, Alphabet.D], 0.0825),
        WeightedReplacement([Alphabet.B, Alphabet.C, Alphabet.A], 1 - 0.0825 - 0.165 - 0.165),
    ]
)

wb = WeightedRule(
    Alphabet.B,
    [
        WeightedReplacement([Alphabet.C, Alphabet.B], 0.75),
        WeightedReplacement([Alphabet.A, Alphabet.D], 0.25),
    ]
)

wa = LeafRule(Alphabet.A)

wd = Rule(
    Alphabet.D,
    [
        [Alphabet.A, Alphabet.B, Alphabet.C]
    ]
)

l = LSystem(Axiom([Alphabet.C]), [wa, wb, wc, wd])
g = l.expand()

for i in g:
    print("".join(map(str, i)))
    input()
