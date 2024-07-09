// Get the buttons
let selectPlaylistButton = document.querySelector('.js-select-playlist-button');
let createNewButton = document.querySelector('.js-create-new-button');

// Get the manual div
let manualDiv = document.querySelector('.manual');
let defaultContent = manualDiv.innerHTML;

// Add event listeners to the buttons
selectPlaylistButton.addEventListener('click', function() {
    // Change the HTML inside the manual div when the select playlist button is clicked
    manualDiv.innerHTML = '<p>Enter your existing playlist name</p> <input type="text" placeholder="playlist name here"><div class="checkbox-container"><p class="checkbox-line">like songs as well:</p><input type="checkbox" class="checkbox"></div><button class="enter-button">Enter</button>';
});

createNewButton.addEventListener('click', function() {
    // Change the HTML inside the manual div when the create new playlist button is clicked
    manualDiv.innerHTML = defaultContent;
});
