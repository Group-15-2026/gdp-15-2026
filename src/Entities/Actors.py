# Class representing a single Actor, holding all data collected throughout its processing

# XX Note to implementer: base this class heavily around the JSON formats for easy conversion between the two
class Actor:
    
    # Convert to a (JSON) string that the LLM will see 
    def __str__(self):
        return NotImplemented