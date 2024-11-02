from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

import PIL.Image
import base64

# Initialiser la base de données et créer une session
engine = create_engine('sqlite:///resources/images.db')
Session = sessionmaker(bind=engine)
session = Session()

# Définir la base de modèle
Base = declarative_base()

# Créer la table 'Images'
class Image(Base):
    __tablename__ = 'images'
    
    id = Column(Integer, primary_key=True)
    image_data = Column(Text, nullable=False)  # Champ pour stocker l'image en base64
    description = Column(String(255))  # Champ pour une chaîne de caractères descriptive

# Créer la table dans la base de données
Base.metadata.create_all(engine)

# Exemple d'ajout d'une entrée dans la table
def add_image(base64_image, description):
    new_image = Image(image_data=base64_image, description=description)
    session.add(new_image)
    session.commit()

def get_image(image_description):
    image = session.query(Image).filter_by(description=image_description).first()
    if image:
        return {"id": image.id, "image_data": image.image_data, "description": image.description}
    else:
        return None

# Exemple d'utilisation
if __name__ == "__main__":
    # Ajouter une image avec une description
    with open(r"resources/Images/n02096585-Boston_bull/n02096585_11836.jpg", "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    add_image(encoded_image, 'boston bull')
    print(get_image("boston bull"))