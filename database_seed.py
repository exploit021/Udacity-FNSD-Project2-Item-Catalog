from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Add initial categories
if session.query(Category).count() == 0:
    categories = []
    categories.append(Category(name="Soccer", user_id="1"))
    categories.append(Category(name="Basketball", user_id="1"))
    categories.append(Category(name="Baseball", user_id="1"))
    categories.append(Category(name="Frisbee", user_id="1"))
    categories.append(Category(name="Snowboarding", user_id="1"))
    categories.append(Category(name="Rock Climbing", user_id="1"))
    categories.append(Category(name="Foosball", user_id="1"))
    categories.append(Category(name="Skating", user_id="1"))
    categories.append(Category(name="Hockey", user_id="1"))
    for category in categories:
        session.add(category)
    session.commit()


# Add initial items
if session.query(Item).count() == 0:
    items = []
    items.append(Item(name="Soccer ball", category_id=1, user_id="1", description="Soccer ball description"))
    items.append(Item(name="Net", category_id=1, user_id="1", description="Net description"))
    items.append(Item(name="Hoop", category_id=2, user_id="1", description="Hoop description"))
    items.append(Item(name="Ball", category_id=2, user_id="1", description="Ball description"))
    items.append(Item(name="Bat", category_id=3, user_id="1", description="Bat description"))
    items.append(Item(name="Ball", category_id=3, user_id="1", description="Ball description"))
    items.append(Item(name="Disc", category_id=4, user_id="1", description="Disc description"))
    items.append(Item(
        name="Snowboard", category_id=5, user_id="1",
        description="Best for any terrain and conditions. "
                    "All-mountain snowboard is "
                    "perform anywhare on a mountain-groomed runs, backcounty, "
                    "even park and pipe. They may be directional "
                    "(meaning downhill only) or twin-top "
                    "(for riding switch, meanint either direction). "
                    "Moast boarders ride all-mountain boards. "
                    "Because of their versability, all-mountain boards are "
                    "good for beginners who are "
                    "still learning what terrain they like."))
    items.append(Item(name="Goggle", category_id=5, user_id="1", description="Goggle description"))
    items.append(Item(name="Ropes", category_id=6, user_id="1", description="Ropes description"))
    items.append(Item(name="Table", category_id=7, user_id="1", description="Table description"))
    items.append(Item(name="Skates", category_id=8, user_id="1", description="Skates description"))
    items.append(Item(name="Gloves", category_id=8, user_id="1", description="Gloves description"))
    items.append(Item(name="Stick", category_id=9, user_id="1", description="Stick description"))
    items.append(Item(name="Puck", category_id=9, user_id="1", description="Puck description"))
    for item in items:
        session.add(item)
    session.commit()


# Add default user
if session.query(User).count() == 0:
    users = []
    users.append(User(
        name="Default User",
        email="defaultuser@defaultuser.com"))
    for user in users:
        session.add(user)
    session.commit()
