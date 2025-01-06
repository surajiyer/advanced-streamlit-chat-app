.PHONY: lint
lint:
	black --line-length 120 .

.PHONY: run
run:
	streamlit run src/main.py
