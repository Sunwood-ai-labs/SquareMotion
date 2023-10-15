# main.py
import streamlit as st
from PIL import Image
import io
import zipfile
import random
import pandas as pd
import os
from image_processor import process_image, create_video_from_image, concatenate_videos, list_files_with_permissions  # 画像処理関数を別ファイルからインポート
from moviepy.editor import *
import tempfile

import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import seaborn as sns

def app_description():
    """Display the description of the app."""
    st.title('SquareMotion v2.0.1')
    st.markdown("""
    ### アプリの概要

    このアプリは、ユーザーがアップロードした画像を基に動画を生成するものです。
    ユーザーは複数の画像をアップロードし、それぞれの画像に基づく動画の再生時間をランダムに設定することができます。
    生成されたこれらの動画は一つの連続した動画として結合することも可能です。
    
    #### 使い方
    1. 正方形の画像をアップロードします。
    2. リサイズ後のサイズとブラーの半径などのパラメータをスライダーで指定します。
    3. 処理された画像/動画を確認し、ダウンロードボタンから保存できます。
                
    #### パラメータ
    """)


def display_processed_images(uploaded_files, target_size, blur_radius, aspect_ratio_w, aspect_ratio_h):
    """画像を処理して表示し、ダウンロードボタンを提供します。"""
    processed_images    = []
    processed_images_np = []
    uploaded_file_names = []
    for uploaded_file in uploaded_files:
        # 画像を読み込み、処理します
        img = Image.open(uploaded_file)
        processed_img = process_image(img, (target_size, target_size), blur_radius, aspect_ratio_w, aspect_ratio_h)
        # st.image(processed_img, caption=f'Processed {uploaded_file.name}', use_column_width=True)
        st.image(processed_img, caption=f'Processed {uploaded_file.name}', width=300)
        
        # 画像のバイトデータを取得
        img_byte_arr = io.BytesIO()
        processed_img.save(img_byte_arr, format='PNG')
        processed_images.append((f'processed_{uploaded_file.name}', img_byte_arr.getvalue()))
        processed_images_np.append(processed_img)
        # 個別の画像ダウンロードボタン
        st.download_button(
            label="処理済み画像をダウンロード",
            data=img_byte_arr.getvalue(),
            file_name=f'processed_{uploaded_file.name}',
            mime="image/png"
        )

        uploaded_file_names.append(uploaded_file.name)

    # 一括ダウンロードのためのZIP作成
    if processed_images:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zf:
            for file_name, img_data in processed_images:
                zf.writestr(file_name, img_data)
        zip_buffer.seek(0)
        
        st.download_button(
            label="すべての処理済み画像をダウンロード (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="processed_images.zip",
            mime="application/zip"
        )

    return processed_images_np, uploaded_file_names

def display_processed_videos(processed_images, uploaded_file_names, min_duration=1, max_duration=3):
    """
    処理済みの画像を使用して動画を作成し、ダウンロードボタンとともに動画を描画します。
    min_duration: 動画の最小期間（秒）
    max_duration: 動画の最大期間（秒）
    """

    video_files = []
    for processed_img, uploaded_name in zip(processed_images, uploaded_file_names):
        
        # 各処理画像に対して動画を作成
        video_duration = random.randint(min_duration, max_duration)  
        video_bytes, mov_name = create_video_from_image(processed_img, video_duration, uploaded_name)
        video_files.append(mov_name)
        # video_bytes.seek(0)
        # 動画を描画
        st.video(video_bytes, format='video/mp4', start_time=0)

        # 動画のダウンロードボタン
        st.download_button(
            label="処理済み動画をダウンロード",
            data=video_bytes,
            file_name=f'processed_{uploaded_name}.mp4',
            mime="video/mp4"
        )


    return video_files
        
def extract_audio_from_file(uploaded_file):
    """アップロードされたファイルから音楽を抽出する関数"""
    if not uploaded_file:
        return None, None

    # 一時ファイルとして保存。拡張子は.wavとする。
    tfile = tempfile.NamedTemporaryFile(delete=False, prefix="audio_extract_", suffix=".wav")
    tfile.write(uploaded_file.getvalue())
    
    audio = None
    if uploaded_file.type == 'video/mp4':
        music_clip = VideoFileClip(tfile.name)
        audio = music_clip.audio
    else:  # 'audio/wav' or 'audio/mpeg' (for MP3)
        audio = AudioFileClip(tfile.name)

    return audio, tfile.name

