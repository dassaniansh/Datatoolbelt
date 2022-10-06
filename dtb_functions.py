#### Library Imports ####
import csv
from io import BytesIO
import json
import xmltodict
import sys
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import xml.etree.ElementTree as ET
from collections import OrderedDict
import numpy as np
from scipy import stats

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

def dicRec(dic, output, layer, prev = None, pos = []):
    if type(dic) == list:
        if type(dic[0]) == dict or type(dic[0]) == OrderedDict:
            for e in dic:
                output, pos = dicRec(e, output, layer, None, pos)
            return output, pos
        elif type(dic[0]) == list:
            dicRec(dic[0], output, layer, prev, pos)
        else:
            return dic, pos

    if layer%2 == 0:
        if output == []:
            output.append(list(dic.keys()))
            pos = [1] * len(output[0])
            t = [None] * len(output[0])
            output.append(t)
        else:
            for i in dic.keys():
                if i not in output[0]:
                    if type(i) == str:
                        i = i.replace("\n", " ")
                    output[0].append(i)
                    pos.append(layer - 1)
                    if max(pos) > len(output):
                        for z in range(max(pos) - len(output)):
                            t = [None] * len(output[0])
                            output.append(t)

        for i in dic.keys():
            if type(dic[i]) == OrderedDict:
                dic[i] = dict(dic[i])

            if type(dic[i]) == dict:
                newlayer = layer + 1
                output, pos = dicRec(dic[i], output, newlayer, i, pos)
            else:
                for k in range(len(output[0])):
                    if output[0][k] == i:
                        #print(pos, output, k)
                        if pos[k] < len(output):
                            if len(output[0]) > len(output[pos[k]]):
                                for _ in range(len(output[0])-len(output[pos[k]])):
                                    output[pos[k]].append(None)
                            
                            if output[pos[k]][k] == None:
                                if type(dic[i]) == str:
                                    dic[i] = dic[i].replace("\n", " ")
                                output[pos[k]][k] = dic[i]
                                pos[k] += 1
                        else:
                            t = [None] * len(output[0])
                            for _ in range(pos[k] - (len(output)-1)):
                                output.append(t)
                            #print(dic, i)
                            if type(dic[i]) == str:
                                dic[i] = dic[i].replace("\n", " ")
                            output[pos[k]][k] = dic[i]
                            pos[k]+=1
                            t = [None] * len(output[0])
                            output.append(t)
                        break
    else:
        for v in dic.keys():
            #print(pos)
            for i in range(len(output[0])):
                if output[0][i] == prev:
                    #print(i, pos, len(output))
                    if pos[i] < len(output):
                        if len(output[0]) > len(output[pos[i]]):
                            for _ in range(len(output[0])-len(output[pos[i]])):
                                output[pos[i]].append(None)

                        if output[pos[i]][i] == None:
                            if type(dic[v]) == OrderedDict or type(dic[v]) == dict:
                                if type(v) == str:
                                    v = v.replace("\n", " ")
                                output[pos[i]][i] = v
                                pos[i] += 1
                            else:
                                o = str(v)+": "+str(dic[v])
                                o = o.replace("\n", " ")
                                output[pos[i]][i] = o
                                pos[i] += 1
                    else:
                        t = [None] * len(output[0])
                        for _ in range(pos[i] - (len(output)-1)):
                            output.append(t)
                        if type(dic[v]) == OrderedDict or type(dic[v]) == dict:
                            if type(v) == str:
                                v = v.replace("\n", " ")
                            output[pos[i]][i] = v
                            pos[i] += 1
                            t = [None] * len(output[0])
                            output.append(t)
                        else:
                            o = str(v)+": "+str(dic[v])
                            o = o.replace("\n", " ")
                            output[pos[i]][i] = o
                            pos[i] += 1
                            t = [None] * len(output[0])
                            output.append(t)
                    
                    break

            if type(dic[v]) == OrderedDict or type(dic[v]) == dict:
                dic[v] = dict(dic[v])
                newlayer = layer+1
                output, pos = dicRec(dic[v], output, newlayer, None, pos)

    return output, pos

#### Backend Stuff - NOT FOR ANSH Ends ####

#### Meta Data Creation ####

def metaData(csvfile):
    output = [] #{NAme: , DataType, }
    df = pd.read_csv(csvfile)
    for col in df.columns:
        temp = {}
        temp["title"] = col
        temp["type"] = df[col].dtypes.name
        if df[col].dtypes.name == "int64" or df[col].dtypes.name == "float64":
            temp["avg"] = str(round(df[col].mean(), 2))
            temp["max"] = str(round(df[col].max(), 2))
            temp["min"] = str(round(df[col].min(), 2))
        else:
            temp["avg"] = "NA"
            temp["max"] = "NA"
            temp["min"] = "NA"
        output.append(temp)

    return output, len(df.index)

