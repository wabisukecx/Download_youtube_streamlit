"""YouTubeおよびYoukuダウンロード用のStreamlitアプリケーション.

このモジュールは、YouTubeとYoukuの動画と音声をダウンロードするStreamlitインターフェースを提供します.
著作権に配慮し、個人的な利用目的のみで使用してください.
"""

import os
import glob
import tempfile
import re
from typing import Dict, Optional, Tuple

import streamlit as st
from yt_dlp import YoutubeDL


class VideoDownloader:
    """YouTubeとYoukuの動画と音声をダウンロードするクラス."""

    @staticmethod
    def validate_url(url: str) -> bool:
        """
        YouTubeまたはYoukuのURL形式を検証する.

        Args:
            url (str): 検証するURL

        Returns:
            bool: 有効なYouTubeまたはYoukuのURLの場合はTrue、そうでない場合はFalse
        """
        youtube_valid = url.startswith(('https://www.youtube.com/', 'https://youtu.be/'))
        youku_valid = url.startswith(('https://v.youku.com/', 'https://m.youku.com/')) or 'youku.com' in url
        return youtube_valid or youku_valid

    @staticmethod
    def get_video_source(url: str) -> str:
        """
        URLからビデオプラットフォームのソースを判定する.

        Args:
            url (str): 動画URL

        Returns:
            str: 'youtube' または 'youku'
        """
        if url.startswith(('https://www.youtube.com/', 'https://youtu.be/')):
            return 'youtube'
        elif 'youku.com' in url:
            return 'youku'
        return 'unknown'

    @staticmethod
    def normalize_youku_url(url: str) -> str:
        """
        Youkuの様々なURL形式を標準形式に変換する.

        Args:
            url (str): 元のYoukuのURL

        Returns:
            str: 標準化されたURL
        """
        if "youku.com" in url and "vid=" in url:
            # VIDを抽出
            vid_match = re.search(r'vid=([^&]+)', url)
            if vid_match:
                vid = vid_match.group(1)
                # 標準的なYoukuのURLフォーマットに変換
                normalized_url = f"https://v.youku.com/v_show/id_{vid}.html"
                return normalized_url
        return url

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
            'quiet': False,             # デバッグのために出力を有効化
            'no_warnings': False,        # デバッグのために警告も表示
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
    def download_video_content(url: str, mode: str) -> Optional[Tuple[bytes, str]]:
        """
        YouTubeまたはYoukuのコンテンツを一時ディレクトリにダウンロードし、ファイル内容を返す.

        Args:
            url (str): 動画URL（YouTubeまたはYouku）
            mode (str): ダウンロードモード（'音声のみ' または '映像'）

        Returns:
            Optional[Tuple[bytes, str]]: ダウンロードしたファイルの内容（バイナリ）とファイル名。失敗した場合はNone
        """
        try:
            # Youkuの場合、URLを標準形式に変換
            source = VideoDownloader.get_video_source(url)
            if source == 'youku':
                original_url = url
                url = VideoDownloader.normalize_youku_url(url)
                if original_url != url:
                    st.info(f"YoukuのURLを標準形式に変換しました: {url}")

            with tempfile.TemporaryDirectory() as temp_dir:
                # ダウンロードオプションの取得
                yt_opt = VideoDownloader.get_download_options(mode)
                yt_opt['outtmpl'] = os.path.join(temp_dir, 'downloaded_file.%(ext)s')
                
                # yt-dlpのバージョン情報をログに出力（デバッグ用）
                import yt_dlp
                st.info(f"yt-dlpバージョン: {yt_dlp.version.__version__}")
                
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
            
            # プラットフォーム固有のエラーメッセージ
            source = VideoDownloader.get_video_source(url)
            if source == 'youku':
                st.warning("""
                Youkuのダウンロードに関する注意:
                1. yt_dlpが最新バージョンか確認してください（pip install -U yt_dlp）
                2. Youkuは地域制限がある場合があります
                3. 通常のYoukuのURLは https://v.youku.com/v_show/id_XXXXXX.html の形式です
                4. 中国本土からのアクセスが必要な場合があります
                """)
            return None


def main():
    """YouTubeおよびYoukuダウンロード用のメインStreamlitアプリケーション."""
    st.title("YouTube・Youkuダウンロードツール")

    st.sidebar.header("アプリケーション情報")
    st.sidebar.info(
        "このツールはYouTubeとYoukuの動画と音声をダウンロードできます。\n\n"
        "注意:\n"
        "- 著作権に注意してください\n"
        "- 個人的な利用目的でのみ使用してください\n"
        "- Youkuの動画は地域制限により利用できない場合があります"
    )

    ope_mode = st.radio(
        "処理モードを選択してください：",
        ["音声のみ", "映像"],
        help="音声のみ: MP3形式でダウンロード, 映像: MP4形式でダウンロード"
    )

    video_url = st.text_input("YouTubeまたはYoukuのURL:", 
                            placeholder="https://www.youtube.com/watch?v=... または https://v.youku.com/...")

    # 詳細設定の折りたたみセクション
    with st.expander("詳細設定"):
        st.checkbox("デバッグモード", value=False, key="debug_mode", 
                    help="有効にすると詳細なログが表示されます")
        st.selectbox("ダウンロード品質", ["最高品質", "標準品質", "低品質"], index=0, key="quality",
                    help="動画/音声のダウンロード品質を選択します")

    if st.button("ダウンロード"):
        if not video_url:
            st.warning("URLを入力してください。")
            return
            
        if not VideoDownloader.validate_url(video_url):
            st.error("無効なYouTubeまたはYoukuのURLです。正しいURLを入力してください。")
            return

        # URLのソースを取得（YouTubeかYoukuか）
        source = VideoDownloader.get_video_source(video_url)
        
        with st.spinner(f'{source.capitalize()}からダウンロード中...'):
            result = VideoDownloader.download_video_content(video_url, ope_mode)
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
                if source == 'youku':
                    st.warning("Youkuの動画は地域制限や最新の仕様変更により、ダウンロードできない場合があります。")


if __name__ == '__main__':
    main()
