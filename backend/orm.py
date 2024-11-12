from typing import List

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import exists

from backend import config, logger
from utils.misc import singleton

# Define the base model for SQLAlchemy
Base = declarative_base()


# ------ Define tables here ------

class Image(Base):
    """
    Define the Image table in the database.
    """
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    data = Column(String, nullable=False)
    embedding_index = Column(Integer, nullable=False, unique=True)
    origin = Column(String, nullable=False)  # From user or from database


@singleton
class ORM:
    """
    ORM class to interact with the database using SQLAlchemy.
    """

    def __init__(self) -> None:
        """
        Initialize the database connection and create a session.

        Sets up the SQLite engine, creates the tables if not already created,
        and establishes a session for database operations.
        """
        # Initialize SQLite database engine
        engine = create_engine(config['database_uri'])

        # Create all tables if they do not exist
        Base.metadata.create_all(engine)
        logger.info("Database and tables initialized.")

        # Set up a session maker bound to the engine
        session = sessionmaker(bind=engine)
        self.session = session()
        logger.info("Session established for database operations.")

    def add_image(
            self,
            filename: str,
            base64_image: str,
            embedding_index: int,
            origin: str,
            disable_logger_success=False) -> None:
        """
        Add a new image entry to the database.

        Args:
            filename (str): The name of the image file.
            base64_image (str): The base64-encoded image data.
            embedding_index (int): The embedding index of the image.
            origin (str): The origin of the image (either 'user' or 'database').
            disable_logger_success (bool, optional): If True, disables success logging.

        Raises:
            Exception: Rolls back transaction if there is an error during commit.
        """
        # Create a new image entry
        new_image = Image(filename=filename, data=base64_image, embedding_index=embedding_index, origin=origin)

        # Add and commit the entry to the database
        try:
            self.session.add(new_image)
            self.session.commit()
            if not disable_logger_success:
                logger.info(f"New image ({filename}) added with embedding index: {embedding_index}")

        except Exception as e:
            logger.error(f"Error adding image to database: {e}")
            self.session.rollback()

    def add_images_bulk(
            self,
            images_data: List,
    ) -> None:
        images = [Image(filename=filename, data=base64_image, embedding_index=embedding_index, origin=origin)
                  for filename, base64_image, embedding_index, origin in images_data]

        self.session.add_all(images)
        self.session.commit()
        logger.info(f"Inserted {len(images)} images into the database.")

    def get_image_by_index(self, embedding_index: int) -> dict:
        """
        Retrieve an image from the database by its embedding index.

        Args:
            embedding_index (int): The embedding index of the image.

        Returns:
            dict: The image's filename and base64-encoded data, or an empty dictionary if not found.
        """
        # Query for the image by embedding index
        image = self.session.query(Image).filter_by(embedding_index=int(embedding_index)).first()

        # Return image data if found, otherwise return an empty dictionary
        if image:
            logger.info(f"Image retrieved for embedding index: {embedding_index}")
            return {"filename": image.filename, "data": image.data}
        else:
            logger.warning(f"No image found for embedding index: {embedding_index}")
            return {}

    def purge_user_data(self):
        """
        Purge all images uploaded by users from the database and FAISS index.

        Returns:
            list: A list of embedding indexes of the images that were purged.
        """
        # Retrieve all user images from the database
        user_images = self.session.query(Image).filter(Image.origin == 'user').all()

        # Get the embedding indexes of the user images
        embedding_indexes = [image.embedding_index for image in user_images]

        # Delete user images from the database
        self.session.query(Image).filter(Image.origin == 'user').delete()
        self.session.commit()

        logger.info(f"Purged {len(user_images)} user images from the database.")
        return embedding_indexes

    def is_sample_db_built(self):
        return self.session.query(exists().where(Image.origin == 'database')).scalar()

# Instantiate ORM object
orm = ORM()
