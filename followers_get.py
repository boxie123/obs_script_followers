import random

import obspython
import requests

url = "https://api.bilibili.com/x/relation/stat"
uid = "1485569"
source_name = ""
interval = 5
agent = [
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36"
]


def script_load(setting):
    obspython.script_log(obspython.LOG_INFO, "脚本载入成功")


def script_description():
    return "实时显示粉丝数"


def script_properties():
    pros = obspython.obs_properties_create()
    obspython.obs_properties_add_text(pros, "uid", "UID", obspython.OBS_TEXT_DEFAULT)
    obspython.obs_properties_add_int(pros, "interval", "更新间隔时间(1-600秒)", 1, 600, 1)
    text_source = obspython.obs_properties_add_list(pros, "source_name", "文字源", obspython.OBS_COMBO_TYPE_LIST,
                                                    obspython.OBS_COMBO_FORMAT_STRING)
    sources = obspython.obs_enum_sources()
    if sources:
        for source in sources:
            source_id = obspython.obs_source_get_unversioned_id(source)
            if source_id in ("text_gdiplus", "text_ft2_source"):
                name = obspython.obs_source_get_name(source)
                obspython.obs_property_list_add_string(text_source, name, name)
        obspython.source_list_release(sources)
    obspython.obs_properties_add_button(pros, "refresh", "立即刷新数据", refresh_pressed)
    return pros


def refresh_pressed(pros, prop):
    update()


def script_defaults(settings):
    obspython.obs_data_set_default_int(settings, "interval", 5)
    obspython.obs_data_set_default_string(settings, "uid", "1485569")


def script_update(setting):
    global interval
    global source_name
    global uid

    source_name = obspython.obs_data_get_string(setting, "source_name")
    interval = obspython.obs_data_get_int(setting, "interval")
    uid = obspython.obs_data_get_string(setting, "uid")

    obspython.timer_remove(update)
    obspython.timer_add(update, interval * 1000)


def update():
    global source_name
    global uid
    source = obspython.obs_get_source_by_name(source_name)
    if source:
        setting = obspython.obs_data_create()
        obspython.obs_data_set_string(setting, "text", str(get_followers(uid)))
        obspython.obs_source_update(source, setting)
        obspython.obs_data_release(setting)
    obspython.obs_source_release(source)


def get_followers(vmid):
    global url
    params = {
        "vmid": vmid,
        "jsonp": "jsonp"
    }
    headers = {
        "User-Agent": get_user_agents(),
        "Referer": "https://space.bilibili.com/{}".format(vmid),
        "origin": "https://space.bilibili.com"
    }
    all_info = requests.get(url=url, params=params, headers=headers).json()
    followers = all_info["data"]["follower"]

    return followers


def get_user_agents():
    global agent
    return random.choice(agent)
