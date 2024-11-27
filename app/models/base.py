from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from app.models.role import Role
from app.models.user import User
from app.models.customer import Customer
from app.models.offer import Offer