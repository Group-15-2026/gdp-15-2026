from pydantic import BaseModel

# XX Note to the implementer: pydantic is used to allow use of objects in mcp tools
# should build this class heavily around the json inter-stage standards we have defined

class Article(BaseModel):
    pass