load();
check_msg();
document.getElementById("submit_button").addEventListener("click", encrypt);
var aim_public_key;
function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
         }
         if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
         }
     }
    return "";
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
function friend_click(cur){
    id = cur.getElementsByClassName("friend_name")[0].innerHTML;
    document.getElementById("aim").value = id;
    alert(id);
}
function load(){
    var sta = document.getElementById("Status");
    var ifsuccess = (getCookie("success") == "True");
    if(ifsuccess == null){
        return;
    }
    if (ifsuccess){
        sta.innerHTML = "Success";
        }
    else{
        sta.innerHTML = "Fail, the input is too long, max 250 words";
    }
}
const sleep = (delay) => new Promise((resolve) => setTimeout(resolve, delay));
function check_msg(){
    if(getCookie("id") == "") {alert("wait");return;}
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 204) {
            //sleep(1000);
            //check_msg();
            return;
       }
       if (this.readyState == 4 && this.status == 200) {
           var message = xhttp.responseText;
           console.warn(xhttp.responseText);
           var messages = message.split("\0");
           for(var i = 1; i < parseInt(messages[0]) * 5 + 1; i+=5){
               var chipter = messages[i+1];
               var chipter_AES_key = messages[i+2];
               var iv = Uint8Array.from(messages[i+3].split("-"));
               var signature = messages[i+4];
               var sender = messages[i];
               get_public_key(sender);
               var plain_AES_key = Uint8Array.from(decrypt(chipter_AES_key).split("-"));
               var chipterBytes = convertHex.toBytes(chipter);
               var aesCbc = new ModeOfOperationCBC(plain_AES_key,iv);
               var decryptedBytes = aesCbc.decrypt(chipterBytes);
               var plain = convertUtf8.fromBytes(decryptedBytes).replace(/\0/g,"");
               var verify = new JSEncrypt();
               verify.setPublicKey(localStorage.getItem("aim_pub"));
		       var verified = verify.verify(chipter + "\0" + chipter_AES_key + "\0" + messages[i+3], signature, sha256);
               var alerts;
               if (! verified){
                    alerts = "\nWarning: failed to check signature of the message, it may send by malignant attacker."
               }
               else{
                   alerts = ""
               }
               var msg = "from:\n" + sender + alerts + "\ntext:\n" + plain;
               alert(msg);
           }
           //sleep(1000);
           //check_msg();
           return;
       }
    };
    xhttp.open("GET", "check_message", true);
    xhttp.send()
    
}

function get_public_key(user){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 404) {
            return;
       }
       if (this.readyState == 4 && this.status == 200) {
           aim_public_key = xhttp.responseText
           localStorage.setItem("aim_pub",xhttp.responseText);
           return;
       }
    };
    xhttp.open("post", "message", false);
    xhttp.send("aim_user=" + user);
}

function encrypt(){
    get_public_key(document.getElementById("aim").value);
    var plaintext = document.getElementById("input").value;
    var AES_key_array = new Uint8Array(32);
    window.crypto.getRandomValues(AES_key_array);
    var AES_iv_array = new Uint8Array(16);
    window.crypto.getRandomValues(AES_iv_array);
    plaintext = plaintext +  new Array(16 - plaintext.length % 16 + 1).join("\0");
    var plainBytes = convertUtf8.toBytes(plaintext);
    var aesCbc = new ModeOfOperationCBC(AES_key_array,AES_iv_array);
    var encryptedBytes = aesCbc.encrypt(plainBytes);
    var encrypted_text = convertHex.fromBytes(encryptedBytes);
    var RSA_encrypt = new JSEncrypt();
    RSA_encrypt.setPublicKey(aim_public_key);
    var chipter_AES_key = RSA_encrypt.encrypt(AES_key_array.join('-'));
    chipter = encrypted_text +"\0" + chipter_AES_key + "\0" + AES_iv_array.join('-');
    var encrypt = new JSEncrypt();
	encrypt.setPrivateKey(localStorage.getItem("private_key"));
    var signature = encrypt.sign(chipter, sha256, "sha256");
    chipter = chipter + '\0' + signature
    document.getElementById("input").value = chipter;
    console.log(chipter);
    return true;
}
function decrypt(chipter_text){
    var RSA_decrypt = new JSEncrypt();
    RSA_decrypt.setPrivateKey(localStorage.getItem("private_key"));
    var plain = RSA_decrypt.decrypt(chipter_text);
    return plain;
}

