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
    document.querySelector('#complete-modal').className = "modal-dialog modal-dialog-centered modal-sm"

    title = document.getElementById('modal-title')
    title.innerHTML = header
    
    body = document.getElementById('modal-body')
    body.style.height = "auto"
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
            
            if(header == "Comments"){
                document.querySelector('#complete-modal').className = "modal-dialog modal-dialog-centered modal-lg"

                Timestamp = document.createElement('small')
                Timestamp.innerHTML = `${user.created}`
                Timestamp.className = 'text-muted'
                UserDetailsContainer.appendChild(Timestamp)

                Description = document.createElement('p')
                Description.innerHTML = `${user.description}`
                Description.className = 'mb-0 text-dark'
                UserDetailsContainer.appendChild(Description)
            }
            
            container.appendChild(UserImage)
            container.appendChild(UserDetailsContainer)
            body.appendChild(container)
        }
    )
}

function GetMutual(ToUserID){
    fetch(`${ToUserID}/Mutual`,{
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

function GetComments(PostID){
    fetch(`posts/comments/${PostID}`,{
        "method": 'GET'
    })
    .then(response => response.json())
    .then(data => {
        CreateUserList("Comments", data)
    })
}

function GetFollowers(ToUserID){
    fetch(`${ToUserID}/Followers`,{
        "method": 'GET'
    })
    .then(response => response.json())
    .then(data => {
        CreateUserList("Followers", data)
    })
}

function GetFollowing(ToUserID){
    fetch(`${ToUserID}/Following`,{
        "method": 'GET'
    })
    .then(response => response.json())
    .then(data => {
        CreateUserList("Following", data)
    })
}

function CreateForm(header){
    document.querySelector('#complete-modal').className = "modal-dialog modal-dialog-centered modal"

    title = document.getElementById('modal-title')
    title.innerHTML = header
    
    body = document.getElementById('modal-body')
    body.style.height = "400px"

    body.innerHTML = ''

    container = document.createElement('div')
    container.className = ''
    container.style.height = "100%"

    form = document.createElement("form");
    form.setAttribute('onsubmit','CreateNewPost(this)');
    form.setAttribute('enctype', 'multipart/form-data')
    // form.method = 'POST'
    // form.action = 'createPost'

    label = document.createElement('label')
    label.for = 'formFile'
    label.className = 'form-label'
    label.innerHTML = "Upload"
    label.style.cssText = "border: 1px solid #ccc;display: inline-block;padding: 6px 12px; cursor: pointer;"

    upload = document.createElement('input');
    upload.id = 'formFile'
    upload.setAttribute('type','file');
    upload.name = 'image'
    upload.className = 'form-control'
    upload.id = 'new-post-image'

    label.appendChild(upload)
    
    image = document.createElement('img')
    
    description = document.createElement('input')
    description.placeholder = 'Describe your new post'
    description.className = 'form-control'
    description.id = 'new-post-description'
    
    button = document.createElement('button')
    button.className = 'btn btn-primary'
    button.innerHTML = 'Create new post'
    button.setAttribute('type', 'submit')

    form.appendChild(label)
    form.appendChild(description)
    form.appendChild(button)
    container.appendChild(form)
    body.appendChild(container)
}

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