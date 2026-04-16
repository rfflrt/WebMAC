from sqlmodel import SQLModel, Field, Relationship, Session, create_engine

engine = create_engine("sqlite:///minesweeper.db")

class User(SQLModel, table=True):
    id: int | None = Field(default = None, primary_key=True)
    name: str
    password: str

class UserStats(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    games_won: int = Field(default=0)
    games_lost: int = Field(default=0)
    current_streak: int = Field(default=0)
    best_streak: int = Field(default=0)

class Game(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    difficulty: str
    rows: int
    cols: int
    mine_count: int
    status: str = Field(default="active")

    mines: str = Field(default="[]")
    open: str = Field(default="[]")
    flags: str = Field(default="[]")
    mover_index: str = Field(default="[]")

    first_click: bool = Field(default=False)
    start_time: float | None = Field(default=None)
    end_time: float | None = Field(default=None)


class BestTime(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    difficulty: str
    time_seconds: float

def create_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session