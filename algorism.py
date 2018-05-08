def fxStrSimilarity(str1, str2, strCharForEliminated):
    listStrings = [str1, str2]
    # 定義所有找到的對角線的list[[dict起點, 對角線長度], [dict起點, 對角線長度]....]
    listAllTmpDiags = []
    # 縱橫軸匹配到的禁區做list
    listXAxisRestrictedZone = []
    listYAxisRestrictedZone = []
    # 定義回傳相似度list
    listResult = []
    # 定義比對到的字串
    strCS = ''
    # 幫字串去前後空白，並且轉小寫，再去掉點，例如40i.u. -> 40iu
    for itemIDX in range(len(listStrings)):
        listStrings[itemIDX] = listStrings[itemIDX].strip().lower().replace('.', '')

    # 當前後元素不相等的時候就先去掉雜七雜八的字元還有空白，
    if listStrings[0] != listStrings[1]:
        for stringIDX in range(len(listStrings)):
            for char in listStrings[stringIDX]:
                if char in strCharForEliminated:
                    listStrings[stringIDX] = listStrings[stringIDX].replace(char, '|')

        # 前置處理完比對的字串後，判斷分母是否為0，也就是沒有要比對的藥品名稱
        # 如果沒有藥名，直接回傳 listResult = [0, '']
        if len(listStrings[0]) == 0:
            listResult = [0, '']
            return listResult

        # 先建立evaluation metrics，建立2-dimention時要注意python特有的深淺複製的問題
        listMetrics = [[0] * len(listStrings[0]) for i in range(len(listStrings[1]))]
        # 用雙層迴圈填入比對字元後的結果填入Metrics(相同為1，不同為0)
        for idxY in range(len(listStrings[1])):
            for idxX in range(len(listStrings[0])):
                if listStrings[0][idxX] == listStrings[1][idxY]:
                    listMetrics[idxY][idxX] = 1
                else:
                    listMetrics[idxY][idxX] = 0

        # 相似分數的分母是str1去掉空白和奇奇怪怪符號後剩下字串長度的平方
        numSimilarityScoreDenominator = len(listStrings[0]) ** 2
        # 相似分數的分子預設為0
        numSimilarityScoreNumerator = 0
        # 暫存對角線長度
        numTempLengthDiagonal = 0
        # 真正最長的對角線長度
        numLengthDiagonalProjectOnXAxis = 0
        # 紀錄暫存對角線起點座標資訊
        # coordinateTempDiag = {'x': 0, 'y': 0}----------------------------------------------
        # 紀錄本層最長對角線起點座標資訊
        coordinateDiag = {'x': None, 'y': None}

        # 找所有的對角線
        for idxY in range(len(listStrings[1])):
            if listStrings[1][idxY] == '|':
                continue
            for idxX in range(len(listStrings[0])):
                # 如果比對的字串遇到分隔符號|，就跳過本次iteration
                if listStrings[0][idxX] == '|':
                    continue
                # 本條對角線的起點(idxY, idxX)
                numTempLengthDiagonal = fxFindTempLengthDiagonal(listStrings, listMetrics, idxX, idxY, listXAxisRestrictedZone)
                if numTempLengthDiagonal > 1:
                    coordinateDiag['x'] = idxX
                    coordinateDiag['y'] = idxY
                    listAllTmpDiags.append([dict(coordinateDiag), numTempLengthDiagonal])
        while len(listAllTmpDiags) > 0:
            # 去除長度<=1的對角線
            listAllTmpDiags = list(filter(lambda x: x[1] > 1, listAllTmpDiags))
            # 找最長的那一條
            TheLongestDiag = max(listAllTmpDiags, key=lambda x: x[1])
            # 算分子並且記錄到有效對角線的strCS
            numSimilarityScoreNumerator = numSimilarityScoreNumerator + TheLongestDiag[1] ** 2
            strCS = strCS + listStrings[0][TheLongestDiag[0]['x']:TheLongestDiag[0]['x'] + TheLongestDiag[1]] + '|'
            # 設定縱橫軸禁區
            listXAxisRestrictedZone += list(range(TheLongestDiag[0]['x'], TheLongestDiag[0]['x'] + TheLongestDiag[1]))
            listYAxisRestrictedZone += list(range(TheLongestDiag[0]['y'], TheLongestDiag[0]['y'] + TheLongestDiag[1]))
            # 從listAllDiag移除最長的那一條
            listAllTmpDiags.remove(TheLongestDiag)
            # 移除對角線起點x座標跟最長對角線一樣的對角線們
            listAllTmpDiags = list(filter(lambda tmpDiag: tmpDiag[0]['x'] != TheLongestDiag[0]['x'], listAllTmpDiags))
            # 移除對角線起點y座標跟最長對角線一樣的對角線們
            listAllTmpDiags = list(filter(lambda tmpDiag: tmpDiag[0]['y'] != TheLongestDiag[0]['y'], listAllTmpDiags))
            # listAllTmpDiags2用來暫存加工過濾過的tempDiag
            listAllTmpDiags2 = []
            # 每一條對角線可以分三種情形：
            #   起點小於最長對角線的頭(身體有可能在禁區內或是禁區外)
            #   起點等於最長對角線的頭(身體一定在禁區內，會被濾掉)
            #   起點大於對角線的頭(身體有可能在禁區內或是禁區外)
            # 但是起點等於最長對角線的頭的已經被濾掉了，所以剩下兩種。
            for tempDiag in listAllTmpDiags:
                # 起點小於最長對角線的頭(身體有可能在禁區內或是禁區外)
                if tempDiag[0]['x'] < TheLongestDiag[0]['x']:
                    # 當對角線有重疊到禁區的，就裁掉落入禁區的那一段，同時要確保裁切後的對角線長度>1；如果檢查都沒問題，就會原樣直接出迴圈
                    for tmpX in range(tempDiag[0]['x'], tempDiag[0]['x'] + tempDiag[1]):
                        # 身體落入禁區還分兩種情況
                        if tmpX in listXAxisRestrictedZone and (tmpX - tempDiag[0]['x']) > 1:
                            tempDiag = [tempDiag[0], tmpX - tempDiag[0]['x']]
                            break
                        elif tmpX in listXAxisRestrictedZone and (tmpX - tempDiag[0]['x']) == 1:
                            # 放棄這條對角線
                            tempDiag[0]['x'] = None
                            tempDiag[0]['y'] = None
                            tempDiag = [tempDiag[0], 0]
                            break
                    # 身體落在禁區的會裁切，沒有落在禁區的會整段出來。不論有沒有裁切過，都會加入到listAllTmpDiags2
                    listAllTmpDiags2.append(tempDiag)
                # 起點大於對角線的頭(身體有可能在禁區內或是禁區外)
                else:
                    for tmpX in range(tempDiag[0]['x'], tempDiag[0]['x'] + tempDiag[1]):
                        if tmpX in listXAxisRestrictedZone:
                            continue
                        break
                    # 跑到這裡有兩種可能：
                    #   整條對角線都在禁區內，直接放棄這條對角線
                    #   表示頭已經跑出禁區外，重設這條對角線的頭
                    # 所以跑到這裡要判斷長度

                    # 整體長度還>2，保留這條對角線
                    # 如果整條在禁區裡，這條對角線長度最多等於1
                    if (tempDiag[0]['x'] + tempDiag[1] - tmpX) > 1:
                        tempDiag[1] = tempDiag[0]['x'] + tempDiag[1] - tmpX
                        tempDiag[0]['y'] += (tmpX - tempDiag[0]['x'])
                        tempDiag[0]['x'] = tmpX
                        tempDiag = [tempDiag[0], tempDiag[1]]
                    else:
                        # 整條對角線都在禁區內，直接放棄這條對角線
                        # 或是跑出禁區外但是整體長度只剩下1
                        tempDiag[0]['x'] = None
                        tempDiag[0]['y'] = None
                        tempDiag = [tempDiag[0], 0]
                    if tempDiag[1] == 0:
                        continue
                    listAllTmpDiags2.append(tempDiag)
            # listAllTmpDiags2會收集到這一輪剩下有效的對角線，然後看看要不要繼續跑while迴圈
            listAllTmpDiags = listAllTmpDiags2
        # 跑完比對迴圈後算分
        numSimilarityScore = numSimilarityScoreNumerator / numSimilarityScoreDenominator
    else:
        numSimilarityScore = 1
        strCS = listStrings[0] + '|'

    # 再加入結果之前先判斷到底對到什麼，如果什麼都沒有對到，就維持listStrCS為''；如果有對到，移除最後一個|
    if strCS != '':
        strCS = strCS[:-1]
    listResult = [numSimilarityScore, strCS]

    return listResult

