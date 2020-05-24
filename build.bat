
# pyinstaller --version
# Above command should return 3.6

pyinstaller --windowed --noconsole --clean --icon=GUI_TekkenMovesetExtractor/natsumi.ico --add-data GUI_TekkenMovesetExtractor;GUI_TekkenMovesetExtractor --add-data game_addresses.txt;. --name TekkenMovesetExtractor GUI_TekkenMovesetExtractor.py