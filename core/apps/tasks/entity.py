from dataclasses import dataclass, field


@dataclass
class Task:
    text: str
    telegram_user_id: str
    id: None | int = field(default=None)


