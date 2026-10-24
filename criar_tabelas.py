from core.database import engine, Base
import models._all_models

def criar_tabelas() -> None:
    print("Criando as tabelas no banco de dados...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    criar_tabelas()