def fxFindTempLengthDiagonal(listStrings, listMetrics, diagX, diagY, listXAxisMatchedZone):
    numTmpLenDiag = 0
    try:
        while listMetrics[diagY][diagX] == 1:
            # 發現對角線的第一格，暫存對角線長度加一
            numTmpLenDiag += 1
            # 座標往下移動一個對角格
            diagX += 1
            diagY += 1
            if diagX in listXAxisMatchedZone or listStrings[1][diagY] == '|' or listStrings[0][diagX] == '|':
                # 落入禁區或是比對的字串中出現|，就return
                return numTmpLenDiag
    except IndexError as e:
        # 超出邊界就return
        return numTmpLenDiag
    # 找完整條當然也要return
    return numTmpLenDiag

# 把輸入的list先依照相似分數由大排到小
# 取符合最大分數的那些items再依照藥品字數由小排到大
# 再取符合最少字的那些items
def fxGetExactMatchedItems(listIuput, numMaxNumOfMatchedItems):
    # 取出配對最高分
    numMaxScore = max(listIuput, key=lambda x: x[1][0])[1][0]
    # 如果0分，就回傳無匹配
    if numMaxScore == 0:
        return [[('無匹配', '', '', ''), [0, '']]]
    # 取出分數最高的items
    listMostSimilarItems = list(filter(lambda x: x[1][0] > numMaxScore - 0.01, listIuput))
    listMostSimilarItems = sorted(listMostSimilarItems, key=lambda x: x[1][0], reverse=True)
    # 如果筆數大於numMaxNumOfMatchedItems，只取numMaxNumOfMatchedItems筆
    if len(listMostSimilarItems) > numMaxNumOfMatchedItems:
        listMostSimilarItems = listMostSimilarItems[0:numMaxNumOfMatchedItems]
    # 找到名稱最短的字典item的字數
    # numMinNameLength = len(min(listMostSimilarItems, key=lambda x: len(x[0][0]))[0][0])
    # 取出字數最少的那些items
    # listMostSimilarItems = list(filter(lambda x: len(x[0][0]) == numMinNameLength, listMostSimilarItems))
    return listMostSimilarItems

def fxCalSimilarity(DictItem, MedItem, strCharForEliminated):
    listSimilarity = fxStrSimilarity(MedItem[2], DictItem[0], strCharForEliminated)
    return [DictItem, listSimilarity]
