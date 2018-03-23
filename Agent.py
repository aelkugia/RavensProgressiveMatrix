# Your Agent for solving Raven's Progressive Matrices. You MUST modify this file.
#
# You may also create and submit new files in addition to modifying this file.
#
# Make sure your file retains methods with the signatures:
# def __init__(self)
# def Solve(self,problem)
#
# These methods will be necessary for the project's main method to run.

# Install Pillow and uncomment this line to access image processing.

from PIL import Image
from PIL import ImageOps
import numpy as np

count = 0


# Return pixels for a given Figure as '1' for blackpixels
def getPixels(image):
    retArray = np.asarray(image.convert('1')).astype(np.int)

    return 1 - retArray


# Add, subtract function comparing A to B
def compute(pixelsA, pixelsB, size):
    return np.abs(pixelsB - pixelsA)


# Check how many pixels within 2-D array of X-Y are the same and compare to 90%
def percentSame(pixelsA, pixelsB, thresh=0.98):
    matrixComp = np.equal(pixelsA, pixelsB).astype(int)
    m = np.mean(matrixComp)
    return m > thresh, m

    width, height = (184, 184)
    match = 0
    for x in range(width):
        for y in range(height):
            if pixelsA[x][y] == pixelsB[x][y]:
                match += 1
    return (match / (184 * 184) > thresh, match / (184 * 184))


# Loop through the possible solutions to find which one meets the percentSame threshold
def check(pixelsD, solPixels, thresh=0.99):
    percent = 0
    returnValue = -1
    for index, element in enumerate(solPixels):
        similiar, moreSimiliar = percentSame(pixelsD, element, thresh=thresh)
        if similiar and (moreSimiliar > percent):
            returnValue = index + 1
            percent = moreSimiliar
    return returnValue


# Count black pixels in figure
def countBlackPixels(pixelsA):
    return np.sum(pixelsA)


# Creating list of counts of Pixels in each figure
def convertPixelList(pixelList):
    return [countBlackPixels(pl) for pl in pixelList]


# To check which index is the sum (if one exists of the other two figures)
def checkSumHelper(g1, g2, g3):
    if np.argmax(g1) != np.argmax(g2):  # checks if max of group 1 & 2 is at the same index
        return -1

    overlap1 = np.sum(g1) - 2 * np.max(g1)  # overlap => A+B-C or A+C-B or C+B-A for every row
    overlap2 = np.sum(g2) - 2 * np.max(g2)
    if np.abs(overlap1 - overlap2) / (184.0 * 184.0) < 0.077:
        con = np.mean([overlap1, overlap2])
        if np.argmax(g1) == 2:
            return g3[0] + g3[1] - con

        return np.max(g3) + con - np.min(g3)

    return -1


# A + C - B = constant or A + B - C or B + C - A
def checkSum(pixelCounts):
    row1 = pixelCounts[:3]
    row2 = pixelCounts[3:6]
    row3 = pixelCounts[6:8]

    retVal = checkSumHelper(row1, row2, row3)  # run checkSum on rows
    if retVal != -1:
        return retVal

    col1 = [pc for i, pc, in enumerate(pixelCounts) if i % 3 == 0]  # repeat checkSum on columns
    col2 = [pc for i, pc, in enumerate(pixelCounts) if i % 3 == 1]
    col3 = [pc for i, pc, in enumerate(pixelCounts) if i % 3 == 2]
    return checkSumHelper(col1, col2, col3)


