import toolutils, hou, os, time, subprocess, shutil, tempfile, webbrowser, logging, concurrent.futures
from PySide2 import QtCore, QtWidgets, QtGui
from tkinter import messagebox, Tk
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

start_time = time.time()
coreCount = os.cpu_count()


ct = time.strftime("%H%M%S", time.localtime())

hipdir = hou.text.expandString("$HIP")
# hipver = hou.text.expandString("$HIPVER")
hipfile = hou.text.expandString("$HIPFILE")
hipname = hou.hipFile.basename().rstrip(".hip")

outFile = "Preview_" + hipname + "_" + ct + ".mp4"


# Create Working Directories if does not Exist
tempdir = tempfile.gettempdir()
tempdir = tempdir + "/flipbook/"
print(tempdir)
outdir = hipdir + "/flipbooks"
backupdir = outdir + "/snapshot/"
if not os.path.exists(tempdir):
    os.mkdir(tempdir)
if not os.path.exists(outdir):
    os.mkdir(outdir)
if not os.path.exists(backupdir):
    os.mkdir(backupdir)

# Initialize Current Scene Settings
scene = toolutils.sceneViewer()
settings = scene.flipbookSettings()
frameRange = settings.frameRange()
frameIncrement = settings.frameIncrement()
frameResolution = settings.resolution()

frameStart = str(int(frameRange[0]))
frameEnd = str(int(frameRange[1]))

resWidth = str(int(frameResolution[0]))
resHeight = str(int(frameResolution[1]))

frameFps = str(int(hou.fps()))
# print(frameFps)

checkDep = subprocess.run("ffmpeg -h", shell=True)
if checkDep.returncode != 0:
    depText = "FFMPEG IS NOT INSTALLED. \nhttps://ffmpeg.org/download.html"
else:
    depText = "Ffmpeg found"

root = Tk()
root.withdraw()


