from ww_models import LetterBag

class Test():

    def assertTrue(self, booleanExpression, description):
        if not booleanExpression:
            raise ValueError("{} is not True".format(description))
        else:
            print('passed test: {}'.format(description))

    def test_create_empty(self):
        bag = LetterBag()
        self.assertTrue(bag.contentCount() == 0, "empty bag contentCount() is zero")
        try:
        	l = bag.remove('c')
        	self.assertTrue(False, "able to remove letter from empty bag")
        except Exception, e:
        	self.assertTrue(True, "exception trying to remove from empty bag")

    def test_simple_example(self):
        bag = LetterBag()
        bag.add('a')
        self.assertTrue(bag.contentCount() == 1, "size is one after adding one")
        bag.add('z')
        self.assertTrue(bag.contentCount() == 2, "2 after adding second")
        bag.add('z')
        self.assertTrue(bag.contentCount() == 3, "3 after adding third")
        try:
            l = bag.remove('c')
            self.assertTrue(False, "able to remove letter not in bag")
        except Exception, e:
            self.assertTrue(True, "exception trying to remove letter not in bag")
        bag.remove('a')
        self.assertTrue(True, "able to remove letter added")
        try:
            l = bag.remove('a')
            self.assertTrue(False, "able to remove letter already removed")
        except Exception, e:
            self.assertTrue(True, "exception trying to remove letter already removed")
        bag.remove('z')
        bag.remove('z')
        self.assertTrue(True, "able to remove every last letter added")

    def test_letterAtIndex(self):
        bag = LetterBag.fromString('aaaccez')
        self.assertTrue( bag.letterAtIndex(0) == 'a', "bag has an 'a' at 0")
        self.assertTrue( bag.letterAtIndex(2) == 'a', "bag has an 'a' at 2")
        self.assertTrue( bag.letterAtIndex(6) == 'z', "bag has an 'z' at 6")
        self.assertTrue( bag.letterAtIndex(5) == 'e', "bag has an 'e' at 5")

    def test_removeRandom(self):
        letters = 'thequickfoxtheolddog'
        total = len(letters)
        bag = LetterBag.fromString(letters)
        self.assertTrue( bag.contentCount() == total, '{} letters in {}'.format(total,letters))
        bag2 = bag.removeRandom(7)
        expectedRemaining = total - 7
        self.assertTrue( bag.contentCount() == expectedRemaining, '{} left after removing 7'.format(expectedRemaining))
        bag3 = bag.removeRandom(expectedRemaining)
        self.assertTrue( bag.contentCount() == 0, 'none left after removing all')
        bag2.addAll(bag3)
        for i in range(total):
            bag2.remove(letters[i])
        self.assertTrue( bag2.contentCount() == 0, 'found all letters in bag2')



t = Test()
t.test_create_empty()
t.test_simple_example()
t.test_letterAtIndex()
t.test_removeRandom()


