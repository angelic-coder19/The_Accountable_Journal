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

    var entry = '';
    
    // Get the entry from the text area and append it to the empty string
    document.querySelector('textarea').addEventListener('keyup', function() {
        entry += document.querySelector('textarea').value;
    });

    // Listen for the save button to be clicked to encrypt and send the entry to the server
    document.querySelector('.submit').addEventListener('click', async function() {
        // Find the mood value that was selected 
        mood = document.querySelector('input[name="mood"]:checked').value;
            
        // Check if the entry is empty
        if (!String(entry).trim() || !mood){
            alert("Please make an entry and select a mood");
            return;
        }   

        
        // Generate a cryptographic key 
        const key = await crypto.subtle.generateKey(
            {name: "AES-GCM", length: 256}, // Algorithm
            true,                           // extractable
            ["encrypt", "decrypt"]          // list of k
        );

        console.log(key);
        
        // Encode the entry into bytes
        const bytes = new TextEncoder().encode(entry);

        // Generate a random initialization vector(iv)
        const IV = crypto.getRandomValues(new Uint8Array(12));

        // Ecrypt the entry to get back an arraybuffer 
        let encryptedEntry = await crypto.subtle.encrypt({name: "AES-GCM", iv: IV}, key, bytes);
        
        // Convert the encryptedEntry in the arraybuffer into Base64
        let buffer = new Uint8Array(encryptedEntry);

        let binaryString = '';
        for (let i = 0; i < buffer.length; i++){
            binaryString += String.fromCharCode(buffer[i]);
        }

        // Convert the binary string to ascii
        let base64string = btoa(binaryString);

        // Convert the iv to Base64
        let binaryIV = '';
        for (let j = 0; j < IV.length; j++){
            binaryIV += String.fromCharCode(IV[j]);
        }

        let base64IV = btoa(binaryIV);

        // Send the ecrypted entry, iv and mood to the database on the server    
        fetch('/home', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                entry : base64string,
                iv : base64IV,
                mood : mood })
        });
        
    });

    // Request for information from the server for decryption
    let response = await fetch("/search");
    let entries = await response.json(); // Get a list of json objects from each entry

    // Find the table element from the DOM
    const table = document.querySelector(".table")

    // Iterate over each json object and collect info
    for (let entry of entries){
        let day = entry["day"];
        let month = entry["month"];
        let time = entry["time"];
        let year = entry["year"];
        let cipherEntry = entry["entry"];
        let iv = entry["iv"];
        let mood = entry["mood"];


    }

});