function addComment(pk){
    var url = "ajax/comment/";
    var body = document.getElementById("id_Comment").value;
    var email = document.getElementById("info").getAttribute("user");
    if (body != ""){
    $.ajax({
        url: url,
        data: {
          'pk': pk,
          'body': body,
          'email':email,
        },
        success: function (data) {
       }
    });
    }
    setTimeout(1, showEssay(pk));
}
function showEssays(){
    var pk = $("#assignment").val();
    if (pk != ""){
        var url = document.getElementById("assignment").getAttribute("url");
        url = url.replace('123', pk);
        $.ajax({
            url: url,
            data:{},
            success: function (data) {
              $("#graded").html(data);
           }
        });
        url = url.replace("graded", "not_graded");
        $.ajax({
            url: url,
            data:{},
            success: function (data) {
              $("#not_graded").html(data);
           }
        });
    } else {
        $("#not_graded").html("");
        $("#graded").html("");
        $("#essay_box").html("");
    }
}
function showEssay(i) {
    var url = $("#essay_box").attr("thing");
    $.ajax({
        url: url,
        data: {
          'pk': i
        },
        success: function (data) {
          $("#essay_box").html(data);
       }
      });
}
function gradeAll() {
    var i = $("#assignment").val();
    var url = $("#thingy").attr("stuff");
    console.log(i);
    url = url.replace("123", i);
    console.log(url);
    $.ajax({
        url: url,
        success: function (data) {
          $("#graded").html(data);
          $("#not_graded").html("<h3>None of your students submitted an essay for this assignment</h3><hr>");
       }
    });
    var g = document.getElementById('graded');
    var ng = document.getElementById('not_graded');
}
function toggleType() {
    var g = document.getElementById('graded');
    var ng = document.getElementById('not_graded');
    $("#essay_box").html("");
    if (g.style.display == "none"){
        g.style.display = "initial";
        ng.style.display = "none";
    } else {
        g.style.display = "none";
        ng.style.display = "initial";
    }
}
function onLoad(){
  showEssays();
  var a = document.getElementsByClassName('assignment_list');
  for (var i = 0; i < a.length; i++) {
    a[i].style.height = window.clientHeight;
  }
  var b = document.getElementById('graded');
  b.style.display = "none";
}
function gradeEssay() {
    var url = $("#add_grade").attr("url");
    var n = $("#numerator").val();
    var d = $("#denominator").val();
    if (n!="" && d!="" && d!="0"){
        $.ajax({
            url: url,
            data: {
              'numerator':n,
              'denominator':d
            },
            success: function (data) {
           }
        });
        $("#essay_box").html("");
    }
}
window.addEventListener('load', onLoad());
$("#assignment").change(showEssays);
setInterval(showEssays, 1000);