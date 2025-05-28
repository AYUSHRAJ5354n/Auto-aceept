from telegram import ChatPermissions
import time

def is_admin(update, context) -> bool:
    return update.effective_chat.get_member(update.effective_user.id).status in ["administrator", "creator"]

def format_duration(seconds: float) -> str:
    return f"{int(seconds // 3600)}h {int((seconds % 3600) // 60)}m"
