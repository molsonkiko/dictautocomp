# -*- coding: utf-8 -*-
import unittest

from trie import Trie, IgnoreCaseTrie, ignorecase_culture_invariant

class TrieTester(unittest.TestCase):
    def test_add_contains(self):
        t = Trie()
        t.add('ab')
        self.assertIn('ab', t)

    def test_remove(self):
        t = Trie()
        t.add('ab')
        t.remove('ab')
        self.assertNotIn('ab', t)

    def test_remove_not_in_t(self):
        t = Trie()
        with self.assertRaisesRegex(KeyError, "not in this Trie"):
            t.remove('ab')

    def test_substring_not_in_t(self):
        t = Trie()
        t.add('aba')
        with self.assertRaisesRegex(KeyError, "not in this Trie"):
            t.remove('ab')

    def test_remove_substring(self):
        t = Trie()
        t.add('aba')
        t.add('ab')
        t.remove('ab')
        self.assertIn('aba', t)

    def test_remove_superstring(self):
        t = Trie()
        t.add('aba')
        t.add('ab')
        t.remove('aba')
        self.assertIn('ab', t)

    def test_remove_unrelated_string(self):
        t = Trie()
        t.add('a')
        t.add('b')
        t.remove('b')
        self.assertIn('a', t)

    def test_empty_string(self):
        t = Trie()
        t.add('')
        self.assertIn('', t)

    def test_remove_empty_string(self):
        t = Trie()
        t.add('')
        t.add('ab')
        t.remove('')
        with self.subTest(t=t):
            self.assertNotIn('', t)
        self.assertIn('ab', t)

    def test_super_words_none(self):
        t = Trie()
        t.add('a')
        self.assertEqual(list(t.super_words('b')), [])

    def test_super_words_word_in_t_one_result(self):
        t = Trie()
        t.add('ab')
        self.assertEqual(list(t.super_words('ab')), ['ab'])

    def test_super_words_word_not_in_t_one_result(self):
        t = Trie()
        t.add('ab')
        self.assertEqual(list(t.super_words('a')), ['ab'])

    def test_super_words_word_in_t_multi_results(self):
        t = Trie()
        t.add('dog')
        t.add('dogged')
        t.add('abacus')
        self.assertEqual(set(t.super_words('dog')), {'dog', 'dogged'})

    def test_super_words_word_not_in_t_multi_results(self):
        t = Trie()
        t.add('dog')
        t.add('abeyance')
        t.add('abacus')
        self.assertEqual(set(t.super_words('ab')), {'abacus', 'abeyance'})

    def test_init_with_list(self):
        t = Trie(['a', 'ab'])
        self.assertEqual(set(t.super_words('')), {'a', 'ab'})

GERMAN_WORDS = [
    'baßk',
    'basst',
    'bLue',
    'blue',
    'blüe',
    'blües',
    'blve',
    'oyster',
    'öyster',
    'spä',
    'Spb',
    'spb',
    'taco',
    'täco',
    'täco',
    'tone',
]

class IgnoreCaseTrieTester(unittest.TestCase):
    def test_super_words(self):
        t = IgnoreCaseTrie()
        t.add('dog')
        t.add('DOG')
        t.add('GODOG')
        self.assertEqual(set(t.super_words('Dog')), {'dog', 'DOG'})

    def test_contains(self):
        t = IgnoreCaseTrie(['dog', 'DOG', 'd', 'GODOG'])
        self.assertIn('Dog', t)

    def test_not_contains(self):
        t = IgnoreCaseTrie(['DOG', 'dog', 'd', 'GODOG'])
        self.assertNotIn('do', t)

    def test_contains_with_unicode(self):
        t = IgnoreCaseTrie(['FÜN'])
        self.assertIn('fu\u0308n', t) # normalized form of ü

    def test_super_words_with_unicode(self):
        t = IgnoreCaseTrie(GERMAN_WORDS)
        self.assertEqual(set(t.super_words('Bas')), {'basst', 'baßk'})

    def test_remove(self):
        t = IgnoreCaseTrie(GERMAN_WORDS)
        t.remove('Basst')
        self.assertNotIn('BASST', t)

    def test_remove_doesnt_remove_unrelated(self):
        t = IgnoreCaseTrie(GERMAN_WORDS)
        t.remove('blüe')
        self.assertEqual(set(t.super_words('bLu')), {'bLue', 'blue', 'blües'})


if __name__ == '__main__':
    unittest.main()