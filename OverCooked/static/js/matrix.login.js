function showDialog(title,msg) {
	$("#myModal").find(".modal-header h3").html(title);
    $("#myModal").attr('class','modal');
    $("#myModal").find(".modal-body p").html(msg);
    setTimeout(function(){
        $("#myModal").attr('class','modal hide');
    },3000);
}

function keydown(e)
{
    var e = e||event;
    var currKey = e.keyCode||e.which||e.charCode;
    if(currKey == 13)
    {
        checkLogin();
    }
}

function checkLogin(){
    var username = $("input[name=username]").val();
    var password = $("input[name=password]").val();

    if ($.trim(username) == "" ||　$.trim(password) == "") {
        return false;
    }

    $.ajax({    
        url: '/login/',
        data: {
            username : username,
            password : password
        },
        type:'post',   
        success:function(data) {

        },    
        error : function() {

        }
    });
}

$(document).ready(function(){


    if($.browser.msie == true && $.browser.version.slice(0,3) < 10) {
        $('input[placeholder]').each(function(){ 
	        var input = $(this);       
	       
	        $(input).val(input.attr('placeholder'));
	               
	        $(input).focus(function(){
	             if (input.val() == input.attr('placeholder')) {
	                 input.val('');
	             }
	        });
	       
	        $(input).blur(function(){
	            if (input.val() == '' || input.val() == input.attr('placeholder')) {
	                input.val(input.attr('placeholder'));
	            }
	        });
	    });    
    }

    $("#modelClose").click(function(){
        $("#myModal").attr('class','modal hide');
    });
    
});