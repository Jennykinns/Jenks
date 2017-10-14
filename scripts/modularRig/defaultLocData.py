def getLegLocData(scale):
    legLocs = {
        (0, 'hip') : {
            'translate' : [1, 6, 0],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale': [(scale, scale, scale)]
        },
        (1, 'knee') : {
            'translate' : [1, 3.5, 0.2],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale': [(scale, scale, scale)]
        },
        (2, 'ankle') : {
            'translate' : [1, 1, 0],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale': [(scale, scale, scale)]
        },
        (3, 'footHeel') : {
            'translate' : [1, 0, 0],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale': [(scale, scale, scale)]
        },
        (4, 'footBall') : {
            'translate' : [1, 0, 1],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale': [(scale, scale, scale)]
        },
        (5, 'footToes') : {
            'translate' : [1, 0, 2],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale': [(scale, scale, scale)]
        },
    }
    return legLocs


def getArmLocData(scale):
    armLocs = {
        (0, 'clav') : {
            'translate' : [0.5, 14, 0],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale,)],
        },
        (1, 'shoulder') : {
            'translate' : [2, 14, -0.5],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale,)],
        },
        (2, 'elbow') : {
            'translate' : [4.5, 14, -0.7],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale,)],
        },
        (3, 'wrist') : {
            'translate' : [7, 14, -0.5],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale,)],
        },
        (4, 'handPalm') : {
            'translate' : [8, 14, -0.5],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale,)],
        },
    }
    return armLocs


def getFngrLocData(scale):
    fngrIndexLocs = {
        (0, 'fngrIndex_base') : {
            'translate' : [8.7, 14, -0.15],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (1, 'fngrIndex_lowMid') : {
            'translate' : [9, 14.1, -0.15],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (2, 'fngrIndex_highMid') : {
            'translate' : [9.3, 14.1, -0.15],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (3, 'fngrIndex_tip') : {
            'translate' : [9.6, 14, -0.15],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
    }
    fngrMiddleLocs = {
        (0, 'fngrMiddle_base') : {
            'translate' : [8.7, 14, -0.45],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (1, 'fngrMiddle_lowMid') : {
            'translate' : [9, 14.1, -0.45],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (2, 'fngrMiddle_highMid') : {
            'translate' : [9.3, 14.1, -0.45],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (3, 'fngrMiddle_tip') : {
            'translate' : [9.6, 14, -0.45],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
    }
    fngrRingLocs = {
        (0, 'fngrRing_base') : {
            'translate' : [8.7, 14, -0.75],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (1, 'fngrRing_lowMid') : {
            'translate' : [9, 14.1, -0.75],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (2, 'fngrRing_highMid') : {
            'translate' : [9.3, 14.1, -0.75],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (3, 'fngrRing_tip') : {
            'translate' : [9.6, 14, -0.75],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
    }
    fngrPinkyLocs = {
        (0, 'fngrPinky_base') : {
            'translate' : [8.7, 14, -1.05],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (1, 'fngrPinky_lowMid') : {
            'translate' : [9, 14.1, -1.05],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (2, 'fngrPinky_highMid') : {
            'translate' : [9.3, 14.1, -1.05],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (3, 'fngrPinky_tip') : {
            'translate' : [9.6, 14, -1.05],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
    }
    fngrThumbLocs = {
        (0, 'fngrThumb_base') : {
            'translate' : [8, 14, 0.3],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (1, 'fngrThumb_lowMid') : {
            'translate' : [8.3, 14.1, 0.3],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (2, 'fngrThumb_highMid') : {
            'translate' : [8.6, 14.1, 0.3],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (3, 'fngrThumb_tip') : {
            'translate' : [8.9, 14, 0.3],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
    }
    return fngrIndexLocs, fngrMiddleLocs, fngrRingLocs, fngrPinkyLocs, fngrThumbLocs

def getToeLocData(scale):
    toeIndexLocs = {
        (0, 'toeIndex_base') : {
            'translate' : [0.8, 0, 1.45],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (1, 'toeIndex_lowMid') : {
            'translate' : [0.8, 0.07, 1.6],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (2, 'toeIndex_highMid') : {
            'translate' : [0.8, 0.06, 1.75],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (3, 'toeIndex_tip') : {
            'translate' : [0.8, 0, 1.9],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
    }
    toeMiddleLocs = {
        (0, 'toeMiddle_base') : {
            'translate' : [1, 0, 1.45],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (1, 'toeMiddle_lowMid') : {
            'translate' : [1, 0.07, 1.6],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (2, 'toeMiddle_highMid') : {
            'translate' : [1, 0.06, 1.75],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (3, 'toeMiddle_tip') : {
            'translate' : [1, 0, 1.9],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
    }
    toeRingLocs = {
        (0, 'toeRing_base') : {
            'translate' : [1.2, 0, 1.45],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (1, 'toeRing_lowMid') : {
            'translate' : [1.2, 0.07, 1.6],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (2, 'toeRing_highMid') : {
            'translate' : [1.2, 0.06, 1.75],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (3, 'toeRing_tip') : {
            'translate' : [1.2, 0, 1.9],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
    }
    toePinkyLocs = {
        (0, 'toePinky_base') : {
            'translate' : [1.4, 0, 1.45],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (1, 'toePinky_lowMid') : {
            'translate' : [1.4, 0.07, 1.6],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (2, 'toePinky_highMid') : {
            'translate' : [1.4, 0.06, 1.75],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (3, 'toePinky_tip') : {
            'translate' : [1.4, 0, 1.9],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
    }
    toeThumbLocs = {
        (0, 'toeThumb_base') : {
            'translate' : [0.6, 0, 1.45],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (1, 'toeThumb_lowMid') : {
            'translate' : [0.6, 0.07, 1.6],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (2, 'toeThumb_highMid') : {
            'translate' : [0.6, 0.06, 1.75],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
        (3, 'toeThumb_tip') : {
            'translate' : [0.6, 0, 1.9],
            'rotate' : [0, 0, 0],
            'scale' : [1, 1, 1],
            'localScale' : [(scale, scale, scale)]
        },
    }
    return toeIndexLocs, toeMiddleLocs, toeRingLocs, toePinkyLocs, toeThumbLocs


def getHeadLocData(scale, side):
    if (side is not 'L' and 'L_' not in side and '_L' not in side
            and side is not 'R' and 'R_' not in side and '_R' not in side):
        headLocs = {
            (0, 'head') : {
                'translate' : [0, 15.5, -0.6],
                'rotate' : [0, 0, 0],
                'scale' : [1, 1, 1],
                'localScale' : [(scale, scale, scale)]
            },
            (1, 'headEnd') : {
                'translate' : [0, 17, -0.4],
                'rotate' : [0, 0, 0],
                'scale' : [1, 1, 1],
                'localScale' : [(scale, scale, scale)]
            },
        }
        headAimPos = [0, 16.25, 10]
    else:
        headLocs = {
            (0, 'head') : {
                'translate' : [1, 15.5, -0.6],
                'rotate' : [0, 0, 0],
                'scale' : [1, 1, 1],
                'localScale' : [(scale, scale, scale)]
            },
            (1, 'headEnd') : {
                'translate' : [1.5, 17, -0.4],
                'rotate' : [0, 0, 0],
                'scale' : [1, 1, 1],
                'localScale' : [(scale, scale, scale)]
            },
        }
        headAimPos = [1, 16.25, 10]

    return headLocs, headAimPos