"""
Spyder Editor

(C) Гладкий Илья ilyalg

Преобразование файлов для Ворожцовой

1. Проверка правильности формата входящих файлов.
2. Сборка потока из входящих файлов в один файл.
3. Преобразование потока в вывод, и разбиение по файлам заданного формата.
4. Проверка правильности формата выходного файла.
5. Проверка правильности данных в исходном и конечной файле. 
6. Проверка отсутствия повторов.
7. Вывод результатов для отправки по электронной почте.

"""

import numpy as np
import pandas as pd
import math
import datetime

from pathlib import Path
import os

import linecache

"""

Глобальные параметры

"""

InputPath = r"J:\Tasks\перекодировка\Test1"
ResExt = 'csv'
InCodeSeparator  = ";"
OutCodeSeparator = ";"
fnametest = r"tmptest.csv"
tmpsumfname = "sum.txt"
checksumfname = "checksum.txt"


# Точность проверки равенства нулю действительного числа
epsilon = 10**-10


# Параметры преобразования файлов
in_maxcodecnt = 30000
in_divisor    = 6

out_maxcodecnt = 56000
out_divisor    = 7

codelen_param  = 9





"""

Процедуры

"""

def DeleteLastEmptyString(FromPath ,fname ,ToPath):
    """
    Удаляем последнюю пустую строку и пустые строки
    Подсчет количества удаленных строк
    """
    EmptyStrCnt = 0
    fullinfname = os.path.join(FromPath, fname)
    fulloutfname = os.path.join(ToPath, fname)
    f5in = open(fullinfname, 'r')
    WholeFileStr = f5in.read()
    infsize = CountLinesInString(WholeFileStr)
    # print("WholeFileStr=\n" + WholeFileStr)
    # Удаление пустых строк
    while WholeFileStr.find("\n\n") != -1:
        WholeFileStr = WholeFileStr.replace('\n\n','')
    f5in.close()
    
    # CntStrInStr = WholeFileStr.count("\n")
    ArofStr = WholeFileStr.split("\n")
    CntStrInStr = len(ArofStr)
    # print("CntStrInStr=" + str(CntStrInStr))
    
    StrLastLine = ArofStr[CntStrInStr-1]
    # print("StrLastLine=\n" + StrLastLine + "\n=StrLastLine")
    
    # Если последний элемент пустой, то удаляем его
    if StrLastLine == "":
        ArofStr.pop()
    
    NewFileStr = '\n'.join(ArofStr)
    outfsize = CountLinesInString(NewFileStr)
    EmptyStrCnt = infsize - outfsize
    #print("infsize=" + str(infsize))
    #print("outfsize=" + str(outfsize))
    
    f5out = open(fulloutfname, 'w')
    f5out.write(NewFileStr)
    f5out.close()
    
    return EmptyStrCnt


def GetLastLine(fname):
    " Получение последней строки из файла"
    f3 = open(fname, 'r')
    for line in f3.readlines():
        pass
    f3.close()
    return line


def NewFileName(fname, Path, NumFileName, ext):
    " Форматирование файлов вывода согласно шаблону"
    StrNumFile = str(NumFileName)
    StrNumFile = StrNumFile.rjust(3, '0')
    OutputFileName = os.path.join(Path, fname + "_" + StrNumFile + "." + ext)
    return OutputFileName


def ChechCodeFormat(fname, Path, NumFileName, ext):
    "Проверка правильности формата кодов"
    StrNumFile = str(NumFileName)
    StrNumFile = StrNumFile.rjust(3, '0')
    OutputFileName = os.path.join(Path, fname + "_" + StrNumFile + "." + ext)
    return OutputFileName


