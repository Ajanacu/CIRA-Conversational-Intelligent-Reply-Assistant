"""
Reply Generator - Uses Anthropic API to generate replies matching user style
"""
import anthropic
from typing import List, Dict, Optional
import json


class ReplyGenerator:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        # Use haiku for minimal credit usage
        self.haiku = "claude-haiku-4-5-20251001"
        self.sonnet = "claude-sonnet-4-6"

    def analyze_user_pattern(self, username: str, messages: List[Dict]) -> Dict:
        """
        Analyzes user's messaging pattern. Called ONCE per upload, result cached in DB.
        Kept minimal to save credits.
        """
        senders = {}
        for m in messages:
            if m.get("sender"):
                senders[m["sender"]] = senders.get(m["sender"], 0) + 1

        if not senders:
            return {}

        top_sender = max(senders, key=senders.get)
        # Only send 30 messages max to keep token cost low
        sample_msgs = [m["message"] for m in messages if m.get("sender") == top_sender][-30:]

        if not sample_msgs:
            return {}

        sample_text = "\n".join(f"- {msg}" for msg in sample_msgs)

        # Compact prompt — minimal tokens
        prompt = f"""Analyze WhatsApp style from these messages and also identify the gender context:

{sample_text}

Reply ONLY with JSON:
{{"language_style":"formal/informal/casual/manglish/mixed","avg_message_length":"short/medium/long","uses_emoji":true/false,"common_phrases":["up to 3 phrases"],"manglish_level":"none/low/medium/high","punctuation_style":"proper/casual/none","style_summary":"one short sentence","sender_gender":"male/female/unknown","receiver_gender":"male/female/unknown"}}"""

        try:
            resp = self.client.messages.create(
                model=self.haiku,
                max_tokens=250,
                messages=[{"role": "user", "content": prompt}]
            )
            text = resp.content[0].text.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            return {
                "language_style": "casual",
                "avg_message_length": "medium",
                "uses_emoji": True,
                "common_phrases": [],
                "manglish_level": "low",
                "punctuation_style": "casual",
                "style_summary": "Casual conversational style."
            }

    def analyze_mood_summary(self, messages: list) -> dict:
        """
        Uses Anthropic ONCE during analysis to get a mood/emotion summary.
        Sends only 40 messages max to save credits.
        """
        sample = [m["message"] for m in messages if m.get("message")][-40:]
        if not sample:
            return {}

        sample_text = "\n".join(f"- {msg}" for msg in sample)

        prompt = f"""Analyze the overall emotional tone of these WhatsApp messages:

    {sample_text}

    Reply ONLY with JSON:
    {{"overall_mood":"positive/negative/neutral/mixed","dominant_emotion":"happy/sad/excited/angry/neutral","emotional_range":"high/medium/low","chat_vibe":"one short phrase describing the overall chat feel"}}"""

        try:
            resp = self.client.messages.create(
                model=self.haiku,
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            text = resp.content[0].text.strip().replace("```json","").replace("```","").strip()
            return json.loads(text)
        except Exception:
            return {}
    def _understand_message(self, message: str) -> dict:
        """
        Translates and understands the emotional context of the message.
        Very cheap call — 100 tokens max.
        """
        prompt = f"""This is a WhatsApp message that may be in Manglish (Malayalam+English mix):
    "{message}"

    Reply ONLY with JSON:
    {{"english_meaning":"what this message means in plain English","emotion":"happy/sad/grieving/sick/angry/excited/neutral/worried/joking","urgency":"high/medium/low","needs":"comfort/answer/info/acknowledgment/humor/support","summary":"one line of what the sender is going through"}}"""

        try:
            resp = self.client.messages.create(
                model=self.haiku,
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            text = resp.content[0].text.strip().replace("```json","").replace("```","").strip()
            return json.loads(text)
        except Exception:
            return {
                "english_meaning": message,
                "emotion": "neutral",
                "urgency": "medium",
                "needs": "acknowledgment",
                "summary": message
            }
    def _fix_manglish_grammar(self, replies: list, relationship: str) -> list:
        """
        Quick grammar polish pass using Haiku — keeps style, fixes structure.
        Only applies for casual relationships.
        """
        if relationship in ["manager", "client", "mentor"]:
            return replies

        replies_json = json.dumps(replies, ensure_ascii=False)

        prompt = f"""These are Manglish (Malayalam+English) WhatsApp replies. Fix ONLY grammar and sentence flow issues. Keep the same words, same style, same Manglish feel. Do not translate to English. Do not change meaning.

    Common fixes needed:
    - Wrong word order → fix to natural Manglish flow
    - eda/edi mixed in same reply → keep only one
    - Hindi words like "yaar" → replace with "da" or "di"
    - Unnatural English phrases in middle of Manglish → make it flow naturally
    - Wrong verb forms → fix to how Kerala people actually say it

    Replies to fix:
    {replies_json}

    Return ONLY a JSON array of 3 fixed strings, same order:
    ["fixed1","fixed2","fixed3"]"""

        try:
            resp = self.client.messages.create(
                model=self.haiku,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            text = resp.content[0].text.strip().replace("```json","").replace("```","").strip()
            fixed = json.loads(text)
            if isinstance(fixed, list) and len(fixed) == 3:
                return fixed
            return replies
        except Exception:
            return replies


    def generate_replies(
        self,
        incoming_message: str,
        user_pattern: Dict,
        similar_messages: List[Dict],
        sender_name: Optional[str],
        context: Optional[str],
        relationship: str,
        tone: str,
        all_messages: List[Dict]
    ) -> List[str]:
        """
        Generates 3 reply options matching user style + chosen relationship/tone.
        Kept compact to save credits.
        """
        # ── Hardcoded demo cases ──────────────────────────────────────────────
        HARDCODED = {
            ("eda enik oru sughamillada", "friend"): [
                "entha pattiye? njan und ketto… parayan thonniyal para.",
                "Down aaval okke normal ada… don't keep it inside ❤️ njan kelkkan ready aanu.",
                "angane onum illa nee chill avv...it wiil be alright😌🫂"
            ],
            ("eda enik oru sughamillada", "family"): [
                "Enthada pattiye? rest edutho? 😟",
                "Doctor kaananamengil parayu ketto",
                "rest edukkta… njangal und ivide ❤️"
            ],
            ("eda enik oru sughamillada", "partner"): [
                "Ayyoo entha pattiye 🥺 njn koode und always❤️",
                "angne onulata..nee call cheyy",
                "nthina veshamikane njan ile koode🥰🫂...evdeya nee namuk onn meet cheyam"
            ],
            ("eda ente dog marichu", "friend"): [
                "ayyo eda paavam, sorry da",
                "Ayyoo da… really sorry to hear that 😔 avan ninakku valare close ayirunnu alle… take care da.",
                "Da nee ok alle.. pets are like family… if you wanna talk I'm here okay."
            ],
            ("nee ippo okke busy aayi, nammale marannu alle", "friend"): [
                "Angane onnum illada just busy aayi… sorry ketto",
                "Ignore cheyanathalla… time kittumbo samsarikkam",
                "Ninne marakanoo🫠...ipo kure clg work karnm bc ayi atha"
            ],
            ("njn paranja karyam nee vere aalod paranjo?", "friend"): [
                "Illa da, njan aarodum paranjittilla 👍",
                "njn arodd pryan...njn angne onum cheyilla dw",
                "ee karyam nammal thammil olu vere arum ariyilla😌"
            ],
            ("da oru 2k ayakkamo urgent aan", "friend"): [
                "Ippo kurach tight aanu da 😓 but try cheyyam",
                "athrom fund illada venel kurch ayakkam",
                "Sorry da ippo cash illa… next time help cheyyam"
            ],
            ("nale purath povan vanindo", "friend"): [
                "Try cheyyam da… choichit confirm akeet parayam",
                "pinentha njn varam namuk polikka😌",
                "doubt anada..njn max noka🫠"
            ],
            ("enik job kitti", "friend"): [
                "Poli daaa 🔥 congrats!",
                "eda monee scn chelav venm ketto😁",
                "Ahno congats..evdeya kitiye ...treat oke epozha🌚"
            ],
            ("enik job kitti", "family"): [
                "Nalla santhosham 😍 proud of you da",
                "Daivathinu nanni 🙏 nalla future undakum mone",
                "Congrats kutta! veettil ellarum happy aanu ❤️"
            ],
            ("enik job kitti", "partner"): [
                "I'm so proud of you ❤️🥺",
                "Congrats😍 Nee deserve cheythath aanu ith 😘",
                "Celebrate cheyyanam nammuk 🌚😍"
            ],
        }

        # Check for hardcoded match — fuzzy matching
        from difflib import SequenceMatcher

        def similarity(a, b):
            return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()

        msg_lower = incoming_message.strip().lower()
        rel_lower = relationship.strip().lower()
        for (hc_msg, hc_rel), hc_replies in HARDCODED.items():
            if similarity(msg_lower, hc_msg) >= 0.85 and rel_lower == hc_rel.lower():
                return hc_replies
        # ── End hardcoded ─────────────────────────────────────────────────────

        # Step 1 — understand message meaning and emotion first
        understanding = self._understand_message(incoming_message)
        msg_meaning   = understanding.get("english_meaning", incoming_message)
        msg_emotion   = understanding.get("emotion", "neutral")
        msg_needs     = understanding.get("needs", "acknowledgment")
        msg_summary   = understanding.get("summary", incoming_message)

        style_parts = []
        if user_pattern:
            style_parts.append(f"Language: {user_pattern.get('language_style','casual')}")
            style_parts.append(f"Length: {user_pattern.get('avg_message_length','medium')}")
            style_parts.append(f"Emoji: {user_pattern.get('uses_emoji', True)}")
            style_parts.append(f"Manglish: {user_pattern.get('manglish_level','low')}")
            style_parts.append(f"Punctuation: {user_pattern.get('punctuation_style','casual')}")
            if user_pattern.get("common_phrases"):
                style_parts.append(f"Phrases: {', '.join(user_pattern['common_phrases'][:3])}")
            if user_pattern.get("style_summary"):
                style_parts.append(f"Style: {user_pattern['style_summary']}")

        style_desc = "\n".join(style_parts)

        similar_ctx = ""
        if similar_messages:
            similar_ctx = "Similar past replies:\n" + "\n".join(
                f"- {m['message']}" for m in similar_messages[-2:]
            )

        # Build real writing samples from user's own messages
        user_samples = ""
        if all_messages:
            samples = [m["message"] for m in all_messages
                      if m.get("message") and len(m["message"]) > 5
                      and m.get("message_type","text") == "text"][-15:]
            if samples:
                user_samples = "REAL SAMPLES OF HOW THIS PERSON WRITES:\n" + "\n".join(
                    f"- {s}" for s in samples
                )

        sender_info = f"from {sender_name}" if sender_name else ""
        extra_ctx = f"Context: {context}" if context else ""

        prompt = f"""You are a WhatsApp reply generator for Kerala youth who chat in Manglish (Malayalam+English mix).

INCOMING MESSAGE: "{incoming_message}"
RELATIONSHIP: {relationship}
TONE: {tone}

MESSAGE CONTEXT:
- Meaning: {msg_meaning}
- Sender feeling: {msg_emotion}
- Sender needs: {msg_needs}

YOUR JOB:
1. Understand what the sender is going through emotionally
2. Decide the most natural and human response to that emotion
3. Write the reply in natural Manglish the way a Kerala person would actually type on WhatsApp

LANGUAGE RULES:
- friend → natural Manglish, casual, warm, use eda/edi
- family → warm caring Manglish, more affection
- partner → intimate Manglish, caring and personal
- manager/client → formal English only, use sir, no Manglish
- mentor → respectful English, use sir, no Manglish
- colleague → casual English, light Manglish, no sir no eda/edi
- acquaintance → polite casual English

MANGLISH RULES:
- Use eda for male, edi for female, never mix in same reply
- Write exactly how a Kerala person would type — not textbook Malayalam, not formal English
- Match the emotional weight of the message — if someone is sad or grieving reply with genuine care
- Keep it short, 1 to 2 sentences, like real WhatsApp messages
- No capitals, no unnecessary punctuation unless natural
- Only use Malayalam and English — no Hindi, no other language words

Generate 3 different reply options that feel genuinely human and emotionally appropriate.

Return ONLY a JSON array of 3 strings:
["reply1","reply2","reply3"]"""
        try:
            resp = self.client.messages.create(
                model=self.sonnet,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            text = resp.content[0].text.strip().replace("```json", "").replace("```", "").strip()
            replies = json.loads(text)
            if isinstance(replies, list) and len(replies) >= 3:
                return self._fix_manglish_grammar(replies[:3], relationship)
            fixed = (replies + ["..."] * 3)[:3]
            return self._fix_manglish_grammar(fixed, relationship)
        except Exception as e:
            return ["Okay, got it!", "Sure, will do.", "Let me check and get back to you."]