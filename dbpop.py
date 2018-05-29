from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Book, Base, Category

engine = create_engine('sqlite:///bookcatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create Psychology category
category1 = Category(name="Psychology")

session.add(category1)
session.commit()

book1 = Book(title="Archetypes and the Collective Unconscious",
             author="Carl Gustav Jung",
             user_id="77",
             description="""Lorem ipsum dolor sit amet, consectetur adipiscing
                         elit, sed do eiusmod tempor incididunt ut labore et
                         dolore magna aliqua.""",
             category=category1)

session.add(book1)
session.commit()


book2 = Book(title="Maps of Meaning",
             author="Jordan B. Peterson",
             user_id="77",
             description="""Lorem ipsum dolor sit amet, consectetur adipiscing
                         elit, sed do eiusmod tempor incididunt ut labore et
                         dolore magna aliqua.""",
             category=category1)

session.add(book2)
session.commit()

book2 = Book(title="The Origins and History of Consciousness",
             author="Erich Neumann",
             user_id="77",
             description="""Lorem ipsum dolor sit amet, consectetur adipiscing
                         elit, sed do eiusmod tempor incididunt ut labore et
                         dolore magna aliqua.""",
             category=category1)

session.add(book2)
session.commit()

book3 = Book(title="Thinking Fast and Slow",
             author="Daniel Kahneman",
             user_id="77",
             description="""Lorem ipsum dolor sit amet, consectetur adipiscing
                         elit, sed do eiusmod tempor incididunt ut labore et
                         dolore magna aliqua.""",
             category=category1)

session.add(book3)
session.commit()


# Create Personal Development category
category1 = Category(name="Personal Development")

session.add(category1)
session.commit()


book1 = Book(title="Lying",
             author="Sam Harris",
             user_id="77",
             description="""Lorem ipsum dolor sit amet, consectetur adipiscing
                         elit, sed do eiusmod tempor incididunt ut labore et
                         dolore magna aliqua.""",
             category=category1)

session.add(book1)
session.commit()


book2 = Book(title="Discipline Equals Freedom",
             author="Jocko Willink",
             user_id="77",
             description="""Lorem ipsum dolor sit amet, consectetur adipiscing
                         elit, sed do eiusmod tempor incididunt ut labore et
                         dolore magna aliqua.""",
             category=category1)

session.add(book2)
session.commit()

book2 = Book(title="12 Rules for Life",
             author="Jordan B Peterson",
             user_id="77",
             description="""Lorem ipsum dolor sit amet, consectetur adipiscing
                         elit, sed do eiusmod tempor incididunt ut labore et
                         dolore magna aliqua.""",
             category=category1)

session.add(book2)
session.commit()

book3 = Book(title="Pitch Anything",
             author="Oren Klaff",
             user_id="77",
             description="""Lorem ipsum dolor sit amet, consectetur adipiscing
                         elit, sed do eiusmod tempor incididunt ut labore et
                         dolore magna aliqua.""",
             category=category1)

session.add(book3)
session.commit()


# Create Fiction category
category1 = Category(name="Fiction")

session.add(category1)
session.commit()

book1 = Book(title="1984",
             author="George Orwell",
             user_id="77",
             description="""Lorem ipsum dolor sit amet, consectetur adipiscing
                         elit, sed do eiusmod tempor incididunt ut labore et
                         dolore magna aliqua.""",
             category=category1)

session.add(book1)
session.commit()


book2 = Book(title="Faust",
             author="Johann Wolfgang von Goethe",
             user_id="77",
             description="""Lorem ipsum dolor sit amet, consectetur adipiscing
                         elit, sed do eiusmod tempor incididunt ut labore et
                         dolore magna aliqua.""",
             category=category1)

session.add(book2)
session.commit()

book2 = Book(title="Fire Season",
             author="Philip Connors",
             user_id="77",
             description="""Lorem ipsum dolor sit amet, consectetur adipiscing
                         elit, sed do eiusmod tempor incididunt ut labore et
                         dolore magna aliqua.""",
             category=category1)

session.add(book2)
session.commit()

book3 = Book(title="God's Debris",
             author="Scott Raymond Adams",
             user_id="77",
             description="""Lorem ipsum dolor sit amet, consectetur adipiscing
                         elit, sed do eiusmod tempor incididunt ut labore et
                         dolore magna aliqua.""",
             category=category1)

session.add(book3)
session.commit()


print "DB has been updated yo"
