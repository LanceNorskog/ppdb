# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division, print_function

"""
Functions for filtering trivial paraphrases from PPDB in Portuguese.
"""

from ppdb import TransformationDict, get_rhs
from ppdb import load_ppdb as _load_ppdb

def _is_trivial_paraphrase(exp1, exp2):
    """
    Return True if:
        - w1 and w2 differ only in gender and/or number
        - w1 and w2 differ only in a heading preposition

    :param exp1: tuple/list of strings, expression1
    :param exp2: tuple/list of strings, expression2
    :return: boolean
    """
    def strip_suffix(word):
        if word[-2:] == 'os' or word[-2:] == 'as':
            return word[:-2]

        if word[-1] in 'aos':
            return word[:-1]

        return word

    prepositions = {'de', 'da', 'do', 'das', 'dos',
                    'em', 'no', 'na', 'nos', 'nas'}
    if exp1[0] in prepositions:
        exp1 = exp1[1:]
    if exp2[0] in prepositions:
        exp2 = exp2[1:]

    if len(exp1) == 0 or len(exp2) == 0:
        return True

    if exp1[-1] in prepositions:
        exp1 = exp1[:-1]
    if exp2[-1] in prepositions:
        exp2 = exp2[:-1]

    if len(exp1) != len(exp2):
        return False

    if exp1 == (',',) or exp2 == (',',):
        return True

    for w1, w2 in zip(exp1, exp2):
        w1 = strip_suffix(w1)
        w2 = strip_suffix(w2)
        if len(w1) == 0 or len(w2) == 0:
            if len(w1) == len(w2):
                continue
            else:
                return False

        if w1 != w2 and \
                not (w1[-1] == 'l' and w2[-1] == 'i' and w1[:-1] == w2[:-1]):
            return False

    return True

cmulist = []
def load_cmu(path):
    global cmulist
    with open(path, 'r') as f:
         cmulist = []
         for line in f:
              parts = line.split('\t')
              for part in parts:
                  cmulist.append(part.lower())

def not_in_cmu(exp1, exp2):
    def not_in_parts(exp):
         parts = exp.split('-')
         for part in parts:
             if not part in cmulist:
                 return True
         return False

    return not (not_in_parts(exp1) or not_in_parts(exp2))

def reject(exp1, exp2):
    #print(str(exp1))
    #print(str(exp2))
    return _is_trivial_paraphrase(exp1[-1], exp2[-1]) or not_in_cmu(exp1[-1], exp2[-1])


articles = {'the', 'of', 'that', 'this', 'as'}


def remove_comma_and_article(expression):
    """
    Filter an expression by removing any leading articles and/or commas.

    :param expression: a list/tuple of strings
    :return: a list of strings
    """
    if len(expression) == 1:
        return expression

    while expression[0] in articles or expression[0] == ',':
        expression = expression[1:]
        if len(expression) == 0:
            return expression

    if expression[-1] == ',':
        expression = expression[:-1]
    return expression


def load_ppdb(path, force=False):
    """
    Load the PPDB, filtering data for English and for CMU Dictionary

    :param path: path to the file
    :param force: if False and the dictionary is already loaded, do nothing.
        If True, always load the dictionary.
    :return: a nested dictionary containing transformations.
        each level of the dictionary has one token of the right-hand side of
        the transformation rule mapping to a tuple (transformations, dict):
        ex:
        {'poder': (set(),
                   {'legislativo': (set('legislatura',
                                    {})})
        }
    """
    return _load_ppdb(path, reject,
                      remove_comma_and_article, force)

import pickle as pk

if __name__ == '__main__':
    load_cmu('/home/lance/open/data/cmudict_0.6.syllablized.txt')
    print('Size of cmulist = {}'.format(len(cmulist)))
    ppdb = load_ppdb('../../data/ppdb-2.0-s-lexical')
    print('Finished loading ppdb')
    with open('/home/lance/open/data/ppdb-2.0-s.pk', 'wb') as f:
        pk.dump(ppdb, f)
