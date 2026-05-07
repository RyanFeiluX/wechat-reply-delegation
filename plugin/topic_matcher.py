from typing import List, Dict, Optional


class TopicMatcher:
    def match(self, text: str, topic_responses: List[Dict], compound_rules: List[Dict], language: str = "zh") -> Optional[Dict]:
        matched_compound = self._match_compound(text, compound_rules, language)
        if matched_compound:
            return matched_compound
        
        matched_topic = self._match_topics(text, topic_responses, language)
        return matched_topic

    def _match_compound(self, text: str, compound_rules: List[Dict], language: str) -> Optional[Dict]:
        for rule in compound_rules:
            if_all = rule.get("if_all", [])
            if if_all and all(keyword in text for keyword in if_all):
                if language == "en":
                    response = rule.get("response_en", rule.get("response", ""))
                else:
                    response = rule.get("response", "")
                return {"response": response, "keywords": if_all}
        return None

    def _match_topics(self, text: str, topic_responses: List[Dict], language: str) -> Optional[Dict]:
        best_match = None
        max_keywords = 0

        for topic in topic_responses:
            keywords = topic.get("keywords", [])
            matched_count = sum(1 for keyword in keywords if keyword in text)
            
            if matched_count > 0 and matched_count >= max_keywords:
                max_keywords = matched_count
                if language == "en":
                    response = topic.get("response_en", topic.get("response", ""))
                else:
                    response = topic.get("response", "")
                best_match = {"response": response, "keywords": keywords}

        return best_match