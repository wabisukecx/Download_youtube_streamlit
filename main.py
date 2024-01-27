import streamlit as st
from yt_dlp import YoutubeDL

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

    try:
        with YoutubeDL(yt_opt) as yt:
            yt.download([yt_url])
        st.success("ダウンロードが完了しました！")
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")

# ダウンロードオプションを取得する関数
def get_download_options(ope_mode):
    if ope_mode == "音声のみ":
        return {
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],'ffmpeg_location': "/usr/bin/ffmpeg" 
        }
    else:
        return {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}],'ffmpeg_location': "/usr/bin/ffmpeg" 
        }

if __name__ == '__main__':
    main()
