function check_username2(){

    var flag = false;
    var usernameElement = document.querySelector();

}
//验证用户名：必填，必须是数字字母组成，长度在6-12字符
function check_username(){
    var flag =false;
    var usernameElement = document.querySelector("input[name='username']");//获得用户名元素控件<input />
    var username = usernameElement.value;  //获得用户名的值
    var username_tip= usernameElement.nextElementSibling;

     
    if(username == null || username ==""){
        username_tip.innerText="用户名必填";
    }else if( !/^[0-9A-Za-z]{6,12}$/.test(username)  ){
        username_tip.innerText="用户名必须是数字字母组成，长度在6-12字符"
    } else{
        username_tip.innerText="";
        flag = true;
    }
    return flag;
}