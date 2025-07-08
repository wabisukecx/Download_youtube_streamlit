# YouTube & Youku Download Tool

This Streamlit application is a tool for downloading videos and audio from YouTube and Youku. Users can select between "audio only" or "video" download modes and retrieve files after downloading.

> **Important Notice:**  
> - Please use this tool for personal purposes only.  
> - Be careful when downloading copyrighted content.  
> - Please comply with YouTube's and Youku's Terms of Service when using this tool.
> - Youku content may be subject to regional restrictions.

## Features

This application offers two primary download modes to suit different user needs. The audio-only mode extracts high-quality MP3 audio files at 192kbps from both YouTube and Youku videos, making it perfect for music or podcast content. The video download mode captures complete videos in MP4 format, preserving both visual and audio content with the best available quality.

## Installation

### Prerequisites

Before installing this application, ensure that Python 3.7 or later is installed on your system. Additionally, you'll need to install ffmpeg, which is essential for audio and video processing. The ffmpeg binary must be properly configured in your system's PATH environment variable.

For Windows users, download the ffmpeg binaries from the official ffmpeg website at https://ffmpeg.org/download.html and configure your system PATH to include the ffmpeg installation directory.

### Installing Required Packages

Install the necessary Python libraries by running the following command in your terminal or command prompt:

```bash
pip install streamlit yt_dlp
```

## Usage

To get started with the application, first clone this repository or download the source code to your local machine. Once you have the files, navigate to the application directory using your terminal or command prompt.

Launch the Streamlit application by executing `streamlit run main.py` in your terminal. The application will start a local web server, and your default browser should automatically open to display the interface. If the browser doesn't open automatically, you can manually navigate to the local URL that appears in your terminal output.

The application interface is straightforward to use. Simply enter a YouTube or Youku video URL into the input field and click the "Download" button. The application supports various URL formats including standard YouTube URLs like `https://www.youtube.com/watch?v=...` and shortened URLs like `https://youtu.be/...`. For Youku, you can use URLs in the format `https://v.youku.com/v_show/id_XXXXXX.html` or other Youku formats, which will be automatically normalized to the standard format.

After processing, the application will generate a file according to your selected download mode and provide a download link for you to retrieve the processed content.

## Important Notes

### Copyright Notice
This tool is designed for educational and personal use only and is not intended to facilitate unauthorized downloading of copyrighted content. Users must strictly adhere to personal use guidelines and comply with both YouTube's and Youku's Terms of Service. Always respect intellectual property rights and ensure you have appropriate permissions before downloading any content.

### Error Handling
When errors occur during the download process, the application displays detailed error messages to help diagnose the issue. These messages are designed to guide you toward a solution, whether the problem relates to URL validity, video availability, or network connectivity.

## Technical Details

The application utilizes modern technologies to provide reliable downloading capabilities. In audio mode, the system downloads the best available audio stream and converts it to MP3 format at 192kbps bitrate, ensuring high-quality audio output. Video mode captures the highest quality video available in MP4 format while preserving the original audio track.

The application supports two major video platforms. YouTube functionality is fully supported with comprehensive format compatibility, while Youku support includes automatic URL normalization and consideration for regional restrictions. The underlying technology stack consists of Streamlit for the web interface, yt-dlp for the core downloading functionality, and ffmpeg for audio and video processing tasks.

## Troubleshooting

### Common Issues
Most download failures stem from a few common causes. If ffmpeg is not properly installed or configured in your system PATH, the application will be unable to process audio and video files. Network connectivity issues can also prevent successful downloads, so ensure your internet connection is stable and reliable.

Video accessibility is another frequent issue. Some videos may be private, deleted, or subject to regional restrictions that prevent downloading. Always verify that the video URL is correct and that the content is publicly accessible before attempting to download.

### Error Diagnosis
The application provides comprehensive error messages to help identify and resolve issues quickly. When troubleshooting persistent problems, first verify that your internet connection is stable and that the target video is not region-restricted, private, or deleted.

### Youku-Specific Considerations
Youku content presents unique challenges due to regional restrictions and platform-specific requirements. The application automatically normalizes Youku URLs to the standard format `https://v.youku.com/v_show/id_XXXXXX.html`, but some content may still be geographically restricted and require access from mainland China.

For optimal Youku compatibility, ensure that yt-dlp is updated to the latest version, as the platform frequently updates its streaming protocols. If you encounter persistent issues with Youku content, the restriction may be related to your geographic location or the specific content's availability policies.

## License

This project is for educational and personal use only. Users are responsible for ensuring their use complies with applicable laws and platform terms of service.

## Author

wabisuke

---

**Disclaimer**: This tool is provided as-is for educational purposes. The authors are not responsible for any misuse or violation of terms of service by users.
