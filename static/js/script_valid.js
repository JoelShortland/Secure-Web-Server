function get_private_key(){
    var xhttp = new XMLHttpRequest();
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
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 404) {
            return;
       }
       if (this.readyState == 4 && this.status == 200) {
           alert(xhttp.responseText);
           var res = JSON.parse(xhttp.responseText);
           var chipter = res.chipter;
           var iv = res.iv;
           var pass = localStorage.getItem("password");
           var key = toint8Array(pass,32);
           iv = toint8Array(iv,16);
           var chipterBytes = convertHex.toBytes(chipter);
           var aesCbc = new ModeOfOperationCBC(key,iv);
           var decryptedBytes = aesCbc.decrypt(chipterBytes);
           localStorage.setItem("private_key",convertUtf8.fromBytes(decryptedBytes).replace(/\0/g,""));
           return;
       }
    };
    xhttp.open("post", "get_private_key", false);
    xhttp.send("password=" +  localStorage.getItem("password"));
}
get_private_key();