import re
import json5
import openai
import pickle
from datetime import datetime, timedelta
from collections import defaultdict, deque
from config import TOKEN_COUNT_THRESHOLD
from tld import get_tld
from rich.console import Console

console = Console()


def ask_ai(headline, url, domain, prompt) -> dict:
    """Ask LLM how newsworthy it thinks an headline is"""

    if count_tokens_normalized(headline) < TOKEN_COUNT_THRESHOLD:
        return None
    
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt + headline + "\n\nJSON:\n",
        temperature=0,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    cost = response['usage']['total_tokens']*0.000002*10  # Get the cost in tokens    
    output = response["choices"][0]["text"].strip()
    try:
        parsed_output = parse_ai_response(output)
        parsed_output["cost_sek"] = cost  # Add cost to the returned dictionary
        parsed_output["url"] = url
        parsed_output["domain"] = domain
        return parsed_output
    except (ValueError, UnboundLocalError):
        console.log("[bold red]Could not parse:")
        console.log(output)
        return None


def parse_ai_response(data: str):
    """Fault tolerant parsing of JSON string"""
    try:
        json_str = re.search(r"\{.*?\}", data, re.S).group()
    except AttributeError:
        try:
            # Try with added bracket
            json_str = re.search(r"\{.*?\}", "{" + data, re.S).group()
        except AttributeError:
            console.log("[red bold]Could not parse response from AI")
            console.log(data)
    return json5.loads(json_str)


def count_tokens_normalized(text):
    """Support counting words in chinese etc"""
    cjk_tokens = re.findall(r'[\u4e00-\u9faf\uac00-\ud7a3]', text)
    all_word_tokens = re.findall(r'\b\w+\b', text)

    return len(all_word_tokens) + len(cjk_tokens)

def get_domain(url):
    """Extract top level domain like nytimes.com from url"""
    domain = get_tld(url, as_object=True).fld
    return domain
    

class DomainLimitedDeque:
    """Memory object keeping track of the urls the scraper has seen"""
    def __init__(
            self,
            filename='memory.pkl', 
            maxlen=30000, 
            time_window=timedelta(minutes=3), 
            max_per_domain=3
        ):
        self.filename = filename
        self.maxlen = maxlen
        self.time_window = time_window
        self.max_per_domain = max_per_domain
        self.data = defaultdict(deque)
        try:
            with open(self.filename, 'rb') as f:
                self.data = pickle.load(f)
        except (FileNotFoundError, EOFError):
            pass

    def append(self, url):
        domain = get_domain(url)
        timestamped_url = (url, datetime.now())
        
        if self.maxlen is not None and len(self.data[domain]) >= self.maxlen:
            self.data[domain].popleft()

        # Add if not already there
        if not url in (stored_url for stored_url, _ in self.data[domain]):
            self.data[domain].append(timestamped_url)

        self._sync_to_disk()

        # Check rate
        current_time = datetime.now()
        domain_deque = self.data.get(domain, deque())
        domain_count = 0
        for _, timestamp in reversed(domain_deque):
            time_diff = current_time - timestamp
            if time_diff <= self.time_window:
                domain_count += 1
            else:
                break

        if domain_count > self.max_per_domain:
            return False  # Too many URLs in short time
        return True  # Safe to proceed

    def _sync_to_disk(self):
        with open(self.filename, 'wb') as f:
            pickle.dump(self.data, f)

    def __contains__(self, url):
        domain = get_domain(url)
        domain_deque = self.data.get(domain, deque())

        if url in (stored_url for stored_url, _ in domain_deque):
            return True
        

class TooMuchTooSoon(Exception):
    pass