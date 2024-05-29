set dotenv-load
set export

circup *ARGS:
	circup --path . {{ARGS}}

sync:
	cp -u ${TARGET_DEVICE}/boot_out.txt ./boot_out.txt
	cp -u -t ${TARGET_DEVICE}/ *.py
	cp -urt ${TARGET_DEVICE}/ lib/
	mkdir -p ${TARGET_DEVICE}/img
	cp -urt ${TARGET_DEVICE}/img img/*.bmp
sync-loop:
	while true; do just sync; sleep 1s; done

console:
	picocom ${SERIAL_TTY}

console-loop:
	#!/bin/bash
	while ! (test -a ${SERIAL_TTY} && picocom ${SERIAL_TTY}); do sleep 1s; done