class Flipbook(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.setObjectName("Form")
        self.setFixedSize(930, 420)

        font = QtGui.QFont()
        font.setPointSize(10)

        self.tab_Main = QtWidgets.QTabWidget(self)
        self.tab_Main.setGeometry(QtCore.QRect(10, 10, 500, 400))
        self.tab_Main.setTabPosition(QtWidgets.QTabWidget.North)
        self.tab_Main.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tab_Main.setDocumentMode(False)
        self.tab_Main.setObjectName("tab_Main")
        self.tab_Main.setFont(font)

        layout = QtWidgets.QVBoxLayout()

        # --------Settings Tab--------
        self.tab_settings = QtWidgets.QWidget()
        self.tab_settings.setObjectName("tab_settings")
        self.label_frange = QtWidgets.QLabel(self.tab_settings)
        self.label_frange.setGeometry(QtCore.QRect(10, 15, 150, 16))
        self.label_frange.setObjectName("label_frange")
        self.input_frange = QtWidgets.QLineEdit(self.tab_settings)
        self.input_frange.setGeometry(QtCore.QRect(10, 35, 150, 30))
        self.input_frange.setObjectName("input_frange")

        self.label_fps = QtWidgets.QLabel(self.tab_settings)
        self.label_fps.setGeometry(QtCore.QRect(140, 15, 31, 20))
        self.label_fps.setObjectName("label_fps")
        self.input_fps = QtWidgets.QSpinBox(self.tab_settings)
        self.input_fps.setGeometry(QtCore.QRect(165, 35, 42, 30))
        self.input_fps.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
        self.input_fps.setProperty("value", 25)
        self.input_fps.setObjectName("input_fps")

        self.label_fstep = QtWidgets.QLabel(self.tab_settings)
        self.label_fstep.setGeometry(QtCore.QRect(190, 15, 41, 20))
        self.label_fstep.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )
        self.label_fstep.setObjectName("label_fstep")
        self.input_fstep = QtWidgets.QLineEdit(self.tab_settings)
        self.input_fstep.setGeometry(QtCore.QRect(210, 35, 30, 30))
        self.input_fstep.setAlignment(QtCore.Qt.AlignCenter)
        self.input_fstep.setObjectName("input_fstep")

        self.label_resolution = QtWidgets.QLabel(self.tab_settings)
        self.label_resolution.setGeometry(QtCore.QRect(10, 75, 101, 16))
        self.label_resolution.setObjectName("label_resolution")
        self.input_reswidth = QtWidgets.QLineEdit(self.tab_settings)
        self.input_reswidth.setGeometry(QtCore.QRect(10, 95, 91, 30))
        self.input_reswidth.setObjectName("input_reswidth")
        self.input_resheight = QtWidgets.QLineEdit(self.tab_settings)
        self.input_resheight.setGeometry(QtCore.QRect(110, 95, 101, 30))
        self.input_resheight.setObjectName("input_resheight")

        self.check_mp4 = QtWidgets.QCheckBox(self.tab_settings)
        self.check_mp4.setGeometry(QtCore.QRect(20, 150, 250, 30))
        self.check_mp4.setChecked(True)
        self.check_mp4.setObjectName("check_mp4")
        self.check_deltemp = QtWidgets.QCheckBox(self.tab_settings)
        self.check_deltemp.setGeometry(QtCore.QRect(20, 180, 250, 30))
        self.check_deltemp.setChecked(True)
        self.check_deltemp.setObjectName("check_deltemp")
        self.check_backup = QtWidgets.QCheckBox(self.tab_settings)
        self.check_backup.setGeometry(QtCore.QRect(20, 210, 250, 30))
        self.check_backup.setChecked(True)
        self.check_backup.setObjectName("check_backup")

        self.tab_Main.addTab(self.tab_settings, "")

        # --------Advanced Tab--------
        self.tab_advanced = QtWidgets.QWidget()
        self.tab_advanced.setObjectName("tab_advanced")
        self.input_threads = QtWidgets.QSpinBox(self.tab_advanced)
        self.input_threads.setGeometry(QtCore.QRect(10, 230, 42, 30))
        self.input_threads.setMinimum(1)
        self.input_threads.setMaximum(32)
        self.input_threads.setProperty("value", coreCount - 4)
        self.input_threads.setObjectName("input_threads")
        self.label_threads = QtWidgets.QLabel(self.tab_advanced)
        self.label_threads.setGeometry(QtCore.QRect(10, 200, 91, 30))
        self.label_threads.setObjectName("label_threads")

        self.input_watermark = QtWidgets.QLineEdit(self.tab_advanced)
        self.input_watermark.setGeometry(QtCore.QRect(10, 90, 185, 30))
        self.input_watermark.setObjectName("input_watermark")
        self.label_watermark = QtWidgets.QLabel(self.tab_advanced)
        self.label_watermark.setGeometry(QtCore.QRect(10, 70, 250, 16))
        self.label_watermark.setOpenExternalLinks(False)
        self.label_watermark.setObjectName("label_watermark")
        self.cb_enable_watermark = QtWidgets.QCheckBox(self.tab_advanced)
        self.cb_enable_watermark.setGeometry(QtCore.QRect(200, 90, 150, 30))
        self.cb_enable_watermark.setChecked(True)
        self.cb_enable_watermark.setObjectName("cb_enable_watermark")

        self.cb_enable_title = QtWidgets.QCheckBox(self.tab_advanced)
        self.cb_enable_title.setGeometry(QtCore.QRect(200, 30, 150, 30))
        self.cb_enable_title.setChecked(True)
        self.cb_enable_title.setObjectName("cb_enable_title")
        self.label_title_overlay = QtWidgets.QLabel(self.tab_advanced)
        self.label_title_overlay.setGeometry(QtCore.QRect(10, 10, 251, 16))
        self.label_title_overlay.setOpenExternalLinks(False)
        self.label_title_overlay.setObjectName("label_title_overlay")
        self.input_titleoverlay = QtWidgets.QLineEdit(self.tab_advanced)
        self.input_titleoverlay.setGeometry(QtCore.QRect(10, 30, 185, 30))
        self.input_titleoverlay.setObjectName("input_titleoverlay")

        self.input_select_font = QtWidgets.QFontComboBox(self.tab_advanced)
        self.input_select_font.setGeometry(QtCore.QRect(10, 150, 185, 30))
        self.input_select_font.setObjectName("input_select_font")
        self.label_font = QtWidgets.QLabel(self.tab_advanced)
        self.label_font.setGeometry(QtCore.QRect(10, 130, 71, 16))
        self.label_font.setOpenExternalLinks(False)
        self.label_font.setObjectName("label_font")

        self.cb_frame_overlay = QtWidgets.QCheckBox(self.tab_advanced)
        self.cb_frame_overlay.setGeometry(QtCore.QRect(300, 30, 250, 30))
        self.cb_frame_overlay.setChecked(True)
        self.cb_frame_overlay.setTristate(False)
        self.cb_frame_overlay.setObjectName("cb_frame_overlay")
        self.cb_placeholder1 = QtWidgets.QCheckBox(self.tab_advanced)
        self.cb_placeholder1.setGeometry(QtCore.QRect(300, 60, 250, 30))
        self.cb_placeholder1.setChecked(False)
        self.cb_placeholder1.setTristate(False)
        self.cb_placeholder1.setObjectName("cb_placeholder1")
        self.cb_placeholder2 = QtWidgets.QCheckBox(self.tab_advanced)
        self.cb_placeholder2.setGeometry(QtCore.QRect(300, 90, 250, 30))
        self.cb_placeholder2.setChecked(False)
        self.cb_placeholder2.setTristate(False)
        self.cb_placeholder2.setObjectName("cb_placeholder2")
        self.tab_Main.addTab(self.tab_advanced, "")

        # ---------Wedging Tab--------
        self.tab_wedge = QtWidgets.QWidget()
        self.tab_wedge.setObjectName("tab_wedge")
        self.input_node = QtWidgets.QLineEdit(self.tab_wedge)
        self.input_node.setGeometry(QtCore.QRect(10, 40, 250, 30))
        self.input_node.setObjectName("input_node")
        self.label_top_out = QtWidgets.QLabel(self.tab_wedge)
        self.label_top_out.setGeometry(QtCore.QRect(10, 10, 150, 30))
        self.label_top_out.setObjectName("label_top_out")
        self.btn_select_top_out = QtWidgets.QPushButton(self.tab_wedge)
        self.btn_select_top_out.setGeometry(QtCore.QRect(265, 40, 30, 30))
        self.btn_select_top_out.setObjectName("btn_select_top_out")
        self.tab_Main.addTab(self.tab_wedge, "")
        dFont = QtGui.QFont()
        dFont.setPointSize(9)
        dFont.setItalic(True)
        self.label_wedgeDesc = QtWidgets.QLabel(self.tab_wedge)
        self.label_wedgeDesc.setFont(dFont)
        self.label_wedgeDesc.setGeometry(QtCore.QRect(10, 55, 350, 60))
        self.label_wedgeDesc.setObjectName("label_wedgeDesc")

        # --------Output Box
        self.box_Output = QtWidgets.QGroupBox(self)
        self.box_Output.setGeometry(QtCore.QRect(520, 10, 400, 400))
        self.box_Output.setFont(font)
        self.box_Output.setFlat(False)
        self.box_Output.setObjectName("box_Output")
        self.label_out = QtWidgets.QLabel(self.box_Output)
        self.label_out.setGeometry(QtCore.QRect(20, 40, 200, 50))
        self.label_out.setObjectName("label_out")
        self.dlabel_out_file = QtWidgets.QLabel(self.box_Output)
        self.dlabel_out_file.setGeometry(QtCore.QRect(20, 60, 400, 50))
        self.dlabel_out_file.setObjectName("dlabel_out_file")
        self.dlabel_res_frames = QtWidgets.QLabel(self.box_Output)
        self.dlabel_res_frames.setGeometry(QtCore.QRect(20, 80, 250, 50))
        self.dlabel_res_frames.setObjectName("dlabel_res_frames")
        self.label_dep = QtWidgets.QLabel(self.box_Output)
        self.label_dep.setGeometry(QtCore.QRect(10, 170, 250, 50))
        self.label_dep.setObjectName("label_dep")
        self.dlabel_ffmpeg = QtWidgets.QLabel(self.box_Output)
        self.dlabel_ffmpeg.setGeometry(QtCore.QRect(10, 200, 250, 60))
        self.dlabel_ffmpeg.setObjectName("dlabel_ffmpeg")
        self.buttonBox = QtWidgets.QDialogButtonBox(self.box_Output)
        self.buttonBox.setGeometry(QtCore.QRect(0, 340, 250, 50))
        self.buttonBox.setFocusPolicy(QtCore.Qt.TabFocus)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.buttonBox.setObjectName("buttonBox")

        self.retranslateUi(self)
        self.tab_Main.setCurrentIndex(0)

        # Signals
        self.buttonBox.rejected.connect(self.close)
        self.buttonBox.accepted.connect(self.runFlipbook)
        self.input_resheight.textChanged.connect(self.updateRes)
        self.input_reswidth.textChanged.connect(self.updateRes)
        self.btn_select_top_out.clicked.connect(self.wedgeSelect)

        # type: ignore
        QtCore.QMetaObject.connectSlotsByName(self)
        self.setTabOrder(self.input_frange, self.input_fps)
        self.setTabOrder(self.input_fps, self.input_fstep)
        self.setTabOrder(self.input_fstep, self.input_reswidth)
        self.setTabOrder(self.input_reswidth, self.input_resheight)
        self.setTabOrder(self.input_resheight, self.check_mp4)
        self.setTabOrder(self.check_mp4, self.check_deltemp)
        self.setTabOrder(self.check_deltemp, self.check_backup)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate

        # Static Labels
        self.setWindowTitle(_translate("Form", "Generate Flipbook"))
        self.label_frange.setText(_translate("Form", "Frame Range"))
        self.label_fstep.setText(_translate("Form", "Step"))
        self.label_fps.setText(_translate("Form", "FPS"))
        self.label_resolution.setText(_translate("Form", "Resolution"))
        self.label_title_overlay.setText(_translate("Form", "Title Overlay"))
        self.label_font.setText(_translate("Form", "Font"))
        self.label_top_out.setText(_translate("Form", "Output TOP Node"))
        self.label_out.setText(_translate("Form", "File Name:"))
        self.label_dep.setText(_translate("Form", "Dependencies"))
        self.label_threads.setText(_translate("Form", "Threads"))
        self.label_watermark.setText(_translate("Form", "Watermark Overlay"))
        self.label_wedgeDesc.setText(
            _translate("Form", "Select the Output TOP Node, then click the button")
        )

        # Dynamic Labels
        self.dlabel_out_file.setText(_translate("Form", outFile))
        self.dlabel_res_frames.setText(
            _translate("Form", resWidth + "x" + resHeight + "@" + frameFps + "fps")
        )
        self.dlabel_ffmpeg.setText(_translate("Form", depText))
        # Input Boxes
        self.input_fstep.setText(_translate("Form", "1"))
        self.input_reswidth.setText(_translate("Form", resWidth))
        self.input_resheight.setText(_translate("Form", resHeight))
        self.input_frange.setText(_translate("Form", frameStart + "-" + frameEnd))
        self.input_watermark.setText(_translate("Form", "Heckler SG"))
        self.input_titleoverlay.setText(_translate("Form", "hipfile"))
        # Checkboxes
        self.check_deltemp.setText(_translate("Form", "Delete Temp Files"))
        self.check_backup.setText(_translate("Form", "Create Backup HIP"))
        self.cb_frame_overlay.setText(_translate("Form", "Frame Num"))
        self.cb_placeholder1.setText(_translate("Form", "Placeholder1"))
        self.cb_placeholder2.setText(_translate("Form", "Placeholder2"))
        self.cb_enable_watermark.setText(_translate("Form", ""))
        self.cb_enable_title.setText(_translate("Form", ""))
        self.check_mp4.setText(_translate("Form", "MP4"))

        self.btn_select_top_out.setText(_translate("Form", "..."))
        self.tab_Main.setTabText(
            self.tab_Main.indexOf(self.tab_settings), _translate("Form", "Settings")
        )
        self.tab_Main.setTabText(
            self.tab_Main.indexOf(self.tab_advanced), _translate("Form", "Advanced")
        )
        self.tab_Main.setTabText(
            self.tab_Main.indexOf(self.tab_wedge), _translate("Form", "Wedging")
        )
        self.box_Output.setTitle(_translate("Form", "Output"))

    def wedgeSelect(self):
        wedgePath = hou.ui.selectNode(multiple_select=False, title="Lowest Wedge Node")
        self.input_node.setText(wedgePath)
        self.activateWindow()
        wedgeNode = hou.node(wedgePath)

    def updateRes(self):
        resWidth = int(self.input_reswidth.text())
        resHeight = int(self.input_resheight.text())
        self.dlabel_res_frames.setText(
            str(resWidth) + "x" + str(resHeight) + "@" + str(frameFps) + "fps"
        )

    def runFlipbook(self):
        # check dependencies
        if checkDep.returncode != 0:
            if (
                hou.ui.displayMessage(
                    "FFMpeg is not installed.\nOpen Link in Browser?",
                    buttons=(
                        "Open",
                        "Cancel",
                    ),
                )
                == 0
            ):
                webbrowser.open("https://ffmpeg.org/download.html")
            return
        # save
        hou.hipFile.save()

        # initialize settings
        settings.output(tempdir + "flipbook_$F.jpg")

        # override-properties-from-inputs
        outframeRange = tuple(map(int, str(self.input_frange.text()).split("-")))
        print(outframeRange)
        settings.frameRange(outframeRange)

        outresHeight = int(self.input_resheight.text())
        outresWidth = int(self.input_reswidth.text())
        outresolution = (outresWidth, outresHeight)

        settings.resolution(outresolution)

        scene.flipbook(None, settings)
        print("flipbookdone")
        self.executeProcess()
        self.runFfmpeg()
        self.cleanUp()
        self.copySnapshot()
        self.close()

    @staticmethod
    def runFfmpeg():
        ffmpegcom = 'ffmpeg -r 25 -i "flipbook_%0d.jpg" -vcodec libx264 flipbookout.mp4'
        os.chdir(tempdir)
        subprocess.run(ffmpegcom)
        out = os.path.abspath(
            shutil.move(tempdir + "flipbookout.mp4", outdir + "/" + outFile)
        )
        print("ffmpeg-encode-done")
        os.startfile(out)

    @staticmethod
    def cleanUp():
        os.chdir(hipdir)
        shutil.rmtree(tempdir)
        print("cleanupcomplete")

    @staticmethod
    def copySnapshot():
        shutil.copy(hipfile, backupdir + ct + ".hip")
        print("snapshotcreated")

    def executeProcess(self):
        images = Path(tempdir).glob("*.jpg")
        format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.input_threads.value()
        ) as executor:
            executor.map(self.processImg, images)
        print("--- %s seconds ---" % (time.time() - start_time))

    @staticmethod
    def processImg(cimage):
        with Image.open(cimage).convert("RGBA") as base:
            cFrame = str(Path(cimage).name).lstrip("flipbook_").rstrip(".jpg")
            txt = Image.new("RGBA", base.size, (255, 255, 255, 0))
            d = ImageDraw.Draw(txt)
            height = base.size[1]
            fntTitle = ImageFont.truetype("C:\WINDOWS\FONTS\Verdana.TTF", 15)
            fntWatermark = ImageFont.truetype("C:\WINDOWS\FONTS\Verdana.TTF", 40)
            d.text(
                (10, height - 50),
                "Heckler SG",
                fill=(255, 255, 255, 128),
                font=fntWatermark,
            )
            d.text(
                (10, 10), outFile + "_" + ct, fill=(255, 255, 255, 128), font=fntTitle
            )
            d.text(
                (base.size[0] - 50, 10),
                cFrame,
                fill=(255, 255, 255, 128),
                font=fntTitle,
            )
            # txt.show()
            out = Image.alpha_composite(base, txt)
            out = out.convert("RGB")
            out.save(cimage)
        print("--- %s seconds ---" % (time.time() - start_time))


dialog = Flipbook()
dialog.show()