# Initially check all object counts is the same in each row
# If count of objects is the same return that count then checks the solutions
# C-01
def checkRatiosHelper(g1, g2, g3):
    thresh = 0.001
    if np.sum(g1) == 0 and np.sum(g2) == 0 and np.sum(g3) == 0:
        return 0

    if np.abs(g1[0] - g1[1]) / np.mean(g1) < thresh and np.abs(g1[0] - g1[2]) / np.mean(g1) < thresh:
        if np.abs(g2[0] - g2[1]) / np.mean(g2) < thresh and np.abs(g2[0] - g2[2]) / np.mean(g2) < thresh:
            if np.abs(g3[0] - g3[1]) / np.mean(g3) < thresh:
                return np.mean(g3)

    max_index1 = np.argmax(g1)
    max_index2 = np.argmax(g2)
    if max_index1 != max_index2:  # checks if max of g 1 & 2 is at the same index
        return -1

    min_index1 = np.argmin(g1)
    min_index2 = np.argmin(g2)
    if min_index1 != min_index2:
        return -1

    normalizedg1 = [r - min(g1) for r in g1 if r != min(
        g1)]  # substract smallest count of object in a row, example: C-05 substract star for first row/column
    normalizedg2 = [r - min(g2) for r in g2 if r != min(g2)]

    if len(normalizedg1) == 0:
        if len(normalizedg2) == 0:
            return g3[0]
        else:
            return -1

    ratio1 = max(normalizedg1) / min(normalizedg1)
    ratio2 = max(normalizedg2) / min(normalizedg2)

    if ratio1 == 1.0:
        if ratio2 == 1.0:
            if max_index1 == 2:
                return -1
            else:
                return min(g3)

    if np.abs(ratio1 - ratio2) < 0.05:
        if max_index1 == 2:
            return min(g3) + ratio1 * (max(g3) - min(g3))

        if min_index1 == 2:
            return (max(g3) - ratio1 * min(g3)) / (1 - ratio1)

        return (max(g3) - min(g3)) / ratio1 + min(g3)

    return -1


def checkRatios(pixelCounts):
    row1 = pixelCounts[:3]
    row2 = pixelCounts[3:6]
    row3 = pixelCounts[6:8]

    retVal = checkRatiosHelper(row1, row2, row3)
    if retVal != -1:
        return retVal

    col1 = [pc for i, pc, in enumerate(pixelCounts) if i % 3 == 0]
    col2 = [pc for i, pc, in enumerate(pixelCounts) if i % 3 == 1]
    col3 = [pc for i, pc, in enumerate(pixelCounts) if i % 3 == 2]
    return checkRatiosHelper(col1, col2, col3)


# return list of figures that meet threshold for checkSum test
def checkNumPixelsFilter(numBlackPixels, solPixels, countMetric, thresh=0.024):
    filterSol = []
    for index, element in enumerate(solPixels):
        if np.abs(countMetric(element) - numBlackPixels) / (184.0 * 184.0) < thresh:
            filterSol.append(element)

    return filterSol


def checkLinesFilter(numLinesCrossed, solPixels, origSolPixels, lineType):
    newSolPixels = []
    for index, element in enumerate(solPixels):
        if countLinesCrossed(element, lineType) == numLinesCrossed:
            newSolPixels.append(element)

    #print("Potential solutions:", [getSolIndex(i, origSolPixels) for i in newSolPixels])
    if newSolPixels != []:
        solPixels = newSolPixels
        if len(solPixels) == 1:
            return solPixels, getSolIndex(solPixels[0], origSolPixels)

    return solPixels, -1


def getSolIndex(pixels, solPixels):
    for index, element in enumerate(solPixels):
        if np.array_equal(pixels, element):
            return index + 1
    return -1


# Intersection/Unions (E-02)
# Union of A & B you get C, union of D & E you get F (row and column)
# Function looks at pixels, not the count
def checkIntersectionHelper(g1, g2, g3, solPixels):
    thresh = 0.971
    if percentSame(g1[2], np.logical_and(g1[0], g1[1]), thresh=thresh)[0] and \
            percentSame(g2[2], np.logical_and(g2[0], g2[1]), thresh=thresh)[
                0]:  # percentSame with last image of row/column (logical_and)
        toCheck = np.logical_and(g3[0], g3[1])
        return check(toCheck, solPixels, thresh=thresh)

    if percentSame(g1[2], np.logical_or(g1[0], g1[1]), thresh=thresh)[0] and \
            percentSame(g2[2], np.logical_or(g2[0], g2[1]), thresh=thresh)[0]:  # logical_or
        toCheck = np.logical_or(g3[0], g3[1])
        return check(toCheck, solPixels, thresh=thresh)

    if percentSame(g1[2], np.logical_xor(g1[0], g1[1]), thresh=thresh)[0] and \
            percentSame(g2[2], np.logical_xor(g2[0], g2[1]), thresh=thresh)[0]:  # logical_xor
        toCheck = np.logical_xor(g3[0], g3[1])
        return check(toCheck, solPixels, thresh=thresh)  # adjust thresh for E-07

    return -1


