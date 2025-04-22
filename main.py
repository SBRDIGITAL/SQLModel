from typing import Optional, List

from fastapi import FastAPI, HTTPException, Depends

from sqlmodel import Field, SQLModel, Session, create_engine, select



class Hero(SQLModel, table=True):
    """
    ## Модель героя.

    Args:
        SQLModel (Type): Базовый класс для моделей SQL.
        table (bool): Указывает, что это таблица в базе данных. По умолчанию True.
    
    Attributes:
        id (Optional[int]): Уникальный идентификатор героя (автоинкрементное поле).
        name (str): Имя героя.
        age (Optional[int]): Возраст героя.
    """ 
    id: Optional[int] = Field(default=None, primary_key=True, alias='identificator')
    name: str
    age: Optional[int] = None


# Инициализация БД
engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)


def get_session():
    """
    ## Генератор сессий для работы с базой данных.

    Yields:
        Session: Объект сессии для работы с базой данных.
    """ 
    with Session(engine) as session:
        yield session


app = FastAPI(
    title="Hero API",
    description="API для управления героями",
    version="1.0.0",
    openapi_tags=[{
        "name": "Heroes",
        "description": "Операции с героями"
    }]
)


@app.post("/heroes/", response_model=Hero, tags=["Heroes"])
def create_hero(hero: Hero, session: Session = Depends(get_session)):
    """
    ## Создание нового героя.

    Args:
        hero (Hero): Объект героя, который нужно создать.
        session (Session, optional): Сессия для работы с базой данных. По умолчанию используется зависимость get_session.

    Returns:
        Hero: Созданный объект героя с автоинкрементным идентификатором.
    """   
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@app.get("/heroes/", response_model=List[Hero], tags=["Heroes"])
def read_heroes(
    name: Optional[str] = None,
    age: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """
    ## Получение списка героев с возможностью фильтрации по имени и возрасту.

    Args:
        name (Optional[str]): Имя героя для фильтрации. По умолчанию None.
        age (Optional[int]): Возраст героя для фильтрации. По умолчанию None.
        session (Session): Сессия для работы с базой данных. По умолчанию используется зависимость get_session.

    Returns:
        List[Hero]: Список героев, соответствующих критериям фильтрации.
    """ 
    query = select(Hero)
    
    if name:
        query = query.where(Hero.name == name)
    if age:
        query = query.where(Hero.age == age)
        
    heroes = session.exec(query).all()
    return heroes


@app.get("/heroes/{hero_id}", response_model=Hero, tags=["Heroes"])
def read_hero(hero_id: int, session: Session = Depends(get_session)):
    """
    ## Получение информации о герое по его идентификатору.

    Args:
        hero_id (int): Уникальный идентификатор героя.
        session (Session): Сессия для работы с базой данных.
            По умолчанию используется зависимость get_session.

    Raises:
        HTTPException: Если герой с указанным идентификатором не найден.

    Returns:
        Hero: Объект героя с указанным идентификатором.
    """  
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)