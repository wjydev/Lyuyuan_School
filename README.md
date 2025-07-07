# 绿园中学物语 (Lyuyuan High School Story)

**绿园中学物语**是一款基于大型语言模型（LLM）驱动的、高度动态的恋爱模拟游戏。在这里，你将扮演男主角“陈辰”，与AI少女“苏糖”展开一段独一无二的校园恋情。

不同于传统GalGame固定的选项和脚本，本作的核心在于一个拥有“统一心智”的AI。角色的情感、记忆和对话，都由同一个强大的语言模型实时分析和生成，为你带来真正身临其境的交互体验。

---

## ✨ 核心特色

*   🧠 **统一心智AI (Unified Mind AI):** 告别“人工情感分析+AI回复”的分裂模式。角色的好感度变化、情绪波动、对话策略和最终回复，全部由LLM在一次调用中完成，实现了真正的情感与行为一致性。
*   🗣️ **自然语言驱动:** 通过自由输入与角色进行对话，你的每一句话都会被AI深度理解，并影响你们的关系走向。
*   💖 **动态情感系统:** AI会根据你的用词、语气、话题和上下文，实时更新她对你的好感度、心情甚至无聊度，并反映在她后续的言行中。
*   💬 **Prompt驱动的角色塑造:** 角色的所有性格、背景、原则和行为逻辑都定义在清晰的Prompt模板中，实现了AI行为的高度可定制化和快速迭代。
*   🌱 **极简核心架构:** 项目经过深度重构，移除了所有冗余和复杂的旧模块，形成了一个以`AI Agent`为核心的、轻量且易于扩展的全新架构。

## 🚀 技术栈

*   **后端:** Python 3, Flask
*   **AI核心:**
    *   **对话与分析:** 依赖外部大语言模型API (如 DeepSeek, OpenAI GPT系列等)
    *   **Prompt工程:** 通过结构化的Prompt模板 (`/prompts`) 指导LLM进行角色扮演和JSON格式的内心分析。
*   **数据存储:**
    *   **游戏存档:** JSON 文件 (`/saves`)
    *   **(未来)长期记忆:** 计划使用向量数据库 (如 ChromaDB)
*   **前端:** 原生 HTML / CSS / JavaScript

## 🔧 如何运行

1.  **克隆仓库**
    ```bash
    git clone https://github.com/wjydev/Lyuyuan_School.git
    cd Lyuyuan_School
    ```

2.  **创建并激活虚拟环境**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```

4.  **配置API密钥**
    *   复制 `.env.example` 文件并重命名为 `.env`。
    *   在 `.env` 文件中填入你的大语言模型API密钥：
        ```
        DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxx"
        ```

5.  **启动Web应用**
    ```bash
    python web_start.py
    ```

6.  在浏览器中打开 `http://127.0.0.1:5000` 即可开始游戏。

## 🏛️ 项目新架构概览

本项目采用了一个以AI Agent为中心的极简架构：

*   **`web_start.py`**: 启动器，负责环境设置和启动Web服务器。
*   **`web_app/`**: Flask应用目录。
    *   **`app.py`**: 处理Web请求和API路由。
    *   **`game_core.py`**: **新的、轻量级的游戏指挥中心**，负责连接Web界面和AI核心。
*   **`Su_Tang.py`**: **AI Agent核心**，封装了所有与LLM的交互逻辑，包括构建Prompt、调用API、解析回复和更新内部状态。
*   **`Game_Storage.py`**: 负责游戏的存档和读档。
*   **`prompts/`**: **AI的“灵魂”所在**，存放定义角色行为的Prompt模板。
*   **`config/`**: 存放游戏中的结构化数据，如角色档案。

## 展望与计划

*   [ ] **长期记忆:** 引入向量数据库，让角色拥有真正的长期记忆。
*   [ ] **场景系统:** 重新引入并简化场景管理，让游戏世界更丰富。
*   [ ] **事件系统:** 基于AI分析结果，动态触发特殊剧情事件。

---

欢迎提出Issues和Pull Requests，一起创造更有灵魂的AI角色！