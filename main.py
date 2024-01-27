import streamlit as st
from yt_dlp import YoutubeDL
import tempfile
import os
import glob

# Streamlitのウェブインターフェース
def main():
    st.title("YouTubeダウンロードツール")

    # ラジオボタンで処理モードを切り替える
    ope_mode = st.radio("処理モードを選択してください：", ["音声のみ", "映像"])

    # YouTubeのURLを入力するテキストボックス
    yt_url = st.text_input("YouTubeのURL : ")

    # ダウンロードボタン
    if st.button("ダウンロード"):
        download_video(yt_url, ope_mode)

# 指定したURLをダウンロードする関数
def download_video(yt_url, ope_mode):
    yt_opt = get_download_options(ope_mode)
    temp_dir = tempfile.mkdtemp()
    yt_opt['outtmpl'] = temp_dir + '/downloaded_file.%(ext)s'

    try:
        with YoutubeDL(yt_opt) as yt:
            yt.download([yt_url])
            # ダウンロードされたファイルを検索
            downloaded_files = glob.glob(temp_dir + '/*')
            if downloaded_files:
                # 最初のダウンロードされたファイルを選択
                filepath = downloaded_files[0]
                with open(filepath, "rb") as file:
                    st.download_button(
                        label="ファイルをダウンロード",
                        data=file,
                        file_name=os.path.basename(filepath),
                        mime="application/octet-stream"
                    )
                st.success("ダウンロードが完了しました！ファイルをダウンロードボタンから保存してください。")
            else:
                st.error("ダウンロードされたファイルが見つかりません。")
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")

# ダウンロードオプションを取得する関数
def get_download_options(ope_mode):
    if ope_mode == "音声のみ":
        return {
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
            'ffmpeg_location': "/usr/bin/ffmpeg"
        }
    else:
        return {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}],
            'ffmpeg_location': "/usr/bin/ffmpeg"
        }

if __name__ == '__main__':
    main()
