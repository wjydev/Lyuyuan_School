# web_app/game_core.py

# 导入我们的AI大脑
from Su_Tang import GalGameAgent

class SimpleGameCore:
    def __init__(self):
        # 1. 创建AI实例：它不通过工厂，直接new一个苏糖出来。
        self.agent = GalGameAgent(is_new_game=True)

    def start_new_game(self):
        """重置游戏状态并返回初始数据"""
        # 2. 响应“开始游戏”请求：它直接告诉AI大脑去初始化。
        self.agent._init_new_game(is_new_game=True)
    
        # 增加返回初始状态的逻辑
        initial_response = "（你走在热闹的校园里，注意到烘焙社的摊位前有个可爱的女孩正在忙碌着...）" # 或者任何你喜欢的开场白
        initial_state = self.get_current_state()
    
        return {
            'response': initial_response,
            'game_state': initial_state
        }

    def chat(self, user_input):
        # 3. 响应“聊天”请求：它把玩家的话直接传给AI大脑，然后把AI的回复拿回来。
        response = self.agent.chat(user_input)
        return response

    def get_current_state(self):
        # 4. 响应“获取状态”请求：它直接去问AI大脑现在的状态是什么。
        return self.agent.game_state
    
    # 5. 响应“存档/读档”请求：它直接告诉AI大脑去执行存档或读档。
    def save_game(self, slot):
        return self.agent.save(slot)

    def load_game(self, slot):
        return self.agent.load(slot)

# 创建一个全局实例，这样 app.py 就可以直接用了
game_core = SimpleGameCore()