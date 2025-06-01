from lsystem import *


class LangAlphabet(AlphabetEnum):
    NOUN = 'N'
    VERB = 'V'
    ANY_NOUN = 'M'
    PL_VERB = 'W'
    ADJECTIVE = 'A'
    PL_NOUN = 'P'
    DETERMINER = 'D'
    PL_DETERMINER = 'G'
    ADVERB = 'B'
    SUBJECT = 'S'
    PREDICATE = 'O'


noun = []
verb = []
adjective = []

with open('words.csv') as f:
    words = f.read().splitlines()
    for word in words:
        word, pos = word.split(',')
        globals()[pos].append(word)



v = LSystem(
    Axiom([LangAlphabet.SUBJECT]),
    [
        Rule(
            LangAlphabet.SUBJECT,
            [
                [LangAlphabet.NOUN, LangAlphabet.VERB],
                [LangAlphabet.PL_NOUN, LangAlphabet.PL_VERB]
            ]
        ),

        Rule(
            LangAlphabet.DETERMINER,
            [['the '], ['a ']]
        ),

        Rule(
            LangAlphabet.PL_DETERMINER,
            [['the '], ['some '], ['many ']]
        ),

        Rule(
            LangAlphabet.NOUN,
            [
                *Filler(LangAlphabet.DETERMINER, LangAlphabet.ADJECTIVE, Filler.VAR_POS, ' ').spread(noun)
            ]
        ),

        Rule(
            LangAlphabet.PL_NOUN,
            [
                *Filler(LangAlphabet.PL_DETERMINER, LangAlphabet.ADJECTIVE, Filler.VAR_POS, 's ').spread(noun),
            ]
        ),

        Rule(
            LangAlphabet.ANY_NOUN,
            [[LangAlphabet.NOUN], [LangAlphabet.PL_NOUN]]
        ),

        WeightedRule(
            LangAlphabet.ADVERB,
            [
                WeightedReplacement([], 25),
                WeightedReplacement(["very ", LangAlphabet.ADVERB], 50),
                WeightedReplacement(["somewhat ", LangAlphabet.ADVERB], 50),
                WeightedReplacement(["mostly ", LangAlphabet.ADVERB], 50),
                WeightedReplacement([LangAlphabet.ADVERB, " ", LangAlphabet.ADVERB], 5)
            ]
        ),

        WeightedRule(
            LangAlphabet.ADJECTIVE,
            [
                *Filler(Filler.VAR_POS, ' ').weighted_spread(adjective, 2),
                WeightedReplacement([], 10),
                WeightedReplacement([LangAlphabet.ADVERB, " ", LangAlphabet.ADJECTIVE], 15)
            ]
        ),

        Rule(
            LangAlphabet.VERB,
            [*Filler(Filler.VAR_POS, 's ', LangAlphabet.ANY_NOUN).spread(verb)]
        ),

        Rule(
            LangAlphabet.PL_VERB,
            [
                *Filler(Filler.VAR_POS, ' ', LangAlphabet.ANY_NOUN).spread(verb)
            ]
        ),
    ],
    warn=False
)

for test in range(25):
    print(v.realize())

# print(spread(noun, LangAlphabet.DETERMINER, LangAlphabet.ADJECTIVE, SPREAD_POS))
