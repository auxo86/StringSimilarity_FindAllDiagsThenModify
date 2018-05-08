from algorism import fxStrSimilarity

strCharForEliminated = ' ()[]{}!@#$^&*_-+/\'\"\t\r\n'
listScoreAndCS = fxStrSimilarity('abcbcdgz', 'abcdgz', strCharForEliminated)
print(listScoreAndCS)
