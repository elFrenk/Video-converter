from tkinter import Tk, ttk

from video_to_frames_gui import VideoToFramesAppEnhanced


def main() -> None:
    root = Tk()

    try:
        root.iconbitmap(default="")
    except Exception:
        pass

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    VideoToFramesAppEnhanced(root)
    root.mainloop()


if __name__ == "__main__":
    main()