def checkIntersection(pixelList, solPixels):
    row1 = pixelList[:3]
    row2 = pixelList[3:6]
    row3 = pixelList[6:8]

    retVal = checkIntersectionHelper(row1, row2, row3, solPixels)
    if retVal != -1:
        return retVal

    col1 = [pc for i, pc, in enumerate(pixelList) if i % 3 == 0]
    col2 = [pc for i, pc, in enumerate(pixelList) if i % 3 == 1]
    col3 = [pc for i, pc, in enumerate(pixelList) if i % 3 == 2]
    return checkIntersectionHelper(col1, col2, col3, solPixels)


# Check for each row/column to see if there is a pattern with count of pixels in terms of distribution
# Ex: D-02
#
def countDistribution(pixelCount, exact=False):
    row1 = pixelCount[:3]
    row2 = pixelCount[3:6]
    row3 = pixelCount[6:8]

    sortedRow1 = sorted(row1)
    sortedRow2 = sorted(row2)
    sortedRow3 = sorted(row3)

    for index in range(len(sortedRow1)):
        if exact:
            if sortedRow1[index] != sortedRow2[index]:
                return -1
        else:
            if np.abs(sortedRow1[index] - sortedRow2[index]) / (184 * 184) > 0.0045:
                return -1

    for index in range(len(sortedRow3)):
        if exact:
            if sortedRow1[index] != sortedRow3[index]:
                return sortedRow1[index]
        else:
            if np.abs(sortedRow1[index] - sortedRow3[index]) / (184 * 184) > 0.0045:
                return sortedRow1[index]

    return sortedRow1[2]


# Ex: C-07.
# Concatenate all figures' pixels into one, # figure = 0
# Check if satisfy mirror, rotate, flipAxis
def holistic(pixels, solPixels, origSolPixels):
    lastRow = pixels[6:]
    lastRow.append(np.zeros(pixels[0].shape))  # append zeros
    newSolPixels = []

    newImage = np.vstack([np.hstack(pixels[0: 3]), np.hstack(pixels[3:6]), np.hstack(lastRow)])

    #newImage = np.block([pixels[0:3], pixels[3:6], lastRow])  # concatenate figure's into one image
    if percentSame(newImage, np.transpose(newImage), thresh=0.98)[0]:  # check diagonal
        newSolPixels = [im for im in solPixels if percentSame(im, np.transpose(im))[0]]
        if len(newSolPixels) == 1:
            return newSolPixels
        elif len(newSolPixels) != 0:
            solPixels = newSolPixels

    lastRow = pixels[6:]  # Vertical
    lastRow.append(np.flipud(pixels[2]))  # append # figure with pixels of C
    newImage = np.vstack([np.hstack(pixels[0: 3]), np.hstack(pixels[3:6]), np.hstack(lastRow)])
    if percentSame(newImage, np.flipud(newImage), thresh=0.98)[0]:
        newSolPixels = [im for im in solPixels if percentSame(im, np.flipud(pixels[2]), thresh=0.98)[0]]
        if len(newSolPixels) == 1:
            return newSolPixels
        elif len(newSolPixels) != 0:
            solPixels = newSolPixels

    lastRow = pixels[6:]  # Horizontal
    lastRow.append(np.fliplr(pixels[6]))  # append # figure with pixels of G
    newImage = np.vstack([np.hstack(pixels[0: 3]), np.hstack(pixels[3:6]), np.hstack(lastRow)])
    if percentSame(newImage, np.fliplr(newImage), thresh=0.98)[0]:
        newSolPixels = [im for im in solPixels if percentSame(im, np.fliplr(pixels[6]), thresh=0.98)[0]]
        if len(newSolPixels) == 1:
            return newSolPixels
        elif len(newSolPixels) != 0:
            solPixels = newSolPixels

    return solPixels


# Gets count of white pixels outside of shape on one side
def outlineCount(pixels):
    firstBlackIndices = np.argmax(pixels, axis=1)
    firstBlackIndices[firstBlackIndices == 0] = pixels.shape[0]
    return np.sum(np.argmax(pixels, axis=1))

