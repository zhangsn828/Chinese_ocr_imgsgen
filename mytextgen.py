#!/usr/bin/python
# -*- coding:utf-8 -*-

import glob
import os
import random
import time
from uuid import uuid1
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

'''中文图片生产器'''

'''全局变量部署'''
backPaths = glob.glob('./bg/*.png')  # 背景图像路径
fonts = glob.glob('./fonts/*.ttf')  # 字体集路径
crupsPaths = glob.glob('./corpus/*.txt')  # 语料库路径
maxLen = 10  # 每行最大字符个数
minLen = 10  # 每行最小字符个数
imgsnum = 0  # 图片个数
shownum = 1000  # 生成n张图片打印一次
imgsize = [860, 1024, 1600]  # 大图尺寸（无需修改，如要修改，请往大的改）
width = 280  # 生成图片实际宽度
height = 32  # 生成图片实际高度
root = './data/0'  # 图片文本数据存放路径
batch = 10  # 生成图片批数（不是实际生成图片数量）
wordclassnum = {}  # 统计字典


def read_txt():
    # 获取语料文本数据
    dataList = []
    intP = 5
    for _ in range(intP):
        txt = np.random.choice(crupsPaths)
        with open(txt, "r") as f:
            datas = f.read().decode('utf-8')
        datas = [line.strip() for line in datas.split(u'\n') if line.strip() != u'' and len(line.strip()) > 1]
        dataList.extend(datas)

    np.random.shuffle(dataList)
    np.random.shuffle(dataList)
    return np.random.choice(dataList, size=100)


def select_txt():
    # 随机产生minlen到maxlen长度的文本
    txtlist = []
    dataList = read_txt()
    # splitPatters = [u',', u':', u'-', u' ', u';', u'。']
    # splitPatter = np.random.choice(splitPatters, 1)
    # data = splitPatter[0].join(dataList)
    data = ''.join(dataList)
    for _ in range(50):
        num = randNum(minLen, maxLen)
        index = randNum(0, len(data) - num)
        txtlist.append(data[index:index + num])
    return txtlist


def randNum(low, high):
    return random.randint(low, high)


def buider_bimg():
    # 图像背景生成
    temp = randNum(0, 10)
    Size = random.choice(imgsize)
    Size = Size, Size
    if temp > 8:
        p = Image.new('RGBA', Size, (255, 255, 255))
    else:
        bg = Image.open(np.random.choice(backPaths))
        p = bg.resize(Size)
    return p, Size


def fromat_box(box):
    # 格式化坐标点
    a, b, a1, b1 = box
    if a1 - a < width and b1 - b < height:
        spanx = (width - a1 + a) // 2
        x1, x2 = a - spanx, a1 + spanx
        spany = (height - b1 + b) // 2
        y1, y2 = b - spany, b1 + spany
    elif a1 - a < width and b1 - b > height:
        spanx = (width - a1 + a) // 2
        x1, x2 = a - spanx, a1 + spanx
        spany = (b1 - b - height) // 2
        y1, y2 = b + spany, b1 - spany
    elif a1 - a > width and b1 - b < height:
        spany = (height - b1 + b) // 2
        y1, y2 = b - spany, b1 + spany
        spanx = (a1 - a - width) // 2
        x1, x2 = a + spanx, a1 - spanx
    else:
        x1, y1, x2, y2 = a - 10, b - 2, a1 + 10, b1 + 2

    return x1, y1, x2, y2


def draw_txt():
    # 绘制文字
    txtlist = select_txt()
    bimg, size = buider_bimg()
    # print size
    X, Y = size
    initX, initY = int(size[0] * 0.1), int(size[0] * 0.1)

    textboxs = []
    imgBoxes = []

    draw = ImageDraw.Draw(bimg)
    fontType = random.choice(fonts)  # 随机获取一种字体

    cX = initX
    cY = initY
    span = 20
    for lable in txtlist:
        fontSize = random.randint(24, 25)  # 字体大小
        # fontSize=10
        font = ImageFont.truetype(fontType, fontSize)

        charW, charH = draw.textsize(text=lable, font=font)
        if cY < Y - initY and cX + charW <= X - initX:
            draw.text(xy=(cX, cY), text=lable, font=font, fill="black")
            box = cX, cY, cX + charW, cY + charH
            x1, y1, x2, y2 = fromat_box(box)
            imgBoxes.append([x1, y1, x2, y2])
            textboxs.append(lable)
            cY += charH + span
        else:
            pass

    temp = randNum(0, 1000)
    if temp >= 700:
        bimg, imgBoxes = setwarp(bimg, size, imgBoxes)
        addline(draw, size)
    elif temp >= 600:
        bimg = setrorate(bimg)
        addline(draw, size)
    elif temp >= 500:
        setnoisy(draw)
        addline(draw, size)
    elif temp >= 500:
        bimg = setdim(bimg)
        addline(draw, size)
    elif temp >= 400:
        bimg = setdim(bimg)
        setnoisy(draw)
    elif temp >= 300:
        setnoisy(draw)
        addline(draw, size)

    return bimg, imgBoxes, textboxs


