pyexec=python3.11
mainfile=main.py
projname=python-rasp-bot

.PHONY: kill
kill:
	kill $$(ps aux | grep '[$(pyexec)] $(mainfile)' | awk '{print $$2}')

.PHONY: run
run:
	$(pyexec) $(mainfile) &

.PHONY: install
install:
	$(pyexec) -m pip install -r requirements.txt

.PHONY: update
update:
	git clone https://github.com/VerS7/$(projname)
	rm $(projname)/files/chats.json
	rm $(projname)/example.png
	rm $(projname)/README.md
	rm -rf $(projname)/tests
	cp -r $(projname)/* .
	rm -rf $(projname)
