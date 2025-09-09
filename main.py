import aiohttp
import asyncio
from urllib.parse import quote_plus
from astrbot.api.event import AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, llm_tool, AstrBotConfig


@register(
    "astrbot_plugin_Xiaomi_BandProMax",
    "Futureppo",
    "提供一个tool用于控制跳蛋",
    "1.0.2",
    "https://github.com/Futureppo/astrbot_plugin_Xiaomi_BandProMax",
)
class Xiaomi_BandProMaxPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig = None):
        super().__init__(context)
        self.config = config or {}
        self.device_url = self.config.get("device_url", "http://192.168.1.5:8080")
        self.display_message = self.config.get("display_message", "控制你")
        self.request_timeout = self.config.get("request_timeout", 10)

    @llm_tool("loveegg_control")
    async def control_Xiaomi_BandProMax(self, event: AstrMessageEvent, s: int) -> str:
        """控制跳蛋震动。

        Args:
            s(number): 震动时间（秒），必须为大于 0 的自然数
        """

        try:
            duration = int(s)
        except Exception:
            return "❌ 参数错误：s 必须为大于 0 的自然数"
        if duration <= 0:
            return "❌ 参数错误：s 必须为大于 0 的自然数"

        base = self.device_url.rstrip("/")
        text_encoded = quote_plus(str(self.display_message))
        url = f"{base}/?text={text_encoded}&s={duration}"

        logger.info(f"发送跳蛋控制指令: {url}")
        try:
            timeout_total = max(int(self.request_timeout), duration + 5)
            timeout = aiohttp.ClientTimeout(total=timeout_total)
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=timeout) as response:
                    resp_text = await response.text()
                    if response.status == 200:
                        logger.info(f"跳蛋控制成功，响应: {resp_text}")
                        return f"✅ 跳蛋控制成功！震动 {duration} 秒，响应: {resp_text}"
                    else:
                        err = f"跳蛋控制失败，HTTP状态码: {response.status}，响应: {resp_text}"
                        logger.error(err)
                        return f"❌ {err}"
        except asyncio.TimeoutError:
            err = "跳蛋控制超时，请检查跳蛋地址和网络连接，或缩短 s 的时间"
            logger.error(err)
            return f"❌ {err}"
        except aiohttp.ClientError as e:
            err = f"跳蛋控制网络错误: {str(e)}"
            logger.error(err)
            return f"❌ {err}"
        except Exception as e:
            err = f"跳蛋控制发生未知错误: {str(e)}"
            logger.error(err)
            return f"❌ {err}" 