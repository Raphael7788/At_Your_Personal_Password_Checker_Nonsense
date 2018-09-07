"""
This version
of this file may be copied for personal, educational,
or commercial purposes.  Use at your own risk.
"""
 
import os
from os import path
import math
 
# Some notes: the configuration module is non-standard. You will
# need to format and read your dictionary file yourself.
from djangoapps import configuration
 
password_dict = path.join(os.sep, 'path', 'to', 'your', 'password.dictionary')
 

class PasswordStrengthChecker(object):
    def __init__(self, strength='medium', pwd_dict=''):
        self.punctuation = list("!@#$%^&* ()_+-='\";:[{]}\|.>,</?`~")
        self.similarity_map = {
            '3': 'e', 'x': 'k', '5': 's', '$': 's', '6': 'g', '7': 't',
            '8': 'b', '|': 'l', '9': 'g', '+': 't', '@': 'a', '0': 'o',
            '1': 'l', '2': 'z', '!': 'i', '1': 'i'}
        password_dictionary = configuration.Configuration(configpath=pwd_dict)
        self.word_list = dict()
        for i in xrange(3, 17):
            self.word_list[i] = password_dictionary.get_option('%s' % i, [])
 
        self.strengths = ['medium', 'strong', 'best']
        self.thresholds = {'medium': 0.8, 'strong': 0.6, 'best': 0.6}
        self.min_length = {'medium': 8, 'strong': 8, 'best': 14}
        self.min_charsets = {'medium': 2, 'strong': 3, 'best': 3}
        self.similarity = {'medium': False, 'strong': True, 'best': True}
 
        if strength not in self.strengths:
            strength = self.strengths[0]
        self.strength = strength
 
    def is_charset_type(self, c, c_class):
        if c_class == 'capital':
            return c.isalpha() and c == c.upper()
        if c_class == 'lower':
            return c.isalpha() and c == c.lower()
        if c_class == 'digit':
            return c.isdigit()
        if c_class == 'punctuation':
            return c in self.punctuation
        return False
 
    def canonicalize_word(self, word, letters_only=False):
        canonicalized = ''
        for c in list(word.lower()):
            if letters_only and not self.is_charset_type(c, 'lower'):
                canonicalized += c
            else:
                canonicalized += self.similarity_map.get(c, c)
        return canonicalized
 
    def charset_span(self, word):
        checks = {'capital': 0, 'lower': 0, 'digit': 0, 'punctuation': 0}
        for c in list(word):
            for key in checks:
                if not checks[key] and self.is_charset_type(c, key):
                    checks[key] = 1
                    break
        return sum(checks.values())
 
    def in_dictionary(self, word):
        similarity_check = self.similarity[self.strength]
        canonicalized = self.canonicalize_word(word, letters_only=similarity_check)
        word_length = len(canonicalized)
        if canonicalized in self.word_list[word_length]:
            return True
        if similarity_check:
            minimum_meaningful_match = int(math.floor((self.thresholds[self.strength]) * word_length))
            for length in xrange(minimum_meaningful_match, word_length):
                for start in xrange(0, word_length - minimum_meaningful_match):
                    subword = canonicalized[start:start + length]
                    if subword in self.word_list[len(subword)]:
                        return True
        return False
 
    def strong_enough(self, password):
        if not password:
            return False
        if len(password) < self.min_length[self.strength]:
            return False
        if self.charset_span(password) < self.min_charsets[self.strength]:
            return False
        if self.in_dictionary(password):
            return False
        return True
 
global password_checker
password_checker = PasswordStrengthChecker(strength='medium', pwd_dict=password_dict)