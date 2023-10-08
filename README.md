# Bloodhound

Scrapes websites for newly published articles and asks an LLM for their breaking news score. Open source data collection part used by AO.news

## Prerequsites

* [Poetry](https://duckduckgo.com)https://python-poetry.org/)

## Installation

1) `export OPEN_AI="sk-YoUrKeyNotMineHihIHHI"`
2) `poetry install`
3) `poetry run python bloodhound.py`
4) Edit `URLS_TO_MONITOR` with the urls you wish to monitor