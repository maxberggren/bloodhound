TOKEN_COUNT_THRESHOLD = 4
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
    'Referer': 'https://www.google.com/',
}
CUSTOM_SETTINGS = {
    "ROBOTSTXT_OBEY": False,
    "USER_AGENT": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "SCHEDULER_PRIORITY_QUEUE": "scrapy.pqueues.DownloaderAwarePriorityQueue",
    "CONCURRENT_REQUESTS": 100,
    "REACTOR_THREADPOOL_MAXSIZE": 20,
    "LOG_LEVEL": "ERROR",
    "COOKIES_ENABLED": False,
    "RETRY_ENABLED": False,
    "DOWNLOAD_TIMEOUT": 15,
    "TELNETCONSOLE_ENABLED": False,
}
BLACKLIST_PATTERN = [r'\.(jpg|jpeg|png|gif|pdf)$', r'mailto:', r'\bcontact\b', r'schema.org']