def save_uploaded_file(uploaded_file):
    """
    StreamlitのUploadedFileを一時ファイルとして保存し、そのファイルパスを返します。
    """
    tfile = tempfile.NamedTemporaryFile(delete=False) 
    tfile.write(uploaded_file.read())
    
    return tfile.name

def visualize_audio_waveform(uploaded_file):
    # 一時ファイルとして保存
    temp_path = save_uploaded_file(uploaded_file)

    # オリジナルのサンプリングレートで音楽ファイルをロード
    y_original, sr_original = librosa.load(temp_path, sr=None)

    # 100分の1のサンプリングレートでロード
    y_resampled, sr_resampled = librosa.load(temp_path, sr=sr_original // 1000)

    # 時刻tを生成
    t = [i/sr_resampled for i in range(len(y_resampled))]

    # pandasのデータフレームを作成
    chart_data = pd.DataFrame({
        'Time': t,
        'Waveform': y_resampled
    })

    # Streamlitのline_chart関数で波形を表示
    st.line_chart(chart_data, x='Time', y='Waveform')

    # 一時ファイルの削除
    # os.remove(temp_path)

def main():
    app_description()
    
    # assets\audioフォルダ内のwavファイルをリストアップ
    audio_files = [f for f in os.listdir('assets/audio') if f.endswith('.wav')]
    audio_files.append("アップロードした音声ファイルを使用する")

    # 音楽として使用するファイルをアップロード
    uploaded_music_file = st.file_uploader('音楽として使用するファイル（MP4/WAV/MP3）をアップロードしてください', type=['mp4', 'wav', 'mp3'])

    # Streamlitのselectboxでwavファイルまたはアップロードされたファイルを選択
    selected_audio_file = st.selectbox("音楽として使用するwavファイルを選択してください", audio_files)

    if selected_audio_file == "アップロードした音声ファイルを使用する":
        if uploaded_music_file:
            # 音楽を抽出
            audio, audio_path = extract_audio_from_file(uploaded_music_file)
        else:
            st.warning("音声ファイルをアップロードしてください")
            audio, audio_path = None, None
    else:
        audio_path = os.path.join('assets/audio', selected_audio_file)
        audio = AudioFileClip(audio_path)

    uploaded_files = st.file_uploader('画像をアップロードしてください', type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

    target_size = st.slider('リサイズ後のサイズ', min_value=100, max_value=3000, value=2000)
    blur_radius = st.slider('ブラーの半径', min_value=0, max_value=50, value=10)
    aspect_ratio_w = st.slider('アスペクト比(W)', min_value=1, max_value=20, value=9)
    aspect_ratio_h = st.slider('アスペクト比(H)', min_value=1, max_value=20, value=16)
    min_duration = st.slider('動画時間の最小値', min_value=1, max_value=7, value=1)
    max_duration = st.slider('動画時間の最大値', min_value=1, max_value=7, value=3)

    st.markdown("### Music visualize")
    if uploaded_music_file:
        visualize_audio_waveform(uploaded_music_file)

    st.markdown("### Vertical transformation")
    processed_images, uploaded_file_names = display_processed_images(uploaded_files, target_size, blur_radius, aspect_ratio_w, aspect_ratio_h)

    
    st.markdown("### Motion transformation")
    video_files = display_processed_videos(processed_images, uploaded_file_names, min_duration,  max_duration)

    st.markdown("### Combined video")    


    # 動画を結合
    if(video_files):

        # video_filesをpandas DataFrameに変換
        df_video_files = pd.DataFrame(video_files, columns=["Video Files"])

        # Streamlitにテーブルとして表示
        st.table(df_video_files)
        
        combined_video = concatenate_videos(video_files, audio_path, audio=audio)

        # Streamlitで表示
        st.video(combined_video, format="video/mp4")

        # ダウンロードボタン
        st.download_button(
            label="結合された動画をダウンロード",
            data=combined_video,
            file_name="combined_video.mp4",
            mime="video/mp4"
        )


if __name__ == "__main__":
    main()
    # streamlit run app.py