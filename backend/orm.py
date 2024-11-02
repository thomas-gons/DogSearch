from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import *
import logging

from utils.config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the base model
Base = declarative_base()

# Define the 'Images' table
class Image(Base):
    __tablename__ = 'images'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    data = Column(String, nullable=False)
    embedding_index = Column(Integer, nullable=False, unique=True)

class ORM:
    def __init__(self) -> None:
        """Initialize the database and create a session."""
        # Initialize SQLite database engine
        engine = create_engine(config['database_uri'])
        
        # Create all tables if they do not exist
        Base.metadata.create_all(engine)
        logger.info("Database and tables initialized.")

        # Set up a session maker bound to the engine
        Session = sessionmaker(bind=engine)
        self.session = Session()
        logger.info("Session established for database operations.")

    def add_image(
            self,
            filename: str,
            base64_image: str,
            embedding_index: int,
            disable_logger_success=False) -> None:

        """Add a new image entry to the database."""
        # Create a new image entry
        new_image = Image(filename=filename, data=base64_image, embedding_index=embedding_index)
        
        # Add and commit the entry to the database
        try:
            self.session.add(new_image)
            self.session.commit()
            if not disable_logger_success:
                logger.info(f"New image added with embedding index: {embedding_index}")

        except Exception as e:
            logger.error(f"Error adding image to database: {e}")
            self.session.rollback()

    def get_image_by_index(self, embedding_index: int) -> dict:
        """Retrieve an image by its embedding index."""
        # Query for the image by embedding index
        image = self.session.query(Image).filter_by(embedding_index=int(embedding_index)).first()
        
        # Return image data if found, otherwise return an empty string
        if image:
            logger.info(f"Image retrieved for embedding index: {embedding_index}")
            return {"filename": image.filename, "data": image.data}
        else:
            logger.warning(f"No image found for embedding index: {embedding_index}")
            return {}

# Initialize the ORM instance for database operations
orm = ORM()
