"""YouTubeダウンロード用のStreamlitアプリケーション.

このモジュールは、YouTubeの動画と音声をダウンロードするStreamlitインターフェースを提供します.
著作権に配慮し、個人的な利用目的のみで使用してください.
"""

import os
import glob
import tempfile
from typing import Dict, Optional, Tuple

import streamlit as st
from yt_dlp import YoutubeDL


class YouTubeDownloader:
    """YouTubeの動画と音声をダウンロードするクラス."""

    @staticmethod
    def validate_url(url: str) -> bool:
        """
        YouTubeのURL形式を検証する.

        Args:
            url (str): 検証するURL

        Returns:
            bool: 有効なYouTube URLの場合はTrue、そうでない場合はFalse
        """
        return url.startswith(('https://www.youtube.com/', 'https://youtu.be/'))

    @staticmethod
    def get_download_options(mode: str) -> Dict:
        """
        選択されたモードに基づいてダウンロードオプションを設定する.

        Args:
            mode (str): ダウンロードモード（'音声のみ' または '映像'）

        Returns:
            Dict: yt-dlp用の設定オプション
        """
        # 共通の基本設定
        common_options = {
            'quiet': True,             # コンソール出力を抑制
            'no_warnings': True,        # 警告メッセージを非表示
            'ffmpeg_location': "/usr/bin/ffmpeg"
        }

        if mode == "音声のみ":
            # 音声のみモード（MP3形式に変換）
            return {
                **common_options,
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }]
            }

        # 映像モード（MP4形式に変換）
        return {
            **common_options,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }]
        }

    @staticmethod
    def download_youtube_content(url: str, mode: str) -> Optional[Tuple[bytes, str]]:
        """
        YouTubeのコンテンツを一時ディレクトリにダウンロードし、ファイル内容を返す.

        Args:
            url (str): YouTubeの動画URL
            mode (str): ダウンロードモード（'音声のみ' または '映像'）

        Returns:
            Optional[Tuple[bytes, str]]: ダウンロードしたファイルの内容（バイナリ）とファイル名。失敗した場合はNone
        """
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # ダウンロードオプションの取得
                yt_opt = YouTubeDownloader.get_download_options(mode)
                yt_opt['outtmpl'] = os.path.join(temp_dir, 'downloaded_file.%(ext)s')

                # ダウンロード実行
                with YoutubeDL(yt_opt) as yt:
                    yt.download([url])

                # 一時ディレクトリ内のファイルを探索
                downloaded_files = glob.glob(os.path.join(temp_dir, '*'))
                if downloaded_files:
                    file_path = downloaded_files[0]
                    file_name = os.path.basename(file_path)
                    with open(file_path, "rb") as f:
                        file_data = f.read()
                    return file_data, file_name
                return None

        except Exception as error:
            st.error(f"ダウンロード中にエラーが発生しました: {error}")
            return None


def main():
    """YouTubeダウンロード用のメインStreamlitアプリケーション."""
    st.title("YouTubeダウンロードツール")

    st.sidebar.header("アプリケーション情報")
    st.sidebar.info(
        "このツールはYouTubeの動画と音声をダウンロードできます。\n\n"
        "注意:\n"
        "- 著作権に注意してください\n"
        "- 個人的な利用目的でのみ使用してください"
    )

    ope_mode = st.radio(
        "処理モードを選択してください：",
        ["音声のみ", "映像"],
        help="音声のみ: MP3形式でダウンロード, 映像: MP4形式でダウンロード"
    )

    yt_url = st.text_input("YouTubeのURL:", placeholder="https://www.youtube.com/watch?v=...")

    if st.button("ダウンロード"):
        if not YouTubeDownloader.validate_url(yt_url):
            st.error("無効なYouTube URLです。正しいURLを入力してください。")
            return

        with st.spinner('ダウンロード中...'):
            result = YouTubeDownloader.download_youtube_content(yt_url, ope_mode)
            if result:
                file_data, file_name = result
                st.download_button(
                    label="ファイルをダウンロード",
                    data=file_data,
                    file_name=file_name,
                    mime="application/octet-stream"
                )
                st.success("ダウンロードが完了しました！")
            else:
                st.error("ダウンロードに失敗しました。URLを確認してください。")


if __name__ == '__main__':
    main()
