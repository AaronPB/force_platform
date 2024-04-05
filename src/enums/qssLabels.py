from enum import Enum


class QssLabels(Enum):
    CONTROL_PANEL_BTN = "cp_btn"
    CRITICAL_CONTROL_PANEL_BTN = "critical_cp_btn"
    CRITICAL_BTN = "critical_btn"
    TITLE_LABEL = "title"
    AUTHOR_COPYRIGHT_LABEL = "author_copy"

    STATUS_LABEL_INFO = "status_info"
    STATUS_LABEL_OK = "status_ok"
    STATUS_LABEL_WARN = "status_warn"

    SENSOR_GROUP = "sensor_group"
    SENSOR = "sensor"

    SENSOR_GROUP_IGNORED = "sensor_group_ignored"
    SENSOR_GROUP_WARN = "sensor_group_warn"
    SENSOR_GROUP_OK = "sensor_group_ok"
    SENSOR_IGNORED = "sensor_ignored"
    SENSOR_ERROR = "sensor_error"
    SENSOR_OK = "sensor_ok"
