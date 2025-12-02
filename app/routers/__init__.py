from .bakery import router as bakery_router
from .chat import router as chat_router
from .search import router as search_router
from .tags import router as tags_router
from .chat_history import router as chat_history_router
from .auth import router as auth_router
from .wishlist import router as wishlist_router

__all__ = ["bakery_router", "chat_router", "search_router", "tags_router", "chat_history_router", "auth_router", "wishlist_router"]
