.PHONY: install uninstall

INSTALL := /usr/local/lib/2048tty
EXECUTABLE := /usr/local/bin/2048tty

install: render.py py2048.py ani.py grid.py getch.py scorecard.py persist.py
	if [ -e $(INSTALL) -o -e $(EXECUTABLE) ]; \
	then \
		echo 'Error: Resources already exist at $(INSTALL) or $(EXECUTABLE).';\
		echo '       Try "make uninstall," or remove any other program that';\
		echo '       might be using these locations.';\
		exit 2;\
	fi
	mkdir $(INSTALL)
	cp -t $(INSTALL) $^
	ln -s $(INSTALL)/py2048.py $(EXECUTABLE) 
	chmod +x $(EXECUTABLE)

uninstall:
	test -L $(EXECUTABLE) && unlink $(EXECUTABLE)
	test -d $(INSTALL) && rm -rf $(INSTALL)