# Count how many black lines are crossed on vertical, horizontal, and both diagonals and return that count
def countLinesCrossed(pixels, lineType):
    inBlack = False
    if lineType == "vertical":
        countV = 0
        middleV = pixels.shape[1] // 2  # integer division
        for h in range(pixels.shape[0]):
            if not inBlack:
                if pixels[h, middleV] == 1:
                    countV += 1
                    inBlack = True
            else:
                if pixels[h, middleV] == 0:
                    inBlack = False
        return countV
    elif lineType == "horizontal":
        middleH = pixels.shape[1] // 2  # integer division
        countH = 0
        for c in range(pixels.shape[1]):
            if not inBlack:
                if pixels[middleH, c] == 1:
                    countH += 1
                    inBlack = True
            else:
                if pixels[middleH, c] == 0:
                    inBlack = False
        return countH
    elif lineType == "diagonal1":
        countD1 = 0
        for c in range(pixels.shape[1]):
            if not inBlack:
                if pixels[c, c] == 1:
                    countD1 += 1
                    inBlack = True
            else:
                if pixels[c, c] == 0:
                    inBlack = False
        return countD1
    else:
        countD2 = 0
        for c in range(pixels.shape[1]):
            if not inBlack:
                if pixels[-c, c] == 1:
                    countD2 += 1
                    inBlack = True
            else:
                if pixels[-c, c] == 0:
                    inBlack = False
        return countD2


def countLinesLists(pixelList):
    numLinesHorizontal = []
    numLinesVertical = []
    numLinesDiagonal1 = []
    numLinesDiagonal2 = []

    for im in pixelList:
        numLinesVertical.append(countLinesCrossed(im, "vertical"))
        numLinesHorizontal.append(countLinesCrossed(im, "horizontal"))
        numLinesDiagonal1.append(countLinesCrossed(im, "diagonal1"))
        numLinesDiagonal2.append(countLinesCrossed(im, "diagonal2"))

    return numLinesVertical, numLinesHorizontal, numLinesDiagonal1, numLinesDiagonal2


def updateSolPixelsOnCount(expectedCount, solPixels, origSolPixels, countMetric, thresh=0.022):
    if expectedCount != -1:
        newSolPixels = checkNumPixelsFilter(expectedCount, solPixels, countMetric, thresh=thresh)
        #print("Potential solutions:", [getSolIndex(i, origSolPixels) for i in newSolPixels])
        if newSolPixels != []:
            solPixels = newSolPixels
            if len(solPixels) == 1:
                return solPixels, getSolIndex(solPixels[0], origSolPixels)
    return solPixels, -1

#Removing the outline shape
def removeOutline(pixelList):
    for pixel in pixelList:
        for i in range(pixel.shape[0]): #loop through rows
            currPixelIndex = 0
            while currPixelIndex < pixel.shape[0]:
                firstBlackIndex = np.argmax(pixel[i, currPixelIndex:])
                if firstBlackIndex == 0:
                    break
                currPixelIndex += firstBlackIndex
                firstWhiteIndexAfter =  np.argmin(pixel[i, currPixelIndex:])
                if firstWhiteIndexAfter == 0:
                    firstWhiteIndexAfter = pixel[i, currPixelIndex:].shape[0]
                if firstWhiteIndexAfter - firstBlackIndex < 24:
                    pixel[i, currPixelIndex:currPixelIndex + firstWhiteIndexAfter].fill(0) #convert black outline to white pixel
                    currPixelIndex += firstWhiteIndexAfter

        for i in range(pixel.shape[0]): #loop through columns
            currPixelIndex = 0
            while currPixelIndex < pixel.shape[0]:
                firstBlackIndex = np.argmax(pixel[currPixelIndex:, i])
                if firstBlackIndex == 0:
                    break
                currPixelIndex += firstBlackIndex
                firstWhiteIndexAfter =  np.argmin(pixel[currPixelIndex:, i])
                if firstWhiteIndexAfter == 0:
                    firstWhiteIndexAfter = pixel[currPixelIndex:, i].shape[0]
                if firstWhiteIndexAfter - firstBlackIndex < 24:
                    pixel[currPixelIndex:currPixelIndex + firstWhiteIndexAfter, i].fill(0) #convert black outline to white pixel
                    currPixelIndex += firstWhiteIndexAfter

    return pixelList

