# -*- encoding:utf-8 -*-
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from moviepy.audio.fx.audio_fadein import audio_fadein
import os
import random
import eyed3
from numpy import *

#读取指定路劲下配置文件 配置文件主要功能用于制作视频剪辑
#配置文件构成  需要剪辑的视频-->需要剪辑的开始时间-->需要剪辑的结束时间

#读取配置文件 配置文件目录文件(D:\handleVideo\config\config.cfg)
def readFile():
    clipList = []
    file = "D:\handleVideo\config\config.cfg"
    with open(file, 'r') as f:
        for l in f:
            clipList.append(l.rstrip('\n').rstrip().split('\t'))
    return clipList

#核心函数 处理视频 根据配置文件处理剪辑视频
def handleVideo(file_content):
    for i in range(0, len(file_content)):
        arr = file_content[i][0].split("-->")
        #列出音频文件文件夹下的所有文件 随机抽取音频插入剪切视频
        musicFiles = os.listdir(arr[1])
        musicFilesTempLength = len(musicFiles) - 1
        #视频信息
        clip = VideoFileClip(arr[0]).subclip(arr[2],arr[3])
        #如果music文件夹下只有一个音频文件 则取第0个文件 其余时候取随机位置的音频
        if musicFilesTempLength>0:
            musicFilesIndex = random.randint(0, musicFilesTempLength)
        else:
            musicFilesIndex = 0

        audioClip = AudioFileClip(arr[1] + musicFiles[musicFilesIndex])
        video = clip.set_audio(audioClip)
        videoDuration = int(video.duration)
        # 获取mp3文件的长度 最多从音频文件的长度-video.duration的长度开始截取长度为video.duration的音频
        # 随机选择Music文件夹下的音频文件
        musicInfo = eyed3.load(arr[1] + musicFiles[musicFilesIndex])
        # 得到mp3文件的长度 单位为秒
        musicSecs = int(format(musicInfo.info.time_secs))
        # 随机开始位置 确保加上video.duration之后不超过mp3文件的总长  最后几秒基本没有声音了 所以最多截到倒数第10秒
        #如果所截视频长度大于音频长度 则从音频的0秒开始截取
        if musicSecs - videoDuration <=0:
            musicStart = 0
            musicEnd = musicSecs

        else:
            musicStart = random.randint(0, musicSecs - videoDuration)
            musicEnd = musicStart + videoDuration

        # 从随机位置开始截取音频 并设置淡入淡出效果
        video.audio = video.audio.subclip(musicStart, musicEnd)
        try:
            video.audio = audio_fadein(video.audio, 2.0)
            video.audio = audio_fadeout(video.audio, 2.0)
        except Exception as e:
            with open('error.txt', mode="w+") as f:
                f.write(str(e))

        # 设置视频尺寸 设置视频居中显示
        result = CompositeVideoClip([video.set_pos(('center'))], size=(1366, 728))
        #创建存储目录
        outputVideoPath = arr[1] + "../outputVideo/"
        isExists = os.path.exists(outputVideoPath)
        if not isExists:
            os.makedirs(outputVideoPath)
        result.write_videofile(outputVideoPath + "outputVideo" + str(i) + ".mp4",
                               codec="libx264",
                               fps=15,
                               bitrate="512K",
                               audio_fps=44100,
                               audio_bitrate="128k")
        i += 1

#获取配置文件内容
file_content = readFile()
handleVideo(file_content)
input()