def GetCodeFormat(curstr):
    """
    Проверка правильности формата кодов
    Каждая строка состоит из нобора кодов,
    разделенных ";", имеющих одинаковую длину.
    Для проверки равенства всех длин используется
    теорема Пифагора.
    """
    if curstr != '':
        ArOfCodes = curstr.split(";")
        midlen = 0
        ArOflen = [len(s) for s in ArOfCodes]
        # print("ArOflen=",ArOflen)
        codecnt = len(ArOfCodes)
        # print("codecnt=",codecnt)
        midlen = sum(ArOflen)/codecnt
        # print("midlen=",midlen)
        Displen = sum([(i - midlen)**2 for i in ArOflen])
        # print("Displen=",Displen)
        "Проверяем что дисперсия равна нулю => это константа"
        if Displen < epsilon:
            estcodelen = round(midlen)
            IsError = False
            # print("Длина кодов",estcodelen)
            # print("Колличество кодов",codecnt)
        else:
            "Иначе в файле ошибка"
            estcodelen = round(midlen)
            IsError = True
        return (codecnt, estcodelen, IsError)
    else:
        codecnt = 0
        estcodelen = 0
        IsError = False
        return (codecnt, estcodelen, IsError)


def CountLinesInFile(fname):
    " Подсчет количества строк в файле"
    f3 = open(fname, 'r')
    TmpStr = f3.read()
    res = CountLinesInString(TmpStr)
    f3.close()
    return res


def CountLinesInString(instr):
    " Подсчет количества строк в строке"
    TmpArofStr = instr.split("\n")
    res = len(TmpArofStr)
    return res


def CodeStatistics(fname, Fefformat):
    """ Собрать статистические данные правильности форматов в файле
        Проверяем весь файл.
        Считаем процент неверных строк.
        Строка с ошибкой, если
            1. В строке есть коды неверного формата
            2. В строке количество кодов или длина кода не равна заданному 
                формату.
    """
    errorscnt = 0
    f3 = open(fname, 'r')
    
    LinesTotal = 0
    TotalCodesCnt = 0
    # ResLine = ""          i = 0
    """ Правильнее будет делать обход файла через массив строк, так как
        в этом случае информация о пустых строках отображается корректно!
    """
    for line in f3.readlines():
        # проверяем все строки в соответсвии
        # с настройками.
        line1 = line.replace('\n','')
        # line1.rstrip('\n')
        # print(line1)
        LinesTotal += 1
        # print("LinesTotal=",LinesTotal)
        codecnt, codelen, er = GetCodeFormat(line1)
        TotalCodesCnt += codecnt
        # Проверяем наличие ошибки в строке
        # Если есть, то счётчик увеличиваем на 1.
        # print(errorscnt)
        # print(codecnt,codelen,Fefformat[0],Fefformat[1])
        # print(er,codecnt!=Fefformat[0],codelen!=Fefformat[1])
        if er:
            # print("er")
            errorscnt += 1
        elif (codecnt!=Fefformat[0]):
            # print("codelen")
            errorscnt += 1
        elif (codelen!=Fefformat[1]):
            # print("codecnt")
            errorscnt += 1
    f3.close()
    
    return (errorscnt, LinesTotal, TotalCodesCnt)



"""

Часть 1
Проверка правильности формата входящих файлов.
Vorogtsova_check.py

"""

# Создаем папку для вывода информации о процессе преобразования,
#    исходных файлах и результате, а так же готовое сообщение 
#    для отправки по электронной почте.
InfoPath = InputPath + r"\Info"
if not os.path.isdir(InfoPath):
    os.mkdir(InfoPath)

infofname = InfoPath + r"\decode_res.txt"
foremail = InfoPath + r"\foremail.txt"

print(infofname)
print(foremail)
# очищаем файл
LogFile = open(infofname, 'w')
LogFile.close()
EmailFile = open(foremail, 'w')
EmailFile.close()
# открываем файл для новых записей
LogFile = open(infofname, 'a+')
EmailFile = open(foremail, 'a+')

