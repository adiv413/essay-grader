function change() {
  var url = $("#essayForm").attr("data-assignments-url");
  var assignmentId = $("#id_teachers").val();
  $.ajax({
    url: url,
    data: {
      'teacher': assignmentId
    },
    success: function (data) {
      $("#id_assignment").html(data);
   }
  });
  setTimeout(checkDueDate, 100);
}
function checkDueDate(){
    var id = document.getElementById("id_assignment").value;
    console.log("assignment: " + id);
    var time = "";
    $.ajax({
    url: "/ajax/validate",
    data: {
      'pk': id
    },
    success: function (data) {
      if (data.expired){
        document.getElementById("id_body").disabled = true;
        document.getElementById("id_title").disabled = true;
        document.getElementById("id_citation_type").disabled = true;
        document.getElementById("btn").disabled = true;
        $("#error").html("Sorry, but this assignment is expired");
      } else {
        document.getElementById("id_body").disabled = false;
        document.getElementById("id_title").disabled = false;
        document.getElementById("id_citation_type").disabled = false;
        document.getElementById("btn").disabled = false;
        $("#error").html("");
      }
   }
  });
}
$("#id_assignment").change(checkDueDate);
$(window).on("load",change);
$("#id_teachers").change(change);
window.setInterval(checkDueDate,5000)