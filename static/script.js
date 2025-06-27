document.addEventListener('DOMContentLoaded', async function(){
    
    // Get the entry from the text area
    document.querySelector('textarea').addEventListener('keyup', function() {
        var entry = document.querySelector('textarea').value;
        console.log(entry);
    });

    // Listen for the save button to be clicked to encrypt and send the entry to the server
    document.querySelector('.submit').addEventListener('click', async function() {
        // Check if the entry is empty
        if (!entry.trim()){
            alert("Please make an entry")
            return;
        }
        
        
        // Generate a cryptographic key 
        const key = await crypto.subtle.generateKey(
            {name: "AES-GCM", length: 256}, // Algorithm
            true,                           // extractable
            ["encrypt", "decrypt"]          // list of k
        );

        
        // Encode the entry into bytes
        const bytes = TextEncoder().encode(entry);

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

        console.log(key);
    });
});