#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
Create an svg timeplan from a csv timelist.

[extended_summary]
"""

import datetime as dt
import dateutil as dl
import svgwrite
import pandas as pd
import csv
import math
from functools import reduce

# for later - TODO
# import os
# import sys
# import argparse as ap

#temporary, should be replaced with argparse - TODO
hP = 140
svgParameters = {
    'maxWidthPx': 640, 
    'heightPx': hP,  
    'totalLengthPx': 5120,
    'fontSize': int(hP/5),
    'verticalSpace': .05*hP,
    #'xStart': 10, 
    'yStart': 10,
    'fontFamily': 'Consolas', 
    'textFill': 'white',
    'boxFill': 'black', 
    'textIndentProportion': .05,
    'outputFilename': 'svgOut.svg',
    'inputFilename': 'datelist.csv'
}

def eventDurationAndContinuity(startDatetime, endDatetime):
    if endDatetime < startDatetime:
        currentDateErrorText = f'''Detected start datetime {startDatetime} after end datetime {endDatetime}.'''
        raise ValueError(currentDateErrorText)
    else: 
        return endDatetime-startDatetime

def calcNanosecsFromPandasTimedelta(pdTd):
    # https://pandas.pydata.org/pandas-docs/version/0.25/reference/api/pandas.Timedelta.html 
    return (1000000000*(pdTd.days*86400 + pdTd.seconds) + pdTd.microseconds + pdTd.nanoseconds)

def createDfSet(fullDf):
    collection = []
    exportOverlapping(fullDf, collection)
    return collection

def exportOverlapping(oldDf, dfCollection):
    oldDf['pdNextInterval']= oldDf['pdInterval'].shift(-1)
    oldDf['pdOverlap'] = oldDf.apply(lambda row: (row['pdInterval'].overlaps(row['pdNextInterval'])) 
                           if (pd.notna(row['pdNextInterval'])) 
                           else False, 
                           axis=1)

    if (True in oldDf['pdOverlap'].values):
        newDf = pd.DataFrame(columns = oldDf.columns)
        cond = oldDf.pdOverlap == True
    
        while (True in oldDf['pdOverlap'].values):
            rows = oldDf.loc[cond, :]
            newDf = newDf.append(rows, ignore_index=True)
            oldDf.drop(rows.index, inplace=True)
            oldDf['pdNextInterval']= oldDf['pdInterval'].shift(-1)
            oldDf['pdOverlap'] = oldDf.apply(lambda row: (row['pdInterval'].overlaps(row['pdNextInterval'])) 
                               if (pd.notna(row['pdNextInterval'])) 
                               else False, 
                               axis=1)
        exportOverlapping(newDf, dfCollection)
        
    dfCollection.append(oldDf)

def importAndProcessDataIntoDataframe(inputFile):
    df = pd.read_csv(inputFile, delimiter='\t')

    df['dtStart'] = df.apply(lambda row: dl.parser.parse(row['START']), axis = 1)
    
    df = df.sort_values(by='dtStart', ascending=True).reset_index(drop=True)
    
    df['dtEnd'] = df.apply(lambda row: dl.parser.parse(row['END']), axis = 1)
    df['dtDuration'] = df.apply(lambda row: eventDurationAndContinuity(row['dtStart'], row['dtEnd']), axis=1)
    
    df['pdInterval'] = df.apply(lambda row: pd.Interval((row['dtStart']), (row['dtEnd']), closed='neither'), axis = 1)
    df['pdNextInterval']= df['pdInterval'].shift(-1)
    
    timeZero = df['dtStart'].min()
    df['svgStart'] = df.apply(lambda row: calcNanosecsFromPandasTimedelta(row['dtStart']-timeZero), axis = 1)
    df['svgDuration'] = df.apply(lambda row: calcNanosecsFromPandasTimedelta(row['dtDuration']), axis=1)
    df['svgEnd'] = df.apply(lambda row: row['svgStart'] + row['svgDuration'], axis=1)
    
    gcd = reduce(lambda x, y: math.gcd(x, y), pd.concat([df['svgStart'], df['svgDuration'], df['svgEnd']]))
    
    df[['svgStart','svgDuration','svgEnd']] = (df[['svgStart','svgDuration','svgEnd']] / gcd).astype(int)
    
    svgMin = df['svgStart'].min() # this SHOULD be 0
    svgMax = df['svgEnd'].max()
    
    # now scale that according to the desired svg sizes
    scalefactor = (svgMax-svgMin)/svgParameters['totalLengthPx']
    
    df[['svgStart','svgDuration','svgEnd']] = (df[['svgStart','svgDuration','svgEnd']] / scalefactor)
    
    ds =createDfSet(df)
    
    return ds

def createSvgFromDataframe(pandasDataFrameSet):
    dwg = svgwrite.Drawing(filename=svgParameters['outputFilename'], debug=True)

    y0 = svgParameters['yStart']

    for idx, val in enumerate(pandasDataFrameSet):
        # begin svg row (one dataframe per row)
        # in this row, iterate over all events: 
        for idxInner, valInner in enumerate(list(list(val.itertuples(index=False, name=None)))):
            dwg.add(dwg.rect((valInner[-4], y0), (valInner[-3], svgParameters['heightPx']), fill=svgParameters['boxFill']))
            dwg.add(dwg.text(valInner[2], insert=(valInner[-4] + svgParameters['textIndentProportion']*valInner[-3], y0 + (.5*svgParameters['heightPx'])), fill = svgParameters['textFill'], font_family = svgParameters['fontFamily'], font_size = svgParameters['fontSize']))
        # add vertical space for next box row
        y0 = y0 + svgParameters['heightPx'] + svgParameters['verticalSpace']

    dwg.save()

def main():
    createSvgFromDataframe(importAndProcessDataIntoDataframe(svgParameters['inputFilename']))

if __name__ == '__main__':
    main()