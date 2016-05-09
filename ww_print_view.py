#!/usr/bin/env python

# view object to print world wars model state to console.
from ww_models import User, GameState, PlayerState

class PrintView(object):

	def showGameState(self, gameState):
		board = gameState.boardContent
		print("Board:")
		for y in range(gameState.height):
			start = y * gameState.width
			end = start + gameState.width
			print(gameState.boardContent[start:end])
		for p in gameState.players:
			print("Player {} has score {} and letters '{}'".format(p.player.name, p.score, p.letters.asString()))
		if gameState.gameOver():
			print("Game over.  {} is the winner.".format(gameState.leader().player.name))
		else:
			print("Next turn belongs to {}".format(gameState.nextPlayer().player.name))


