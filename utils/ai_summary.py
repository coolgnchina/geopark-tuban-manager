"""
AI摘要工具模块

集成智谱AI (GLM-4) API，自动生成公文内容摘要。
"""

import os
import requests


def get_api_key() -> str | None:
    """获取智谱AI API Key"""
    env_key = os.environ.get("ZHIPU_API_KEY")
    if env_key:
        return env_key.strip()

    key_file = os.path.join(os.path.dirname(__file__), "..", "zhipukey.txt")
    try:
        with open(key_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def generate_summary(content: str, max_tokens: int = 500) -> str | None:
    """
    使用智谱AI生成公文内容摘要

    Args:
        content: 公文原始内容
        max_tokens: 最大token数量

    Returns:
        摘要文本，失败返回None
    """
    api_key = get_api_key()
    if not api_key:
        return None

    # 构建提示词
    prompt = f"""请对以下公文内容进行摘要，要求：
1. 提取关键信息（发文单位、收文单位、主要事项、时间节点等）
2. 摘要简洁明了，不超过200字
3. 使用规范公文语言

公文内容：
{content}

请直接输出摘要，无需额外说明。"""

    try:
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "glm-4",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        if result.get("choices") and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"].strip()

        return None

    except requests.exceptions.RequestException as e:
        print(f"智谱AI API请求失败: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"智谱AI API响应解析失败: {e}")
        return None


def generate_summary_with_context(
    content: str, project_name: str = "", tuban_code: str = ""
) -> str | None:
    """
    使用智谱AI生成公文摘要（带项目上下文）

    Args:
        content: 公文原始内容
        project_name: 项目名称（可选）
        tuban_code: 图斑编号（可选）

    Returns:
        摘要文本，失败返回None
    """
    api_key = get_api_key()
    if not api_key:
        return None

    # 构建提示词（带上下文）
    context = ""
    if project_name:
        context += f"项目名称：{project_name}\n"
    if tuban_code:
        context += f"关联图斑：{tuban_code}\n"

    prompt = f"""{context}请对以下公文内容进行摘要，要求：
1. 提取关键信息（发文单位、收文单位、主要事项、时间节点、需要采取的行动等）
2. 摘要简洁明了，150-200字
3. 使用规范公文语言
4. 如有关联项目或图斑，请一并说明

公文内容：
{content}

请直接输出摘要，无需额外说明。"""

    try:
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "glm-4",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.7,
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        if result.get("choices") and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"].strip()

        return None

    except requests.exceptions.RequestException as e:
        print(f"智谱AI API请求失败: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"智谱AI API响应解析失败: {e}")
        return None
