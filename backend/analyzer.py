"""
WhatsApp Chat Analyzer - Parses exported chat files and computes statistics
"""
import re
from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Dict, Optional
import statistics


# WhatsApp export format patterns
PATTERNS = [
    # 12-hour: 1/1/23, 10:30 am - Name: msg
    re.compile(r'(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}\s*[aApP][mM])\s*-\s*([^:]+):\s*(.+)'),
    # 24-hour: 01/01/2023, 22:30 - Name: msg
    re.compile(r'(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2})\s*-\s*([^:]+):\s*(.+)'),
    # With brackets: [1/1/23, 10:30:00 AM] Name: msg
    re.compile(r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?::\d{2})?\s*(?:[aApP][mM])?)\]\s*([^:]+):\s*(.+)'),
]

SYSTEM_PHRASES = [
    "messages and calls are end-to-end encrypted",
    "created group",
    "added you",
    "you were added",
    "left",
    "changed the subject",
    "changed this group",
    "security code changed",
    "null",
]

MEDIA_TYPES = ["<media omitted>", "image omitted", "video omitted", "audio omitted",
               "document omitted", "sticker omitted", "gif omitted", "contact card omitted"]

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
_vader = SentimentIntensityAnalyzer()

MANGLISH_POSITIVE = [
    "adipoli", "kollam", "superb", "nalla", "sheriyaa", "shari", "mast",
    "thakaraar", "done ayi", "okke ayi", "aayii", "seri", "sheri", "njn",
    "enthaa", "lol", "haha", "hhaha", "hahaha", "😍", "❤", "👍", "🔥",
    "kollallo", "adipoliiii", "supeerb", "😊", "😄", "😂", "🤣", "yay",
    "great", "awesome", "nice", "good", "happy", "love", "perfect", "👌"
]
MANGLISH_NEGATIVE = [
    "poda", "podi", "mandan", "paavam", "poyii", "ayyo", "pinne", "stress",
    "tired", "mosham", "waste", "😒", "😤", "😔", "😭", "😢", ":(", "ugh",
    "worst", "terrible", "hate", "sad", "miss", "sorry", "difficult", "hard"
]
MANGLISH_EXCITED = [
    "machane", "eda", "ede", "enthaaa", "woww", "adipoliiii", "no way",
    "seriously", "omg", "🎉", "🤩", "😱", "!!", "kollallo", "enthada",
    "enthedi", "really", "whaat", "ayyooo"
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class WhatsAppAnalyzer:
    def __init__(self, raw_text: str, username: str):
        self.raw_text = raw_text
        self.username = username
        self.messages: List[Dict] = []

    def parse_messages(self) -> List[Dict]:
        lines = self.raw_text.split("\n")
        parsed = []
        current = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            matched = False
            for pattern in PATTERNS:
                m = pattern.match(line)
                if m:
                    date_str, time_str, sender, message = m.groups()
                    sender = sender.strip()
                    message = message.strip()

                    # Skip system messages
                    if any(p in message.lower() for p in SYSTEM_PHRASES):
                        matched = True
                        break

                    # Determine message type
                    msg_type = "text"
                    if any(mt in message.lower() for mt in MEDIA_TYPES):
                        msg_type = "media"
                    elif message.startswith("http") or "www." in message:
                        msg_type = "link"

                    # Parse datetime
                    try:
                        dt = self._parse_datetime(date_str, time_str)
                    except Exception:
                        dt = None

                    entry = {
                        "sender": sender,
                        "message": message,
                        "timestamp": f"{date_str} {time_str}",
                        "date": date_str,
                        "time": time_str,
                        "hour": dt.hour if dt else 0,
                        "day_of_week": DAYS[dt.weekday()] if dt else "",
                        "message_type": msg_type,
                        "mood": self._detect_mood(message),
                        "char_count": len(message),
                        "word_count": len(message.split()),
                    }
                    parsed.append(entry)
                    current = entry
                    matched = True
                    break

            if not matched and current and line:
                # Continuation of previous message
                current["message"] += " " + line
                current["char_count"] = len(current["message"])
                current["word_count"] = len(current["message"].split())

        self.messages = parsed
        return parsed

    def _parse_datetime(self, date_str: str, time_str: str) -> Optional[datetime]:
        time_str = time_str.strip()
        formats = [
            ("%d/%m/%y %I:%M:%S %p", f"{date_str} {time_str}"),
            ("%d/%m/%Y %I:%M:%S %p", f"{date_str} {time_str}"),
            ("%d/%m/%y %I:%M %p", f"{date_str} {time_str}"),
            ("%d/%m/%Y %I:%M %p", f"{date_str} {time_str}"),
            ("%d/%m/%y %H:%M:%S", f"{date_str} {time_str}"),
            ("%d/%m/%Y %H:%M:%S", f"{date_str} {time_str}"),
            ("%d/%m/%y %H:%M", f"{date_str} {time_str}"),
            ("%d/%m/%Y %H:%M", f"{date_str} {time_str}"),
            ("%m/%d/%y %I:%M:%S %p", f"{date_str} {time_str}"),
            ("%m/%d/%Y %I:%M:%S %p", f"{date_str} {time_str}"),
            ("%m/%d/%y %I:%M %p", f"{date_str} {time_str}"),
            ("%m/%d/%Y %I:%M %p", f"{date_str} {time_str}"),
        ]
        for fmt, val in formats:
            try:
                return datetime.strptime(val, fmt)
            except Exception:
                continue
        return None

    def _detect_mood(self, message: str) -> str:
        msg_lower = message.lower()

        # Manglish keyword scores
        pos_score = sum(1 for w in MANGLISH_POSITIVE if w in msg_lower)
        neg_score = sum(1 for w in MANGLISH_NEGATIVE if w in msg_lower)
        exc_score = sum(1 for w in MANGLISH_EXCITED if w in msg_lower)

        # VADER score for English parts
        vader_scores = _vader.polarity_scores(message)
        compound = vader_scores["compound"]

        # Combine both
        total_pos = pos_score + (1 if compound >= 0.1 else 0)
        total_neg = neg_score + (1 if compound <= -0.1 else 0)
        total_exc = exc_score

        if total_exc > 0 and total_exc >= total_neg:
            return "excited"
        elif total_pos > total_neg and total_pos > 0:
            return "happy"
        elif total_neg > total_pos and total_neg > 0:
            return "sad" if compound > -0.5 else "angry"
        elif compound >= 0.5:
            return "excited"
        elif compound >= 0.1:
            return "happy"
        elif compound <= -0.5:
            return "angry"
        elif compound <= -0.1:
            return "sad"
        else:
            return "neutral"

    def compute_statistics(self) -> Dict:
        if not self.messages:
            return {}

        msgs = self.messages
        senders = list(set(m["sender"] for m in msgs))

        # Per-sender stats
        sender_stats = {}
        for sender in senders:
            sender_msgs = [m for m in msgs if m["sender"] == sender]
            sender_stats[sender] = {
                "total_messages": len(sender_msgs),
                "avg_length": round(statistics.mean(len(m.get("message", "")) for m in sender_msgs), 1),
                "media_count": sum(1 for m in sender_msgs if m["message_type"] == "media"),
                "link_count": sum(1 for m in sender_msgs if m["message_type"] == "link"),
                "mood_distribution": self._mood_distribution([{"mood": self._detect_mood(m.get("message",""))} for m in sender_msgs]),
                "most_active_hour": self._most_common([m.get("hour", 0) for m in sender_msgs]),
                "most_active_day": self._most_common([m.get("day_of_week", "") for m in sender_msgs]),
            }

        # Overall stats
        hourly = Counter(int(m.get("hour", 0)) for m in msgs)
        daily = Counter(m["day_of_week"] for m in msgs)
        moods = Counter(self._detect_mood(m.get("message","")) for m in msgs)

        # Top words (all senders combined)
        all_words = []
        for m in msgs:
            if m["message_type"] == "text":
                words = re.findall(r'\b[a-zA-Z]{3,}\b', m["message"].lower())
                all_words.extend(words)
        stop = {"the", "and", "for", "are", "that", "this", "with", "have", "from",
                "was", "but", "not", "you", "all", "can", "her", "been", "his", "they",
                "had", "him", "did", "its", "our", "out", "get", "one", "who", "got",
                "how", "now", "any", "also", "just", "like", "will", "your", "more",
                "than", "what", "when", "there", "then", "into", "some", "about"}
        top_words = Counter(w for w in all_words if w not in stop).most_common(20)

        # Response time analysis
        response_times = self._compute_response_times(msgs)

        return {
            "total_messages": len(msgs),
            "total_senders": len(senders),
            "senders": senders,
            "sender_stats": sender_stats,
            "hourly_distribution": dict(sorted(hourly.items())),
            "daily_distribution": dict(daily),
            "mood_distribution": dict(moods),
            "top_words": top_words,
            "date_range": {
                "first": msgs[0]["timestamp"] if msgs else None,
                "last": msgs[-1]["timestamp"] if msgs else None,
            },
            "avg_response_time_minutes": response_times,
            "message_type_distribution": {
                "text": sum(1 for m in msgs if m["message_type"] == "text"),
                "media": sum(1 for m in msgs if m["message_type"] == "media"),
                "link": sum(1 for m in msgs if m["message_type"] == "link"),
            }
        }

    def _mood_distribution(self, msgs: List[Dict]) -> Dict:
        c = Counter(m.get("mood", "neutral") for m in msgs)
        total = len(msgs)
        return {mood: round(count / total * 100, 1) for mood, count in c.items()}

    def _most_common(self, items: List) -> Optional[str]:
        if not items:
            return None
        return Counter(items).most_common(1)[0][0]

    def _compute_response_times(self, msgs: List[Dict]) -> Optional[float]:
        # Simplified: not stored in DB so skip for now
        return None
