.PHONY: install uninstall tags

INSTALL := /usr/local/lib/2048tty
EXECUTABLE := /usr/local/bin/2048tty
MANPAGE := 2048tty.6
MANDEST := /usr/local/share/man/man6/2048tty.6

install: render.py py2048.py ani.py grid.py getch.py scorecard.py \
		persist.py 2048tty.6
	if [ -e $(INSTALL) -o -e $(EXECUTABLE) -o -e $(MANDEST) ]; \
	then \
		echo 'Error: Resources already exist at $(INSTALL) or $(EXECUTABLE).';\
		echo '       Try "make uninstall," or remove any other program that';\
		echo '       might be using these locations.';\
		exit 2;\
	fi
	mkdir -p $(INSTALL)
	mkdir -p $(basename $(MANDEST))
	cp -t $(INSTALL) $^
	ln -s $(INSTALL)/py2048.py $(EXECUTABLE) 
	ln -s $(INSTALL)/$(MANPAGE) $(MANDEST)
	chmod +x $(EXECUTABLE)

uninstall:
	test -L $(EXECUTABLE) && unlink $(EXECUTABLE) || true
	test -L $(MANDEST) && unlink $(MANDEST) || true
	test -d $(INSTALL) && rm -rf $(INSTALL) || true

tags:
	ctags --python-kinds=-i -R *
