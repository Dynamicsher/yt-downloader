from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.uix.widget import Widget

import threading
from yt_dlp import YoutubeDL
import os

# Set background color
Window.clearcolor = (0.07, 0.07, 0.1, 1)


class StatusLog(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self.label = Label(
            text="Waiting for input...",
            font_size="13sp",
            color=(0.6, 0.9, 0.6, 1),
            size_hint_y=None,
            halign="left",
            valign="top",
            padding=(10, 10),
            markup=True,
        )
        self.label.bind(texture_size=self._update_height)
        self.label.bind(width=self._update_text_width)
        self.add_widget(self.label)

    def _update_height(self, instance, value):
        instance.height = value[1]

    def _update_text_width(self, instance, value):
        instance.text_size = (value, None)

    def log(self, msg, color="99ff99"):
        def _update(dt):
            self.label.text += f"\n[color=#{color}]{msg}[/color]"
            self.scroll_y = 0
        Clock.schedule_once(_update)

    def set(self, msg, color="99ff99"):
        def _update(dt):
            self.label.text = f"[color=#{color}]{msg}[/color]"
            self.scroll_y = 1
        Clock.schedule_once(_update)


class CardBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.12, 0.12, 0.18, 1)
            self.rect = RoundedRectangle(radius=[12], pos=self.pos, size=self.size)
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class YTDownloaderApp(App):
    def build(self):
        self.title = "YT Downloader"
        self.formats = []

        root = BoxLayout(orientation="vertical", padding=16, spacing=12)

        # Title
        title = Label(
            text="[b]YT Downloader[/b]",
            markup=True,
            font_size="22sp",
            color=(1, 0.3, 0.3, 1),
            size_hint=(1, None),
            height=40,
        )
        root.add_widget(title)

        # URL Card
        url_card = CardBox(orientation="vertical", padding=12, spacing=8,
                           size_hint=(1, None), height=100)
        url_card.add_widget(Label(text="YouTube URL", font_size="13sp",
                                  color=(0.7, 0.7, 0.9, 1),
                                  size_hint=(1, None), height=20, halign="left"))
        self.url_input = TextInput(
            hint_text="https://youtube.com/watch?v=...",
            multiline=False,
            font_size="14sp",
            background_color=(0.18, 0.18, 0.26, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1),
            cursor_color=(1, 0.3, 0.3, 1),
            size_hint=(1, None),
            height=40,
        )
        url_card.add_widget(self.url_input)
        root.add_widget(url_card)

        # Type + Fetch row
        row1 = BoxLayout(orientation="horizontal", spacing=10,
                         size_hint=(1, None), height=50)

        self.type_spinner = Spinner(
            text="Video",
            values=["Video", "Audio (MP3)"],
            font_size="14sp",
            background_color=(0.2, 0.2, 0.3, 1),
            color=(1, 1, 1, 1),
            size_hint=(0.4, 1),
        )
        self.type_spinner.bind(text=self._on_type_change)

        fetch_btn = Button(
            text="Fetch Formats",
            font_size="14sp",
            background_color=(0.2, 0.4, 0.8, 1),
            color=(1, 1, 1, 1),
            size_hint=(0.6, 1),
        )
        fetch_btn.bind(on_press=self.fetch_formats)

        row1.add_widget(self.type_spinner)
        row1.add_widget(fetch_btn)
        root.add_widget(row1)

        # Format picker (video only)
        self.format_card = CardBox(orientation="vertical", padding=12, spacing=8,
                                   size_hint=(1, None), height=90)
        self.format_card.add_widget(
            Label(text="Select Quality", font_size="13sp",
                  color=(0.7, 0.7, 0.9, 1),
                  size_hint=(1, None), height=20, halign="left"))
        self.format_spinner = Spinner(
            text="Fetch formats first",
            values=[],
            font_size="13sp",
            background_color=(0.2, 0.2, 0.3, 1),
            color=(0.8, 0.8, 0.8, 1),
            size_hint=(1, None),
            height=40,
        )
        self.format_card.add_widget(self.format_spinner)
        root.add_widget(self.format_card)

        # Download button
        self.dl_btn = Button(
            text="⬇  Download",
            font_size="16sp",
            bold=True,
            background_color=(0.85, 0.15, 0.15, 1),
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=52,
        )
        self.dl_btn.bind(on_press=self.start_download)
        root.add_widget(self.dl_btn)

        # Status log
        log_card = CardBox(orientation="vertical", padding=10, spacing=6,
                           size_hint=(1, 1))
        log_card.add_widget(Label(text="Status", font_size="13sp",
                                  color=(0.7, 0.7, 0.9, 1),
                                  size_hint=(1, None), height=20))
        self.status = StatusLog(size_hint=(1, 1))
        log_card.add_widget(self.status)
        root.add_widget(log_card)

        return root

    def _on_type_change(self, spinner, text):
        self.format_card.opacity = 0 if text == "Audio (MP3)" else 1
        self.format_card.disabled = text == "Audio (MP3)"

    def fetch_formats(self, *args):
        url = self.url_input.text.strip()
        if not url:
            self.status.set("Please enter a URL first.", color="ff6666")
            return
        if self.type_spinner.text == "Audio (MP3)":
            self.status.set("Audio mode — no format selection needed.\nReady to download.", color="aaddff")
            return
        self.status.set("Fetching available formats...", color="ffdd88")
        threading.Thread(target=self._fetch_formats_thread, args=(url,), daemon=True).start()

    def _fetch_formats_thread(self, url):
        try:
            opts = {"quiet": True, "no_warnings": True}
            with YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)

            self.formats = []
            seen = set()
            for f in info.get("formats", []):
                height = f.get("height")
                ext = f.get("ext")
                fmt_id = f.get("format_id")
                if height and ext == "mp4" and height not in seen:
                    seen.add(height)
                    label = f"{height}p  [{fmt_id}]"
                    self.formats.append((label, fmt_id))

            self.formats.sort(key=lambda x: -int(x[0].split("p")[0]))

            if not self.formats:
                Clock.schedule_once(lambda dt: self.status.set(
                    "No MP4 formats found for this video.", color="ff6666"))
                return

            labels = [f[0] for f in self.formats]
            def _update(dt):
                self.format_spinner.values = labels
                self.format_spinner.text = labels[0]
                self.status.set(f"Found {len(labels)} formats. Select one and hit Download.", color="99ff99")
            Clock.schedule_once(_update)

        except Exception as e:
            Clock.schedule_once(lambda dt: self.status.set(f"Error: {e}", color="ff6666"))

    def start_download(self, *args):
        url = self.url_input.text.strip()
        if not url:
            self.status.set("Please enter a URL.", color="ff6666")
            return

        mode = self.type_spinner.text
        if mode == "Video":
            if not self.formats or self.format_spinner.text == "Fetch formats first":
                self.status.set("Please fetch formats first.", color="ff6666")
                return
            fmt_id = next((f[1] for f in self.formats if f[0] == self.format_spinner.text), None)
            if not fmt_id:
                self.status.set("Could not resolve format ID.", color="ff6666")
                return
            threading.Thread(target=self._download_video, args=(url, fmt_id), daemon=True).start()
        else:
            threading.Thread(target=self._download_audio, args=(url,), daemon=True).start()

    def _get_download_path(self):
        # Android: save to Downloads folder; fallback to current dir
        try:
            from android.storage import primary_external_storage_path
            base = primary_external_storage_path()
            path = os.path.join(base, "Download")
        except ImportError:
            path = os.path.expanduser("~")
        os.makedirs(path, exist_ok=True)
        return path

    def _progress_hook(self, d):
        if d["status"] == "downloading":
            pct = d.get("_percent_str", "?").strip()
            speed = d.get("_speed_str", "?").strip()
            Clock.schedule_once(lambda dt: self.status.set(
                f"Downloading... {pct}  at {speed}", color="ffdd88"))
        elif d["status"] == "finished":
            Clock.schedule_once(lambda dt: self.status.log(
                "Processing file...", color="aaddff"))

    def _download_audio(self, url):
        self.status.set("Starting audio download...", color="ffdd88")
        path = self._get_download_path()
        opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(path, "%(title)s.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "progress_hooks": [self._progress_hook],
            "quiet": True,
        }
        try:
            with YoutubeDL(opts) as ydl:
                ydl.download([url])
            self.status.log(f"Done! Saved to {path}", color="99ff99")
        except Exception as e:
            self.status.log(f"Error: {e}", color="ff6666")

    def _download_video(self, url, fmt_id):
        self.status.set("Starting video download...", color="ffdd88")
        path = self._get_download_path()
        opts = {
            "format": f"{fmt_id}+bestaudio/best",
            "outtmpl": os.path.join(path, "%(title)s.%(ext)s"),
            "merge_output_format": "mp4",
            "progress_hooks": [self._progress_hook],
            "quiet": True,
        }
        try:
            with YoutubeDL(opts) as ydl:
                ydl.download([url])
            self.status.log(f"Done! Saved to {path}", color="99ff99")
        except Exception as e:
            self.status.log(f"Error: {e}", color="ff6666")


if __name__ == "__main__":
    YTDownloaderApp().run()
