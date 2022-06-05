// Form for create new post using DOM manipulation
function CreateForm(header){
    document.querySelector('#complete-modal').className = "modal-dialog modal-dialog-centered modal"

    title = document.getElementById('modal-title')
    title.innerHTML = header
    
    body = document.getElementById('modal-body')
    body.style.height = "400px"

    body.innerHTML = ''
    
    // Container for form
    container = document.createElement('div')
    container.className = ''
    container.style.height = "100%"

    // Form to create new post
    form = document.createElement("form");
    form.setAttribute('onsubmit','CreateNewPost(this)');
    form.setAttribute('enctype', 'multipart/form-data')

    // Label for upload image
    label = document.createElement('label')
    label.for = 'formFile'
    label.className = 'form-label'
    label.innerHTML = "Upload"
    label.style.cssText = "border: 1px solid #ccc;display: inline-block;padding: 6px 12px; cursor: pointer;"

    // Image upload input field
    upload = document.createElement('input');
    upload.id = 'formFile'
    upload.setAttribute('type','file');
    upload.name = 'image'
    upload.className = 'form-control'
    upload.id = 'new-post-image'
    
    label.appendChild(upload)
    
    // Input field for post description
    description = document.createElement('input')
    description.placeholder = 'Describe your new post'
    description.className = 'form-control'
    description.id = 'new-post-description'
    
    // Submit form button
    button = document.createElement('button')
    button.className = 'btn btn-primary'
    button.innerHTML = 'Create new post'
    button.setAttribute('type', 'submit')

    // Append all containers
    form.appendChild(label)
    form.appendChild(description)
    form.appendChild(button)
    container.appendChild(form)
    body.appendChild(container)
}

// Add users to modal by DOM manipulation
function CreateUserList(header, data){
    document.querySelector('#complete-modal').className = "modal-dialog modal-dialog-centered modal-sm"

    title = document.getElementById('modal-title')
    title.innerHTML = header
    
    body = document.getElementById('modal-body')
    body.style.height = "auto"
    body.innerHTML = ''

    // For each user, generate content
    data.forEach(user => {
        // Container for each user
        container = document.createElement('div')
        container.className = 'mb-3 post-block'

        // User image container
        ImageLink = document.createElement('a')
        ImageLink.setAttribute('href', `u/${user.id}`);

        // User image
        var UserImage = document.createElement('img');
        UserImage.className = 'author-img modal-image'
        UserImage.src = `${user.profilePicture}`;
        UserImage.setAttribute('draggable', false)

        ImageLink.appendChild(UserImage)

        // Container for user details
        UserDetailsContainer = document.createElement('div')

        // Username
        UserName = document.createElement('a')
        UserName.setAttribute('href', `u/${user.id}`);
        UserName.className = 'mb-0 text-dark'
        UserName.innerHTML = `${user.username}`
        
        UserDetailsContainer.appendChild(UserName)
        
        // Special case for comments (Comments need description)
        if(header == "Comments"){
            document.querySelector('#complete-modal').className = "modal-dialog modal-dialog-centered modal-lg"

            // Comment timestamp
            Timestamp = document.createElement('small')
            Timestamp.innerHTML = `${user.created}`
            Timestamp.className = 'text-muted'
            UserDetailsContainer.appendChild(Timestamp)

            // Comment description
            Description = document.createElement('p')
            Description.innerHTML = `${user.description}`
            Description.className = 'mb-0 text-dark'
            UserDetailsContainer.appendChild(Description)
        }
        
        // Append all containers
        container.appendChild(ImageLink)
        container.appendChild(UserDetailsContainer)
        body.appendChild(container)
    })
}