import random
import re
from enum import Enum
from typing import Iterable, override


def near_equals(a, b, epsilon=1e-6):
    return abs(a - b) < epsilon


def is_iterable(p):
    try:
        iter(p)
        return True
    except TypeError:
        return False


class AlphabetEnum(Enum):
    """
    The alphabet of the L-System. Subclass this base-class and define an enum case for each symbol in the alphabet.
    """

    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.name}: {self.value}>"

    def __str__(self):
        return self.value


class Axiom:
    """
    Represents a single axiom in an L-System. This is the starting point of the L-System generation.
    It should be composed of a list of Alphabet cases.
    """

    def __init__(self, pattern: Iterable[AlphabetEnum]):
        self.pattern = pattern

    def __str__(self):
        return "Axiom(" + "".join(map(str, self.pattern)) + ")"


class WeightedReplacement:
    """
    Represents a single replacement in a WeightedRule.
    The replacement is a list of Alphabet cases.
    The weight is can be specified in 1 of 2 ways:
        1) Provide a float value between 0 and 1 specifying the percent chance to pick that weight
        2) Provide an int value specifying the relative proportion of outcomes that should result in that replacement being chosen
    The weight determines the likelihood of the replacement being chosen in the WeightedRule.
    Higher weights have a higher chance of being chosen.
    """

    def __init__(self, replacement: list[AlphabetEnum | str], weight: float):
        self.replacement = replacement
        self.weight = weight

    def __iter__(self):
        return iter(self.replacement)

    def __repr__(self):
        return "WeightedReplacement(" + str(self.replacement) + ", " + str(self.weight) + ")"

    def __str__(self):
        return str(self.replacement) + " (" + str(self.weight) + ")"


class Rule:
    """
    A simple replacement rule in an LSystem that
    defines the pattern to match for replacement and the replacement candidates.
    A randomly chosen element will be selected from the list of replacements to serve as the replacement.
    If there is only 1 item in the list, that item will always be chosen as the replacement.
    If there is no list of replacements, the pattern itself will be used as the replacement; a more semantic way of
    saying this is to use the LeafRule.
    """

    def __init__(self, pattern: AlphabetEnum, replacements: list[Iterable[AlphabetEnum | str]]):
        """
        Initialize the rule
        :param pattern: the pattern to search for
        :param replacements: The list of replacement candidates. A random element will be chosen
                            from the list of lists to serve as the replacement. If there is
                            only 1 item in the list, that item will always be chosen as the
                            replacement.
        """
        self.pattern = pattern
        self.replacements = replacements

    def get_replacement(self):
        return random.choice(self.replacements) if self.replacements else [self.pattern]

    def __str__(self):
        return "Rule(" + str(self.pattern) + " -> " + str(self.replacements) + ")"


class LeafRule(Rule):
    def __init__(self, pattern: AlphabetEnum):
        super().__init__(pattern, [])

    def get_replacement(self):
        return [self.pattern]


class WeightedRule(Rule):
    """
    A more complex rule that allows for weighted replacements.
    Like with Rule, define the pattern to match for replacement.
    Also, the replacement is chosen from a list of replacement candidates, but each candidate contains not only
    the list of replacements but also a weight. The replacement is chosen randomly based on the weights with
    higher weights having a higher chance of being chosen.

    Weights must be between 0 and 1 and must sum to 1.
    """
    replacements: list[WeightedReplacement]

    def __init__(self, pattern: AlphabetEnum, replacements: list[WeightedReplacement]):
        super().__init__(pattern, sorted(replacements, key=lambda x: x.weight, reverse=True))
        total = 0
        all_int = True
        for replacement in self.replacements:
            total += replacement.weight
            if isinstance(replacement.weight, float):
                all_int = False
        if not near_equals(total, 1):
            if not all_int:
                print("Warning: WeightedRule.normalize_weights() called on WeightedRule with float weights. ")
            self.normalize_weights()

    def normalize_weights(self):
        total = sum(map(lambda x: x.weight, self.replacements))
        for replacement in self.replacements:
            replacement.weight /= total

    def random_weighted_choice(self):
        chance = random.random()
        for replacement in self.replacements:
            chance -= replacement.weight
            if chance <= 0:
                return replacement.replacement

        return self.replacements[-1].replacement

    @override
    def get_replacement(self):
        return self.random_weighted_choice()


