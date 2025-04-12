from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import requests
import datetime
@register("movie_rank_plugin", "YourName", "获取国内电影实时票房排行", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
    
    @filter.command("movie_rank")
    async def movie_rank(self, event: AstrMessageEvent):
        '''🎬 获取国内电影实时票房排行'''
        api_url = "https://api.52vmy.cn/api/wl/top/movie"
        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status() # Raises an exception for bad status codes
            data = response.json()

            if data.get("code") == 200 and data.get("data"):
                movie_data = data["data"]
                movie_list = movie_data.get("list", [])
                update_info = movie_data.get("updateInfo", {})
                national_box = movie_data.get("nationalBox", {})

                update_time_str = f"{update_info.get('date', '')} {update_info.get('time', '')}"
                national_box_str = f"{national_box.get('num', 'N/A')}{national_box.get('unit', '')}"

                reply_message = f"📊 国内电影实时票房排行\n"
                reply_message += f"🕒 更新时间: {update_time_str}\n"
                reply_message += f"💰 全国单日票房: {national_box_str}\n"
                reply_message += "--------------------------\n"

                rank_emojis = ["🥇", "🥈", "🥉"] + ["🏅"] * (len(movie_list) - 3) # Top 3 + others

                for i, movie in enumerate(movie_list):
                    rank = rank_emojis[i] if i < len(rank_emojis) else f"{i+1}."
                    movie_info = movie.get("movieInfo", {})
                    name = movie_info.get("movieName", "未知电影")
                    release = movie_info.get("releaseInfo", "未知")
                    box_desc = movie.get("boxDesc", "N/A") + "万" # Assuming unit is 万
                    sum_box_desc = movie.get("sumBoxDesc", "N/A")

                    reply_message += f"{rank} {name} ({release})\n"
                    reply_message += f"   今日票房: {box_desc}\n"
                    reply_message += f"   累计票房: {sum_box_desc}\n\n"
                
                # Remove trailing newline
                reply_message = reply_message.strip()

                yield event.plain_result(reply_message)

            else:
                error_msg = data.get("msg", "未知错误")
                logger.error(f"获取电影票房失败: API返回错误 - {error_msg}")
                yield event.plain_result(f"😕 获取电影票房信息失败: {error_msg}")

        except requests.exceptions.RequestException as e:
            logger.error(f"获取电影票房失败: 网络请求错误 - {e}")
            yield event.plain_result("😕 网络错误，无法获取电影票房信息，请稍后再试。")
        except json.JSONDecodeError:
            logger.error("获取电影票房失败: 无法解析API响应")
            yield event.plain_result("😕 获取电影票房信息失败，API响应格式错误。")
        except Exception as e:
            logger.error(f"处理电影票房信息时发生未知错误: {e}")
            yield event.plain_result("😕 处理电影票房信息时发生内部错误。")

    async def terminate(self):
        '''插件被卸载/停用时调用，用于执行清理操作。'''
        logger.info("🎬 电影票房插件已停止。")
