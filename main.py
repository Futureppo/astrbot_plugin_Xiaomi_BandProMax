import asyncio
import aiohttp
from astrbot.api.event import AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, llm_tool, AstrBotConfig


@register(
    "astrbot_plugin_loveegg",
    "Futureppo",
    "提供一个tool用于控制跳蛋",
    "1.0.0",
    "https://github.com/Futureppo/astrbot_plugin_group_loveegg",
)
class LoveEggPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig = None):
        super().__init__(context)
        self.config = config or {}
        # 获取配置项，如果没有配置则使用默认值
        self.device_url = self.config.get("device_url", "http://127.0.0.1:8080")
        self.display_message = self.config.get("display_message", "AstrBot控制")
        self.request_timeout = self.config.get("request_timeout", 10)
        self.vibration_duration = 0.5
        logger.info(f"跳蛋控制插件已加载，设备地址: {self.device_url}，显示消息: {self.display_message}")

    @llm_tool("loveegg_control")
    async def control_loveegg(
        self, 
        event: AstrMessageEvent, 
        intensity: str = "normal"
    ) -> str:
        """控制跳蛋设备震动。当用户需要控制跳蛋或让跳蛋震动时调用此工具。每次调用震动0.5秒，可以多次调用增加时长。

        Args:
            intensity(string): 震动强度描述，如 "轻微"、"正常"、"强烈" 等，用于在远端显示不同的控制信息
        """
        try:
            # 根据强度参数构建显示消息
            display_text = f"{self.display_message} - {intensity}"
            
            # 构建完整的请求URL
            url = f"{self.device_url}?text={display_text}"
            
            logger.info(f"发送跳蛋控制指令: {url}")
            
            # 使用异步HTTP客户端发送请求
            timeout = aiohttp.ClientTimeout(total=self.request_timeout)
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        response_text = await response.text()
                        logger.info(f"跳蛋控制成功，响应: {response_text}")
                        
                        # 固定等待0.5秒震动时间
                        await asyncio.sleep(self.vibration_duration)
                        
                        return f"✅ 跳蛋控制成功！震动 {self.vibration_duration} 秒，强度: {intensity}，设备响应: {response_text}"
                    else:
                        error_msg = f"跳蛋控制失败，HTTP状态码: {response.status}"
                        logger.error(error_msg)
                        return f"❌ {error_msg}"
                        
        except aiohttp.ClientTimeout:
            error_msg = "跳蛋控制超时，请检查设备地址和网络连接"
            logger.error(error_msg)
            return f"❌ {error_msg}"
        except aiohttp.ClientError as e:
            error_msg = f"跳蛋控制网络错误: {str(e)}"
            logger.error(error_msg)
            return f"❌ {error_msg}"
        except Exception as e:
            error_msg = f"跳蛋控制发生未知错误: {str(e)}"
            logger.error(error_msg)
            return f"❌ {error_msg}"

    async def terminate(self):
        """插件卸载时调用"""
        logger.info("跳蛋控制插件已卸载")