class LSystem:
    def __init__(self, axiom: Axiom, rules: list[Rule], /, warn=True):
        self.axiom = axiom
        self.rules = rules
        self.warn = warn

    def expand(self):
        data = [*self.axiom.pattern]
        while True:
            new_data = []
            for i in range(len(data)):
                for rule in self.rules:
                    if data[i] == rule.pattern:
                        new_data.extend(rule.get_replacement())
                        break
                else:
                    if self.warn:
                        print("Warning no rule found for:", data[i])
                    new_data.append(data[i])
            if data == new_data:
                break
            data = new_data
            yield data

    def realize(self):
        f = self.expand()
        result = None
        for i in f:
            result = i
        return ''.join(result)


class Filler:
    """
    Class that can be used to generate replacement rules for many atoms with the same alphabet symbols around them
    Example:
    >>> nouns = ['cat', 'hat', 'bat']
    >>> Filler(Alphabet.A, Alphabet.B, Filler.VAR_POS).spread(nouns)
    # returns [[Alphabet.A, Alphabet.B, 'cat'], [Alphabet.A, Alphabet.B, 'hat'], [Alphabet.A, Alphabet.B, 'bat']]
    can also be used to generate weighted replacements by using the weighted_spread method and including a weight
    in this case, a list of instances of WeightedReplacement will be returned instead of a list of lists of replacements
    """
    VAR_POS = object()

    def __init__(self, *recipe):
        assert Filler.VAR_POS in recipe
        self.recipe = recipe

    def spread(self, supplement):
        results = []
        for word in supplement:
            result = []
            for arg in self.recipe:
                if arg is Filler.VAR_POS:
                    result.append(word)
                else:
                    result.append(arg)
            results.append(result)
        return results

    def weighted_spread(self, supplement, weight):
        results = []
        for word in supplement:
            result = []
            for arg in self.recipe:
                if arg is Filler.VAR_POS:
                    result.append(word)
                else:
                    result.append(arg)
            results.append(WeightedReplacement(result, weight))
        return results


class RuleConverter:
    '''
    Allows you to create very simple rules using strings instead of constructing many objects
    example:
    >>> r = RuleConverter(Alphabet, '@', '@')
    >>> r.convert(Alphabet.A, '@N@ something else', '@V@ @A@ and @V@@V@')
    # becomes Rule(Alphabet.A, [[Alphabet.N, 'something else'], [Alphabet.V, Alphabet.A, 'and', Alphabet.V, Alphabet.V]])
    this can be reused to convert many strings, simplifying the productino of rules
    '''

    def __init__(self, alphabet: type[AlphabetEnum], start: str, end: str):
        self.start = start
        self.end = end
        self.reg = re.compile(fr'({self.start}.+?{self.end})')
        self.alphabet = alphabet

    def convert(self, pattern: AlphabetEnum, *s: str):
        replacements = []
        for replacement_str in s:
            replacement = []
            contents = [i for i in self.reg.split(replacement_str) if i]
            for c in contents:
                if c.startswith(self.start) and c.endswith(self.end):
                    replacement.append(self.alphabet[c[1:-1]])
                else:
                    replacement.append(c)
            replacements.append(replacement)

        return Rule(pattern, replacements)


# example
class Alphabet(AlphabetEnum):
    A = 'A'
    B = 'B'
    C = 'C'


def main():
    i = LSystem(
        Axiom([Alphabet.A]),
        [
            # A will be replaced a weighted random choice based on the weights of the WeightedReplacement objects in w
            WeightedRule(Alphabet.A, [
                WeightedReplacement([Alphabet.A, Alphabet.B], 0.95),
                WeightedReplacement([Alphabet.B, Alphabet.C], 0.05)
            ]),

            # B will always be replaced by [C, A, C] since it is the only item in the list
            Rule(Alphabet.B, [
                [Alphabet.C, Alphabet.A, Alphabet.C]
            ]),

            # C will be replaced by either [B, B] or [B, A, B] with equal likelihoods to each option since no weights are given
            Rule(Alphabet.C, [
                [Alphabet.B, Alphabet.B], [Alphabet.B, Alphabet.A, Alphabet.B]
            ])
        ]
    )

    for exp in i.expand():
        print("".join(map(str, exp)))
        input()


if __name__ == '__main__':
    main()
