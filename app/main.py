#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from repositories import GameStateRepository, NotificationRepository

from models import User, GameState


class TurnNotification(webapp2.RequestHandler):
    def get(self):
        """Find users who've taken more than 5 minutes to play their turn.
        Send a reminder email (only once) to each with instructions to play.
        Called every few minutes using a cron job.  See cron.yaml"""

        print('============in TurnNotification============')
        #get all games in play
        activeGames = GameStateRepository().allActive()
        #get those NOT updated in the last five minutes
        idleGames = [game for game in activeGames
            if (datetime.datetime.now - elem.lastUpdate).total_seconds() > 300]

        #get list of users whose turn it is
        usersUp = [game.nextPlayer().user for game in idleGames]

        #filter by those who have not been notified in the last day
        notifications = NotificationRepository()
        usersNotified = notifications.getUsersRecentlyNotified()
        usersToNotify = [user for user in usersUp if not user.name in usersNotified]

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
