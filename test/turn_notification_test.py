import sys
sys.path.append('wordwars-1311')

from main import TurnNotification

class Test():

    def assertTrue(self, booleanExpression, description):
        if not booleanExpression:
            raise ValueError("{} is not True".format(description))
        else:
            print('passed test: {}'.format(description))

    def test_get(self):
        notif = TurnNotification()
        notif.get()
        self.assertTrue(True, "able to call get()")

t = Test()
t.test_get()
