import cv2
import numpy as np


from PIL import Image, ImageFilter

from moviepy.editor import concatenate_videoclips, VideoFileClip
from moviepy.editor import *
import tempfile

import os
import stat

def list_files_with_permissions(directory='.'):
    files = os.listdir(directory)
    permissions = []

    for file in files:
        file_stat = os.stat(os.path.join(directory, file))
        file_mode = file_stat.st_mode

        # ファイルモードを権限の文字列に変換
        perm_str = ''
        for who, who_code in [('USR', 'USR'), ('GRP', 'GRP'), ('OTH', 'OTH')]:
            for perm, perm_code in [('R', 'R'), ('W', 'W'), ('X', 'X')]:
                if file_mode & getattr(stat, f'S_I{perm_code}{who_code}'):
                    perm_str += perm.lower()
                else:
                    perm_str += '-'
        permissions.append(perm_str)

    return list(zip(files, permissions))


def save_uploaded_file(uploaded_file):
    """
    StreamlitのUploadedFileを一時ファイルとして保存し、そのファイルパスを返します。
    """
    tfile = tempfile.NamedTemporaryFile(delete=False) 
    tfile.write(uploaded_file.read())
    print(f"tfile.name is {tfile.name}")
    return tfile.name

def concatenate_videos(video_files, audio_path, audio=None):
    """
    与えられた動画ファイルのリストを結合して1つの動画を作成します。
    video_files: 動画ファイルのパスのリスト
    返り値: 結合された動画のバイトIOオブジェクト
    """
    clips = [VideoFileClip(video_file) for video_file in video_files]
    concatenated_clip = concatenate_videoclips(clips, method="compose")
    
    # 音楽を追加
    if audio:
        # 音楽の長さを動画の長さに合わせる
        print(f"audio_path is {audio_path}")
        audio_clip = AudioFileClip(audio_path)
        video_duration = concatenated_clip.duration

        if audio_clip.duration > video_duration:
            audio_clip = audio_clip.subclip(0, video_duration)
        else:
            # 音楽を繰り返すことで動画の長さに合わせる
            audio_clip = audio_clip.fx(vfx.loop, duration=video_duration)
        
        # 合成された音楽を動画に設定
        concatenated_clip = concatenated_clip.set_audio(audio_clip)

    # 一時ファイル名を定義
    temp_file_name = "temp_concatenated_video.mp4"
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
    # ビデオの名前を設定
    mov_name = f'{uploaded_name}.mp4'
    
    # PIL画像をNumPy配列に変換
    img_np = np.array(image)

    # RGBをBGRに変換 (OpenCVはBGRフォーマットを使用します)
    img_rgb = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
    
    # NumPy配列からmoviepyのVideoClipを作成
    clip = ImageSequenceClip([img_rgb], durations=[duration])

    # 動画をファイルとして保存
    clip.write_videofile(mov_name, fps=30, codec='libx264')

    ls_file_name = os.listdir(".")
    print(f"./ files is {ls_file_name}")

    # 使用例
    for file, perm in list_files_with_permissions("."):
        print(f"{file}: {perm}")

    with open(mov_name, 'rb') as video_file:
        video_bytes = video_file.read()

    return video_bytes, mov_name    

if __name__ == "__main__":
    video_files = ['IMG_2791.JPG.mp4']
    concatenate_videos(video_files)