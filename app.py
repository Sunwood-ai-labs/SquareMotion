# main.py
import streamlit as st
from PIL import Image
import io
import zipfile
import random
import pandas as pd
import os
from image_processor import process_image, create_video_from_image, concatenate_videos  # 画像処理関数を別ファイルからインポート

def app_description():
    """Display the description of the app."""
    st.title('SquareMotion v1.2')
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
        

def main():
    app_description()
    
    uploaded_files = st.file_uploader('画像をアップロードしてください', type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

    target_size = st.slider('リサイズ後のサイズ', min_value=100, max_value=3000, value=2000)
    blur_radius = st.slider('ブラーの半径', min_value=0, max_value=50, value=10)
    aspect_ratio_w = st.slider('アスペクト比(W)', min_value=1, max_value=20, value=9)
    aspect_ratio_h = st.slider('アスペクト比(H)', min_value=1, max_value=20, value=16)
    min_duration = st.slider('動画時間の最小値', min_value=1, max_value=7, value=1)
    max_duration = st.slider('動画時間の最大値', min_value=1, max_value=7, value=3)

    st.markdown("### Vertical transformation")
    processed_images, uploaded_file_names = display_processed_images(uploaded_files, target_size, blur_radius, aspect_ratio_w, aspect_ratio_h)

    st.markdown("### Motion transformation")
    video_files = display_processed_videos(processed_images, uploaded_file_names, min_duration,  max_duration)



    st.markdown("### Combined video")
    
    ls_file_name = os.listdir()
    st.markdown(f"files is {ls_file_name}")

    # video_filesをpandas DataFrameに変換
    df_video_files = pd.DataFrame(video_files, columns=["Video Files"])

    # Streamlitにテーブルとして表示
    st.table(df_video_files)

    # 動画を結合
    combined_video = concatenate_videos(video_files)

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