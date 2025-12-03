from .bakery import router as bakery_router
from .chat import router as chat_router
from .tags import router as tags_router
from .chat_history import router as chat_history_router
from .auth import router as auth_router
from .wishlist import router as wishlist_router
from .visit_records import router as visit_records_router

__all__ = ["bakery_router", "chat_router", "tags_router", "chat_history_router", "auth_router", "wishlist_router", "visit_records_router"]
