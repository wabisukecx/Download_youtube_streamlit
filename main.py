"""YouTubeおよびYoukuダウンロード用のStreamlitアプリケーション - 403エラー対策版.

このモジュールは、YouTubeとYoukuの動画と音声をダウンロードするStreamlitインターフェースを提供します.
403エラー対策として複数の回避策を実装しています.
"""

import os
import glob
import tempfile
import re
import time
from typing import Dict, Optional, Tuple

import streamlit as st
from yt_dlp import YoutubeDL


class VideoDownloader:
    """YouTubeとYoukuの動画と音声をダウンロードするクラス - 403エラー対策版."""

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
    def get_download_options(mode: str, use_cookies: bool = False) -> Dict:
        """
        選択されたモードに基づいて403エラー対策を含むダウンロードオプションを設定する.

        Args:
            mode (str): ダウンロードモード（'音声のみ' または '映像'）
            use_cookies (bool): ブラウザのクッキーを使用するかどうか

        Returns:
            Dict: yt-dlp用の設定オプション（403エラー対策含む）
        """
        # Streamlit Cloud用 403エラー対策の基本設定
        common_options = {
            'quiet': False,
            'no_warnings': False,
            # Streamlit CloudではffmpegはPATHから自動検出
            # 'ffmpeg_location': os.getenv('FFMPEG_PATH', 'ffmpeg'),
            
            # 403エラー対策設定（Streamlit Cloud最適化）
            'extractor_retries': 5,
            'fragment_retries': 5,
            'retry_sleep_functions': {
                'http': lambda n: min(4 ** n, 16),  # 最大16秒まで
                'fragment': lambda n: min(2 ** n, 8)
            },
            'sleep_interval': 2,  # Streamlit Cloudでは少し長めに
            'max_sleep_interval': 5,
            
            # より強力なユーザーエージェントとヘッダー設定
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            },
            
            # 地域制限対策
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            
            # Streamlit Cloud環境での追加設定
            'no_check_certificate': True,  # SSL証明書チェックをスキップ
            'prefer_insecure': False,
            'call_home': False,  # テレメトリを無効化
        }

        # クッキー設定（必要に応じて）
        if use_cookies:
            common_options.update({
                'cookiesfrombrowser': ('firefox',),  # Firefoxのクッキーを使用
                # または特定のクッキーファイルを指定
                # 'cookiefile': '/path/to/cookies.txt',
            })

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
            'format': 'best[ext=mp4]/best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }]
        }

    @staticmethod
    def clear_cache():
        """Streamlit Cloud環境でyt-dlpのキャッシュをクリアする."""
        try:
            # Streamlit Cloud環境でのキャッシュディレクトリ候補
            possible_cache_dirs = [
                os.path.expanduser('~/.cache/yt-dlp'),
                os.path.join(os.getcwd(), '.cache', 'yt-dlp'),
                '/tmp/yt-dlp-cache',
                '/app/.cache/yt-dlp'  # Streamlit Cloud特有のパス
            ]
            
            cache_cleared = False
            for cache_dir in possible_cache_dirs:
                if os.path.exists(cache_dir):
                    try:
                        import shutil
                        shutil.rmtree(cache_dir)
                        st.info(f"キャッシュをクリアしました: {cache_dir}")
                        cache_cleared = True
                    except Exception as e:
                        st.warning(f"キャッシュクリア失敗 ({cache_dir}): {e}")
            
            if not cache_cleared:
                st.info("クリアするキャッシュが見つかりませんでした")
                
        except Exception as e:
            st.warning(f"キャッシュクリア中にエラー: {e}")

    @staticmethod
    def download_video_content(url: str, mode: str, use_cookies: bool = False, 
                             clear_cache_first: bool = False) -> Optional[Tuple[bytes, str]]:
        """
        403エラー対策を含むYouTubeまたはYoukuのコンテンツダウンロード.

        Args:
            url (str): 動画URL（YouTubeまたはYouku）
            mode (str): ダウンロードモード（'音声のみ' または '映像'）
            use_cookies (bool): ブラウザのクッキーを使用するかどうか
            clear_cache_first (bool): ダウンロード前にキャッシュをクリアするかどうか

        Returns:
            Optional[Tuple[bytes, str]]: ダウンロードしたファイルの内容（バイナリ）とファイル名。失敗した場合はNone
        """
        try:
            # キャッシュクリア（必要に応じて）
            if clear_cache_first:
                VideoDownloader.clear_cache()

            # Youkuの場合、URLを標準形式に変換
            source = VideoDownloader.get_video_source(url)
            if source == 'youku':
                original_url = url
                url = VideoDownloader.normalize_youku_url(url)
                if original_url != url:
                    st.info(f"YoukuのURLを標準形式に変換しました: {url}")

            with tempfile.TemporaryDirectory() as temp_dir:
                # ダウンロードオプションの取得（403エラー対策含む）
                yt_opt = VideoDownloader.get_download_options(mode, use_cookies)
                yt_opt['outtmpl'] = os.path.join(temp_dir, 'downloaded_file.%(ext)s')
                
                # yt-dlpのバージョン情報をログに出力
                import yt_dlp
                st.info(f"yt-dlpバージョン: {yt_dlp.version.__version__}")
                
                # プログレスフックを追加（オプション）
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        if 'total_bytes' in d:
                            percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                            st.progress(percent / 100)
                
                yt_opt['progress_hooks'] = [progress_hook]
                
                # 複数回の試行を実装
                max_attempts = 3
                for attempt in range(max_attempts):
                    try:
                        st.info(f"ダウンロード試行 {attempt + 1}/{max_attempts}")
                        
                        # ダウンロード実行
                        with YoutubeDL(yt_opt) as yt:
                            yt.download([url])
                        break  # 成功した場合はループを抜ける
                        
                    except Exception as e:
                        error_msg = str(e)
                        st.warning(f"試行 {attempt + 1} 失敗: {error_msg}")
                        
                        if "403" in error_msg or "Forbidden" in error_msg:
                            if attempt < max_attempts - 1:
                                wait_time = (attempt + 1) * 2
                                st.info(f"{wait_time}秒待機してからリトライします...")
                                time.sleep(wait_time)
                            else:
                                raise Exception("403エラーが継続しています。後で再試行してください。")
                        else:
                            raise e

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
            error_msg = str(error)
            st.error(f"ダウンロード中にエラーが発生しました: {error_msg}")
            
            # 403エラー固有のアドバイス（Streamlit Cloud用）
            if "403" in error_msg or "Forbidden" in error_msg:
                st.error("❌ HTTP 403 Forbidden エラーが発生しました")
                st.info("""
                **Streamlit Cloud での 403エラー解決策:**
                1. 📋 requirements.txt で yt-dlp>=2025.01.15 を指定
                2. 🔄 アプリを再デプロイしてyt-dlpを更新
                3. 🍪 「ブラウザクッキーを使用」オプションを試す
                4. 🗑️ 「キャッシュをクリア」してから再試行
                5. ⏰ しばらく時間をおいてから再試行
                6. 🌍 動画が地域制限されている可能性があります
                7. 🔧 GitHub リポジトリで requirements.txt を確認
                """)
                
                # Streamlit Cloud特有の追加情報
                st.warning("""
                **Streamlit Cloud 環境での注意:**
                - yt-dlpのバージョンは requirements.txt で管理されます
                - アプリの再デプロイが必要な場合があります
                - 一部の動画は Streamlit Cloud のネットワーク制限により利用できない場合があります
                """)
            
            # プラットフォーム固有のエラーメッセージ
            source = VideoDownloader.get_video_source(url)
            if source == 'youku':
                st.warning("""
                **Youkuのダウンロードに関する注意:**
                1. yt-dlpが最新バージョンか確認してください
                2. Youkuは地域制限がある場合があります
                3. 中国本土からのアクセスが必要な場合があります
                """)
            return None


