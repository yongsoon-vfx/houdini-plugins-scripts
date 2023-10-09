import toolutils , hou , os , time , subprocess , shutil , tempfile , webbrowser
from PySide2 import QtCore , QtWidgets , QtGui 
from tkinter import messagebox , Tk

#Global Variables

ct = time.strftime("%H%M%S",time.localtime())

hipdir = hou.text.expandString("$HIP")
#hipver = hou.text.expandString("$HIPVER")
hipfile = hou.text.expandString("$HIPFILE")
hipname = hou.hipFile.basename().rstrip('.hip')
    
outFile = 'Preview_' + hipname + '_' + ct + '.mp4'

#Create Working Directories if does not Exist
tempdir = tempfile.gettempdir() 
tempdir = tempdir + "/flipbook/"
#print(tempdir)
outdir = hipdir + "/flipbooks"
backupdir = outdir + '/snapshot/'
if not os.path.exists(tempdir):
    os.mkdir(tempdir)
if not os.path.exists(outdir):
    os.mkdir(outdir)
if not os.path.exists(backupdir):
    os.mkdir(backupdir)

#Initialize Current Scene Settings
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
#print(frameFps)

checkDep = subprocess.run("ffmpeg -h" , shell = True )
if checkDep.returncode != 0:
    depText = 'FFMPEG IS NOT INSTALLED. https://ffmpeg.org/download.html'
else:
    depText = 'Ffmpeg found'

root = Tk()
root.withdraw()



