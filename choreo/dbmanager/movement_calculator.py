# 움직임 크기 계산하기
# 
# 1. 2마디 단위로 잘린 영상 가져오기
# 2. 영상을 9개 구간으로 나눠서(박자마다) 포즈 값 불러오기
# 3. 포즈 값을 하나씩 불러 올 때마다 움직임 값 상위 3개 합쳐서 저장

import os
import cv2
import csv
import youtube_dlc
from parse import *


def sec_to_time(sec):
    time = ""
    temp = 0
    for i in range(3):
        temp = sec % 60
        time = str(sec % 60) + time if temp >= 10 else "0" + str(temp) + time
        sec //= 60
        if i < 2:
            time = ":" + time
    return time


def download_video(vidlink, start_sec, end_sec):
    ydl = youtube_dlc.YoutubeDL({'format': 'best/best'}, )

    with ydl:
        video = ydl.extract_info(
            vidlink,
            download=False
        )
    url = video['url']
    fps = video['fps']

    start_time = sec_to_time(start_sec)
    duration_time = sec_to_time(end_sec - start_sec)

    if os.path.exists('vid.mp4'):
        os.remove('vid.mp4')

    os.system("ffmpeg -i '%s' -ss %s -t %s -async 1 -strict -2 'vid.mp4'" % (url, start_time, duration_time))


def calc_movement(i, row):
    vidcap = cv2.VideoCapture('slice_vid_' + str(i - 3) + '.mp4')
    frame_num = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
    idx = 0;
    count = 0;

    front = [([0] * 2)] * 18
    back = [([0] * 2)] * 18

    first_time = True

    while (vidcap.isOpened()):
        ret, image = vidcap.read()

        if ret == False:
            break

        if count == (int)((frame_num - 2) * idx / 8):
            cv2.imwrite('movementImage.jpg', image)
            os.system('python tf_openpose/run.py --model=cmu --resize=432x368 --image=movementImage.jpg')

            value = 0.0
            front = []
            for i in range(18):
                front.append(back[i])

            key_point_csv = open('key_point_coordinates.csv', 'r')

            back = []
            key_point_raw = []

            for line in key_point_csv:
                key_point_raw.append(line.strip('\n'))

            for i in range(0, len(key_point_raw)):
                back.append(key_point_raw[i].split(','))

            x_mean = int(back[18][0].strip())
            y_min = int(back[19][0].strip())

            for i in range(0, 18):
                back[i][0] = int(back[i][0].strip())
                back[i][1] = int(back[i][1].strip())

                if back[i][0] != 0 or back[i][1] != 0:
                    back[i][0] -= x_mean
                    back[i][1] -= y_min

            if first_time:
                first_time = False
                idx += 1
                continue

            dist = [0] * 18

            for i in range(18):
                if (front[i][0] == 0 and front[i][1] == 0) or (back[i][0] == 0 and back[i][1] == 0):
                    dist[i] = 0
                else:
                    dist[i] = pow(pow((front[i][0] - back[i][0]), 2) + pow((front[i][1] - back[i][1]), 2), 0.5)

            dist.sort(reverse=True)

            for i in range(3):
                value += dist[i]
            idx += 1
            row.append(value)
        count += 1
        return value


if __name__ == '__main__':
    f1 = open('Database_origin.csv', 'r', encoding='utf-8')
    f2 = open('movement.csv', 'w', encoding='utf-8')
    reader = csv.reader(f1)
    writer = csv.writer(f2)

    idx = 0
    start = 1  # 측정할 영상 시작 번호, 1~, start 번호의 영상도 포함됨
    end = 1  # 측적할 영상 끝 번호, end 번호의 영상도 포함됨

    for line in reader:
        idx += 1

        if (idx < start or idx > end):
            continue

        vidlink = line[0]
        choreo_id = parse("{}?v={}", vidlink)[1]
        print(choreo_id)

        start_sec = int(line[1])
        end_sec = int(line[2])

        download_video(vidlink, start_sec, end_sec)
        vidcap = cv2.VideoCapture('vid.mp4')

        # slice video
        for i in range(4, len(line)):
            if line[i] == '' or line[i] == '\n':
                continue

            row = []
            row.append(choreo_id + '_' + str(i - 3))

            frame_range = line[i]
            parsing_frame = parse("{}~{}", frame_range)
            start_frame = int(parsing_frame[0])
            end_frame = int(parsing_frame[1])

            fps = vidcap.get(cv2.CAP_PROP_FPS)
            width = int(vidcap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter('slice_vid_' + str(i - 3) + '.mp4', fourcc, fps, (width, height))

            count = 0

            while (vidcap.isOpened()):
                ret, image = vidcap.read()
                count += 1

                if ret == False:
                    break

                if count >= start_frame + 20 and count <= end_frame - 20:
                    out.write(image)

                if (count > end_frame):
                    break

            out.release()
            row.append(calc_movement(i, row))
            print(row)
            writer.writerow(row)
            if (os.path.exists('slice_vid_' + str(i - 3) + '.mp4')):
                os.remove('slice_vid_' + str(i - 3) + '.mp4')
            break

        vidcap.release()

    f1.close()
    f2.close()