def getColumnPage(csvfile, col, page):
    df = pd.read_csv(csvfile)[col]
    maxlen = len(df.index)
    l = page * 25
    r = min((page + 1) * 25, maxlen - 1)
    df = df.iloc[l:r]
    if np.issubdtype(df.dtype, np.number):
        df = df.round(decimals=2)
    df = df.fillna('')
    return list(df)


#### Format Conversion ####

def csvTojson(csvfile, primeKey = None):
    f = open(csvfile, "r", encoding="utf8")
    lines = f.readlines()
    f.close()

    output = listTodic(lines, primeKey)

    return json.dumps(output)


def jsonTocsv(jsonfile, csvfile):
    data = {}
    with open(jsonfile, encoding="utf8") as json_file:
        data = json.load(json_file)

    output = []

    layer = 0
    output, pos = dicRec(data, output, layer)

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
    output, pos = dicRec(data, output, layer)

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


def csvToxml(csvfile, primeKey=None):
    f = open(csvfile, "r", encoding="utf8")
    lines = f.readlines()
    f.close()

    data = listTodic(lines, primeKey)
    output = xmltodict.unparse(data, pretty=True).encode('utf-8')

    f = BytesIO()
    f.write(output)
    f.seek(0)
    return BytesIO(f.read())


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

def normalization(csvfile, pKey, lower, higher, replace = False):
    df = pd.read_csv(csvfile)
    nkey = pKey
    if replace:
        pass
    else:
        nkey = pKey+"_norm"
    df[nkey] = df[pKey]/df[pKey].abs().max()
    df[nkey] = (df[nkey]*(higher-lower)) + lower

    df.to_csv(csvfile, encoding='utf-8', index=False)
    return csvfile

def outlier(csvfile, pKey, lower, higher, remove = False):
    df = pd.read_csv(csvfile)
    nkey = pKey+"_noOut"
    res = []
    for v in df[pKey].iteritems():
        v = list(v)
        if v[1] < lower or v[1] > higher:
            res.append(None)
        else:
            res.append(v[1])
    df[nkey] = res

    if remove:
        nullValues(csvfile, nkey, 1)
    else:
        df.to_csv(csvfile, encoding='utf-8', index=False)

    return csvfile


def nullValues(csvfile, pKey, method, replacement = None):
    df = pd.read_csv(csvfile)
    if method == 1:
        df = df.dropna(subset=[pKey])
    elif method == 2:
        rep = []
        if replacement == "Average":
            rep = df[pKey].mean()
        elif replacement == "Maximum":
            rep = df[pKey].max()
        elif replacement == "Minimum":
            rep = df[pKey].min()

        df[pKey].fillna(value=rep, inplace=True) 
    else:
        pass

    df.to_csv(csvfile, encoding='utf-8', index=False)
    return csvfile

#### Data Cleaning Ends ####
#### Data Visualization ####

def columnRep(csvfile, graph, pkey):
    df = pd.read_csv(csvfile)
    data = df[pkey]
    data_ls = list(data)
    bins = 0
    if type(data_ls[1]) == int or type(data_ls[1]) == float:
        mx = data.max()
        mn = data.min()
        bins = (mx - mn)
    elif type(data[1]) == str:
        bins = len(data.unique())
    #print(bins)
    fig = plt.hist(data, bins=bins)
    plt.gca().set(title=str(pkey)+'Frequency Histogram', ylabel='Frequency', xlabel = str(pkey))
    #plt.show()
    return fig

def coorelation_analysis(csvfile, cols,title='Coorelation Analysis',size=(12,12)):
    df = pd.read_csv(csvfile)
    cols = sorted(cols)
    fig,axes = plt.subplots(1,1,figsize=size)
    df_corr = df[cols].corr()
    fig = sns.heatmap(df_corr,annot=True,cmap='RdBu_r')
    axes.title.set_text(title)
    #plt.show()
    return fig


def columnComp(csvfile, graph, colx, cols):
    df = pd.read_csv(csvfile)
    plt.figure(figsize=(10,5))
    fig = plt.plot(df[colx], df[cols])
    #plt.legend(loc='best')
    #plt.show()
    return fig

#### Data Visualization Ends ####

#### Data Processing Begins ####

def columnCreation(csvfile, col1, col2, eq, newCol = "newCol"):
    df = pd.read_csv(csvfile)
    eq.replace("col1", col1)
    eq.replace("col2", col2)
    eq = newCol+" = "+eq
    df.eval(eq, inplace = True)

    df.to_csv(csvfile, encoding='utf-8', index=False)
    return csvfile

#### Data Processing Ends ####

#### Testing ####
csvfile = "testdata.csv"
jsonfile = "testdata.json"
xmlfile = "testdata.xml"
#jsonTocsv(jsonfile, csvfile)
"""
metaData(csvfile)
#csvTojson(csvfile, jsonfile, "ID")
jsonToxml(jsonfile, xmlfile)
xmlTocsv(xmlfile, csvfile)
outlier(csvfile, "Age", 21, 21)
print(nullValues(csvfile, "Age_noOut", 2, "Maximum"))

"""
#### Testing Ends ####