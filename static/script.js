document.addEventListener('DOMContentLoaded', async function(){

    var entry = '';
    
    // Get the entry from the text area and append it to the empty string
    document.querySelector('textarea').addEventListener('keyup', function() {
        entry += document.querySelector('textarea').value;
    });

    // document.querySelector('textarea').innerHTML = entry;

    // Listen for the save button to be clicked to encrypt and send the entry to the server
    document.querySelector('.submit').addEventListener('click', async function() {
    
        // Check if the entry is empty
        if (!String(entry).trim()){
            alert("Please make an entry");
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

        // Find the mood value that was selected 
        mood = document.querySelector('input[name="mood"]:checked').value;
        
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
        
        console.log(base64string);
        console.log(base64IV);

    });

    
});