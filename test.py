from lsystem import *

nouns = ['cat', 'hat', 'bat']
print(Filler(Alphabet.A, Alphabet.B, Filler.VAR_POS).spread(nouns))

nouns = ['cat', 'horse', 'whale', 'bat']
print(Filler(Alphabet.A, Filler.VAR_POS, Alphabet.B).weighted_spread(nouns, lambda repl: 2 if len(repl[1]) > 3 else 3))

nouns = ['cat', 'horse', 'whale', 'bat']
print(Filler(Alphabet.A, Filler.VAR_POS, Alphabet.B).weighted_spread(nouns, 0.25))

example = [(1, 2), (3, 4), (5, 6)]
print(Filler(Alphabet.A, Alphabet.B, Filler.VAR_1, Alphabet.C, Filler.VAR_2).spread(example))

example = [(1, 2), (3, 4), (5, 6)]
print(Filler(Alphabet.A, Alphabet.B, Filler.VAR_2, Alphabet.C, Filler.VAR_1).spread(example))

