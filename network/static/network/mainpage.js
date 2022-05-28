hollowHeart = '<svg style="pointer-events: none;" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-heart" viewBox="0 0 16 16"><path d="m8 2.748-.717-.737C5.6.281 2.514.878 1.4 3.053c-.523 1.023-.641 2.5.314 4.385.92 1.815 2.834 3.989 6.286 6.357 3.452-2.368 5.365-4.542 6.286-6.357.955-1.886.838-3.362.314-4.385C13.486.878 10.4.28 8.717 2.01L8 2.748zM8 15C-7.333 4.868 3.279-3.04 7.824 1.143c.06.055.119.112.176.171a3.12 3.12 0 0 1 .176-.17C12.72-3.042 23.333 4.867 8 15z"/></svg>'

fullHeart = '<svg style="color: red; pointer-events: none;" xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-heart-fill" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314z"/></svg>'

function toggleLike(likeButton){
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

//Variable which is used to check if an edit area is currently open
editOpen = null

function openEdit(id){
    // If an edit textarea is already open, close it
    if (editOpen != null){
        closeEdit(editOpen)
    }
    editContainer = document.querySelector(`#editContainer-${id}`)
    children = editContainer.children
    formElements = children.editForm.children
    children.editLabel.style.display = "none"
    formElements.editArea.style.display = "block"
    formElements.editSave.style.display = "block"
    document.querySelector(`#postDescription-${id}`).style.display = "none"
    editOpen = id
}

function closeEdit(id){
    editContainer = document.querySelector(`#editContainer-${id}`)
    children = editContainer.children
    formElements = children.editForm.children
    children.editLabel.style.display = "block"
    formElements.editArea.style.display = "none"
    formElements.editSave.style.display = "none"
    document.querySelector(`#postDescription-${editOpen}`).style.display = "block"
    editOpen = null
}

function editPost(editForm, post_id){
    event.preventDefault()
    fetch(`posts/edit/${post_id}`,{
        "method": 'PUT',
        "body": JSON.stringify({
            "post_id": post_id,
            "new_desc": editForm.editArea.value
        })
    })
    document.querySelector(`#postDescription-${post_id}`).innerHTML = editForm.editArea.value
    closeEdit(post_id)
}

function CreateNewComment(NewCommentForm, post_id){
    event.preventDefault()
    comment = document.getElementById(`NewComment-${post_id}`)
    fetch(`posts/createcomment/${post_id}`,{
        "method": 'POST',
        "body": JSON.stringify({
            "post_id": post_id,
            "comment": comment.value
        })
    })
    comment.value=""
}

function CreateUserList(header, data){
    title = document.getElementById('modal-title')
    title.innerHTML = header
    
    body = document.getElementById('modal-body')
    body.innerHTML = ''


    data.forEach(user => {
            container = document.createElement('div')
            container.className = 'mb-3 post-block'

            UserImage = document.createElement('a')
            UserImage.setAttribute('href', `u/${user.id}`);

            var img = document.createElement('img');
            img.className = 'author-img modal-image'
            img.src = `${user.profilePicture}`;
            img.setAttribute('draggable', false)

            UserImage.appendChild(img)

            UserDetailsContainer = document.createElement('div')

            UserName = document.createElement('a')
            UserName.setAttribute('href', `u/${user.id}`);
            UserName.className = 'mb-0 text-dark'
            UserName.innerHTML = `${user.username}`

            UserDetailsContainer.appendChild(UserName)

            container.appendChild(UserImage)
            container.appendChild(UserName)
            body.appendChild(container)
        }
    )
}

function GetMutual(ToUserID){
    fetch(`u/${ToUserID}/Mutual`,{
        "method": 'GET'
    })
    .then(response => response.json())
    .then(data => {
        CreateUserList("Followers", data)
    })
}

function GetLikes(PostID){
    fetch(`posts/likes/${PostID}`,{
        "method": 'GET'
    })
    .then(response => response.json())
    .then(data => {
        CreateUserList("Likes", data)
    })
}