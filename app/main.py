#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

#import sys
#sys.path.insert(1, '/usr/local/google_appengine/lib/webapp2-2.5.2')
#sys.path.insert(2, '/usr/local/google_appengine/lib/webob-1.2.3')
#sys.path.insert(3, '/usr/local/google_appengine')

import webapp2
from google.appengine.api import mail, app_identity
from repositories import GameStateRepository, NotificationRepository

from models import User, GameState


class TurnNotification(webapp2.RequestHandler):
    def get(self):
        """Find users who need reminder to play their turn.
        Send a reminder email to each with instructions to play.
        Record the notification so we don't annoy users with repeat email.
        Called every few minutes using a cron job.  See cron.yaml"""

        print('============in TurnNotification============')
        usersToNotify = GameStateRepository().playersToNotify()
        print('============len(usersToNotify)={}'.format(len(usersToNotify)))

        #send email notification
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None)
        for user in usersToNotify:
            # remember notification so we don't harass the user repeatedly
            notifications.registerTurnNotification(user, game)
            subject = 'This is a reminder!'
            body = 'Hello {}, its your turn to play WordWars!'.format(user.name)
            print('=====sending email to {}'.format(user.name))
            mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                           user.email,
                           subject,
                           body)


app = webapp2.WSGIApplication([
    ('/crons/turn_notification', TurnNotification),
], debug=True)
