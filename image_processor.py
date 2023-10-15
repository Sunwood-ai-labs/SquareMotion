import cv2
import numpy as np


from PIL import Image, ImageFilter

from moviepy.editor import concatenate_videoclips, VideoFileClip
import os

import os
import stat

def list_files_with_permissions(directory='/'):
    files = os.listdir(directory)
    permissions = []

    for file in files:
        file_stat = os.stat(os.path.join(directory, file))
        file_mode = file_stat.st_mode

        permissions.append(file_mode)

    return list(zip(files, permissions))

def concatenate_videos(video_files):
    """
    与えられた動画ファイルのリストを結合して1つの動画を作成します。
    video_files: 動画ファイルのパスのリスト
    返り値: 結合された動画のバイトIOオブジェクト
    """
    clips = [VideoFileClip(video_file) for video_file in video_files]
    concatenated_clip = concatenate_videoclips(clips, method="compose")
    
    # 一時ファイル名を定義
    temp_file_name = "/temp_concatenated_video.mp4"
    concatenated_clip.write_videofile(temp_file_name, codec="libx264")  # 一時ファイルに書き込む
    
    # 一時ファイルを読み込んでバイトとして返す
    with open(temp_file_name, 'rb') as f:
        video_bytes = f.read()

    # 一時ファイルを削除
    os.remove(temp_file_name)
    
    return video_bytes

def process_image(img, target_size, blur_radius, aspect_ratio_w, aspect_ratio_h):
    """
    Process the uploaded image:
    - Resize
    - Apply Gaussian blur
    - Center the original image over the blurred one
    - Crop to a 16:9 aspect ratio (vertical)
    """
    img_resized = img.resize(target_size).filter(ImageFilter.GaussianBlur(blur_radius))
    img_resized.paste(img, (int((target_size[0] - img.width) / 2), int((target_size[1] - img.height) / 2)))

    aspect_ratio = aspect_ratio_w/aspect_ratio_h
    # aspect_ratio = 16/9
    new_width = img_resized.height * aspect_ratio
    left = (img_resized.width - new_width) / 2
    right = left + new_width
    img_cropped = img_resized.crop((left, 0, right, img_resized.height))
    
    return img_cropped

def create_video_from_image(image, duration, uploaded_name):
    """
    与えられたPIL画像と指定した期間（秒）を使用して動画を作成します。
    動画をバイトとして返します。
    """
    # PIL画像をNumPy配列に変換
    img_np = np.array(image)
    
    # RGBをBGRに変換 (OpenCVはBGRフォーマットを使用します)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    
    height, width, layers = img_bgr.shape
    size = (width, height)
    
    # 動画の設定
    fps = 30
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # .mp4フォーマットのために'mp4v'を使用
    fourcc = cv2.VideoWriter_fourcc(*'H264')  # .mp4フォーマットのために'mp4v'を使用

    mov_name = f'/{uploaded_name}.mp4'
    
    out = cv2.VideoWriter(mov_name, fourcc, fps, size)
    
    for _ in range(int(fps * duration)):
        out.write(img_bgr)
    out.release()
    
    ls_file_name = os.listdir("/")
    print(f"/ files is {ls_file_name}")
    # 使用例
    for file, perm in list_files_with_permissions():
        print(f"{file}: {perm}")
        
    with open(mov_name, 'rb') as video_file:
        video_bytes = video_file.read()
    
    return video_bytes, mov_name

if __name__ == "__main__":
    video_files = ['IMG_2791.JPG.mp4']
    concatenate_videos(video_files)