def problemSolverForPixelList(pixels, solPixels, origSolPixels):
    pixelCounts = convertPixelList(pixels)

    #print("checkRatios")
    numPixelsRatios = checkRatios(pixelCounts)
    solPixels, retVal = updateSolPixelsOnCount(numPixelsRatios, solPixels, origSolPixels, countBlackPixels)
    if retVal != -1:
        return retVal

    #print("checkSum")
    numPixelsSum = checkSum(pixelCounts)
    solPixels, retVal = updateSolPixelsOnCount(numPixelsSum, solPixels, origSolPixels, countBlackPixels)
    if retVal != -1:
        return retVal

    retVal = checkIntersection(pixels, origSolPixels)
    if retVal != -1:
        return retVal

    #print("Distribution")
    numDistribution = countDistribution(pixelCounts)
    solPixels, retVal = updateSolPixelsOnCount(numDistribution, solPixels, origSolPixels, countBlackPixels)
    if retVal != -1:
        return retVal

    solPixels = holistic(pixels, solPixels, origSolPixels)
    if len(solPixels) == 1:
        return getSolIndex(solPixels[0], origSolPixels)

    # reference pixel list (separe tuple to two lists)
    numLinesVertical, numLinesHorizontal, numLinesDiagonal1, numLinesDiagonal2 = countLinesLists(pixels)
    #print("numLinesVerticalRatio")
    numLinesV = checkRatios(numLinesVertical)
    if numLinesV != -1:
        solPixels, retVal = checkLinesFilter(numLinesV, solPixels, origSolPixels, "vertical")
        if retVal != -1:
            return retVal

    #print("numLinesHorizontalRatio")
    numLinesH = checkRatios(numLinesHorizontal)
    if numLinesH != -1:
        solPixels, retVal = checkLinesFilter(numLinesH, solPixels, origSolPixels, "horizontal")
        if retVal != -1:
            return retVal

    #print("numLinesDiagonal1Ratio")
    numLinesD1 = checkRatios(numLinesDiagonal1)
    if numLinesD1 != -1:
        solPixels, retVal = checkLinesFilter(numLinesD1, solPixels, origSolPixels, "diagonal1")
        if retVal != -1:
            return retVal

    #print("numLinesDiagonal2Ratio")
    numLinesD2 = checkRatios(numLinesDiagonal2)
    if numLinesD2 != -1:
        solPixels, retVal = checkLinesFilter(numLinesD2, solPixels, origSolPixels, "diagonal2")
        if retVal != -1:
            return retVal

    #print("numLinesVerticalDistribution")
    numLinesV = countDistribution(numLinesVertical, exact=True)
    if numLinesV != -1:
        solPixels, retVal = checkLinesFilter(numLinesV, solPixels, origSolPixels, "vertical")
        if retVal != -1:
            return retVal

    #print("numLinesHorizontalDistribution")
    numLinesH = countDistribution(numLinesHorizontal, exact=True)
    if numLinesH != -1:
        solPixels, retVal = checkLinesFilter(numLinesH, solPixels, origSolPixels, "horizontal")
        if retVal != -1:
            return retVal

    #print("numLinesDiagonal1Distribution")
    numLinesD1 = countDistribution(numLinesDiagonal1, exact=True)
    if numLinesD1 != -1:
        solPixels, retVal = checkLinesFilter(numLinesD1, solPixels, origSolPixels, "diagonal1")
        if retVal != -1:
            return retVal

    #print("numLinesDiagonal2Distribution")
    numLinesD2 = countDistribution(numLinesDiagonal2, exact=True)
    if numLinesD2 != -1:
        solPixels, retVal = checkLinesFilter(numLinesD2, solPixels, origSolPixels, "diagonal2")
        if retVal != -1:
            return retVal

    #print("outlineCounts")
    outlineCounts = [outlineCount(im) for im in pixels]
    numDistribution = countDistribution(outlineCounts)
    solPixels, retVal = updateSolPixelsOnCount(numDistribution, solPixels, origSolPixels, outlineCount, thresh=0.0047)
    if retVal != -1:
        return retVal

    return solPixels

