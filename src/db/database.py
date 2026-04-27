from sqlmodel import SQLModel, create_engine, Session

engine = create_engine("sqlite:///database.db", echo=True)

SQLModel.metadata.create_all(engine)

# might not be necessary
def get_session():
    with Session(engine) as session:
        yield session
