import copy
import json
from nonebot.adapters.onebot.v11 import Bot
import datetime


def filterFriend(comment, mode, allowTextList):
    if mode != 'friend':
        return True
    if allowTextList == []:
        return True
    return any(allowText in comment for allowText in allowTextList)


async def parseMsg(resMsg):
    if type(resMsg) is list:
        temp = ''.join(str(item)+'\n' for item in resMsg)
        temp = temp.replace("'", "").replace('"', '')
        resMsg = temp
    return resMsg[:400]
    # if len(resMsg)<=300 and isText==1:
    #    return resMsg
    # else:
    #     title = commandText
    #     img = Txt2Img(font_size)
    #     pic = img.save(title, resMsg)
    #     return MessageSegment.image(pic)


async def getReferIdList(bot: Bot, idName='group_id'):
    '''获取朋友或群id列表'''
    if idName == 'user_id':
        referInfoList = await bot.get_friend_list()
    else:
        idName = 'group_id'
        referInfoList = await bot.get_group_list()
    return [temp[idName] for temp in referInfoList]


async def sendMsg(bot: Bot, recipientList, msg: str, op=0):
    '''群发消息'''
    if not isinstance(recipientList, list):
        if isinstance(recipientList, str) and recipientList.isdigit():
            recipientList = [recipientList]
        else:
            return
    for recipient in recipientList:
        recipient = int(recipient)
        if op == 0:
            await bot.send_private_msg(user_id=recipient, message=msg)
        else:
            await bot.send_group_msg(group_id=recipient, message=msg)


def getExist(plainCommandtext: str, wholeMessageText: str, argsText: str) -> str | bool:
    '''返回命令'''
    commandText = wholeMessageText[::-
                                   1].replace(argsText[::-1], '', 1)[::-1].strip()
    return plainCommandtext in commandText if plainCommandtext else commandText


def readTime(numDict: dict) -> dict:
    '''读时间'''
    # global num,now,old
    # if not os.path.exists(numPath):
    #     now = datetime.datetime.now()
    #     with open(numPath, "w", encoding="utf-8") as fp:
    #         fp.write('1'+','+str(now))
    # with open(numPath,'r',encoding='utf-8') as fp:
    #     data_list=fp.read().split(',')
    #     if len(data_list)<2:
    #         now = datetime.datetime.now()
    #         data_list=['1',str(now)]
    # num=int(data_list[0])sssssssss
    # old=datetime.datetime.strptime(data[type]["time"], "%Y-%m-%d %H:%M:%S.%f")
    # now = datetime.datetime.now()
    for dictid in numDict:
        for typemode in numDict[dictid].keys():
            numDict[dictid][typemode]["time"] = datetime.datetime.strptime(
                numDict[dictid][typemode]["time"], "%Y-%m-%d %H:%M:%S.%f")
    return numDict


def writeTime(numDictPath, numDict: dict) -> dict:
    '''写时间'''
    numDictTemp = copy.deepcopy(numDict)
    for dictid in numDictTemp:
        for typemode in numDictTemp[dictid].keys():
            numDictTemp[dictid][typemode]["time"] = str(
                numDictTemp[dictid][typemode]["time"])
    with open(numDictPath, 'w', encoding='utf-8') as fp:
        json.dump(numDictTemp, fp, ensure_ascii=False)
    return numDictTemp


def writeLog(logPath, logContent):
    with open(logPath, "a", encoding="utf-8") as fp:
        fp.write(logContent)


def isNormalAdd(config, autoType, addInfo, agreeAutoApprove):
    blackDict = config["blackDict"][autoType]
    warnDict = config["warnDict"][autoType]
    statusDict = config["statusDict"]
    blackStatusDict = statusDict["blackDict"][autoType]
    warnStatusDict = statusDict["warnDict"][autoType]
    if autoType == "group":
        name = addInfo["group_name"]
        id = addInfo["group_id"]
    else:
        name = addInfo["nickname"]
        id = addInfo["user_id"]
    status = blackStatusDict["status"]+"\n昵称"+name
    if id in blackDict["id"]:
        return -1, status
    for balckText in blackDict["text"]:
        if balckText in name:
            return -1, status
    status = warnStatusDict["status"] + f"\n昵称{name}\n是否同意"
    if id in warnDict["id"]:
        return 0, status
    for warnText in warnDict["text"]:
        if warnText in name:
            return 0, status
    if agreeAutoApprove == 1:
        status = f'\nqq{id}昵称{name}添加成功'
        return agreeAutoApprove, status
    # 当初应该没在agreeAutoApprove上区分警告和非自动同意，状态里区分了
    status = f"\n昵称{name}\n是否同意"
    return agreeAutoApprove, status


def parseTimeInterval(old='2022-06-21 20:57', now='', op='int'):
    if isinstance(old, str):
        old = datetime.datetime.strptime(old, "%Y-%m-%d %H:%M:%S.%f")
    if now == '':
        now = datetime.datetime.now()
    elif isinstance(now, str):
        now = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S.%f")
    symbol = 1
    if now.date() <= old.date():
        temp = datetime.datetime.strptime(str(now.date()), "%Y-%m-%d")
        if (now-temp).seconds < (old-temp).seconds:
            old, now = now, old
            symbol = -1
    interval = now-old
    days = interval.days
    seconds = interval.seconds
    if op == 'int':
        return (days*3600*24+seconds)*symbol
    return {'days': days*3600*24*symbol, 'seconds': seconds*symbol}


def parseTime(numControl: dict, numTypedDict, now):
    time = parseTimeInterval(numTypedDict["time"], now)
    if numControl['unit'] == 'h':
        if time/3600 > numControl['time']:
            numTypedDict["count"] = 0
    elif numControl['unit'] == 'm':
        if time/60 > numControl['time']:
            numTypedDict["count"] = 0
    elif time/3600/24 > numControl['time']:
        numTypedDict["count"] = 0
    if numTypedDict["count"] >= numControl["maxNum"]:
        return -1
    numTypedDict["count"] = numTypedDict["count"]+1
    numTypedDict['time'] = now
    return numTypedDict["count"]
