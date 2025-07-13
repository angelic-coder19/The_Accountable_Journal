document.addEventListener('DOMContentLoaded', async function(){

    // To convert the number format months into readable words 
    function getStringDate(month){
        switch(month){
            case 1:
                return 'January';
            case 2:
                return 'February';
            case 3:
                return 'March';
            case 4:
                return 'April';
            case 5:
                return 'May';
            case 6:
                return 'June';
            case 7:
                return 'July';
            case 8:
                return 'August';
            case 9:
                return 'September';
            case 10:
                return 'October';
            case 11:
                return 'November';
            case 12:
                return 'December';
        }
    }

    // Get the background color of an info card give the mood
    function getBGcolor(mood) {
        switch(mood){
            case 'Happy':
                return "#FFf200"; // light yellow
            case 'Sad':
                return "#5c6bc0";  // 
            case 'Angry':
                return "#f40a04"; // bright red 
            case 'Calm':
                return "#47ffeb";
            case 'Anxious':
                return "#ef8a8a";
            case 'Anxious':
                return "#ce83d8";
            case 'Confident':
                return "#0fb4FA";  
            case 'Meh':
                return "#858585"; // a dark gray
            case 'Hopeful':
                return "#ff6f02"; // orangeish 
            case 'Tired':
                return "#90a4ae"; // bluish grey
            case 'Grateful':
                return "#aeee23"  // olive green  
            case 'Lonely':
                return "#b39ddb"; // bluish-grey
            case 'Inspired':
                return "#f0e035"; // dark yeallow
            default:
                return "#ffffff"; // White 
        }
    }
    
    // Get the ordinal suffix (th, nd, rd ...)of the date 
    function ordinalIndicator(date) {
        let last_digit = date % 10;
        switch(last_digit){
            case 1:
                if (date == 11){
                    return 'th';
                }
                return 'st';
            case 2:
                if (date == 12){
                    return 'th';
                }
                return 'nd';
            case 3:
                if (date == 13){
                    return 'th';
                }
                return 'rd';
            default:
                return 'th';
        }
    }

    // To get back bytes ready for decryption from base64 
    function base64ToBytes(base64string) {
        let bytes = atob(base64string);
        let array = new Uint8Array(bytes.length);
        for (let i = 0; i < bytes.length; i++){
            array[i] = bytes.charCodeAt(i);
        }
        return array;
    } 

    // To convert bytes to base64 
    function bytesTobase64(buffer) {
        const bytes = new Uint8Array(buffer);
        let binaryString = '';
        for (let i = 0; i < bytes.length; i++){
            binaryString += String.fromCharCode(bytes[i]);
        }
        return btoa(binaryString);
    }
    async function decryptEntry(cipherEntry, iv){
        // Decrypt the encrypted message
        let encryptedBytes = base64ToBytes(cipherEntry);
        let ivBytes = base64ToBytes(iv);

        let decryptedBuffer = await crypto.subtle.decrypt(
            {
                name: "AES-GCM", 
                iv: ivBytes
            },
            cryptoKey,
            encryptedBytes
        ); 
        const plainText = new TextDecoder().decode(decryptedBuffer);
        return plainText;
    }

    async function renderEntries(entries, id) {
    try {
        // Find the body object from the DOM
        var body = document.querySelector(`${id}`); 

            // Iterate over each json object and collect info
            for (let entry of entries){
                let day = entry["day"];
                let month = entry["month"]; // Convert the integar date to human readalbe month
                let time = entry["time"];
                let year = entry["year"];
                let cipherEntry = entry["entry"]; // Base 64 string encrypted Entry 
                let iv = entry["iv"];             // Base 64 string initialization vector
                let mood = entry["mood"];

                // Get the plain text from decyrption function
                const plainText = await decryptEntry(cipherEntry, iv);
    
                // Dyanmically generate card to display a single entry and it's information
                body.innerHTML += `
                <div class="col-lg-3 col-sm-12 p-0 my-0.5">
                    <div class="infoCard" style="background-color: ${getBGcolor(mood)}">
                        <div class="row">
                            <div class="col text-start">
                                <p>${day + ordinalIndicator(day)} ${getStringDate(month)}, ${year}</p>
                            </div>
                            <div class="col text-end">
                                <p class="time">${time}</p>
                            </div>
                            </div>
                            <div class="row text-center entry">
                                <p>${plainText}</p>
                            </div>
                            <div class="row">
                            <div class="col text-start binIcon">
                                <img src="/static/icons/delete_icon.svg" class="deleteIcon"/>
                            </div>
                            <div class="col text-end">
                                <p>Feeling <b class="mood">${mood}</b></p>
                            </div>
                        </div>
                    </div>
                </div>
                `    
            }
        } catch (TypeError) {
            console.log("Everything is fine🙂");
        }
    }
    /* DO NOT DE - COMMENT THIS CODE!! THIS WAS A ONE TIME THING 
    // Generate a cryptographic key 
    const key = await crypto.subtle.generateKey(
        {name: "AES-GCM", length: 256}, // Algorithm
        true,                           // extractable
        ["encrypt", "decrypt"]          // list of k
    );

    // Export the key for use accross devices and sessions
    const keyBytes = await crypto.subtle.exportKey("raw", key);
    // Convert the key bytes to a base 64 string
    const base64Key = bytesTobase64(keyBytes);

    // Send this key One time to the server for storage
    fetch ("/search", {
        method: "POST",
        headers: {
            'content-type' : 'application/json',
        },
        body: JSON.stringify({
            key : base64Key
        })
    });
    */

    // Fetch the encryption key from the bakend as base64 string
    const keyresponse = await fetch("/key");
    let key = await keyresponse.json();
    
    key = base64ToBytes(key); // Convert the base64 key back to bytes 

    // Make the key ready for local decryption use
    const cryptoKey = await crypto.subtle.importKey(
        "raw",                  // format
        key,                    // Uint8Array key
        { name : "AES-GCM" },     // Algorithm
        true,                   // Extractable
        ["encrypt", "decrypt"]  // Key Uses 
    );
    try {                           
        var entry = '';
        let words = 1;

        // Get the entry from the text area and append it to the empty string
        document.querySelector('textarea').addEventListener('blur', function() {
            entry = document.querySelector('textarea').value;
            for (let i = 0; i < entry.length; i++){
                if (entry[i] == " ") {
                    words++;
                }
            }
        });
    } catch (TypeError) {
        console.log("Everything is fine🙂");
    }

    try {
        // Listen for the save button to be clicked to encrypt and send the entry to the server
        document.querySelector('#submit').addEventListener('click', async function() {
        // Find the mood value that was selected 
            try {
                mood = document.querySelector('input[name="mood"]:checked').value;
                
                // Check if the entry is empty
                if (!String(entry).trim() || !mood){
                    alert("Please make an entry and select a mood");
                    return;
                }
            } catch (TypeError) {
                alert("Select a mood");
            }   
            
            // Encode the entry into bytes
            const bytes = new TextEncoder().encode(entry);

            // Generate a random initialization vector(iv)
            const IV = crypto.getRandomValues(new Uint8Array(12));

            // Ecrypt the entry to get back an arraybuffer 
            let encryptedEntry = await crypto.subtle.encrypt(
                { name: "AES-GCM", iv: IV }, // Algorithim and Initialisation vector 
                cryptoKey,                   // crypto key (imported)
                bytes                        // Array buffer of entry
            );
            
            // Convert the encryptedEntry and iv to Base64
            const base64string = bytesTobase64(encryptedEntry);
            const base64IV = bytesTobase64(IV);
            console.log(base64string)

            // Send the ecrypted entry, iv and mood to the database on the server    
            const response = await fetch('/make_entry', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    entry : base64string,
                    iv : base64IV,
                    mood : mood })
            });

            // Await a response from the front end to redirect
            const result = await response.json();
            if (result.status === "success"){
                window.location.href = result.redirect;
            }
        });
    } catch (TypeError) {
        console.log("Everything is fine🙂")
    }
     /*
        // Get the contents of the from and convert them into a json object 
        document.querySelector('#searchForm').addEventListener('submit', async function(event){
            // Prevent the default form from bing sent
            event.preventDefault();

            const form = event.target;
            const formData = new FormData(form);
            const json = Object.fromEntries(formData.entries());

            console.log(json);
            // Send this from data to the search route via POST
            const response = await fetch ("/results", {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(json)
            });

            const results = response.json();
            console.log(results);
        }); */
    // Get the search results
    const searchResponse = await fetch("/results");
    const results = await searchResponse.json();
    
    if (results.length > 0) {
        renderEntries(results, '#searchResults');
    } 
            // Request for information from the server for decryption
        let response = await fetch("/info");
        let entries = await response.json(); // Get a list of json objects from each entry

        const body = document.getElementById("mainBody");

    try {
        // Show placeholders 
        for (let j = 0; j <  4; j++) {
            body.innerHTML += `
            <div class="col-lg-3 col-sm-12 p-0 my-0.5 placeholder-card">
            <div class="card placeholder-glow p-2 m-1" style="outline: none">
                <div class="row">
                <div class="col text-start">
                    <p class="placeholder col-6"></p>
                </div>
                <div class="col text-end">
                    <p class="placeholder col-4"></p>
                </div>
                </div>
                <div class="row text-center entry">
                    <p class="placeholder-text">
                        <span class="placeholder col-2"></span>
                        <span class="placeholder col-4"></span>
                        <span class="placeholder col-5"></span>
                        <span class="placeholder col-5"></span>
                        <span class="placeholder col-3"></span>
                        <span class="placeholder col-3"></span>
                        <span class="placeholder col-1"></span>
                        <span class="placeholder col-4"></span>
                        <span class="placeholder col-2"></span>
                        <span class="placeholder col-3"></span>
                    </p>
                </div>
                <div class="row">
                <div class="col placeholder-wave">
                    <span class="placeholder col-3"></span>
                </div>
                <div class="col text-end">
                    <p class="placeholder col-6"></p>
                </div>
                </div>
            </div>
            </div>
            `
        }
            const delay = 1570; // Delay to render entries in miliseconds
            setTimeout(async () => {
                // Clear the placholders 
                body.innerHTML = "";

                // Fetch the actual entries and render them
                await renderEntries(entries, '#mainBody');
            }  , delay)
        } catch(TypeError){
            console.log("Everything is Fine🙂, search page loaded")
        }
        // Find the number of entries in the info JSON 
        let entryCount = Object.keys(entries).length;

        // Find all delete icons and make the ready for deletion
        let deleteButtons = document.querySelectorAll('.deleteIcon');
        
        for (let deleteButton of deleteButtons){
            deleteButton.addEventListener('click', function (event){
                // Find which button was clicked
                deleteButton = event.target;
                
                // Navigate up the DOM tree and delte that row
                card = deleteButton.closest('.infoCard');

                // API to delete the entry from the database 
                const time = card.querySelector('.time').innerHTML;
                const mood = card.querySelector('.mood').innerHTML;

                fetch("/delete",{
                    method: "POST", 
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        del_time : time,
                        del_mood : mood 
                    })
                });

                // Delete the entry card client side
                card.remove();
            });        
        }
        
        // Everything statisticall will be done here 
        try { 
            document.querySelector("#entryCount").innerHTML += `<div class="col text-start py-2 stat"> 
                                                                    Total Entries: <span class="statistic"> ${entryCount} </span>
                                                                </div>`;

            const ctx = document.getElementById("pieChart");            
            const statsResponse = await fetch("/stats");
            const stats = await statsResponse.json();

            // Find the most frequent mood by iterating over each frequency in the times array
            const index = stats.times.indexOf(Math.max(...stats.times));
            // Get the mood from moods array using the index
            const mostCommon = stats.moods[index];
            document.querySelector("#mostCommon").innerHTML += ` <span class="statistic"    uu>${mostCommon}</span>`;

            // Dynamically get the theme colors of each mood using the getBGcolor function 
            const colors = new Array(stats.moods.length);
            for (let i = 0; i < stats.moods.length; i++){
                // Populate colors array with the custom color for each mood
                colors[i] = getBGcolor(stats.moods[i]);

                // Calculate the percntage of each mood
                stats.moods[i] += " - " + Math.round((stats.times[i]/entryCount) * 100) + "%";
            }
            const config = {
                type: 'doughnut',
                data:{
                    labels: stats.moods,
                    datasets: [{
                        labels: stats.moods,
                        data: stats.times,
                        backgroundColor: colors, // Use of dynamically generated array for colors
                        hoverOffset: 10,
                        spacing: 0,
                        borderDashOffset: 3,
                        weight: 1,
                        borderJoinStyle: 'miter'
                    }],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true, 
                    aspectRatio: 1,
                }
            };
            
            new Chart(ctx, config);
            
            // Find the number of words in the most verbose entry
            const longestEntry = stats.longest_entry[0].entry;
            const IV = stats.longest_entry[0].iv;
            const longest_entry = await decryptEntry(longestEntry, IV);
            let wordCount = 1;
            for (let j = 0; j < longest_entry.length; j++){
                if (longest_entry[j] == ' '){
                    wordCount++;
                }
            }
            // Add this word count for user to see
            document.getElementById("wordCount").innerHTML += `<span class="statistic"> ${wordCount} words </span>`;
            
            // Render the most verbose entry
            renderEntries(stats.longest_entry,"#longestEntry");
        } catch (TypeError) {
            console.log("Everthing is fine, not on stats page yet🙂")
        }  
}); 