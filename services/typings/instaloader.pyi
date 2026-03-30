# typings/instaloader.pyi
# Type stub for instaloader to satisfy type checkers

from typing import Any, List, Optional

class Instaloader:
    context: Any
    def __init__(self) -> None: ...

class Profile:
    biography: str
    followers: int
    full_name: str
    mediacount: int
    
    @staticmethod
    def from_username(context: Any, username: str) -> Profile: ...
    
    def get_posts(self) -> Any: ...