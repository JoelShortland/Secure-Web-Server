document.getElementById("submit_button").addEventListener("click", getRsaKeys);
function send_register_msg(){
    var pass = document.getElementById("pass").value;
    var uname = document.getElementById("username").value;
    var pri_key = localStorage.getItem("pri_key"); 
    pri_key = pri_key +  new Array(16 - pri_key.length % 16 + 1).join("\0");
    var hash = sha256.create();
    hash.update(pass+uname);
    var hashed_pass = hash.hex();
    var s_iv = randStr(16);
    var key = toint8Array(pass,32);
    var iv = toint8Array(s_iv,16);
    var plainBytes = convertUtf8.toBytes(pri_key);
    var aesCbc = new ModeOfOperationCBC(key,iv);
    var encryptedBytes = aesCbc.encrypt(plainBytes);
    var encrypted_secret_key = convertHex.fromBytes(encryptedBytes);
    document.getElementById("pass").value = hashed_pass;
    document.getElementById("iv").value = s_iv;
    document.getElementById("aes_prikey").value = encrypted_secret_key;
    document.getElementById("pubkey").value = localStorage.getItem("pub_key");
    document.register.submit();
}

function randStr(n){
    var chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678';  
    var maxPos = chars.length;
    var str = '';
    for (i = 0; i < n; i++) {
        str += chars.charAt(Math.floor(Math.random() * maxPos));
    }
    return str;
}
function toint8Array(string,len){
    var arr = new Array();
    for(var i = 0; i < 32 && i < len; i++){
        if (i < string.length)
            arr.push(string.charAt(i).charCodeAt());
        else
            arr.push(0)
    }
    return arr;
}
function getRsaKeys(){
    function ab2str(buf) {
        return String.fromCharCode.apply(null, new Uint8Array(buf));
      }
    window.crypto.subtle.generateKey(
        {
            name: "RSA-OAEP",
            modulusLength: 2048, //can be 1024, 2048, or 4096
            publicExponent: new Uint8Array([0x01, 0x00, 0x01]),
            hash: {name: "SHA-512"}, //can be "SHA-1", "SHA-256", "SHA-384", or "SHA-512"
        },
        true, //whether the key is extractable (i.e. can be used in exportKey)
        ["encrypt", "decrypt"] //must be ["encrypt", "decrypt"] or ["wrapKey", "unwrapKey"]
    ).then((keypair) => {
        window.crypto.subtle.exportKey(
            "pkcs8", 
            keypair.privateKey 
        ).then((exported)=>{
            let exportedAsString = ab2str(exported);
            let exportedAsBase64 = window.btoa(exportedAsString);
            let pemExported = `-----BEGIN PRIVATE KEY-----\n${exportedAsBase64}\n-----END PRIVATE KEY-----`;
            localStorage.setItem("pri_key",pemExported);
        }).then(() => {
        window.crypto.subtle.exportKey(
            "spki",
            keypair.publicKey 
        ).then((exported)=>{
            let exportedAsString = ab2str(exported);
            let exportedAsBase64 = window.btoa(exportedAsString);
            let pemExported = `-----BEGIN PUBLIC KEY-----\n${exportedAsBase64}\n-----END PUBLIC KEY-----`;
            localStorage.setItem("pub_key",pemExported);
        }).then(() => {send_register_msg();})
    })
    })
}