#### Library Imports ####
import csv
import json
import xmltodict
import sys
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import xml.etree.ElementTree as ET
from collections import OrderedDict

#### Library Import Ends ####
#### Backend Stuff - NOT FOR ANSH ####

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
    
    if primeKey != None:
        for i in range(len(lines[0])):
            if primeKey == lines[0][i]:
                keyNum = i

    if keyNum == 0:
        primeKey = lines[0][0]

    output[primeKey] = {}
    for i in range(len(lines) - 1):
        output[primeKey][lines[i+1][keyNum]] = {}
        for j in range(len(lines[0])):
            if lines[0][j] != primeKey:
                output[primeKey][lines[i+1][keyNum]][lines[0][j]] = lines[i+1][j]

    return output

def dicRec(dic, output, layer, prev = None):
    if layer%2 == 0:
        if output == []:
            output.append(list(dic.keys()))
        else:
            for i in dic.keys():
                if i not in output[0]:
                    output[0].append(i)

        for i in dic.keys():
            if type(dic[i]) == OrderedDict:
                dic[i] = dict(dic[i])

            if type(dic[i]) == dict:
                newlayer = layer + 1
                output = dicRec(dic[i], output, newlayer, i)
            else:
                for k in range(len(output[0])):
                    if output[0][k] == i:
                        if len(output[0]) > len(output[-1]):
                            for _ in range(len(output[0])-len(output[-1])):
                                output[-1].append(None)
                        
                        if output[-1][k] == None:
                            output[-1][k] = dic[i]
                        else:
                            t = [None] * len(output[0])
                            output.append(t)
                            output[-1][k] = dic[i]
                        
                        break
    else:
        for v in dic.keys():
            for i in range(len(output[0])):
                if output[0][i] == prev:
                    if len(output[0]) > len(output[-1]):
                        for _ in range(len(output[0])-len(output[-1])):
                            output[-1].append(None)

                    if output[-1][i] == None:
                        output[-1][i] = v
                    else:
                        t = [None] * len(output[0])
                        output.append(t)
                        output[-1][i] = v
                    
                    break

            if type(dic[v]) == OrderedDict:
                dic[v] = dict(dic[v])
                newlayer = layer+1
                output = dicRec(dic[v], output, newlayer)

    return output

#### Backend Stuff - NOT FOR ANSH Ends ####

#### Meta Data Creation ####

def metaData(csvfile):
    output = []
    df = pd.read_csv(csvfile)
    for col in df.columns:
        temp = {}
        temp["Title"] = col
        temp["Type"] = df[col].dtypes.name
        if df[col].dtypes.name == "int64" or df[col].dtypes.name == "float64":
            temp["Average"] = df[col].mean()
            temp["Max"] = df[col].max()
            temp["Min"] = df[col].min()
        else:
            temp["Average"] = "NA"
            temp["Max"] = "NA"
            temp["Min"] = "NA"
        output.append(temp)

    return output


#### Format Conversion ####

def csvTojson(csvfile, jsonfile, primeKey = None):
    f = open(csvfile, "r", encoding="utf8")
    lines = f.readlines()
    f.close()

    output = listTodic(lines, primeKey)

    with open(jsonfile, "w", encoding="utf8") as outfile:
        json.dump(output, outfile)

    return jsonfile
    

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
    parser = ET.XMLParser(encoding="utf-8")
    tree = ET.parse(xmlFile, parser=parser)
    xml_data = tree.getroot()
    xmlstr = ET.tostring(xml_data, encoding='utf-8', method='xml')
    data = dict(xmltodict.parse(xmlstr))
    output = []
    layer = 0
    output = dicRec(data, output, layer)

    with open(csvfile, "w", newline="", encoding="utf8") as f:
        writer = csv.writer(f)
        writer.writerows(output)

    return csvfile

def xmlTojson(xmlFile, jsonfile):
    parser = ET.XMLParser(encoding="utf-8")
    tree = ET.parse(xmlFile, parser=parser)
    xml_data = tree.getroot()
    xmlstr = ET.tostring(xml_data, encoding='utf-8', method='xml')
    output = dict(xmltodict.parse(xmlstr))
    
    with open(jsonfile, "w", encoding="utf8") as outfile:
        json.dump(output, outfile)

    return jsonfile


def csvToxml(csvfile, xmlFile, primeKey=None):
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
    if type(data[1]) == int or type(data[1]) == float:
        mx = data.max()
        mn = data.min()
        bins = (mx - mn)
    elif type(data[1]) == str:
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


#### Testing ####
"""
csvfile = "testdata.csv"
jsonfile = "testdata.json"
xmlfile = "testdata.xml"

metaData(csvfile)
#csvTojson(csvfile, jsonfile, "ID")
#jsonToxml(jsonfile, xmlfile)
#xmlTocsv(xmlfile, csvfile)
"""
#### Testing Ends ####