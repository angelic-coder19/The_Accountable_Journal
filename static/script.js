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

    var entry = '';
    
    // Get the entry from the text area and append it to the empty string
    document.querySelector('textarea').addEventListener('keyup', function() {
        entry = document.querySelector('textarea').value;
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
        let month = getStringDate(entry["month"]); // Convert the integar date to human readalbe month
        let time = entry["time"];
        let year = entry["year"];
        let cipherEntry = entry["entry"]; // Base 64 string encrypted Entry 
        let iv = entry["iv"];             // Base 64 string initialization vector
        let mood = entry["mood"];

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
        console.log(plainText);
    }
}); 