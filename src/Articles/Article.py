# Class representing a single news article, holding all data collected throughout its processing

# XX Note to implementer: base this class heavily around the JSON formats for easy conversion between the two
class Article:
    
    # Convert to a (JSON) string that the LLM will see 
    def __str__(self):
        return NotImplemented