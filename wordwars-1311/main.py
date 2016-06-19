#!/usr/bin/env python
"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""


import webapp2
from google.appengine.api import mail, app_identity
from repositories import GameStateRepository, NotificationRepository

from models import User, GameState


class TurnNotification(webapp2.RequestHandler):
    def get(self):
        """Find users who need reminder to play their turn.
        Send a reminder email to each with instructions to play.
        Record the notification so we don't annoy users with repeat email.
        Called every few minutes using a cron job.  See cron.yaml.
        TODO: consider holding notifications for users that indicate they
        do not want to be bothered, at night time for example."""

        # send email notification
        app_id = app_identity.get_application_id()
        users = User.query(User.email != None)
        for playerState in GameStateRepository().playersToNotify():
            user = playerState.player
            if user.email:
                # remember notification so we don't harass the user repeatedly
                NotificationRepository().registerTurnNotification(
                    user, playerState.game)
                subject = 'This is a reminder!'
                body = 'Hello {}, its your turn to play WordWars!'.format(
                    user.name)
                mail.send_mail(
                    'noreply@{}.appspotmail.com'.format(app_id),
                    user.email,
                    subject,
                    body)


app = webapp2.WSGIApplication([
    ('/crons/turn_notification', TurnNotification),
], debug=True)
