import os
from app.tools.settings_data import SettingField, SettingsData, FieldType
from app.shared import SAVE_FOLDER_PATH


"""
App Settings

1. Audio
    * Music volume
    * SFX volume

2. Graphics
    * Windowed
    * Window resolution
    * FPS limit

3. Interface
    * Start-up sequence
    * Background
"""
app_settings = SettingsData([
    # region Audio
    SettingField("music_volume", "Music Volume", FieldType.SLIDER,
                 80, (0, 100),
                 new_section="Audio"),

    SettingField("sfx_volume", "SFX Volume", FieldType.SLIDER,
                 80, (0, 100)),
    # endregion

    # region Graphics
    SettingField("windowed", "Windowed", FieldType.TOGGLE_SWITCH,
                 False,
                 new_section="Graphics"),

    SettingField("window_resolution", "Window Resolution", FieldType.ITEM_PICKER,
                 1, [(800, 600), (1280, 720), (1366, 768), (1920, 1080)],
                 format_func=lambda x: f"{x[0]} × {x[1]}"),

    SettingField("fps_limit", "FPS Limit", FieldType.ITEM_PICKER,
                 3, [0, 30, 45, 60, 90, 120, 144, 240],
                 format_func=lambda x: "Unlimited" if x == 0 else str(x)),
    # endregion

    # region Interface
    SettingField("show_startup", "Show Start-up Sequence", FieldType.TOGGLE_SWITCH,
                 True,
                 new_section="Interface"),

    SettingField("background", "Background", FieldType.TOGGLE_SWITCH,
                 True)
    # endregion

], os.path.join(SAVE_FOLDER_PATH, "app_settings.ini"))



