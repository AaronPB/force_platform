import os
from enum import Enum


class ImagePaths(Enum):
    _image_folder = os.path.join(os.path.dirname(__file__), "..", "..", "images")

    WINDOW_ICON = os.path.join(_image_folder, "window_icon.ico")
    LOGO = os.path.join(_image_folder, "project_ui_logo.svg")
    PLATFORM = os.path.join(_image_folder, "platform.png")


class IconPaths(Enum):
    _icon_folder = os.path.join(
        os.path.dirname(__file__), "..", "..", "images", "icons"
    )

    GITHUB = os.path.join(_icon_folder, "github.svg")
    TAG = os.path.join(_icon_folder, "tag.svg")
    SEND = os.path.join(_icon_folder, "send-plane-horizontal.svg")
    SETTINGS = os.path.join(_icon_folder, "filter-horizontal.svg")
    GRAPH = os.path.join(_icon_folder, "graph-trend-line.svg")

    STATUS_OK = os.path.join(_icon_folder, "check-tick-circle.svg")
    STATUS_WARN = os.path.join(_icon_folder, "troubleshoot.svg")
    STATUS_ERROR = os.path.join(_icon_folder, "multiple-cross-cancel-circle.svg")
    STATUS_OFF = os.path.join(_icon_folder, "minus-circle.svg")

    LOADCELL_ICON = os.path.join(_icon_folder, "purse-bag.svg")
    ENCODER_ICON = os.path.join(_icon_folder, "map-pin.svg")
    IMU_ICON = os.path.join(_icon_folder, "bot.svg")
    CAMERA_ICON = os.path.join(_icon_folder, "camera.svg")

    PLATFORM_ICON = os.path.join(_icon_folder, "layer-two.svg")
    DEFAULT_GROUP_ICON = os.path.join(_icon_folder, "layout-grid-stack-down.svg")
