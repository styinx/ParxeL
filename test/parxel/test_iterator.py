from source.parxel.iterator import Iterator
from unittest import TestCase
from random import randint 


class IteratorTest(TestCase):
    ALPHABET = [chr(x) for x in range(26)]

    def test___bool__(self):
        # Empty buffer
        it = Iterator([])
        self.assertFalse(it)

        # Non-empty buffer
        it = Iterator(['a'])
        self.assertTrue(it)
        it.next()
        self.assertFalse(it)

    def test_empty_buffer(self):
        it = Iterator([])

        self.assertFalse(it)
        self.assertEqual(it.get(), None)
        self.assertEqual(it.next(), None)
        self.assertEqual(it.prev(), None)

    def test_simple_buffer(self):
        it = Iterator('bli kla dub')

        self.assertTrue(it)
        self.assertEqual(it.get(), 'b')
        self.assertEqual(it.next(), 'l')
        self.assertEqual(it.prev(), 'b')
        self.assertEqual(it.advance(2), 'i')
        self.assertEqual(it.peek(2), 'k')
        self.assertEqual(it.consume('i'), True)
        self.assertEqual(it.consume_any(' '), True)

    def test_complex_logic(self):
        it = Iterator([IteratorTest.ALPHABET[randint(0, 25)] for _ in range(20)])

        self.assertTrue(it)

        s = ''
        while it:
            if it.get() not in ' \n\r.()[]=\',:\\+_':
                s += it.get()

            it.next()
        
        self.assertFalse(it)
        self.assertEqual(len(set([x.isalnum() for x in s])), 1)
