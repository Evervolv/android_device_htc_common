ifneq ($(TARGET_SIMULATOR),true)
ifeq ($(TARGET_ARCH),arm)

LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)

# librecovery_ui_htc is a static library included by all the recovery
# UI libraries for specific devices (passion, sapphire, dream).  It
# knows how to recover the log stored in the cache partition when a
# radio or hboot update is done.

LOCAL_SRC_FILES := log_recovery.c
LOCAL_C_INCLUDES += bootable/recovery
LOCAL_MODULE := librecovery_ui_htc
include $(BUILD_STATIC_LIBRARY)

include $(CLEAR_VARS)

# librecovery_update_htc is a set of edify extension functions for
# doing radio and hboot updates on HTC devices.

LOCAL_MODULE_TAGS := optional

LOCAL_SRC_FILES := recovery_updater.c firmware.c bootloader.c
LOCAL_STATIC_LIBRARIES += libmtdutils
LOCAL_C_INCLUDES += bootable/recovery
LOCAL_MODULE := librecovery_updater_htc
include $(BUILD_STATIC_LIBRARY)

endif   # TARGET_ARCH == arm
endif   # !TARGET_SIMULATOR