class Flipbook(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.setObjectName("Form")
        self.setFixedSize(685, 250)
        self.frame = QtWidgets.QFrame(self)
        self.frame.setGeometry(QtCore.QRect(10, 30, 300, 201))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.frame.setFont(font)
        self.frame.setStyleSheet("")
        self.frame.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label_frange = QtWidgets.QLabel(self.frame)
        self.label_frange.setGeometry(QtCore.QRect(20, 10, 120, 16))
        self.label_frange.setObjectName("label_frange")
        self.input_frange = QtWidgets.QLineEdit(self.frame)
        self.input_frange.setGeometry(QtCore.QRect(20, 30, 121, 20))
        self.input_frange.setFocusPolicy(QtCore.Qt.TabFocus)
        self.input_frange.setObjectName("input_frange")
        self.input_fps = QtWidgets.QSpinBox(self.frame)
        self.input_fps.setGeometry(QtCore.QRect(150, 30, 42, 22))
        self.input_fps.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
        self.input_fps.setProperty("value", 25)
        self.input_fps.setObjectName("input_fps")
        self.label_fps = QtWidgets.QLabel(self.frame)
        self.label_fps.setGeometry(QtCore.QRect(150, 10, 31, 20))
        self.label_fps.setObjectName("label_fps")
        self.input_reswidth = QtWidgets.QLineEdit(self.frame)
        self.input_reswidth.setGeometry(QtCore.QRect(20, 80, 91, 20))
        self.input_reswidth.setObjectName("input_reswidth")
        self.input_resheight = QtWidgets.QLineEdit(self.frame)
        self.input_resheight.setGeometry(QtCore.QRect(120, 80, 101, 20))
        self.input_resheight.setObjectName("input_resheight")
        self.label_resolution = QtWidgets.QLabel(self.frame)
        self.label_resolution.setGeometry(QtCore.QRect(20, 60, 101, 16))
        self.label_resolution.setObjectName("label_resolution")
        self.input_fstep = QtWidgets.QLineEdit(self.frame)
        self.input_fstep.setGeometry(QtCore.QRect(200, 30, 21, 20))
        self.input_fstep.setAlignment(QtCore.Qt.AlignCenter)
        self.input_fstep.setObjectName("input_fstep")
        self.label_fstep = QtWidgets.QLabel(self.frame)
        self.label_fstep.setGeometry(QtCore.QRect(120, 10, 101, 16))
        self.label_fstep.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_fstep.setObjectName("label_fstep")
        self.check_mp4 = QtWidgets.QCheckBox(self.frame)
        self.check_mp4.setGeometry(QtCore.QRect(20, 110, 91, 18))
        self.check_mp4.setChecked(True)
        self.check_mp4.setObjectName("check_mp4")
        self.check_deltemp = QtWidgets.QCheckBox(self.frame)
        self.check_deltemp.setGeometry(QtCore.QRect(20, 130, 121, 18))
        self.check_deltemp.setChecked(True)
        self.check_deltemp.setObjectName("check_deltemp")
        self.check_backup = QtWidgets.QCheckBox(self.frame)
        self.check_backup.setGeometry(QtCore.QRect(20, 150, 121, 18))
        self.check_backup.setChecked(True)
        self.check_backup.setObjectName("check_backup")
        self.label_settings = QtWidgets.QLabel(self)
        self.label_settings.setGeometry(QtCore.QRect(10, 10, 100, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_settings.setFont(font)
        self.label_settings.setObjectName("label_settings")
        self.frame_2 = QtWidgets.QFrame(self)
        self.frame_2.setGeometry(QtCore.QRect(325, 30, 350, 201))
        self.frame_2.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.dlabel_out_file = QtWidgets.QLabel(self.frame_2)
        self.dlabel_out_file.setGeometry(QtCore.QRect(10, 35, 350, 21))
        self.dlabel_out_file.setObjectName("dlabel_out_file")
        self.label_out = QtWidgets.QLabel(self.frame_2)
        self.label_out.setGeometry(QtCore.QRect(10, 15, 100, 20))
        self.label_out.setObjectName("label_out")
        self.dlabel_res_frames = QtWidgets.QLabel(self.frame_2)
        self.dlabel_res_frames.setGeometry(QtCore.QRect(10, 70, 200, 16))
        self.dlabel_res_frames.setObjectName("dlabel_res_frames")
        self.dlabel_ffmpeg = QtWidgets.QLabel(self.frame_2)
        self.dlabel_ffmpeg.setGeometry(QtCore.QRect(10, 85, 350, 90))
        self.dlabel_ffmpeg.setObjectName("dlabel_ffmpeg")
        self.dlabel_ffmpeg.setWordWrap(True)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.frame_2)
        self.buttonBox.setGeometry(QtCore.QRect(10, 170, 161, 23))
        self.buttonBox.setFocusPolicy(QtCore.Qt.TabFocus)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label_output = QtWidgets.QLabel(self)
        self.label_output.setGeometry(QtCore.QRect(325, 10, 61, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_output.setFont(font)
        self.label_output.setObjectName("label_output")
        self.frame_2.raise_()
        self.frame.raise_()
        self.label_settings.raise_()
        self.label_output.raise_()




        #SIGNALS
        self.retranslateUi(self)
        self.buttonBox.rejected.connect(self.close)
        self.buttonBox.accepted.connect(self.runFlipbook)
        self.input_resheight.textChanged.connect(self.updateRes)
        self.input_reswidth.textChanged.connect(self.updateRes)
        
        
         # type: ignore
        QtCore.QMetaObject.connectSlotsByName(self)
        self.setTabOrder(self.input_frange, self.input_fps)
        self.setTabOrder(self.input_fps, self.input_fstep)
        self.setTabOrder(self.input_fstep, self.input_reswidth)
        self.setTabOrder(self.input_reswidth, self.input_resheight)
        self.setTabOrder(self.input_resheight, self.check_mp4)
        self.setTabOrder(self.check_mp4, self.check_deltemp)
        self.setTabOrder(self.check_deltemp, self.check_backup)

    def flip(self):
        print('runnin')

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "Generate Flipbook"))
        self.label_frange.setText(_translate("Form", "Frame Range"))
        self.input_frange.setText(_translate("Form", frameStart + '-' + frameEnd ))
        self.label_fps.setText(_translate("Form", "FPS"))
        self.input_reswidth.setText(_translate("Form", resWidth))
        self.input_resheight.setText(_translate("Form", resHeight))
        self.label_resolution.setText(_translate("Form", "Resolution"))
        self.input_fstep.setText(_translate("Form", "1"))
        self.label_fstep.setText(_translate("Form", "Step"))
        self.check_mp4.setText(_translate("Form", "MP4"))
        self.check_deltemp.setText(_translate("Form", "Delete Temp Files"))
        self.check_backup.setText(_translate("Form", "Create Backup HIP"))
        self.label_settings.setText(_translate("Form", "Settings"))
        self.dlabel_out_file.setText(_translate("Form", outFile))
        self.label_out.setText(_translate("Form", "File Name:"))
        self.dlabel_res_frames.setText(_translate("Form", resWidth + 'x' + resHeight + '@' + frameFps + 'fps'))
        self.dlabel_ffmpeg.setText(_translate("Form", depText))
        self.label_output.setText(_translate("Form", "Output"))


    def updateRes(self):
        resWidth = int(self.input_reswidth.text())
        resHeight = int(self.input_resheight.text())
        self.dlabel_res_frames.setText(str(resWidth) + 'x' + str(resHeight) + '@' + str(frameFps) + 'fps')

    def runFlipbook(self):
        #check dependencies
        if checkDep.returncode != 0:
            messagebox.showerror('FFMPEG Not Installed','Open Link in Browser')
            webbrowser.open('https://ffmpeg.org/download.html')
            return
        #save
        hou.hipFile.save()


        #initialize settings
        scene = toolutils.sceneViewer()
        settings = scene.flipbookSettings()
        settings.output(tempdir + 'flipbook_$F.jpg')

        #override-properties-from-inputs
        outframeRange = tuple(map(int ,str(self.input_frange.text()).split("-")))
        print(outframeRange)
        settings.frameRange(outframeRange)

        outresHeight = int(self.input_resheight.text())
        outresWidth = int(self.input_reswidth.text())
        outresolution = (outresWidth , outresHeight)

        settings.resolution(outresolution)




        scene.flipbook(None, settings)
        print('flipbookdone')
        self.runFfmpeg()
        self.cleanUp()
        self.copySnapshot()
        self.close()

    def runFfmpeg(self):
        ffmpegcom = 'ffmpeg -r 25 -i "flipbook_%0d.jpg" flipbookout.mp4'
        os.chdir(tempdir)
        subprocess.run(ffmpegcom)
        out = os.path.abspath(shutil.move(tempdir + 'flipbookout.mp4' , outdir + "/" + outFile))
        print('ffmpeg-encode-done')
        os.startfile(out)
    
    def cleanUp(self):
        os.chdir(hipdir)
        shutil.rmtree(tempdir)
        print('cleanupcomplete')
    
    def copySnapshot(self):
        shutil.copy(hipfile , backupdir + ct +'.hip')
        print('snapshotcreated')
    
dialog = Flipbook()
dialog.show()





#runFlipbook()