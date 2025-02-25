"""YouTubeダウンロード用のStreamlitアプリケーション.

このモジュールは、YouTubeの動画と音声をダウンロードするStreamlitインターフェースを提供します.
著作権に配慮し、個人的な利用目的のみで使用してください.
"""

import os
import glob
import tempfile
from typing import Dict, Optional

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
            'quiet': True,  # コンソール出力を抑制
            'no_warnings': True,  # 警告メッセージを非表示
            'ffmpeg_location': "/usr/bin/ffmpeg"
        }

        # 音声のみモード
        if mode == "音声のみ":
            return {
                **common_options,
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',  # MP3形式に変換
                    'preferredquality': '192'  # 高音質設定
                }]
            }
        
        # 映像モード
        return {
            **common_options,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'  # MP4形式に変換
            }]
        }

    @staticmethod
    def download_youtube_content(url: str, mode: str) -> Optional[str]:
        """
        YouTubeのコンテンツを一時ディレクトリにダウンロードする.

        Args:
            url (str): YouTubeの動画URL
            mode (str): ダウンロードモード（'音声のみ' または '映像'）

        Returns:
            Optional[str]: ダウンロードしたファイルのパス。失敗した場合はNone
        """
        try:
            # 一時ディレクトリを作成してダウンロード
            with tempfile.TemporaryDirectory() as temp_dir:
                # ダウンロードオプションを取得
                yt_opt = YouTubeDownloader.get_download_options(mode)
                yt_opt['outtmpl'] = os.path.join(temp_dir, 'downloaded_file.%(ext)s')

                # 動画/音声をダウンロード
                with YoutubeDL(yt_opt) as yt:
                    yt.download([url])

                # ダウンロードされたファイルを検索
                downloaded_files = glob.glob(os.path.join(temp_dir, '*'))
                return downloaded_files[0] if downloaded_files else None

        except Exception as error:
            # ダウンロード中にエラーが発生した場合
            st.error(f"ダウンロード中にエラーが発生しました: {error}")
            return None


def main():
    """YouTubeダウンロード用のメインStreamlitアプリケーション."""
    # アプリケーションのタイトルを設定
    st.title("YouTubeダウンロードツール")

    # サイドバーにアプリケーション情報を表示
    st.sidebar.header("アプリケーション情報")
    st.sidebar.info(
        "このツールはYouTubeの動画と音声をダウンロードできます。\n\n"
        "注意:\n"
        "- 著作権に注意してください\n"
        "- 個人的な利用目的でのみ使用してください"
    )

    # ダウンロードモードを選択
    ope_mode = st.radio(
        "処理モードを選択してください：",
        ["音声のみ", "映像"],
        help="音声のみ: MP3形式でダウンロード, 映像: MP4形式でダウンロード"
    )

    # URLを入力
    yt_url = st.text_input("YouTubeのURL:", placeholder="https://www.youtube.com/watch?v=...")

    # ダウンロードボタン
    if st.button("ダウンロード"):
        # URLを検証
        if not YouTubeDownloader.validate_url(yt_url):
            st.error("無効なYouTube URLです。正しいURLを入力してください。")
            return

        # ダウンロード中にスピナーを表示
        with st.spinner('ダウンロード中...'):
            # ダウンロードを試行
            filepath = YouTubeDownloader.download_youtube_content(yt_url, ope_mode)

            # ダウンロード結果を処理
            if filepath:
                # ファイルをバイナリモードで開く
                with open(filepath, "rb") as file:
                    st.download_button(
                        label="ファイルをダウンロード",
                        data=file,
                        file_name=os.path.basename(filepath),
                        mime="application/octet-stream"
                    )
                st.success("ダウンロードが完了しました！")
            else:
                st.error("ダウンロードに失敗しました。URLを確認してください。")


if __name__ == '__main__':
    main()
