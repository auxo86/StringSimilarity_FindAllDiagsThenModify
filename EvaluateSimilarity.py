from algorism import fxStrSimilarity

strCharForEliminated = ' ()[]{}!@#$^&*_-+/\'\"\t\r\n'
# listScoreAndCS = fxStrSimilarity('abcbcdgz', 'abcdgz', strCharForEliminated)
listScoreAndCS = fxStrSimilarity('!STIVARGA FC TAB 40 MG', 'Stivarga Film-Coated Tablets 40mg_臺灣拜耳股份有限公司_BAYER AG', strCharForEliminated)
print(listScoreAndCS)