def setwarp(im, size, imageboxs):
    # 创建扭曲
    temp = randNum(1, 10)
    if temp < 8:
        x = random.random() * 0.03
        y = random.random() * 0.03
        for index in range(len(imageboxs)):
            imageboxs[index][0] -= 12  # 偏移量（10个字最优）
            imageboxs[index][1] -= 4
            imageboxs[index][2] -= 12
            imageboxs[index][3] -= 4

    elif temp < 6:
        x = random.random() * 0.03 * 0.3
        y = random.random() * 0.03
        for index in range(len(imageboxs)):
            imageboxs[index][0] -= 12
            imageboxs[index][1] -= 4
            imageboxs[index][2] -= 12
    elif temp < 4:
        x = random.random() * 0.05
        y = random.random() * 0.05 * -0.5
        for index in range(len(imageboxs)):
            imageboxs[index][0] -= 17
            imageboxs[index][1] += 4
            imageboxs[index][2] -= 17
            imageboxs[index][3] += 5
    else:
        x = random.random() * 0.05 * -0.4
        y = random.random() * 0.05 * -0.4
        for index in range(len(imageboxs)):
            imageboxs[index][0] += 8
            imageboxs[index][1] += 3
            imageboxs[index][2] += 8
            imageboxs[index][3] += 4
    im = im.transform(size, Image.AFFINE, (1, x, 0.8, y, 1, 0.8),
                      Image.BILINEAR)  # 创建扭曲
    # im = im.filter(ImageFilter.EDGE_ENHANCE_MORE)
    return im, imageboxs


def setrorate(im):
    # 旋转
    temp = randNum(-5, 5)
    if temp != 0:
        angle = np.pi / 6 / temp
        im = im.rotate(angle)
    return im


def setdim(im):
    # 模糊处理
    fts = [ImageFilter.DETAIL, ImageFilter.SMOOTH, ImageFilter.SMOOTH_MORE]
    return im.filter(np.random.choice(fts))


def setnoisy(draw):
    # 填充噪点
    color = (0, 0, 0)
    for _ in range(randNum(300, 500)):
        draw.point((randNum(0, 850), randNum(0, 50)), fill=color)


def addline(draw, size):
    # 添加干扰线
    draw.line((randNum(0, size[0]), randNum(0, size[1]), randNum(0, size[0]), randNum(0, size[1])),
              fill=(0, 0, 0), width=randNum(2, 4))


def imgscreate():
    global imgsnum
    # 图像生成和对应文本保存
    im, imgBoxes, texts = draw_txt()
    for index, box in enumerate(imgBoxes):
        # print box
        imgsnum += 1
        smimg = im.crop(box)
        path = os.path.join(root, uuid1().__str__())
        smimg = smimg.resize((280, 32), Image.ANTIALIAS)
        sming = smimg.convert("RGB")
        sming.save(path + ".jpg")

        with open(path + ".txt", "w") as datatxt:
            datatxt.write(texts[index].encode('utf-8'))

        for word in texts[index]:
            if word not in wordclassnum.keys():
                wordclassnum[word] = 1
            else:
                num = wordclassnum[word]
                wordclassnum[word] = num + 1

        if imgsnum % shownum == 0:
            print "create %d picture" % imgsnum


if __name__ == "__main__":
    start = time.time()
    if not os.path.exists(root):
        os.makedirs(root)

    for i in range(batch):
        imgscreate()

    with open("Statistics.txt", 'w') as fs:
        Stat = ""
        for key, value in wordclassnum.items():
            Stat += key.encode('utf-8') + "->" +str(value) + "\n"
        fs.write(Stat)

    end = time.time()
    print "spend times:%f" % (end - start)
