from models import User, GameState, PlayerState

"""Utility view object to print world wars model."""
class PrintView(object):

	"""Print game state to console."""
	def showGameState(self, gameState):
		print("Board:")
		boardString = ''.join(gameState.boardContent)
		for y in range(gameState.height):
			start = y * gameState.width
			end = start + gameState.width
			print(boardString[start:end])
		for p in gameState.players:
			print("Player {} has score {} and letters '{}'".format(p.player.name, p.score, p.bag.asString()))
		if gameState.gameOver():
			print("Game over.  {} is the winner.".format(gameState.leader().player.name))
		else:
			print("Next turn belongs to {}".format(gameState.nextPlayer().player.name))
