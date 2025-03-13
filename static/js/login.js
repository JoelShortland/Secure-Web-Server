function storePassWord_and_hash(){
    localStorage.setItem("password",document.getElementById("password").value);
    var pass = document.getElementById("password").value;
    var uname = document.getElementById("uname").value;
    var hash = sha256.create();
    hash.update(pass+uname);
    var hashed_pass = hash.hex();
    document.getElementById("password").value = hashed_pass;
}
document.getElementById("submit").addEventListener("click",storePassWord_and_hash);