#### Library Imports ####
import csv
import json
import xmltodict
import sys
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

#### Library Import Ends ####
#### Global Variable Definition ####

#### Global Variable Definition Ends ####
#### Format Conversion ####

def listTodic(lines, primeKey = None):
    output = {}
    keyNum = 0

    for l, _ in enumerate(lines):
        lines[l] = lines[l].split(",")
        for i in range(len(lines[l])):
            if lines[l][i][0] == " " or lines[l][i][0] == "\n":
                lines[l][i] = lines[l][i][1:]
            if lines[l][i][-1] == " " or lines[l][i][-1] == "\n":
                lines[l][i] = lines[l][i][:-1]
    
    if primeKey not None:
        for i in range(len(lines[0])):
            if primeKey == lines[0][i]:
                keyNum = i

    if keyNum == 0:
        primeKey = lines[0][0]

    output[primeKey] = {}
    for i in range(len(lines) - 1):
        output[primeKey][lines[i+1][keyNum]] = {}
        for j in range(len(lines[0]) - 1):
            if lines[0][j] not primeKey:
                output[primeKey][lines[i+1][keyNum]][lines[0][j]] = lines[i+1][j]

    return output

def csvTojson(csvfile, jsonfile, primeKey = None):
    f = open(csvfile, "r", encoding="utf8")
    lines = f.readlines()
    f.close()

    output = listTodic(lines, primeKey)

    with open(jsonfile, "w", encoding="utf8") as outfile:
        json.dump(output, outfile)

    return jsonfile


def dicRec(dic, output, layer, prev = None):
    if layer%2 == 0:
        if output == []:
            output.append(list(dic.keys()))
        else:
            for i in dic.keys():
                if i not in output[0]:
                    output[0].append(i)

        for i in dic.keys():
            if type(dic[i]) == dict:
                layer += 1
                output = dicRec(dic[i], output, layer, i)
            else:
                for k in len(range(output[0])):
                    if output[0][k] == i:
                        if output[-1][k] == None:
                            output[-1][k] = dic[i]
                        else:
                            t = [None] * len(output[0])
                            output.append(t)
                            output[-1][k] = dic[i]
                        
                        break
    else:
        for v in dic.keys():
            for i in len(range(output[0])):
                if output[0][i] == prev:
                    if output[-1][i] == None:
                        output[-1][i] = v
                    else:
                        t = [None] * len(output[0])
                        output.append(t)
                        output[-1][i] = v
                    
                    break

            if type(dic[v]) == dict:
                layer += 1
                output = dicRec(dic[v], output, layer)

    return output
    

def jsonTocsv(jsonfile, csvfile):
    data = {}
    with open(jsonfile, encoding="utf8") as json_file:
        data = json.load(json_file)

    output = []

    layer = 0
    output = dicRec(data, output, layer)

    with open(csvfile, "w", newline="", encoding="utf8") as f:
        writer = csv.writer(f)
        writer.writerows(output)

    return csvfile


def xmlTocsv(xmlFile, csvfile):
    contents = open(xmlFile).read()
    data = xmltodict.parse("\"\"\""+contents+"\"\"\"")

    layer = 0
    output = dicRec(data, output, layer)

    with open(csvfile, "w", newline="", encoding="utf8") as f:
        writer = csv.writer(f)
        writer.writerows(output)

    return csvfile

def xmlTojson(xmlFile, jsonfile):
    contents = open(xmlFile).read()

    output = xmltodict.parse("\"\"\""+contents+"\"\"\"")

    with open(jsonfile, "w", encoding="utf8") as outfile:
        json.dump(output, outfile)

    return jsonfile


def csvToxml(csvfile, xmlFile):
    f = open(csvfile, "r", encoding="utf8")
    lines = f.readlines()
    f.close()

    data = listTodic(lines, primeKey)
    output = xmltodict.unparse(data, pretty=True)

    f = open(xmlFile, "w")
    f.write(output)
    f.close()


