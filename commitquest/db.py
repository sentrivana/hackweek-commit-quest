from sqlmodel import Session, SQLModel, create_engine


engine = create_engine("sqlite:///commitquest.db")


def init_db():
    SQLModel.metadata.create_all(engine)