"По 6 кодов в строке. Как вариант возможно 1 код в строке."
"Формат входящего файла:         Колличество кодов, Длина кодов"
INefformat = (in_divisor, codelen_param)
"По 7 кодов в строке."
"Формат результирующего файла:   Колличество кодов, Длина кодов"
OUTefformat = (out_divisor, codelen_param)


"""

Обрабатываем заданную папку
Проходим по всем файлам и проверяем соответствие формата
файла 

"""


LogFile.write("========================================" + "\n")
DtTimeSrt = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
LogFile.write("Проверка каталога начата:" + DtTimeSrt + "\n")


CodesInFolder = 0
fnames = os.listdir(InputPath)
fnames.sort()
for name in fnames:
    fullname = os.path.join(InputPath, name)
    if os.path.isfile(fullname):
        print(fullname)
        DtTimeSrt = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S") + "\r\n"
        LogFile.write(DtTimeSrt)
        LogFile.write("Обрабатываем:" + fullname + "\r\n")
        e1, t1, tc1 = CodeStatistics(fullname, INefformat)
        CodesInFolder += tc1
        LogFile.write("Ошибок в файле=" + str(e1) + "\r\n")
        LogFile.write("Общее количество строк=" + str(t1) + "\r\n")
        LogFile.write("Всего кодов в файле=" + str(tc1) + "\r\n")
    pass
DtTimeSrt = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
LogFile.write("Проверка каталога завершена:" + DtTimeSrt + "\r\n")
LogFile.write("Всего кодов в каталоге=" + str(CodesInFolder) + "\r\n")



"========================================"
# Автоматическое определение названия файла


CommonfNames = []
for name in fnames:
    fullname = os.path.join(InputPath, name)
    if os.path.isfile(fullname):
        fnamewoext, ext = name.split(".")
        CommonfNames.append(fnamewoext)
    pass

prefferedname = ''
szfn = len(CommonfNames)

ArOffnames = [[] for i in range(szfn)]
#print(ArOffnames)

j = 0
# print(CommonfNames)
maxlen = 0
for fname in CommonfNames:
    fnlen = len(fname)
    if maxlen < fnlen:
        maxlen = fnlen
    for i in range(fnlen):
        # print("i,j=" + str(i) + ", "+ str(j))
        ArOffnames[j].append(fname[i])
    j += 1

"""
for k in range(szfn):
    print(ArOffnames[k])
    """

# массив возможных символов по каждой позиции в названии
Simbols = [[] for i in range(maxlen)]
ProbAr  = [[] for i in range(maxlen)]

# критерий вероятности выбора конкретного символа
pcrit = 0.5

#IsInArray = [False for i in range(maxlen)]

# Заполняем массив Simbols искомыми символами
for j in range(maxlen):
    for i in range(szfn):
        if j < len(ArOffnames[i]):
            cursmbl = ArOffnames[i][j]
            IsInArray = False
            curlensmbl = len(Simbols[j])
            k = 0
            while not IsInArray and (k <= curlensmbl-1):
                if cursmbl == Simbols[j][k]:
                    IsInArray = True
                k += 1
            if not IsInArray:
                Simbols[j].append(cursmbl)

filenamecalculated = ''
# вычисляем вероятность элементов массива Simbols
for j in range(maxlen):
    curlensmbl = len(Simbols[j])
    for k in range(curlensmbl):
        cursmbl = Simbols[j][k]
        cnt = 0
        for i in range(szfn):
            if (j < len(ArOffnames[i])) and (cursmbl == ArOffnames[i][j]):
                cnt += 1
        p = cnt/szfn
        ProbAr[j].append(p)
        if p >= pcrit:
            filenamecalculated += cursmbl

LogFile.write("Вычисленное имя файла:" + filenamecalculated + "\r\n")
# print(filenamecalculated)


"""
for k in range(maxlen):
    curlensmbl = len(Simbols[k])
    print(Simbols[k])
    print(ProbAr[k])
"""




"""

Предварительная подготовка
Удаляем последнюю пустую строку 
Скоректированные файлы помещаем в папку ToPath

(FromPath ,fname ,ToPath)

"""


