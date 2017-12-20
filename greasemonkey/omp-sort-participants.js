// ==UserScript==
// @name     LangSciPress, order participants alphabetically
// @include  http://langsci-press.org/workflow/*
// @require  http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js
// @require  https://gist.github.com/raw/2625891/waitForKeyElements.js
// @grant    GM_addStyle
// ==/UserScript==
/*- The @grant directive is needed to work around a design change
    introduced in GM 1.0.   It restores the sandbox.
*/

function changeOrder (jNode) {   
  var my_options = $("#userId option");
  my_options.sort(function(a,b) {
        //retrieve last name and sort accordingly
        var aarray = a.text.split(' ');
        var alastname = aarray[aarray.length - 1];
        var barray = b.text.split(' ');
        var blastname = barray[barray.length - 1]
        if (alastname > blastname) return 1;
        else if (alastname < blastname) return -1;
        else return 0
    })   
//   empty initial selection and append
   $("#userId").empty().append( my_options );
}


function setChanger (jNode) {
//   attach the sorting event to the user group dropdown
// signal status by color  
  $("#userGroupId").css({'background':'red'});     
  $("#userGroupId").blur( function(){changeOrder(jNode)  
})
}

                         
// the participant list is loaded via AJAX. 
//We wait for the <select> to appear and then attach an event to it                         
waitForKeyElements ("#userGroupId", setChanger);
