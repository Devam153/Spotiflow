document.addEventListener("DOMContentLoaded", function() {
    const inputfile = document.getElementById("input-file");
    const imgview = document.getElementById("img-view");
    const uploadButton = document.getElementById("upload-button");

    uploadButton.addEventListener("click", function(e) {
        e.stopPropagation(); // Prevents the event from bubbling up the DOM tree
        inputfile.click();
    });

    inputfile.addEventListener("change", function() {
        uploadImage();
    });

    imgview.addEventListener("dragover", function(e) {
        e.preventDefault();
    });

    imgview.addEventListener("drop", function(e) {
        e.preventDefault();
        inputfile.files = e.dataTransfer.files;
        uploadImage();
    });

    function uploadImage() {
        let imgLink = URL.createObjectURL(inputfile.files[0]);
        imgview.style.backgroundImage = `url(${imgLink})`;
        imgview.textContent = '';
        imgview.style.border = '0';
    }
});
