import networkx as nx
import matplotlib.pyplot as plt
from network.serializers.serializer import UserSerializer
from .api_views import GetDegreeData, GetMutualFollowers
from .models import User

# Recommender function to generate scores for each candidate
# and return a sorted list
def Recommend(fromUser):
    # Get all candidates and first order nieghbours
    Candidates = GenerateCandidates(fromUser)
    FirstOrderFollowing, AllEdges = GetDegreeData(fromUser)

    # Generate scores for each recommendation criteria
    history = RankSearchHistory(fromUser)
    influence = RankInfluence(fromUser, Candidates, FirstOrderFollowing, AllEdges)
    likes = RankCommonLikes(fromUser, Candidates)
    mutual = RankMutualFollowers(Candidates, FirstOrderFollowing, AllEdges)
    ReccomendList = {}

    # Combine all scores for each candidate
    for user in Candidates:
        score = 0
        score = influence[user] + likes[user] + mutual[user]

        # Add a score for candidates in the user search history
        if user in history:
            score += 0.4
        print(user, influence[user], likes[user], mutual[user], score)
        user = User.objects.get(id=user)
        ReccomendList[user] = score
    
    ReccomendList = sorted(ReccomendList, key=ReccomendList.get, reverse=True)
    return ReccomendList[0:4]

# Add candidates who the main user searched for
def RankSearchHistory(fromUser):
    serializer = UserSerializer()
    history = serializer.get_history(fromUser)
    return history    

# Generate a score for each candidate based on influence
def RankInfluence(fromUser, SecondOrder, FirstOrderFollowing, AllEdges):
    SecondOrder = list(set(SecondOrder))
    RecommendList = {}
    for node in SecondOrder:
        candidate = User.objects.get(id=node)
        mutual = GetMutualFollowers(fromUser, candidate)
        RecommendList[node] = 0
        for user in mutual:
            RecommendList[node] += 1 / user.followingCount

    return RecommendList

# Generate a score for each candidate based on the number of posts
# where both the candidate and the main user have liked
def RankCommonLikes(fromUser, Candidates):
    RecommendList = {}
    serializer = UserSerializer()

    # Get posts which have been liked by the main user
    likes = set(serializer.get_likes(fromUser))
    for user in Candidates:
        # Get posts which have been liked by the candidate
        clikes = set(serializer.get_likes(User.objects.get(id=user)))

        # Calculate jaccard index for posts liked by both candiadate and main user
        try:
            jaccard_index = len(likes & clikes) / len(likes | clikes)
        except:
            jaccard_index = 0

        RecommendList[user] = jaccard_index
    return RecommendList


# Generate a score for each candidate based on mutual followers only
def RankMutualFollowers(Candidates, FirstOrderFollowing, AllEdges):
    
    # Generate a digraph
    G = nx.DiGraph()
    G.add_nodes_from(FirstOrderFollowing)
    G.add_nodes_from(Candidates)
    G.add_edges_from(AllEdges)
    nx.draw(G, with_labels=True)
    # plt.show()

    RecommendList = {}
    for node in Candidates:
        RecommendList[node] = G.in_degree(node) * 0.6

    return RecommendList

# Generate candidates which are second order neighbours and not yet
# followed by the user
def GenerateCandidates(fromUser):
    serializer = UserSerializer()
    FirstOrderFollowing, AllEdges = GetDegreeData(fromUser)
    SecondOrder = []

    # Get first order neighbours
    for user_id in FirstOrderFollowing:
        FollowUser = User.objects.get(id=user_id)

        # Get second order neighbours
        for seconduser in serializer.get_following(FollowUser):
            if seconduser not in FirstOrderFollowing and seconduser != fromUser.id:
                SecondOrder.append(seconduser)

    SecondOrder = list(set(SecondOrder))
    return SecondOrder