// Create or delete a new like for a post
function toggleLike(likeButton){
    // Like the post
    if (likeButton.dataset.like == "true"){
        likeButton.dataset.like = false
        likeCount = document.getElementById(`likeCount-${likeButton.id}`)
        fetch(`/posts/toggleLike/${likeButton.id}`, {
            "method": "PUT",
            "body": JSON.stringify({
                "liked": likeButton.dataset.like
            })
        })
        likeCount.innerHTML = `${parseInt(likeCount.innerHTML)-1}`
        likeIcon = document.getElementById(`likeIcon-${likeButton.id}`)
        likeIcon.className = "fa-regular fa-heart fa-xl"
    }
    // Remove like from the post
    else if(likeButton.dataset.like == 'false'){
        likeButton.dataset.like = true
        likeCount = document.querySelector(`#likeCount-${likeButton.id}`)
        fetch(`/posts/toggleLike/${likeButton.id}`, {
            "method": "PUT",
            "body": JSON.stringify({
                "liked": likeButton.dataset.like
            })
        })
        likeCount.innerHTML = `${parseInt(likeCount.innerHTML)+1}`
        likeIcon = document.getElementById(`likeIcon-${likeButton.id}`)
        likeIcon.className = "fa-solid fa-heart fa-beat fa-xl"
        likeIcon.style.cssText = "--fa-animation-iteration-count: 1; --fa-animation-duration: 0.4s; color: red"
    }
}

// Create or delete a new following for a user
function toggleFollow(followButton, user_id){
    fetch(`/u/${user_id}/toggleFollow`, {
        "method": "PUT",
        "body": JSON.stringify({
            "follow": followButton.dataset.follow
        })
    })
    follow = followButton.dataset.follow
    followers = document.querySelector('#followers')
    followButton.innerHTML = (follow == 'true') ? "Follow" : "Unfollow"
    followButton.dataset.follow = (follow == 'true') ? false : true

    if(follow == 'true'){
        followers.innerHTML = (`${parseInt(followers.innerHTML)-1}`)
    }

    else if(follow == 'false'){
        followers.innerHTML = (`${parseInt(followers.innerHTML)+1}`)
    }
}

// Create a new comment on a post
function CreateNewComment(NewCommentForm, post_id){
    event.preventDefault()
    comment = document.getElementById(`NewComment-${post_id}`)
    fetch(`/posts/createcomment/${post_id}`,{
        "method": 'POST',
        "body": JSON.stringify({
            "post_id": post_id,
            "comment": comment.value
        })
    })
    comment.value=""
}

// Get a list of mutual followers between main user and the touser
function GetMutual(ToUserID){
    fetch(`/u/${ToUserID}/Mutual`,{
        "method": 'GET'
    })
    .then(response => response.json())
    .then(data => {
        CreateUserList("Followers", data)
    })
}

// Get all users who have liked a post
function GetLikes(PostID){
    fetch(`http://localhost:8000/posts/likes/${PostID}`,{
        "method": 'GET'
    })
    .then(response => response.json())
    .then(data => {
        CreateUserList("Likes", data)
    })
}

// Get all comments made on a post
function GetComments(PostID){
    fetch(`http://localhost:8000/posts/comments/${PostID}`,{
        "method": 'GET'
    })
    .then(response => response.json())
    .then(data => {
        CreateUserList("Comments", data)
    })
}

// Get all followers of a user
function GetFollowers(ToUserID){
    fetch(`${ToUserID}/Followers`,{
        "method": 'GET'
    })
    .then(response => response.json())
    .then(data => {
        CreateUserList("Followers", data)
    })
}

// Get all following of a user
function GetFollowing(ToUserID){
    fetch(`${ToUserID}/Following`,{
        "method": 'GET'
    })
    .then(response => response.json())
    .then(data => {
        CreateUserList("Following", data)
    })
}

// Create new post
function CreateNewPost(form){
    event.preventDefault()
    input = document.getElementById('new-post-image')
    image = input.files[0];
    description = document.getElementById('new-post-description').value

    const formData = new FormData()
    formData.append('image', input.files[0])
    formData.append('description', description)

    fetch('createPost',{
        "method": 'POST',
        "body": formData
    })
}

// Get a list of users based on search query
function SearchUser(){
    event.preventDefault()
    query = document.querySelector('#search-bar').value
    fetch(`searchuser/${query}`,{
        "method": 'GET'
    })
    .then(response => response.json())
    .then(data => {
        CreateUserList("Search", data)
    })
}