// loader
    let visible = document.querySelector('.loaders')
    window.addEventListener('load',flash)
    function flash(){
        setTimeout(() => {
            visible.classList.add('disappear')
        }, 2000)
    }
// loader