PathCorrectedFiles = InputPath + r"\Corrected"
if not os.path.isdir(PathCorrectedFiles):
    os.mkdir(PathCorrectedFiles)

# EmpCnt = DeleteLastEmptyString(InputPath,fnametest,PathCorrectedFiles)
# print("EmpCnt=" + str(EmpCnt))



LogFile.write("----------------------------------" + "\n")
LogFile.write("Предварительная подготовка." + "\n")
LogFile.write("Удаляем последнюю пустую строку." + "\n")
fnames = os.listdir(InputPath)
fnames.sort()
for name in fnames:
    fullfilename = os.path.join(InputPath, name)
    if os.path.isfile(fullfilename):
        # Удаляем последнюю пустую строку 
        EmpCnt = DeleteLastEmptyString(InputPath,name,PathCorrectedFiles)
        line = "Из файла " + name
        # print(line.ljust(50) + " удалено=" + str(EmpCnt) + " строк")
        LogFile.write(line.ljust(50) + " удалено=" + str(EmpCnt) + " строк." + "\n")
    pass





"""

Часть 2
Сборка потока из входящих файлов в один файл.
Vorogtsova_decode7.py

Обратное преобразование из файла разбитого на столбцы по 6
собрать файл столбец без разделителей: 1 код в одной строке

"""


# Создаем папку для вывода результата суммы файлов
SumOutputPath = InputPath + "\SumOutput"
if not os.path.isdir(SumOutputPath):
    os.mkdir(SumOutputPath)


SumOutputFileName = os.path.join(SumOutputPath, tmpsumfname)
SumOutputFile = open(SumOutputFileName, 'w+')
LogFile.write("Перезаписываю файл " + SumOutputFileName + "\n")



fnames = os.listdir(PathCorrectedFiles)
fnames.sort()
FileCnt = len(fnames)
ifile = 0
for name in fnames:
    fullfilename = os.path.join(PathCorrectedFiles, name)
    ifile += 1
    if os.path.isfile(fullfilename):
        # print(fullname)
        LogFile.write("Обрабатываем:" + fullfilename + "\n")
        if (ifile == FileCnt):
            CntStr = CountLinesInFile(fullfilename)
        # Читаем файл, проходим по файлу
        #   значении выводим результат
        f2 = open(fullfilename, 'r')
        NextFile = 0
        
        # OutputFileName = os.path.join(OutputPath, fname + "_" + StrNextFile + "." + ext)
        ResLine = ""
        # data = pd.read_csv(fullname, parse_dates=False)
        iline = 0
        icodes = 0
        for line in f2.readlines():
            # Переход на новую строку
            iline += 1
            line1 = line.replace(InCodeSeparator,'\n')
            codecnt, codelen, er = GetCodeFormat(line)
            icodes += codecnt
            if line1[-1:] != "\n":
                line1 = line1 + "\n"
            SumOutputFile.write(line1)
            pass
        f2.close()
        LogFile.write("Обработано " + str(iline) + " строк \n")
        LogFile.write("Обработано " + str(icodes) + " кодов \n")
    pass

SumOutputFile.close()


"""

Удаляем последнюю пустую строку 

"""


DeleteLastEmptyString(SumOutputPath,tmpsumfname,SumOutputPath)

LogFile.write("Файл " + tmpsumfname + " создан\n")
LogFile.write("Пустые строки с конца удалены!\n")


# CntStr = CountLinesInFile(SumOutputFileName)
e1, t1, tc1 = CodeStatistics(SumOutputFileName, INefformat)
LogFile.write("Всего кодов в файле " + tmpsumfname + " = " + str(tc1) + "\n")





"""

=============================================
=============================================
=============================================

=============================================
=============================================
=============================================

"""


"""

Часть 3
Преобразование потока в вывод, и разбиение по файлам заданного формата.

"""

