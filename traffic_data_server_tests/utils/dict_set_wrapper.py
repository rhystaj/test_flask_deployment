'''
@summary: A hashable wrapper that wraps a dict, allowing it to be stored in a set and 
other hash-based data structures
'''
class DictSetWrapper:

    def __init__(self, wrappedDict):
        self.wrappedDict = wrappedDict


    def __hash__(self):
        
        result = 0
        for key in self.wrappedDict:
            result = result + hash(self.wrappedDict[key])
        
        return result

    
    def __eq__(self, other):
        return isinstance(other, DictSetWrapper) and \
            other.wrappedDict == self.wrappedDict


    def __str__(self):
        return str(self.wrappedDict)

    def __repr__(self):
        return str(self)


'''
@summary: create a set of wrapped dictionaries out of a list of dictionaries.
'''
def dictSet(dictList):
    return set([ DictSetWrapper(d) for d in dictList ])