def jsonToxml(jsonfile, xmlFile):
    data = {}
    with open(jsonfile, encoding="utf8") as json_file:
        data = json.load(json_file)
    output = xmltodict.unparse(data, pretty=True)

    f = open(xmlFile, "w")
    f.write(output)
    f.close()

#### Format Conversion Ends ####

#### Data Cleaning ####

def normalization(csvfile, pKey, lower, higher):
    f = open(csvfile, "r", encoding="utf8")
    lines = f.readlines()
    f.close()
    num = 0
    for i, _ in enumerate(lines[0]):
        if lines[0][i] == pKey:
            num = i
            break

    for i in range(1, len(lines)):
        lines[i][num] = (lines[i][num]*(higher - lower)) + lower

    with open(csvfile, "w", newline="", encoding="utf8") as f:
        writer = csv.writer(f)
        writer.writerows(lines)

    return csvfile

def outlier(csvfile, pKey, lower, higher):
    f = open(csvfile, "r", encoding="utf8")
    lines = f.readlines()
    f.close()
    num = 0
    for i, _ in enumerate(lines[0]):
        if lines[0][i] == pKey:
            num = i
            break

    tot = 0
    for i in range(1, len(lines)):
        if lines[i][num] > higher or lines[i][num] < lower:
            tot += 1
            del lines[i]


    with open(csvfile, "w", newline="", encoding="utf8") as f:
        writer = csv.writer(f)
        writer.writerows(lines)

    return csvfile, tot


def nullValues(csvfile, pKey, method, replacement = None):
    f = open(csvfile, "r", encoding="utf8")
    lines = f.readlines()
    f.close()
    num = 0
    for i, _ in enumerate(lines[0]):
        if lines[0][i] == pKey:
            num = i
            break

    if method == 1:
        tot = 0
        for i in range(1, len(lines)):
            if lines[i][num] == None or lines[i][num] == "" or lines[i][num] == " ":
                tot += 1
                del lines[i]
    elif method == 2:
        subs = 0
        if replacement == "Average":
            for i in range(1, len(lines)):
                subs += lines[i][num]
            if type(lines[1][num]) == int:
                subs = subs//(len(lines) - 1)
            elif type(lines[1][num]) == float:
                subs = subs/(len(lines) - 1)
        elif replacement == "Maximum":
            for i in range(1, len(lines)):
                if subs < lines[i][num]:
                    subs = lines[i][num]
        elif replacement == "Maximum":
            subs = sys.maxint
            for i in range(1, len(lines)):
                if subs > lines[i][num]:
                    subs = lines[i][num]
        else:
            pass

        for i in range(1, len(lines)):
            if lines[i][num] == None or lines[i][num] == "" or lines[i][num] == " ":
                tot += 1
                lines[i][num] = subs


    with open(csvfile, "w", newline="", encoding="utf8") as f:
        writer = csv.writer(f)
        writer.writerows(lines)

    return csvfile, tot

#### Data Cleaning Ends ####
#### Data Visualization ####

def columnRep(csvfile, graph, pkey):
    df = pd.read_csv(csvfile)
    data = df[pkey]
    bins = 0
    if type(data[1]) = int or type(data[1]) = float:
        mx = data.max()
        mn = data.min()
        bins = (mx - mn)
    elif type(data[1]) = string:
        bins = len(data.unique())

    fig = plt.hist(data, bins=bins)
    plt.gca().set(title=str(pkey)+'Frequency Histogram', ylabel='Frequency', xlabel = str(pkey))
    plt.show()
    return fig

def coorelation_analysis(csvfile, cols,title='Coorelation Analysis',size=(12,12)):
    df = pd.read_csv(csvfile)
    cols = sorted(cols)
    fig,axes = plt.subplots(1,1,figsize=size)
    df_corr = df[cols].corr()
    fig = sns.heatmap(df_corr,annot=True,cmap='RdBu_r')
    axes.title.set_text(title)
    return fig


def columnComp(csvfile, graph, colx, cols):
    df = pd.read_csv(csvfile)
    fig = plt.plot(x=df[colx], y=df[cols], figsize=(10,5), grid=True)
    plt.legend(loc='best')
    return fig

#### Data Visualization Ends ####