class Agent:
    # The default constructor for your Agent. Make sure to execute any
    # processing necessary before your Agent starts solving problems here.
    #
    # Do not add any variables to this signature; they will not be used by
    # main().
    def __init__(self):
        pass

    # The primary method for solving incoming Raven's Progressive Matrices.
    # For each problem, your Agent's Solve() method will be called. At the
    # conclusion of Solve(), your Agent should return an int representing its
    # answer to the question: 1, 2, 3, 4, 5, or 6. Strings of these ints
    # are also the Names of the individual RavensFigures, obtained through
    # RavensFigure.getName(). Return a negative number to skip a problem.
    #
    # Make sure to return your answer *as an integer* at the end of Solve().
    # Returning your answer as a string may cause your program to crash.

    def Solve(self, problem):

        returnVal = -1

        figures = problem.figures

        if (problem.problemType == '2x2'):

            imageA = Image.open(figures['A'].visualFilename)
            imageB = Image.open(figures['B'].visualFilename)
            imageC = Image.open(figures['C'].visualFilename)
            image1 = Image.open(figures['1'].visualFilename)
            image2 = Image.open(figures['2'].visualFilename)
            image3 = Image.open(figures['3'].visualFilename)
            image4 = Image.open(figures['4'].visualFilename)
            image5 = Image.open(figures['5'].visualFilename)
            image6 = Image.open(figures['6'].visualFilename)

            pixelsA = getPixels(imageA)
            pixelsB = getPixels(imageB)
            pixelsC = getPixels(imageC)

            pixels1 = getPixels(image1)
            pixels2 = getPixels(image2)
            pixels3 = getPixels(image3)
            pixels4 = getPixels(image4)
            pixels5 = getPixels(image5)
            pixels6 = getPixels(image6)

            solPixels = [pixels1, pixels2, pixels3, pixels4, pixels5, pixels6]

            if np.array_equal(pixelsA, pixelsB):
                pixelsD = pixelsC
                for index, element in enumerate(solPixels):
                    if np.array_equal(pixelsD, element):
                        returnVal = index + 1
                        break
            elif np.array_equal(pixelsA, pixelsC):
                pixelsD = pixelsB
                for index, element in enumerate(solPixels):
                    if np.array_equal(pixelsD, element):
                        returnVal = index + 1
                        break

            else:

                mirrorpixelsA = getPixels(ImageOps.mirror(imageA))
                flippixelsA = getPixels(ImageOps.flip(imageA))

                if returnVal == -1 and percentSame(mirrorpixelsA, pixelsB)[1] > .95:
                    returnVal = check(getPixels(ImageOps.mirror(imageC)), solPixels)
                if returnVal == -1 and percentSame(mirrorpixelsA, pixelsC)[1] > .95:
                    returnVal = check(getPixels(ImageOps.mirror(imageB)), solPixels)

                if returnVal == -1 and percentSame(flippixelsA, pixelsB)[1] > .98:
                    returnVal = check(getPixels(ImageOps.flip(imageC)), solPixels)
                if returnVal == -1 and percentSame(flippixelsA, pixelsC)[1] > .98:
                    returnVal = check(getPixels(ImageOps.flip(imageB)), solPixels)

                if returnVal == -1:

                    transformAB = compute(pixelsA, pixelsB, imageA.size)
                    transformAC = compute(pixelsA, pixelsC, imageA.size)

                    pixelsD1 = compute(transformAB, pixelsC, imageA.size)
                    pixelsD2 = compute(transformAC, pixelsB, imageA.size)
                    pixelsD = compute(pixelsD1, pixelsD2, imageA.size)

                    for index, element in enumerate(solPixels):
                        if np.array_equal(pixelsD, element) or np.array_equal(pixelsD1, element) or np.array_equal(
                                pixelsD2, element):
                            returnVal = index + 1
                            break

                    if returnVal == -1:
                        returnVal = check(pixelsD1, solPixels)
                    if returnVal == -1:
                        returnVal = check(pixelsD2, solPixels)
                    if returnVal == -1:
                        returnVal = check(pixelsD, solPixels)
            pass

        else:

            if (problem.problemType == '3x3'):

                names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
                solNames = ['1', '2', '3', '4', '5', '6', '7', '8']

                pixels = [getPixels(Image.open(figures[n].visualFilename)) for n in names]
                origSolPixels = [getPixels(Image.open(figures[n].visualFilename)) for n in solNames]
                solPixels = [getPixels(Image.open(figures[n].visualFilename)) for n in solNames]

                #print(problem.name)
                # check if pattern is A + B - C = constant and other permutations

                retVal = problemSolverForPixelList(pixels, solPixels, origSolPixels)
                if isinstance(retVal, int):
                    return retVal
                solPixels = retVal

                solPixelsIndices = [getSolIndex(i, origSolPixels) for i in solPixels]
                origSolPixels = [origSolPixels[i - 1] for i in solPixelsIndices]

                removeOutline(pixels)
                removeOutline(solPixels)
                removeOutline(origSolPixels)

                retVal = problemSolverForPixelList(pixels, solPixels, origSolPixels)
                if isinstance(retVal, int):
                    return solPixelsIndices[retVal - 1]
                solPixels = retVal

        return returnVal