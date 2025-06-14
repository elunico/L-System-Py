# LSYS file format

### Please note: LSYS file parsing is new and experimental. Please report any bugs using issues

Instead of writing all the necessary information to construct an L-System in Python directly, you can write a `.lsys` file that can be parsed into an L-System.

The specification for this type of file is provided below

## Universals
Any line may start with a `#`. That line is a comment and is ignored

## Alphabet 
The first non-comment line of the file should be the alphabet. The line should start with `%` and each letter constant should be wrriten with commas between. The letters much be alphanumeric + `_` only and cannot start with a number

Example
```
%NOUN, VERB, ARTICLE
```

## Axiom
After the alphabet, the axiom is written between `@`. It should be composed of comma separated values. Literal strings should go in quotes and alphabet letters should be unquoted and case-sensitive

Example
```aiignore
@NOUN, VERB, NOUN@
```

## Rules
Rules are the most complicated feature to describe. To begin, write `$` followed by the alphabet letter you want the rule to match.
Then provide `=` and begin specifying replacement cases. Replacement cases must be separated by a `|`. Literal strings must be quoted and alphabet letters should be unquoted. Adjacent strings, letters, or a mix thereof will be grouped in order into
a single replacement case. The rule is terminated by placing a `~` after all replacement cases are specified

Example
```aiignore
$NOUN = "dog " | "cat " | "house party " | ADJECTIVE NOUN 
~

```

Additionally, weights can be supplied at the end of each case after a colon but before the case-terminating `|`. If one 
possible replacement case has a weight then **all cases** in that rule must be given a weight

Example
```aiignore
$NOUN = "dog ":5 | "cat ":5 | "house party ":2 | ADJECTIVE NOUN:8
~
```

This will result in 5/20s of the time getting dog, 5/20 of the time getting cat, 2/20 of the time getting "house party" and 8/20 of the time getting `ADJECTIVE NOUN`

Weights can also be specified in decimal form as a percent-chance to select that case