# Создаем папку для вывода результата преобразования файлов
#    в новый формат.
OutputPath = InputPath + "\Output"
if not os.path.isdir(OutputPath):
    os.mkdir(OutputPath)


StrFi = 0

# Берем файл sum.txt
fullsumfname = os.path.join(SumOutputPath,tmpsumfname)
if os.path.isfile(fullsumfname):
    CntStr = CountLinesInFile(fullsumfname)
    LogFile.write("Строк в файле " + tmpsumfname + " = " + str(CntStr) + "\n")
    print(fullsumfname,"     ",str(CntStr))
    i = 0
    fi = 0
    LastStr = CntStr // out_divisor
    # print(str(LastStr))
    # Читаем файл, проходим по файлу и на каждом 7-ом
    #   значении выводим результат
    #   При достижении 56 000 создаем новый файл
    f2 = open(fullsumfname, 'r')
    if filenamecalculated != '':
        fname = filenamecalculated
    else:
        fname, ext = tmpsumfname.split(".")
    NextFile = 0
    OutputFileName = NewFileName(fname, OutputPath, NextFile, ResExt)
    print(OutputFileName)
    # OutputFileName = os.path.join(OutputPath, fname + "_" + StrNextFile + "." + ext)
    OutputFile = open(OutputFileName, 'w')
    LogFile.write("Формирую файл=" + OutputFileName + "\n")
    for line in f2.readlines():
        # больше  out_maxcodecnt
        # Обнуляем счетчик и создаем новый файл
        if i > out_maxcodecnt - 1:
            OutputFile.close()
            NextFile += 1
            OutputFileName = NewFileName(fname, OutputPath, NextFile, ResExt)
            print(OutputFileName)
            OutputFile = open(OutputFileName, 'w')
            i = 0
        line1 = line.replace('\n','')
        # print(line1,i)
        NumStr = i % out_divisor
        StrFi = fi // out_divisor
        if (NumStr == 0):
            ResLine = line1
        else:
            ResLine = ResLine + OutCodeSeparator + line1
        # Выводим результат
        if (NumStr == out_divisor - 1):
            if (i < out_maxcodecnt - 1) and (StrFi != LastStr - 1):
                ResLine = ResLine + "\n"
            OutputFile.write(ResLine)
            # print(ResLine,i)
            ResLine = ""
        i += 1
        fi += 1
    OutputFile.close()
    LogFile.write("Выведено " + str(fi) + "\n")
    # Выводим остаток
    # Выводить хвост файла - неиспользованные коды
    if (NumStr < out_divisor - 1):
        StrNumFile = 'Хвост'
        OutputFileName = os.path.join(OutputPath, fname + "_" + StrNumFile + "." + ext)
        OutputFile = open(OutputFileName, 'w')
        OutputFile.write(ResLine)
    OutputFile.close()
    f2.close()
else:
    LogFile.write("Файле " + tmpsumfname + " не обнаружен. " + "\n")
pass







Ostatok = CntStr % out_divisor
print("Хвост = ",str(Ostatok))
print("StrFi = ",str(StrFi))



i = 0
CodeSeparator = ";"
ResArr1 = []


# Сохранение файла для проверки



ChechSumOutputFileName = os.path.join(SumOutputPath, checksumfname)
OutputFile = open(ChechSumOutputFileName, 'w')
print("Перезаписываю файл " + checksumfname)
print(ChechSumOutputFileName)
FileCnt = 0
ifile = 0

fnames = os.listdir(OutputPath)
fnames.sort()
FileCnt = len(fnames)
for name in fnames:
    fullname = os.path.join(OutputPath, name)
    if os.path.isfile(fullname):
        print(fullname)
        # Читаем файл, проходим по файлу
        #   значении выводим результат
        f2 = open(fullname, 'r')
        ifile += 1
        
        # OutputFileName = os.path.join(OutputPath, fname + "_" + StrNextFile + "." + ext)
        ResLine = ""
        # data = pd.read_csv(fullname, parse_dates=False)
        for line in f2.readlines():
            # Переход на новую колонку
            line1 = line.replace(CodeSeparator,'\n')
            if (line1[-1:] != '\n') and (ifile < FileCnt):
                line1 = line1 + "\n"
            OutputFile.write(line1)
            # codesAr = line.split(CodeSeparator)
        f2.close()
    pass

