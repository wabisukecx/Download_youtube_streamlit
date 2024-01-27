import streamlit as st
from yt_dlp import YoutubeDL
import os
from tempfile import NamedTemporaryFile

# Streamlitのウェブインターフェース
def main():
    st.title("YouTubeダウンロードツール")

    # ラジオボタンで処理モードを切り替える
    ope_mode = st.radio("処理モードを選択してください：", ["音声のみ", "映像"])

    # YouTubeのURLを入力するテキストボックス
    yt_url = st.text_input("YouTubeのURL : ")

    # ダウンロードボタン
    if st.button("ダウンロード"):
        with NamedTemporaryFile(delete=False, suffix=".mp4") as tmpfile:
            download_success, file_path = download_video(yt_url, ope_mode, tmpfile.name)
            if download_success:
                st.success("ダウンロードが完了しました！")
                st.download_button(label="ファイルをダウンロード", data=open(file_path, "rb"), file_name=os.path.basename(file_path))
            else:
                st.error("ダウンロードに失敗しました。")

# 指定したURLをダウンロードする関数
def download_video(yt_url, ope_mode, output_path):
    yt_opt = get_download_options(ope_mode, output_path)

    try:
        with YoutubeDL(yt_opt) as yt:
            yt.download([yt_url])
        return True, output_path
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        return False, None

# ダウンロードオプションを取得する関数
def get_download_options(ope_mode, output_path):
    if ope_mode == "音声のみ":
        return {
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            'ffmpeg_location': "/usr/bin/ffmpeg",
            'outtmpl': output_path
        }
    else:
        return {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}],
            'ffmpeg_location': "/usr/bin/ffmpeg",
            'outtmpl': output_path
        }

if __name__ == '__main__':
    main()
