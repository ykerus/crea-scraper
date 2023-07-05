# import promttemplate from langchain
from langchain.prompts import PromptTemplate


def search_prompt_template() -> PromptTemplate:

    template = """
I have a database with course titles and descriptions in both English and Dutch.
For a given user query, I want to find the most interesting courses in the database for the user.
I need you to convert the user query to a set of keywords in both english and dutch that match the intent of the user.
These keywords can then be used to do similarity search over the database.

For example:
    - User query: I want to do something practical with my hands.
      houtbewerking, practical, pottery, electonics, sculptuur, ...
    - User query: I like to play jazz.
      jazz, muziek, instrument, band, not classical, not hip hop, jazzband, playing music, ...
    - User query: Ik wil een nieuwe taal leren. I kan al Nederlands en Engels.
      spreken, taal, Spaans, Frans, language, French, new language, niet Nederlands, not English ...
    - User query: I like to play a new instrument. I already play guitar.
      instrument, music, play, not guitar, piano, muziek maken, viool, drums, jammen, jamming, ...
      * note that the user already plays guitar and wants to learn something new, so guitar is negated.
    - Ik dans ballet, maar nu wil ik iets nieuws leren.
      dansen, not ballet, hip hop, salsa, geen ballet,...
    - User query: Ik wil iets sociaals doen, maar niet iets waar skill voor nodig is.
      social, sociaal, no skill, communicatie, praten, people, conversation, beginner, ...

Note:
    - The user query can be in either English or Dutch.
    - The keywords should be a mix of both English and Dutch (without indicating the language).
    - Keep the keywords concise, try to avoid uncommon composites, e.g. balletlessen.
    - The output should only be the keywords or phrases, separated by a comma, nothing more.
    - A keyword cannot be negated and not negated in the same output.
    - The frequency of similar keywords should be in line with the intent of the user.
    - If the user does NOT want something (could be explicit or implicit),
      then it should be negated either with not, no, niet, or geen.

Users query: {query}
"""

    return PromptTemplate(
        input_variables=["query"],
        template=template,
    )
