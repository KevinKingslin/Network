import networkx as nx
import matplotlib.pyplot as plt
from network.serializers.serializer import UserSerializer, LikeSerializer
from .models import User

def GetDegreeData(fromUser):
    serializer = UserSerializer()
    AllEdges = []
    FirstOrderFollowing = serializer.get_following(fromUser)

    for user_id in FirstOrderFollowing:
        FollowUser = User.objects.get(id=user_id)
        AllEdges.append((fromUser.id, user_id))

        for seconduser in serializer.get_following(FollowUser):
            # Prevent fromUser from being added as edge
            if seconduser != fromUser.id:
                AllEdges.append((FollowUser.id, seconduser))
    return FirstOrderFollowing, AllEdges

def Recommend(fromUser):
    Candidates = GenerateCandidates(fromUser)
    FirstOrderFollowing, AllEdges = GetDegreeData(fromUser)


    history = RankSearchHistory(fromUser)
    influence = RankInfluence(Candidates, FirstOrderFollowing, AllEdges)
    likes = RankCommonLikes(fromUser, Candidates)
    mutual = RankMutualFollowers(Candidates, FirstOrderFollowing, AllEdges)
    ReccomendList = {}

    for user in Candidates:
        score = 0
        score = influence[user] + likes[user] + mutual[user]
        if user in history:
            score += 0.4
        user = User.objects.get(id=user)
        ReccomendList[user] = score
    
    ReccomendList = sorted(ReccomendList, key=ReccomendList.get, reverse=True)
    return ReccomendList[0:4]

    #weights = {"mutual-friends": 1, "history": 0.5, "influence": 0.75, "commonlikes": 0.8}


def RankSearchHistory(fromUser):
    serializer = UserSerializer()
    history = serializer.get_history(fromUser)
    return history    

def RankInfluence(SecondOrder, FirstOrderFollowing, AllEdges):
    G = nx.DiGraph()
    G.add_nodes_from(FirstOrderFollowing)
    G.add_nodes_from(SecondOrder)
    G.add_edges_from(AllEdges)
    nx.draw(G, with_labels=True)

    SecondOrder = list(set(SecondOrder))
    RecommendList = {}
    for node in SecondOrder:
        user = User.objects.get(id=node)
        RecommendList[node] = G.in_degree(node) / user.followingCount

    return RecommendList

def RankCommonLikes(fromUser, Candidates):
    RecommendList = {}
    serializer = UserSerializer()
    likes = set(serializer.get_likes(fromUser))
    for user in Candidates:
        clikes = set(serializer.get_likes(User.objects.get(id=user)))

        jaccard_index = len(likes & clikes) / len(likes | clikes)
        RecommendList[user] = jaccard_index
    return RecommendList


def RankMutualFollowers(Candidates, FirstOrderFollowing, AllEdges):
    """ Rank users based on mutual followers only """
    
    G = nx.DiGraph()
    G.add_nodes_from(FirstOrderFollowing)
    G.add_nodes_from(Candidates)
    G.add_edges_from(AllEdges)
    nx.draw(G, with_labels=True)

    RecommendList = {}
    for node in Candidates:
        RecommendList[node] = G.in_degree(node)

    return RecommendList


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