def main():
    """YouTube・Youkuダウンロード用のメインStreamlitアプリケーション - 403エラー対策版."""
    st.title("🎥 YouTube・Youkuダウンロードツール")
    st.caption("403エラー対策版")

    # サイドバーでの設定
    st.sidebar.header("⚙️ 設定")
    
    # 403エラー対策オプション
    st.sidebar.subheader("403エラー対策")
    use_cookies = st.sidebar.checkbox(
        "ブラウザクッキーを使用", 
        help="Firefoxのクッキーを使用してダウンロードします（一部の制限動画に有効）"
    )
    
    clear_cache = st.sidebar.checkbox(
        "ダウンロード前にキャッシュをクリア", 
        help="古いキャッシュが原因の403エラーを防ぎます"
    )

    if st.sidebar.button("🗑️ 手動でキャッシュクリア"):
        VideoDownloader.clear_cache()

    st.sidebar.header("ℹ️ Streamlit Cloud 情報")
    st.sidebar.info(
        "**環境:** Streamlit Cloud\n\n"
        "**このツールについて:**\n"
        "- YouTubeとYoukuの動画・音声をダウンロード\n"
        "- 403エラー対策を実装\n"
        "- Cloud環境最適化済み\n\n"
        "**注意事項:**\n"
        "- 著作権法を遵守してください\n"
        "- 個人利用目的でのみ使用\n"
        "- 地域制限に注意してください\n"
        "- アップデートは再デプロイが必要"
    )
    
    # Streamlit Cloud特有の情報
    st.sidebar.header("🔧 トラブルシューティング")
    with st.sidebar.expander("403エラーが発生する場合"):
        st.write("""
        1. **requirements.txt確認**
           - yt-dlp>=2025.01.15 が記載されているか
        
        2. **アプリの再デプロイ**
           - GitHubでコミット後、自動再デプロイ
        
        3. **設定オプション**
           - ブラウザクッキー使用をON
           - キャッシュクリアをON
        
        4. **代替手段**
           - 時間をおいて再試行
           - 異なる動画で確認
        """)

    # メインインターフェース
    ope_mode = st.radio(
        "📁 処理モードを選択:",
        ["音声のみ", "映像"],
        help="音声のみ: MP3形式 | 映像: MP4形式"
    )

    video_url = st.text_input(
        "🔗 YouTubeまたはYoukuのURL:", 
        placeholder="https://www.youtube.com/watch?v=... または https://v.youku.com/...",
        help="動画のURLを貼り付けてください"
    )

    # 詳細設定
    with st.expander("🔧 詳細設定"):
        debug_mode = st.checkbox("デバッグモード", value=False, help="詳細なログを表示")
        quality = st.selectbox(
            "品質設定", 
            ["最高品質", "標準品質", "低品質"], 
            index=0,
            help="ダウンロード品質を選択"
        )

    # ダウンロードボタン
    if st.button("⬇️ ダウンロード", type="primary"):
        if not video_url:
            st.warning("⚠️ URLを入力してください")
            return
            
        if not VideoDownloader.validate_url(video_url):
            st.error("❌ 無効なYouTubeまたはYoukuのURLです")
            return

        # URLのソースを表示
        source = VideoDownloader.get_video_source(video_url)
        st.info(f"🎯 ソース: {source.upper()}")
        
        # プログレスバーとスピナー
        progress_bar = st.progress(0)
        
        with st.spinner(f'🔄 {source.capitalize()}からダウンロード中...'):
            result = VideoDownloader.download_video_content(
                video_url, 
                ope_mode, 
                use_cookies=use_cookies,
                clear_cache_first=clear_cache
            )
            
            if result:
                file_data, file_name = result
                progress_bar.progress(100)
                
                st.success("✅ ダウンロードが完了しました！")
                
                # ファイル情報の表示
                file_size = len(file_data) / (1024 * 1024)  # MB
                st.info(f"📄 ファイル名: {file_name}")
                st.info(f"📏 ファイルサイズ: {file_size:.2f} MB")
                
                # ダウンロードボタン
                st.download_button(
                    label="💾 ファイルをダウンロード",
                    data=file_data,
                    file_name=file_name,
                    mime="application/octet-stream",
                    type="primary"
                )
            else:
                progress_bar.empty()
                st.error("❌ ダウンロードに失敗しました")
                
                if source == 'youku':
                    st.warning("⚠️ Youkuの動画は地域制限や仕様変更により利用できない場合があります")

    # フッター
    st.markdown("---")
    st.markdown(
        "**🌐 Streamlit Cloud で実行中** | "
        "**⚠️ 免責事項:** このツールは教育目的で提供されています。"
        "利用者は著作権法およびプラットフォームの利用規約を遵守する責任があります。"
    )


if __name__ == '__main__':
    main()
