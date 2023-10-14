import streamlit as st
from PIL import Image, ImageFilter
import io
import zipfile

def process_image(img, target_size, blur_radius):
    # リサイズしてブラーさせる
    img_resized = img.resize(target_size).filter(ImageFilter.GaussianBlur(blur_radius))
    
    # ブラーさせた画像に元の画像をはめ込む
    img_resized.paste(img, (int((target_size[0] - img.width) / 2), int((target_size[1] - img.height) / 2)))
    
    # 16:9の縦長の画像になるようにクロップ
    aspect_ratio = 9/16
    new_width = img_resized.height * aspect_ratio
    left = (img_resized.width - new_width) / 2
    right = left + new_width
    img_cropped = img_resized.crop((left, 0, right, img_resized.height))
    
    return img_cropped


st.title('SquareMotion v1.0')

st.write("""
## アプリの概要
このアプリは、アップロードされた正方形の画像を指定されたサイズにリサイズし、ブラー効果を追加した後、16:9の縦長の画像にクロップします。
## 使い方
1. 正方形の画像をアップロードします。
2. リサイズ後のサイズとブラーの半径をスライダーで指定します。
3. 処理された画像を確認し、ダウンロードボタンから保存できます。
""")


uploaded_files = st.file_uploader('画像をアップロードしてください', type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

target_size = st.slider('リサイズ後のサイズ', min_value=100, max_value=3000, value=2000)
blur_radius = st.slider('ブラーの半径', min_value=0, max_value=50, value=10)

processed_images = []

if uploaded_files:
    for uploaded_file in uploaded_files:
        img = Image.open(uploaded_file)
        processed_img = process_image(img, (target_size, target_size), blur_radius)
        
        st.image(processed_img, caption=f'Processed {uploaded_file.name}', use_column_width=True)
        
        img_byte_arr = io.BytesIO()
        processed_img.save(img_byte_arr, format='PNG')
        processed_images.append((f'processed_{uploaded_file.name}', img_byte_arr.getvalue()))
        
        # 個別の画像ダウンロードボタン
        st.download_button(
            label="Download Processed Image",
            data=img_byte_arr.getvalue(),
            file_name=f'processed_{uploaded_file.name}',
            mime="image/png"
        )
    
    # 一括ダウンロードのためのZIP作成
    if processed_images:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zf:
            for file_name, img_data in processed_images:
                zf.writestr(file_name, img_data)
        zip_buffer.seek(0)
        
        st.download_button(
            label="Download All Processed Images (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="processed_images.zip",
            mime="application/zip"
        )