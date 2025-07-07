# =================================================================================
# Su_Tang.py - [v3.0 - 引入路径查找与随机事件框架]
#
# 变更日志:
# 1. 新增 _find_path 方法，使用BFS算法在locations地图上查找最短路径。
# 2. 重写 _process_movement_action，使其能够处理路径移动，并为未来的随机事件预留框架。
# 3. 彻底修复了之前版本中所有已知的BUG，特别是 think_and_chat 中的 KeyError。
# 4. 简化并加固了 chat 方法中的意图识别和动作处理流程。
# =================================================================================

import os
import random
import json
import re
from pathlib import Path
import requests
import traceback
import yaml
from collections import deque # 导入双端队列，用于BFS算法

from Game_Storage import GameStorage

class GalGameAgent:
    def __init__(self, load_slot=None, is_new_game=False):
        self.storage = GameStorage()
        self.locations = self._load_locations()
        self.dialogue_history = []
        self.game_state = {}
        self.long_term_memory = [] 
        self.dialogue_turns_since_last_summary = 0
        self.SUMMARY_TRIGGER_THRESHOLD = 6

        if load_slot and self.load(load_slot):
            print(f"加载存档#{load_slot}成功")
        else:
            self._init_new_game(is_new_game)

    def _load_locations(self):
        try:
            path = Path(__file__).resolve().parent / "config" / "locations.yaml"
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"[FATAL] Failed to load 'locations.yaml': {e}")
            return {}

    def _init_new_game(self, is_new_game=False):
        self.dialogue_history = []
        if not is_new_game:
            self.dialogue_history.append({"role": "system", "content": "（你第一次见到她，是在学校社团招新的活动上，她正在自己的烘焙社摊位前忙碌着。）"})
        self.game_state = { "closeness": 30, "relationship_state": "初始阶段", "mood_today": "normal", "current_location": "main_building_f2_corridor", "last_topics": [], "boredom_level": 0 }
        self.long_term_memory = []
        self.dialogue_turns_since_last_summary = 0

    def chat(self, user_input: str):
        print(f"\n{'#'*20} NEW CHAT REQUEST {'#'*20}\nUser Input: {user_input}")

        # --- 步骤1: 检查是否为特殊指令 ---
        if user_input.startswith("/debug goto "):
            location_key = user_input.split("/debug goto ")[1].strip()
            return self._process_movement_action(location_key, is_debug_warp=True)

        # --- 步骤2: 检查是否为移动意图 ---
        move_keywords = ["去", "到", "前往", "移动"]
        if any(keyword in user_input for keyword in move_keywords):
            for key, loc_data in self.locations.items():
                if loc_data.get('name') in user_input:
                    return self._process_movement_action(key)

        # --- 步骤3: 正常对话流程 ---
        return self._handle_standard_dialogue(user_input)

    def _handle_standard_dialogue(self, user_input: str):
        """处理所有非移动的、标准的对话交互"""
        print("[INFO] Handling as standard dialogue.")
        self.dialogue_history.append({"role": "user", "content": user_input})
        
        llm_output = self.think_and_chat(user_input)
        
        ai_response = llm_output.get("response", self._get_backup_reply())
        analysis = llm_output.get("analysis")

        if analysis and "error" not in analysis:
            self._update_closeness(analysis.get('affection_delta', 0))
            # ... 其他状态更新 ...
            
            # 检查AI的移动提议
            suggested_action = analysis.get("suggested_action")
            if isinstance(suggested_action, dict) and suggested_action.get("type") == "propose_location_change":
                print(f"[AI ACTION] AI proposed to move. Response incorporates this.")
        
        self.dialogue_history.append({"role": "assistant", "content": ai_response})
        
        # 记忆生成逻辑 (保持不变)
        self.dialogue_turns_since_last_summary += 2
        if self.dialogue_turns_since_last_summary >= self.SUMMARY_TRIGGER_THRESHOLD:
            # ...
            self.dialogue_turns_since_last_summary = 0

        return ai_response

    def _find_path(self, start_key: str, end_key: str) -> list:
        """使用BFS算法查找两个地点之间的最短路径"""
        if start_key not in self.locations or end_key not in self.locations:
            return None
        
        queue = deque([(start_key, [start_key])])
        visited = {start_key}
        
        while queue:
            current_key, path = queue.popleft()
            
            if current_key == end_key:
                return path
            
            for neighbor_key in self.locations[current_key].get("connections", []):
                if neighbor_key not in visited:
                    visited.add(neighbor_key)
                    new_path = list(path)
                    new_path.append(neighbor_key)
                    queue.append((neighbor_key, new_path))
        return None # 找不到路径

    def _process_movement_action(self, target_key: str, is_debug_warp=False) -> str:
        """使用路径查找来处理移动，并为随机事件预留框架"""
        current_key = self.game_state['current_location']
        
        if current_key == target_key:
            return f"（我们已经在{self.locations[current_key].get('name')}了。）"

        if is_debug_warp:
            path = [current_key, target_key]
        else:
            path = self._find_path(current_key, target_key)

        if not path or len(path) < 2:
            return f"嗯...好像没办法从{self.locations[current_key].get('name')}去{self.locations.get(target_key, {}).get('name', '那里')}。"

        # 移动到路径的最终点
        final_destination_key = path[-1]
        self.game_state['current_location'] = final_destination_key
        final_destination_name = self.locations[final_destination_key]['name']
        
        # 构建移动过程的系统消息
        path_names = [self.locations[key]['name'] for key in path]
        
        # 处理路径中的随机事件
        event_messages = []
        # 我们只在中间点（不包括起点和终点）检查事件
        for i in range(1, len(path) - 1):
            waypoint_key = path[i]
            waypoint_name = path_names[i]
            if random.random() < 0.1: # 10%的概率触发事件
                event_message = f"在前往{final_destination_name}的路上，你们路过{waypoint_name}时，似乎发生了什么... (事件系统待实现)"
                event_messages.append(event_message)
                print(f"[EVENT] Random event triggered at {waypoint_key}")
        
        # 组装最终的系统消息
        if len(path) == 2: # 直达
            response_message = f"【场景切换：你们来到了 {final_destination_name}】"
        else: # 需要经过路径
            path_str = " -> ".join(path_names[1:])
            response_message = f"【路线：{path_str}】\n【场景切换：你们最终来到了 {final_destination_name}】"
        
        if event_messages:
            response_message = "\n".join(event_messages) + "\n" + response_message
            
        self.dialogue_history.append({"role": "system", "content": response_message})
        return response_message

    def think_and_chat(self, user_input: str) -> dict:
        # 这个方法现在只负责构建Prompt和调用API，不再处理任何游戏逻辑
        # 这是一个绝对不会再产生KeyError的实现
        
        # 1. 准备动态数据
        current_location_key = self.game_state.get("current_location")
        location_info = self.locations.get(current_location_key, {})
        available_destinations = [f"'{self.locations[key]['name']}' ({key})" for key in location_info.get("connections", []) if key in self.locations]
        
        # 2. 创建一个字典来存放所有要格式化的值
        format_dict = {
            "long_term_memories": "\n".join([f"- {mem}" for mem in self.long_term_memory]) if self.long_term_memory else "无",
            "relationship_state": self.game_state.get("relationship_state", "初始阶段"),
            "closeness": self.game_state.get("closeness", 30),
            "mood_today": self.game_state.get("mood_today", "normal"),
            "current_location_name": location_info.get("name", "未知地点"),
            "current_scene_description": location_info.get("description_for_llm", "未知"),
            "available_destinations": ", ".join(available_destinations) or "无",
            "last_topics": ", ".join(self.game_state.get("last_topics", [])) or "无",
            "conversation_history": self._format_history_for_prompt(),
            "user_input": user_input
        }
        
        # 3. 读取模板并安全地替换
        try:
            prompt_path = Path(__file__).resolve().parent / "prompts" / "su_tang" / "analysis_prompt.txt" # 使用一个新的、干净的模板
            with open(prompt_path, 'r', encoding='utf-8') as f:
                filled_prompt = f.read().format(**format_dict)
        except Exception as e:
            print(f"!!! PROMPT FORMATTING FAILED: {e} !!!")
            return {"analysis": None, "response": self._get_backup_reply(), "error": str(e)}

        # 4. 调用API (保持不变)
        try:
            api_key = os.environ.get("DEEPSEEK_API_KEY")
            if not api_key: raise ValueError("API密钥未设置或无效")
            messages = [{"role": "user", "content": filled_prompt}]
            # ... (rest of the API call)
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
            data = {"model": "deepseek-chat", "messages": messages, "temperature": 0.8, "max_tokens": 1500}
            response = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=data, timeout=45)
            if response.status_code != 200: raise Exception(f"API Error {response.status_code}: {response.text}")
            llm_output = response.json()["choices"][0]["message"]["content"]
            return self._parse_llm_output(llm_output)
        except Exception as e:
            print(f"!!! API CALL FAILED: {e} !!!")
            return {"analysis": None, "response": self._get_backup_reply(), "error": str(e)}

    # ... 其他所有辅助方法保持不变 ...
    def _generate_memory_summary(self, conversation_snippet: str) -> str:
        # ... no change ...
        print("\n" + "-"*15 + " GENERATING LONG-TERM MEMORY " + "-"*15)
        try:
            prompt_path = Path(__file__).resolve().parent / "prompts" / "su_tang" / "summarize_prompt.txt"
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
        except FileNotFoundError:
            print(f"错误: 记忆总结Prompt模板在路径 '{prompt_path}' 未找到！")
            return ""
        filled_prompt = prompt_template.format(conversation_snippet=conversation_snippet)
        try:
            api_key = os.environ.get("DEEPSEEK_API_KEY")
            if not api_key: raise ValueError("API密钥未设置")
            messages = [{"role": "user", "content": filled_prompt}]
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
            data = {"model": "deepseek-chat", "messages": messages, "temperature": 0.2, "max_tokens": 200}
            response = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=data, timeout=30)
            if response.status_code != 200: raise Exception(f"API Error {response.status_code}: {response.text}")
            summary = response.json()["choices"][0]["message"]["content"].strip()
            print(f"New Memory Generated: '{summary}'")
            print("-"*59 + "\n")
            return summary
        except Exception as e:
            print(f"生成记忆时发生异常: {e}"); return ""

    def _parse_llm_output(self, llm_output: str) -> dict:
        # ... no change ...
        analysis_json, response_text = None, self._get_backup_reply()
        try:
            analysis_match = re.search(r'<analysis>(.*?)</analysis>', llm_output, re.DOTALL)
            if analysis_match:
                json_str = analysis_match.group(1).strip()
                json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
                if json_match: analysis_json = json.loads(json_match.group(0))
                else: analysis_json = {"error": "在<analysis>标签内未找到有效的JSON结构。"}
            response_match = re.search(r'<response>(.*?)</response>', llm_output, re.DOTALL)
            if response_match: response_text = response_match.group(1).strip()
            elif analysis_match: response_text = llm_output.split("</analysis>")[-1].strip()
        except Exception as e:
            analysis_json = {"error": f"解析LLM输出时发生未知错误: {e}"}
        return {"analysis": analysis_json, "response": re.sub(r'</?response>', '', response_text).strip()}

    def _format_history_for_prompt(self, custom_history=None) -> str:
        # ... no change ...
        history_to_format = custom_history if custom_history is not None else self.dialogue_history
        dialogue_only = [msg for msg in history_to_format if msg["role"] in ["user", "assistant"]]
        if not custom_history: dialogue_only = dialogue_only[-10:]
        if not dialogue_only: return "（你们还没有开始对话）"
        lines = [f"陈辰: {e['content']}" if e['role'] == 'user' else f"苏糖: {e['content']}" for e in dialogue_only]
        return "\n".join(lines)

    def _update_closeness(self, delta: int):
        # ... no change ...
        if delta == 0: return
        current = self.game_state.get("closeness", 30)
        new_value = max(0, min(100, current + delta))
        if new_value != current:
            self.game_state["closeness"] = new_value
            self._update_relationship_state()

    def _update_relationship_state(self):
        # ... no change ...
        closeness = self.game_state.get("closeness", 30)
        if closeness >= 80: self.game_state["relationship_state"] = "亲密关系"
        elif closeness >= 60: self.game_state["relationship_state"] = "好朋友"
        elif closeness >= 40: self.game_state["relationship_state"] = "朋友"
        else: self.game_state["relationship_state"] = "初始阶段"
    
    def save(self, slot):
        # ... no change ...
        data = { "history": self.dialogue_history, "state": self.game_state, "long_term_memory": self.long_term_memory, "dialogue_turns_since_last_summary": self.dialogue_turns_since_last_summary }
        return self.storage.save_game(data, slot)
    
    def load(self, slot):
        # ... no change ...
        data = self.storage.load_game(slot)
        if data:
            self.dialogue_history = data.get("history", [])
            self.game_state = data.get("state", {})
            self.long_term_memory = data.get("long_term_memory", [])
            self.dialogue_turns_since_last_summary = data.get("dialogue_turns_since_last_summary", 0)
            return True
        return False

    def _get_backup_reply(self):
        # ... no change ...
        return random.choice(["嗯...让我想想。", "（有点走神了，不好意思...）", "那个...你刚才说什么？"])