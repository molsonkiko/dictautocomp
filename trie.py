'''An implementation of the Trie data structure, which enables efficient
searches for strings based on substrings that begin them.
See https://en.wikipedia.org/wiki/Trie.
'''
import json
from typing import Iterator
import pprint
import unittest
import unicodedata

class TrieInterface:
    def __init__(self, words: list[str]=None) -> None:
        raise NotImplementedError

    def add(self, word: str, **kwargs) -> None:
        raise NotImplementedError

    def add_all(self, words: list[str]) -> None:
        raise NotImplementedError

    def remove(self, word: str) -> bool:
        raise NotImplementedError

    def _delete(child: dict, word: str, d: int) -> bool:
        raise NotImplementedError

    def __contains__(self, word, **kwargs) -> bool:
        raise NotImplementedError

    def super_words(self, word: str, **kwargs) -> Iterator[str]:
        raise NotImplementedError

    def json(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError



class Trie(TrieInterface):
    '''An implementation of tries, based on a tree mapping values to dicts.'''
    def __init__(self, words: list[str]=None) -> None:
        self.tree = {}
        if not words:
            return
        self.add_all(words)

    def add(self, word: str, **kwargs) -> None:
        assert isinstance(word, str), 'only strings allowed in Trie'
        if 'child' not in kwargs:
            child = self.tree
        else:
            child = kwargs['child']
        if not word:
            child[''] = {}
            return
        child.setdefault(word[0], {})
        self.add(word[1:], child = child[word[0]])

    def add_all(self, words: list[str]) -> None:
        for word in words:
            self.add(word)

    def remove(self, word: str) -> bool:
        """Eagerly remove the word from the trie rooted at `root`.
    Return whether the trie rooted at `root` is now empty.
    THIS METHOD IS SLIGHTLY MODIFIED FROM THE delete() METHOD IN THE WIKIPEDIA
    ARTICLE https://en.wikipedia.org/wiki/Trie.
        """
        def _delete(child: dict, word: str, d: int) -> bool:
            """Clear the node corresponding to word[d], and delete
            the child word[d+1] if that subtrie is completely empty,
            and return whether `node` has been cleared.
            """
            if d == len(word):
                try:
                    del child['']
                except:
                    raise KeyError(f"{repr(word)} is not in this Trie")
            else:
                c = word[d]
                try:
                    if _delete(child[c], word, d+1):
                        del child[c]
                except:
                    raise KeyError(f"{repr(word)} is not in this Trie.")
            # is the subtrie rooted at `node` now completely empty?
            return len(child) == 0
        return _delete(self.tree, word, 0)

    def __contains__(self, word, **kwargs) -> bool:
        if 'child' not in kwargs:
            child = self.tree
        else:
            child = kwargs['child']
        if not word:
            if '' in child:
                return True
            return False
        if word[0] in child:
            return self.__contains__(word[1:], child = child[word[0]])

    def super_words(self, word: str, **kwargs) -> Iterator[str]:
        if 'curword' not in kwargs:
            curword = ''
        else:
            curword = kwargs['curword']
        if 'child' not in kwargs:
            child = self.tree
        else:
            child = kwargs['child']
        if word == '':
            for val in child:
                if val == '':
                    yield curword
                yield from self.super_words('',
                                            curword = curword + val,
                                            child = child[val])
            return
        if word[0] in child:
            yield from self.super_words(word[1:],
                                        curword = curword + word[0],
                                        child = child[word[0]])
        return

    def json(self) -> str:
        return json.dumps(self.tree)

    def __str__(self) -> str:
        return f"Trie({pprint.pformat(self.tree, width = 40)})"


def ignorecase_culture_invariant(x):
    return unicodedata.normalize('NFD', x.upper())


class IgnoreCaseTrie(TrieInterface):
    trie: Trie
    ignorecase_to_ogcase: dict[str, list[str]]

    def __init__(self, words: str=None) -> None:
        self.trie = Trie()
        self.ignorecase_to_ogcase = {}
        if not words:
            return
        self.add_all(words)

    def add(self, word: str) -> None:
        ignorecase = ignorecase_culture_invariant(word)
        self.trie.add(ignorecase)
        self.ignorecase_to_ogcase.setdefault(ignorecase, []).append(word)

    def add_all(self, words: list[str]) -> None:
        for word in words:
            self.add(word)

    def remove(self, word: str) -> None:
        ignorecase = ignorecase_culture_invariant(word)
        if ignorecase in self.trie:
            self.trie.remove(ignorecase)
            del self.ignorecase_to_ogcase[ignorecase]

    def __contains__(self, word: str, **kwargs) -> bool:
        return ignorecase_culture_invariant(word) in self.trie

    def super_words(self, word: str) -> Iterator[str]:
        '''return an iterator of all the *originally added words*
        (in their original case)
        that have word as a prefix when ignoring case.
        For example, if ['foo', 'FOO', 'FOOB'] were added to the trie,
        super_words('Foo') would yield ['foo', 'FOO', 'FOOB']
        '''
        ignorecase = ignorecase_culture_invariant(word)
        ignore_sups = self.trie.super_words(ignorecase)
        for ignore_sup in ignore_sups:
            yield from self.ignorecase_to_ogcase[ignore_sup]
            
    def json(self) -> str:
        return {
            'trie': self.trie.tree,
            'ignorecase_to_ogcase': self.ignorecase_to_ogcase
        }

    def __str__(self):
        return pprint.pformat({
            'trie': self.trie.tree,
            'ignorecase_to_ogcase': self.ignorecase_to_ogcase
        }, width=48)