"""
Real-Time Interview Co-Pilot Engine
Processes transcribed speech, identifies question intent, and delivers sub-second architectural defense talking points.
"""

import json
import re
import math
import os
from typing import Dict, List, Any, Optional

class InterviewEngine:
    def __init__(self, kb_path: Optional[str] = None):
        if kb_path is None:
            kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
        self.kb_path = kb_path
        self.kb_data = self._load_kb()
        self.topics = self.kb_data.get("topics", [])
        self.profile = self.kb_data.get("candidate_profile", {})
        self._build_index()

    def _load_kb(self) -> Dict[str, Any]:
        with open(self.kb_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        words = re.findall(r'\b[a-z0-9_\-]{2,}\b', text)
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with",
            "about", "against", "between", "into", "through", "during", "before", "after",
            "above", "below", "from", "up", "down", "is", "are", "was", "were", "be",
            "been", "being", "have", "has", "had", "do", "does", "did", "can", "could",
            "should", "would", "how", "what", "why", "when", "where", "who", "which",
            "tell", "me", "you", "your", "our", "their", "this", "that", "these", "those"
        }
        return [w for w in words if w not in stop_words]

    def _build_index(self):
        self.topic_docs = []
        doc_count = len(self.topics)
        token_doc_freq = {}

        for topic in self.topics:
            doc_tokens = []
            # keywords weighted 8x
            for kw in topic.get("keywords", []):
                doc_tokens.extend(self._tokenize(kw) * 8)
            # questions weighted 4x
            for q in topic.get("questions", []):
                doc_tokens.extend(self._tokenize(q) * 4)
            # title weighted 4x
            doc_tokens.extend(self._tokenize(topic.get("title", "")) * 4)
            # points & hook weighted 1x
            doc_tokens.extend(self._tokenize(topic.get("opening_hook", "")))
            for pt in topic.get("architecture_points", []):
                doc_tokens.extend(self._tokenize(pt))
            
            tf = {}
            unique_tokens = set()
            for token in doc_tokens:
                tf[token] = tf.get(token, 0) + 1
                unique_tokens.add(token)

            for token in unique_tokens:
                token_doc_freq[token] = token_doc_freq.get(token, 0) + 1

            self.topic_docs.append({
                "topic": topic,
                "tf": tf,
                "total_tokens": len(doc_tokens),
                "keywords": [kw.lower() for kw in topic.get("keywords", [])]
            })

        # Calculate IDF
        self.idf = {}
        for token, df in token_doc_freq.items():
            self.idf[token] = math.log((doc_count - df + 0.5) / (df + 0.5) + 1.0)

    def match_question(self, query: str) -> Dict[str, Any]:
        query_tokens = self._tokenize(query)
        query_lower = query.lower()
        if not query_tokens:
            default_topic = self.topics[0] if self.topics else {}
            return {
                "query": query,
                "matched": False,
                "confidence": 0.0,
                "topic": default_topic,
                "profile": self.profile
            }

        scores = []
        for item in self.topic_docs:
            score = 0.0
            tf = item["tf"]
            total = item["total_tokens"]
            
            for token in query_tokens:
                if token in tf:
                    count = tf[token]
                    idf_val = self.idf.get(token, 1.0)
                    # BM25 formula
                    score += idf_val * (count * 2.2) / (count + 1.2 * (0.25 + 0.75 * (total / 150.0)))
            
            # Substring / keyword bonus with IDF
            for kw in item["keywords"]:
                if re.search(r'\b' + re.escape(kw) + r'\b', query_lower):
                    kw_tokens = self._tokenize(kw)
                    kw_idf = sum(self.idf.get(t, 1.5) for t in kw_tokens) or 2.0
                    score += 8.0 * kw_idf
                elif kw in query_lower:
                    score += 4.0

            scores.append((score, item["topic"]))

        scores.sort(key=lambda x: x[0], reverse=True)
        best_score, best_topic = scores[0]

        # Calculate confidence
        confidence = min(round((best_score / (len(query_tokens) * 3.0 + 1.0)) * 50, 1), 99.0)
        matched = confidence >= 20.0

        return {
            "query": query,
            "matched": matched,
            "confidence": confidence,
            "topic": best_topic,
            "alternatives": [t["title"] for s, t in scores[1:4] if s > 0.5],
            "profile": self.profile
        }

    def get_topic_by_id(self, topic_id: str) -> Optional[Dict[str, Any]]:
        for topic in self.topics:
            if topic["id"] == topic_id:
                return topic
        return None

    def get_all_topics_summary(self) -> List[Dict[str, str]]:
        return [
            {
                "id": t["id"],
                "title": t["title"],
                "category": t["category"]
            }
            for t in self.topics
        ]

if __name__ == "__main__":
    engine = InterviewEngine()
    test_queries = [
        "How do you handle policy latency in distributed microservices?",
        "What happens when UAV swarm drones lose connection or have packet loss?",
        "How do you enforce risk management and drawdown in trading systems?",
        "Why should we hire you as a remote contractor from Portugal?",
        "Tell me how you design high throughput distributed systems with kafka"
    ]
    for q in test_queries:
        res = engine.match_question(q)
        print(f"Q: {q}")
        print(f"   -> Match: {res['topic']['title']} (Confidence: {res['confidence']}%)")
        print(f"   -> Hook: {res['topic']['opening_hook'][:70]}...")
        print()
