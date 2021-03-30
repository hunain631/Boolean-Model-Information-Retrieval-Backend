import bmr
import json
from operator import eq

precedence = {'or': 1, 'and': 2, 'not': 3 }

def hello_world():
    return json.dumps(bmr.i_index)

def findWord(word):
    try:
        return set(bmr.i_index[word])
    except:
        print('"%s" is not a key in the dictionary' % word)
        return set()

def checkPrecedence(stack, q):
    try:
        if precedence[q] <= precedence[stack[-1]]:
            return True
        else:
            return False
    except KeyError: 
        return False

def infixToPostfix(query):
    op = []
    post = []
    # convert infix to post fix
    for q in query:
        if q not in precedence.keys():   # not operator then appent term
            post.append(q)
        else:
            while op and checkPrecedence(op, q):
                post.append(op.pop())
            op.append(q)
    while op:
        post.append(op.pop())
    
    return post

def BooleanQuery(query):
    query = bmr.removePunctuation(query.lower()).split()
    query = [bmr.ps.stem(word) for word in query]

    if len(query) == 1:
        print("normal case", query)
        result = findWord(query[0])
        if result:
            print(list(result))
            return json.dumps(list(result), indent=4)
        else:
            print("No document found!")
            return ("No document found!")

    post = infixToPostfix(query)
    output = []
    print("complex case", query)
    for p in post:
        if p not in precedence.keys():
            output.append(findWord(p))
        elif precedence[p] == 3:
            output.append(set(bmr.docid) - output.pop())
        elif precedence[p] == 2:
            a = output.pop()
            output.append(a.intersection(output.pop()))
        elif precedence[p] == 1:
            a = output.pop()
            output.append(a.union(output.pop()))
    
    if output:
        print(sorted(list(output[0]), key=int))
        return json.dumps({"result": list(output[0]), "error": ""}, indent=4)
    else:
        return json.dumps({"result": [], "error": "No document found!"})

# 0 = term, 1=or, 2=and, 3=not
def isValidQuery(test):
    position = [(1,2), (2,1), (3,1), (3,2), (0, 3)]
    # adjecent values should not be euqal or same eg1. "term term" not allowed eg2. "and and" not allowed
    if any(map(eq, test, test[1:])):
        return False
    # query shouldn't start with these two word "and" "or" and shouldn't end with operator
    elif (test[0] == 1 or test[0] == 2) or (test[-1] == 1 or test[-1] == 2 or test[-1] == 3):
        return False
    # and or shouldn't be adjecent in any order 2nd "and, or" shouldn't come after "not"
    # 3rd "not" shouldn't come after term
    elif any(item in position for item in zip(test, test[1:])):
        return False
    else:
        return True


def queryType(query):
    if '/' in query:
        return ("proximity query")
    else:
        query = query.replace("-", " and ").replace("—", " and ")
        test = [precedence.get(x, 0) for x in query.split()]
        if isValidQuery(test):
            return BooleanQuery(query)
        else:
            return json.dumps({"result": [], "error": "Query is Invalid"})


# TODO remove stopwords from query
def SimpleQuery(query):
    query = bmr.removePunctuation(query.lower()).split()
    query = [bmr.ps.stem(word) for word in query]
    print(query)
    result = set()
    # for queries containing only OR operator also run for one word queries
    if ('and' not in query) and ('not' not in query):
        print("or query run")
        query = [x for x in query if x != 'or']
        for word in query:
            s1 = findWord(word)
            if s1:
                result = result.union(s1)

    elif ('or' not in query) and ('not' not in query):   # for queries containing only AND operator
        print("and query run")
        query = [x for x in query if x != 'and']
        for i, word in enumerate(query):
            if i == 0:
                result = findWord(word)
                continue
            s1 = findWord(word)
            result = result.intersection(s1)

    elif ('or' not in query) and ('and' not in query) and ('not' == query[0]):
        print("not query run")
        s1 = findWord(query[1])
        result = set(bmr.docid) - s1

    if result:
        return json.dumps(sorted(list(result), key=int), indent=4)
    else:
        return ("No document found!")