OutputFile.close()

CheckFile1Name = os.path.join(SumOutputPath, checksumfname)
CheckFile2Name = os.path.join(SumOutputPath, tmpsumfname)

# Узнаем длины файлов 1 и 2
# Если длины файлов разные то файлы разные!
# Иначе идем по длинне по читаем строку из ф1 и ф2 и сравниваем
# до первой различной строки!



"""

Часть 4
4. Проверка правильности формата выходного файла.

"""


LogFile.write("========================================" + "\n")
DtTimeSrt = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
LogFile.write("Проверка каталога начата:" + DtTimeSrt + "\n")


CodesInFolder = 0
fnames = os.listdir(OutputPath)
fnames.sort()
for name in fnames:
    fullname = os.path.join(OutputPath, name)
    if os.path.isfile(fullname):
        # print(fullname)
        DtTimeSrt = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S") + "\r\n"
        LogFile.write(DtTimeSrt)
        LogFile.write("Обрабатываем:" + fullname + "\r\n")
        e1, t1, tc1 = CodeStatistics(fullname, OUTefformat)
        CodesInFolder += tc1
        LogFile.write("Ошибок в файле=" + str(e1) + "\r\n")
        LogFile.write("Общее количество строк=" + str(t1) + "\r\n")
        LogFile.write("Всего кодов в файле=" + str(tc1) + "\r\n")
    pass
DtTimeSrt = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
LogFile.write("Проверка каталога завершена:" + DtTimeSrt + "\r\n")
LogFile.write("Всего кодов в каталоге=" + str(CodesInFolder) + "\r\n")







"""

Часть 5
5. Проверка правильности данных в исходном и конечной файле. 

"""



CntStrF1 = CountLinesInFile(CheckFile1Name)
CntStrF2 = CountLinesInFile(CheckFile2Name)
i = 0
Filesequal = True

if CntStrF1 == CntStrF2:
    print("\nСравниваем файлы:")
    print("1. ",CheckFile1Name)
    print("2. ",CheckFile2Name)
    # Читаем файл, проходим по файлу
    #   значении выводим результат
    f1 = open(CheckFile1Name, 'r')
    f2 = open(CheckFile2Name, 'r')
    f2.seek(0)
    NextFile = 0
    
    # OutputFileName = os.path.join(OutputPath, fname + "_" + StrNextFile + "." + ext)
    ResLine = ""
    # data = pd.read_csv(fullname, parse_dates=False)
    for line in f1.readlines():
        # 
        # Считаем количество строк
        i += 1
        linef1 = line.replace(CodeSeparator,'\n')
        line2 = f2.readline()
        linef2 = line2.replace(CodeSeparator,'\n')
        if (linef1 != linef2):
            Filesequal = False
            print(linef1,"!=",linef2,"<=>",str(linef1 != linef2))
            print("В файлах различается строка - ",str(i))
            break
        else:
            Filesequal = Filesequal and True
        # codesAr = line.split(CodeSeparator)
    f2.close()
else:
    print("Файлы 1 и 2 различаются по количеству строк:")
    print("1. ",CheckFile1Name,str(CntStrF1))
    print("2. ",CheckFile2Name,str(CntStrF2))
    Filesequal = False

if Filesequal:
    print("Контрольный и проверочный файл совпадают")


f1.close()
f2.close()




"""

Часть 6 
6. Проверка отсутствия повторов.
7. Вывод результатов для отправки по электронной почте.

"""






LogFile.close()
EmailFile.close()


