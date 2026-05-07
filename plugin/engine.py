from typing import Dict, Any, Optional
from .time_matcher import TimeMatcher
from .topic_matcher import TopicMatcher
from .status_detector import OnlineStatusDetector


class ConditionEngine:
    def __init__(self):
        self.time_matcher = TimeMatcher()
        self.topic_matcher = TopicMatcher()
        self.status_detector = OnlineStatusDetector()

    def evaluate(self, group_config: Dict, message, language: str = "zh") -> Dict:
        global_config = {"timezone": "Asia/Shanghai"}
        
        if not group_config.get("enabled", False):
            return {"passed": False, "reason": "Group proxy not enabled", "matched_topic": None, "response_text": None}
        
        schedule = group_config.get("schedule", {})
        if schedule.get("enabled", False):
            time_ranges = schedule.get("time_ranges", [])
            if not self.time_matcher.is_in_schedule(time_ranges, global_config.get("timezone")):
                return {"passed": False, "reason": "Time not in schedule", "matched_topic": None, "response_text": None}
        
        online_status_config = group_config.get("online_status", {})
        reply_when = online_status_config.get("reply_when", "always")
        user_status = self.status_detector.get_status()
        
        if reply_when == "offline_only" and user_status != "offline":
            return {"passed": False, "reason": "User is not offline", "matched_topic": None, "response_text": None}
        if reply_when == "online_only" and user_status != "online":
            return {"passed": False, "reason": "User is not online", "matched_topic": None, "response_text": None}
        
        triggers = group_config.get("triggers", {})
        message_text = getattr(message, "text", "")
        mentioned_users = getattr(message, "mentioned_users", [])
        is_at_mention = bool(mentioned_users)
        is_at_all = getattr(message, "is_at_all", False)
        
        at_mention_required = triggers.get("at_mention", False)
        if at_mention_required and not is_at_mention:
            return {"passed": False, "reason": "At mention required but not met", "matched_topic": None, "response_text": None}
        
        at_all_enabled = triggers.get("at_all", False)
        if not at_all_enabled and is_at_all:
            return {"passed": False, "reason": "At all not allowed", "matched_topic": None, "response_text": None}
        
        keywords = triggers.get("keywords", [])
        if keywords:
            found_keyword = any(keyword in message_text for keyword in keywords)
            if not found_keyword:
                return {"passed": False, "reason": "No keyword matched", "matched_topic": None, "response_text": None}
        
        instructions = group_config.get("instructions", {})
        topic_responses = instructions.get("topic_responses", [])
        compound_rules = instructions.get("compound", [])
        
        matched_response = self.topic_matcher.match(message_text, topic_responses, compound_rules, language)
        
        if matched_response:
            response_text = matched_response["response"]
            matched_topic = matched_response.get("keywords", "")
        else:
            if language == "en":
                response_text = instructions.get("default_en", "Hello, the user is unavailable. They will reply when they see your message.")
            else:
                response_text = instructions.get("default", "您好，用户暂时不在，他看到消息后会尽快回复您 🙏")
            matched_topic = None
        
        return {"passed": True, "reason": "All conditions passed", "matched_topic": matched_topic, "response_text": response_text}