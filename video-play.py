import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox,
    QSlider,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QStyle,
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaDevices, QAudio
from PyQt6.QtCore import QUrl, Qt, QSettings, QPoint, QSize, QTimer
from PyQt6.QtGui import QMouseEvent


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("Farhad", "VideoPlayer")
        self.initUI()
        self.setWindowTitle("Video Player")
        self.setWindowIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        )
        self.firstTimeLoad = True  # todo: Привью загрузки файла

        # todo: Счетчик времени
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(1000)

    def initUI(self):
        # todo: Основное окно
        mainLayout = QVBoxLayout()

        # todo: Верхний  окно для видео
        topLayout = QHBoxLayout()
        self.video_widget = QVideoWidget()
        topLayout.setObjectName("videoWidget")
        topLayout.addWidget(self.video_widget)

        # todo: Подключения видео окна
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.video_widget)

        # todo: Подключения звука
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        # todo: Подключение видео привью
        self.player.mediaStatusChanged.connect(self.handleMediaStatusChanged)

        # todo: Кнопка открытия файла
        self.open_button = QPushButton()
        self.open_button.clicked.connect(self.open_video)
        self.open_button.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        self.open_button.setToolTip("Открыть файл")
        self.open_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DirHomeIcon)
        )
        self.open_button.setIconSize(QtCore.QSize(24, 24))

        # todo: Кнопка запуска видео
        self.play_button = QPushButton(self)
        self.play_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        )
        self.play_button.clicked.connect(self.play_pause)
        self.play_button.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        self.play_button.setToolTip("Пуск - Пауза")
        self.play_button.setIconSize(QtCore.QSize(24, 24))

        # todo: Кнопка стоп видео
        self.stop_button = QPushButton()
        self.stop_button.clicked.connect(self.stop_video)
        self.stop_button.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        self.stop_button.setToolTip("Стоп")
        self.stop_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop)
        )
        self.stop_button.setIconSize(QtCore.QSize(24, 24))
        self.stop_button.setObjectName("Stop")

        # todo: Кнопка выбор аудио выхода видео
        self.change_output_button = QPushButton()
        self.change_output_button.clicked.connect(self.change_audio_output)
        self.change_output_button.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        self.change_output_button.setToolTip("Выбор аудио выхода")
        self.change_output_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        )
        self.change_output_button.setIconSize(QtCore.QSize(24, 24))
        self.change_output_button.setObjectName("Seek_choice")

        # todo: Иконка звуковой дорожки
        self.muteButton = QPushButton(self)
        self.muteButton.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume)
        )
        self.muteButton.clicked.connect(self.toggleMute)
        self.muteButton.setFixedSize(25, 25)
        self.muteButton.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )

        # todo: Слайдер перемотки
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.player.durationChanged.connect(
            self.start_slider
        )  # Начальная точка ползунка
        self.slider.sliderMoved.connect(
            self.drag_and_drop_slider
        )  # Перетаскивание ползунка
        self.player.positionChanged.connect(self.traffic_slider)  # Движение ползунка
        self.slider.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))

        # todo: Добавление слайдера
        vbox = QHBoxLayout()
        vbox.addWidget(self.slider)
        # todo: Добавления счетчика времени
        self.timeLabel = QPushButton("0:00/0:00")
        vbox.addWidget(self.timeLabel)
        self.timeLabel.setStyleSheet("font-size: 15px; color:#000;")

        # todo: Звуковой слайдер
        self.volumeSlider = QSlider(Qt.Orientation.Horizontal, self)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setValue(100)
        self.volumeSlider.setMaximumWidth(100)
        self.volumeSlider.valueChanged.connect(self.changeVolume)
        self.volumeSlider.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )

        # todo: Полнорежимный экран
        self.fullScreenButton = QPushButton(self)
        self.fullScreenButton.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton)
        )
        self.fullScreenButton.setToolTip("Полноэкранный Режим")
        self.fullScreenButton.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        self.fullScreenButton.setFixedSize(25, 25)
        self.fullScreenButton.setStyleSheet("color:red;")
        self.fullScreenButton.clicked.connect(self.toggleFullScreen)

        # todo: Установка видеовиджета в плеер
        bottomLayout = QHBoxLayout()
        bottomLayout.addWidget(self.open_button)
        bottomLayout.addWidget(self.play_button)
        bottomLayout.addWidget(self.stop_button)
        bottomLayout.addWidget(self.change_output_button)
        bottomLayout.addWidget(self.muteButton)
        bottomLayout.addWidget(self.volumeSlider)
        bottomLayout.addWidget(self.fullScreenButton)

        # todo: Добавляем вложенные макеты в основной макет
        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(vbox)
        mainLayout.addLayout(bottomLayout)

        # todo: Установка основного макета для виджета
        self.setLayout(mainLayout)

        # todo: Загрузка настроек
        self.loadSettings()

    # todo: Функция Добавление свои настроек для окна
    def loadSettings(self):
        self.resize(self.settings.value("size", QSize(778, 541)))
        self.move(self.settings.value("pos", QPoint(160, 60)))

    # todo: Открытие видефайла
    def open_video(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open Video", "", "Video Files (*.mp4 *.avi *.mkv)"
        )
        if filepath:
            self.player.setSource(QUrl.fromLocalFile(filepath))

    # todo: Функция при клике на окно Выбор Файла и Пуск - Пауза
    def play_pause(self):
        if (
            not self.player.source().isValid()
        ):  # Проверка, установлен ли допустимый источник видео.
            msg_box = QMessageBox(self)  # Если не выбран файл выводит сообщение
            msg_box.setWindowTitle("Нет видео")
            msg_box.setText("Видео не выбрано. Сначала выберите видео.")
            msg_box.setIcon(QMessageBox.Icon.Warning)
            upload_button = msg_box.addButton(
                "Загрузить", QMessageBox.ButtonRole.YesRole
            )
            msg_box.setStyleSheet("color:#333; padding: 10px; font-size:15px")
            msg_box.addButton("Отмена", QMessageBox.ButtonRole.NoRole)
            msg_box.exec()  # Отмена
            if msg_box.clickedButton() == upload_button:
                self.open_video()
            return

        if self.player.isPlaying():  # Свойство IsPlaying проверяется, чтобы определить,
            # вызывается ли метод Play или Stop для переключения воспроизведения.
            self.player.pause()
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            )
        else:
            self.player.play()
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
            )

    def stop_video(self):
        self.player.stop()

    # todo: Функция паузы при клике на окно
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.video_widget.geometry().contains(event.position().toPoint()):
                self.play_pause()

    # todo: Функция Счетчика времени и продолжительности
    def updateTime(self):
        currentTime = self.player.position() // 1000
        totalTime = self.player.duration() // 1000
        self.timeLabel.setText(
            f"{currentTime // 60}:{currentTime % 60:02}/{totalTime // 60}:{totalTime % 60:02}"
        )

    # todo: Функция выбора аудивыхода
    def change_audio_output(self):
        audio_outputs = QMediaDevices.audioOutputs()
        audio_output_names = [output.description() for output in audio_outputs]
        dialog = QMessageBox()
        dialog.setWindowTitle("Выберите аудио выход")
        dialog.setText("Выберите устройство вывода звука:")
        for name in audio_output_names:
            dialog.addButton(name, QMessageBox.ButtonRole.YesRole)
        dialog.exec()
        selected_button = dialog.clickedButton()
        if selected_button:
            selected_index = audio_output_names.index(selected_button.text())
            selected_device = audio_outputs[selected_index]
            self.audio_output = QAudioOutput(selected_device)
            self.player.setAudioOutput(self.audio_output)

    # todo: Начальная точка ползунка
    def start_slider(self, duration):
        self.slider.setRange(0, duration)

    # todo: Движение ползунка
    def traffic_slider(self, position):
        self.slider.setValue(position)

    # todo: #Перетаскивание ползунка
    def drag_and_drop_slider(self, position):
        self.player.setPosition(position)

    # todo: Функция звуковая дорожка
    def changeVolume(self, value):
        self.audio_output.setVolume(value / 100.0)
        if value == 0 or self.audio_output.isMuted():
            self.muteButton.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolumeMuted)
            )
        else:
            self.muteButton.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume)
            )

    # todo: Функция отключения звука
    def toggleMute(self):
        self.audio_output.setMuted(
            not self.audio_output.isMuted()
        )  # получаем значение, указывающее,
        # отключен ли звук мультимедиа
        if self.audio_output.isMuted():
            self.muteButton.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolumeMuted)
            )
        else:
            self.muteButton.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume)
            )

    # todo:Функция полнорежимный экран
    def toggleFullScreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.fullScreenButton.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton)
            )
        else:
            self.showFullScreen()
            self.fullScreenButton.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarNormalButton)
            )

    # todo: Видео превью
    def handleMediaStatusChanged(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            )
            self.player.setPosition(0)
        elif status == QMediaPlayer.MediaStatus.LoadedMedia:
            if self.firstTimeLoad:
                self.player.pause()
                self.firstTimeLoad = False

    # todo: Выход с сохранением настроек при закрытии приложения
    def closeEvent(self, event):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтвердить выход")
        msg_box.setText("Сохранить текущие местоположение Video Player ?  ")
        msg_box.setStyleSheet("color:red; padding: 10px; font-size:15px")
        yes_button = msg_box.addButton("Yes", QMessageBox.ButtonRole.YesRole)
        msg_box.addButton("No", QMessageBox.ButtonRole.NoRole)
        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            self.settings.setValue("size", self.size())
            self.settings.setValue("pos", self.pos())
            super().closeEvent(event)
        else:
            super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoPlayer()
    app.setStyleSheet(
        "QSlider {"
        "min-height: 34px;"
        "max-height: 34px;"
        "}"
        "QSlider::groove:horizontal {"
        "border: 1px solid #fff;"
        "height: 5px;"
        "margin: 0px 1px;"
        "border-radius:5px;"
        "}"
        "QSlider::handle:horizontal {"
        "background:#78A75A;"
        "border: 1px solid #fff;"
        "width: 6px;"
        "height: 100px;"
        "margin: -5px -2px;"
        "border-radius:5px;"
        "}"
        "QSlider::add-page:qlineargradient {"
        "background: rgb(51, 217, 33);"
        "border-top-right-radius: 5px;"
        "border-bottom-right-radius: 5px;"
        "border-top-left-radius: 0px;"
        "border-bottom-left-radius: 0px;"
        "}"
        "QSlider::sub-page:qlineargradient {"
        "background: red;"
        "border-top-right-radius: 0px;"
        "border-bottom-right-radius: 0px;"
        "border-top-left-radius: 5px;"
        "border-bottom-left-radius: 5px;"
        "}"
        "QPushButton:hover {"
        "background: rgb(51, 217, 33);"
        "color:#fff;"
        "}"
        "}"
    )
    window.show()
    sys.exit(app.exec())
