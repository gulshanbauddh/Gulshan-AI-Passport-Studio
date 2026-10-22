import os
import io
import sys
import threading
import urllib.request
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageOps

# Lazy import rembg to ensure GUI opens instantly
remove_bg = None

# Model Configuration
MODEL_URL = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/bria-rmbg-2.0.onnx"
USER_HOME = os.path.expanduser("~")
MODEL_DIR = os.path.join(USER_HOME, ".rembg", "models", "bria-rmbg")
MODEL_PATH = os.path.join(MODEL_DIR, "bria-rmbg.onnx")

# Standard Indian Passport Dimensions (35mm x 45mm @ 300 DPI)
TARGET_W, TARGET_H = 413, 531
TARGET_RATIO = TARGET_W / TARGET_H


class PassportStudioApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Gulshan Studio - AI Passport Photo Maker")
        # self.iconbitmap("app_icon.ico")
        self.geometry("680x620")
        self.minsize(620, 560)
        self.configure(bg="#F1F5F9")

        self.is_processing = False
        self.is_downloading = False

        self.setup_ui()
        self.check_model_status()

    def setup_ui(self):
        # 1. Header Banner
        header = tk.Frame(self, bg="#0F2942", height=70)
        header.pack(fill="x")

        title_lbl = tk.Label(
            header,
            text="Gulshan AI PASSPORT STUDIO",
            font=("Segoe UI", 15, "bold"),
            fg="#FFFFFF",
            bg="#0F2942"
        )
        title_lbl.pack(anchor="w", padx=20, pady=(12, 2))

        sub_lbl = tk.Label(
            header,
            text="Automated White Background & Standard Passport Cropping",
            font=("Segoe UI", 9),
            fg="#CBD5E1",
            bg="#0F2942"
        )
        sub_lbl.pack(anchor="w", padx=20, pady=(0, 10))

        content = tk.Frame(self, bg="#F1F5F9", padx=20, pady=15)
        content.pack(fill="both", expand=True)

        # 2. AI Model Status Card
        model_card = tk.LabelFrame(
            content,
            text=" AI Engine Status ",
            font=("Segoe UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#0F2942",
            padx=15,
            pady=10
        )
        model_card.pack(fill="x", pady=(0, 12))

        status_row = tk.Frame(model_card, bg="#FFFFFF")
        status_row.pack(fill="x")

        self.status_dot = tk.Label(status_row, text="●", font=("Segoe UI", 14), bg="#FFFFFF", fg="#DC2626")
        self.status_dot.pack(side="left", padx=(0, 6))

        self.status_lbl = tk.Label(
            status_row,
            text="Checking AI Model...",
            font=("Segoe UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#334155"
        )
        self.status_lbl.pack(side="left")

        self.btn_download_model = tk.Button(
            status_row,
            text="Download AI Model (1.02 GB)",
            font=("Segoe UI", 8, "bold"),
            bg="#2563EB",
            fg="#FFFFFF",
            activebackground="#1D4ED8",
            activeforeground="#FFFFFF",
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.start_model_download
        )
        self.btn_download_model.pack(side="right")
        self.btn_download_model.pack_forget()

        self.download_progress = ttk.Progressbar(model_card, mode="determinate")
        self.download_info_lbl = tk.Label(model_card, text="", font=("Segoe UI", 8), bg="#FFFFFF", fg="#64748B")

        # 3. Folder Configuration Card
        folder_card = tk.LabelFrame(
            content,
            text=" Directory Setup ",
            font=("Segoe UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#0F2942",
            padx=15,
            pady=12
        )
        folder_card.pack(fill="x", pady=(0, 12))

        # Input Directory
        tk.Label(folder_card, text="Source Folder (Raw Photos):", font=("Segoe UI", 9), bg="#FFFFFF").pack(anchor="w")
        in_frame = tk.Frame(folder_card, bg="#FFFFFF")
        in_frame.pack(fill="x", pady=(3, 10))

        self.in_entry = tk.Entry(in_frame, font=("Segoe UI", 9), relief="solid", bd=1)
        self.in_entry.pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 8))

        btn_browse_in = tk.Button(
            in_frame,
            text="Browse...",
            font=("Segoe UI", 9),
            bg="#E2E8F0",
            relief="flat",
            padx=12,
            pady=2,
            command=self.browse_input
        )
        btn_browse_in.pack(side="right")

        # Output Directory
        tk.Label(folder_card, text="Destination Folder (Passport Photos):", font=("Segoe UI", 9), bg="#FFFFFF").pack(anchor="w")
        out_frame = tk.Frame(folder_card, bg="#FFFFFF")
        out_frame.pack(fill="x", pady=(3, 5))

        self.out_entry = tk.Entry(out_frame, font=("Segoe UI", 9), relief="solid", bd=1)
        self.out_entry.pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 8))

        btn_browse_out = tk.Button(
            out_frame,
            text="Browse...",
            font=("Segoe UI", 9),
            bg="#E2E8F0",
            relief="flat",
            padx=12,
            pady=2,
            command=self.browse_output
        )
        btn_browse_out.pack(side="right")

        # Set default folders if available
        cwd = os.getcwd()
        def_raw = os.path.join(cwd, "raw_photos")
        def_out = os.path.join(cwd, "passport_photos")
        if os.path.exists(def_raw):
            self.in_entry.insert(0, def_raw)
        self.out_entry.insert(0, def_out)

        # 4. Processing Control & Progress Card
        proc_card = tk.LabelFrame(
            content,
            text=" Batch Processing ",
            font=("Segoe UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#0F2942",
            padx=15,
            pady=12
        )
        proc_card.pack(fill="both", expand=True)

        self.proc_progress = ttk.Progressbar(proc_card, mode="determinate")
        self.proc_progress.pack(fill="x", pady=(4, 6))

        self.proc_status_lbl = tk.Label(
            proc_card,
            text="Ready. Select input/output folders and click Start.",
            font=("Segoe UI", 9),
            bg="#FFFFFF",
            fg="#475569"
        )
        self.proc_status_lbl.pack(anchor="w", pady=(0, 10))

        btn_row = tk.Frame(proc_card, bg="#FFFFFF")
        btn_row.pack(fill="x")

        self.btn_start = tk.Button(
            btn_row,
            text="▶  Start Processing Photos",
            font=("Segoe UI", 10, "bold"),
            bg="#16A34A",
            fg="#FFFFFF",
            activebackground="#15803D",
            activeforeground="#FFFFFF",
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            command=self.start_processing_thread
        )
        self.btn_start.pack(side="left")

        btn_about = tk.Button(
            btn_row,
            text="ℹ About",
            font=("Segoe UI", 9),
            bg="#E2E8F0",
            relief="flat",
            padx=14,
            pady=6,
            command=self.show_about
        )
        btn_about.pack(side="right")

        # 5. Footer Bar
        footer = tk.Frame(self, bg="#E2E8F0", height=28)
        footer.pack(fill="x", side="bottom")

        dev_lbl = tk.Label(
            footer,
            text="Developer: Gulshan  |  Developer Gulshan",
            font=("Segoe UI", 8),
            bg="#E2E8F0",
            fg="#475569"
        )
        dev_lbl.pack(side="left", padx=15, pady=4)

        ver_lbl = tk.Label(
            footer,
            text="Version 1.0.0 (64-bit)",
            font=("Segoe UI", 8),
            bg="#E2E8F0",
            fg="#64748B"
        )
        ver_lbl.pack(side="right", padx=15, pady=4)

    # Model Verification Logic
    def check_model_status(self):
        if os.path.exists(MODEL_PATH) and os.path.getsize(MODEL_PATH) > 500 * 1024 * 1024:
            self.status_dot.configure(fg="#16A34A")  # Green
            self.status_lbl.configure(
                text="AI Engine Ready (bria-rmbg-2.0 Model Installed)",
                fg="#166534"
            )
            self.btn_download_model.pack_forget()
            return True
        else:
            self.status_dot.configure(fg="#DC2626")  # Red
            self.status_lbl.configure(
                text="AI Model Missing (~1.02 GB download required)",
                fg="#991B1B"
            )
            self.btn_download_model.pack(side="right")
            return False

    def start_model_download(self):
        if self.is_downloading:
            return
        self.is_downloading = True
        self.btn_download_model.configure(state="disabled")
        self.download_progress.pack(fill="x", pady=(8, 4))
        self.download_info_lbl.pack(anchor="w")

        threading.Thread(target=self._download_worker, daemon=True).start()

    def _download_worker(self):
        os.makedirs(MODEL_DIR, exist_ok=True)
        temp_file = MODEL_PATH + ".download"

        try:
            req = urllib.request.Request(
                MODEL_URL,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req) as resp, open(temp_file, "wb") as out_f:
                total_size = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                block_size = 1024 * 1024  # 1 MB chunk

                while True:
                    chunk = resp.read(block_size)
                    if not chunk:
                        break
                    out_f.write(chunk)
                    downloaded += len(chunk)

                    if total_size > 0:
                        pct = (downloaded / total_size) * 100
                        mb_down = downloaded / (1024 * 1024)
                        mb_tot = total_size / (1024 * 1024)
                        self.after(
                            0,
                            lambda p=pct, d=mb_down, t=mb_tot: self._update_download_ui(p, d, t)
                        )

            if os.path.exists(MODEL_PATH):
                os.remove(MODEL_PATH)
            os.rename(temp_file, MODEL_PATH)

            self.after(0, self._on_download_complete)
        except Exception as e:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            self.after(0, lambda err=str(e): self._on_download_failed(err))

    def _update_download_ui(self, pct, mb_down, mb_tot):
        self.download_progress["value"] = pct
        self.download_info_lbl.configure(
            text=f"Downloading AI Model: {mb_down:.1f} MB / {mb_tot:.1f} MB ({pct:.1f}%)"
        )

    def _on_download_complete(self):
        self.is_downloading = False
        self.download_progress.pack_forget()
        self.download_info_lbl.pack_forget()
        self.check_model_status()
        messagebox.showinfo("Download Complete", "AI Engine Model downloaded and installed successfully!")

    def _on_download_failed(self, error_msg):
        self.is_downloading = False
        self.btn_download_model.configure(state="normal")
        self.download_progress.pack_forget()
        self.download_info_lbl.configure(text=f"Download failed: {error_msg}", fg="#DC2626")
        messagebox.showerror("Download Error", f"Failed to download AI model:\n{error_msg}")

    # Folder Pickers
    def browse_input(self):
        folder = filedialog.askdirectory(title="Select Folder Containing Raw Photos")
        if folder:
            self.in_entry.delete(0, tk.END)
            self.in_entry.insert(0, folder)

    def browse_output(self):
        folder = filedialog.askdirectory(title="Select Destination Folder for Passport Photos")
        if folder:
            self.out_entry.delete(0, tk.END)
            self.out_entry.insert(0, folder)

    # Batch Photo Processing
    def start_processing_thread(self):
        if self.is_processing:
            return

        if not self.check_model_status():
            messagebox.showwarning(
                "Model Required",
                "Please download the AI Model first by clicking 'Download AI Model'."
            )
            return

        in_dir = self.in_entry.get().strip()
        out_dir = self.out_entry.get().strip()

        if not in_dir or not os.path.isdir(in_dir):
            messagebox.showerror("Invalid Folder", "Please select a valid Source Folder containing photos.")
            return

        if not out_dir:
            messagebox.showerror("Invalid Folder", "Please select a Destination Folder.")
            return

        os.makedirs(out_dir, exist_ok=True)

        valid_exts = (".jpg", ".jpeg", ".png", ".webp")
        files = [f for f in os.listdir(in_dir) if f.lower().endswith(valid_exts)]

        if not files:
            messagebox.showinfo("No Images Found", f"No valid images (.jpg, .png) found in:\n{in_dir}")
            return

        self.is_processing = True
        self.btn_start.configure(state="disabled", text="Processing...")
        self.proc_progress["value"] = 0
        self.proc_progress["maximum"] = len(files)

        threading.Thread(target=self._batch_worker, args=(in_dir, out_dir, files), daemon=True).start()

    def _batch_worker(self, in_dir, out_dir, files):
        global remove_bg
        if remove_bg is None:
            self.after(0, lambda: self.proc_status_lbl.configure(text="Loading AI Engine into memory..."))
            from rembg import remove as rem_func
            remove_bg = rem_func

        total = len(files)
        success_count = 0

        for idx, filename in enumerate(files, 1):
            in_file = os.path.join(in_dir, filename)
            out_name = os.path.splitext(filename)[0] + ".jpg"
            out_file = os.path.join(out_dir, out_name)

            self.after(
                0,
                lambda i=idx, t=total, fn=filename: self.proc_status_lbl.configure(
                    text=f"Processing ({i}/{t}): {fn}"
                )
            )

            try:
                with open(in_file, "rb") as f:
                    in_bytes = f.read()

                # 1. Background removal
                fg_bytes = remove_bg(in_bytes)
                fg_img = Image.open(io.BytesIO(fg_bytes)).convert("RGBA")

                bbox = fg_img.getbbox()
                if bbox:
                    bx0, by0, bx1, by1 = bbox
                    bw = bx1 - bx0
                    bh = by1 - by0
                    cx = (bx0 + bx1) / 2

                    # Frame head & upper chest
                    crop_h = bh * 1.15
                    crop_w = crop_h * TARGET_RATIO
                    if crop_w < bw * 1.2:
                        crop_w = bw * 1.2
                        crop_h = crop_w / TARGET_RATIO

                    crop_top = max(0, by0 - (bh * 0.12))
                    crop_bottom = min(fg_img.height, crop_top + crop_h)
                    crop_left = max(0, cx - (crop_w / 2))
                    crop_right = min(fg_img.width, crop_left + crop_w)

                    cropped_fg = fg_img.crop((crop_left, crop_top, crop_right, crop_bottom))
                else:
                    cropped_fg = fg_img

                # 2. Pure White Background (#FFFFFF)
                white_bg = Image.new("RGBA", cropped_fg.size, (255, 255, 255, 255))
                combined = Image.alpha_composite(white_bg, cropped_fg).convert("RGB")

                # 3. Fit to standard passport dimensions (413x531)
                final_img = ImageOps.fit(combined, (TARGET_W, TARGET_H), method=Image.Resampling.LANCZOS)
                final_img.save(out_file, "JPEG", quality=95)
                success_count += 1
            except Exception as ex:
                print(f"Error processing {filename}: {ex}")

            self.after(0, lambda v=idx: self._update_proc_progress(v))

        self.after(0, lambda s=success_count, t=total: self._on_processing_finished(s, t))

    def _update_proc_progress(self, val):
        self.proc_progress["value"] = val

    def _on_processing_finished(self, success, total):
        self.is_processing = False
        self.btn_start.configure(state="normal", text="▶  Start Processing Photos")
        self.proc_status_lbl.configure(text=f"Completed: Successfully processed {success}/{total} photos.")
        messagebox.showinfo(
            "Batch Complete",
            f"Processing Completed!\n\nSuccessfully generated {success} of {total} passport photos."
        )

    # About Modal
    def show_about(self):
        about_win = tk.Toplevel(self)
        about_win.title("About Gulshan AI Passport Studio")
        about_win.geometry("420x260")
        about_win.resizable(False, False)
        about_win.configure(bg="#FFFFFF")
        about_win.transient(self)
        about_win.grab_set()

        tk.Label(
            about_win,
            text="Gulshan AI Passport Studio",
            font=("Segoe UI", 13, "bold"),
            fg="#0F2942",
            bg="#FFFFFF"
        ).pack(pady=(20, 4))

        tk.Label(
            about_win,
            text="Version 1.0.0",
            font=("Segoe UI", 9),
            fg="#64748B",
            bg="#FFFFFF"
        ).pack()

        info_text = (
            "An automated desktop utility designed for Developer Gulshan\n"
            "to perform AI-powered background removal and standard\n"
            "Indian passport photo cropping (35mm x 45mm).\n\n"
            "AI Engine: bria-rmbg-2.0 (ONNX Runtime)\n"
            "Developer: Gulshan"
        )

        tk.Label(
            about_win,
            text=info_text,
            font=("Segoe UI", 9),
            fg="#334155",
            bg="#FFFFFF",
            justify="center"
        ).pack(pady=15)

        tk.Button(
            about_win,
            text="OK",
            font=("Segoe UI", 9, "bold"),
            bg="#0F2942",
            fg="#FFFFFF",
            relief="flat",
            padx=20,
            pady=3,
            command=about_win.destroy
        ).pack()


if __name__ == "__main__":
    app = PassportStudioApp()
    app.mainloop()