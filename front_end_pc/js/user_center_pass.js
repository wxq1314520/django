var vm=new Vue({
    el:'#update',
    data:{
        host,
        user_id:sessionStorage.user_id ||localStorage.user_id,
        token:sessionStorage.token || localStorage.token,
        username:sessionStorage.username || localStorage.username,

        erro_oldpassword:false,
        error_newpwd:false,
        error_newpwdagin:false,

        oldpassword:'',
        newpwd:'',
        newpwdagin:'',

    },methods:{

    }
})