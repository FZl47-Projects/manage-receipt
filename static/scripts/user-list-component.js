let users_select_component = document.getElementById('users-select')

function initUserSelect() {
    let users_select = document.querySelectorAll('.user-select')

    for (let user_select of users_select) {
        user_select.addEventListener('click', function () {
            unSelectUsers()
            user_select.setAttribute('selected', 'true')
            input_select_user_component.value = user_select.getAttribute('user-id')
            try{
                input_select_user_component_name.innerText = user_select.querySelector('[full-name]').innerText
                input_select_user_component_name.setAttribute('label-content-seted','')
            }catch (e){}
            $('#container-users').modal('hide')
        })
    }

    function unSelectUsers() {
        input_select_user_component.value = null
        for (let user_select of users_select) {
            user_select.removeAttribute('selected')
        }
    }
}

initUserSelect()


let form_search_users_component = document.getElementById('form-search-users-component')
form_search_users_component.addEventListener('submit', function (e) {
    createLoading(users_select_component.parentElement)
    e.preventDefault()
    sendAjax({
        url: form_search_users_component.getAttribute('action'),
        data: {
            'search': form_search_users_component.querySelector('input[name="search"]').value
        },
        success: function (response) {
            response = JSON.parse(response)
            clearContentUsersSelect()
            for (let user of response) {
                createUserComponentElement(user)
            }
            initUserSelect()
            removeLoading(users_select_component.parentElement)
        }, error: function () {
            removeLoading(users_select_component.parentElement)
            createNotify({
                title:'مشکلی پیش امده است',
                theme:'error'
            })
        }
    })
})

function clearContentUsersSelect() {
    users_select_component.innerHTML = ''
}

function createUserComponentElement(user) {
    let user_el = `
        <div class="user-select detail-row" user-id="${user.pk}">
            <div class="col-4" full-name>
                ${user.fields.first_name} ${user.fields.last_name}
            </div>
            <div class="col-4">
                ${getRawPhonenumber(user.fields.phonenumber)}
            </div>
            <div class="col-4">
                ${truncate(user.fields.email, 15)}
            </div>
        </div>
    `
    users_select_component.innerHTML += user_el
}