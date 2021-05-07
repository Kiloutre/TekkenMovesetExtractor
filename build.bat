
# pyinstaller --version
# Above command should return 3.6

pyinstaller --windowed --noconsole --clean --icon=InterfaceData/natsumi.ico --add-data InterfaceData;InterfaceData --add-data CameraAnimations;CameraAnimations --add-data game_addresses.txt;. --name TekkenMovesetExtractor GUI_TekkenMovesetExtractor.py